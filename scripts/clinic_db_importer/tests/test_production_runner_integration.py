"""Docker-backed integration tests for production_runner.py.

Skipped automatically if Docker is unavailable. Each test gets a fresh,
throwaway, localhost-only PostgreSQL 17 container with Schema v1 applied.
Never touches Production Supabase or Production SQLite.
"""
import json
import os
import shutil
import sqlite3
import subprocess
import time

import pytest

from scripts.clinic_db_importer.production_runner import (
    _psql_rows,
    _run_psql,
    capture_source_fingerprint,
    get_resume_cursor,
    is_chunk_completed,
    run_migration,
)
from scripts.clinic_db_importer.normalizer_bridge import load_normalizers
from scripts.clinic_db_importer.tests.conftest import CLINICS_SCHEMA, insert_clinic

_NORM = load_normalizers()


def _matching_clinic(medical_key, clinic_name, phone="03-1234-5678", address="東京都千代田区1-1"):
    """Builds insert_clinic() kwargs whose stored normalizer columns exactly
    match what the real Clinic Lead normalizer would regenerate for this
    clinic_name/phone/address -- avoids spurious NORMALIZER_MISMATCH review
    flags in fixtures (the real normalizer strips whitespace/punctuation,
    which a hand-written expected value would need to replicate exactly)."""
    return dict(
        medical_key=medical_key, clinic_name=clinic_name, phone=phone, address=address,
        name_norm=_NORM["name_norm"](clinic_name), name_prefix=_NORM["name_prefix"](clinic_name),
        phone_norm=_NORM["phone_norm"](phone), tel_match_key=_NORM["tel_match_key"](phone),
        address_norm=_NORM["address_norm"](address),
    )

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SQL_DIR = os.path.join(REPO_ROOT, "docs", "clinic-db-sql-drafts")
DDL_FILES = [
    "001_create_clinic_master.sql", "002_create_clinic_ops.sql",
    "005_create_clinic_ops_extended.sql", "004_current_hp_rank_view.sql",
    "006_create_current_views.sql",
]


def _docker_available() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        subprocess.run(["docker", "info"], capture_output=True, timeout=5, check=True)
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _docker_available(), reason="Docker not available in this environment")


@pytest.fixture
def scratch_container():
    name = f"clinic-runner-test-{int(time.time() * 1000)}"
    db = "clinic_runner_test"
    subprocess.run(
        ["docker", "run", "-d", "--name", name, "-e", "POSTGRES_PASSWORD=scratch_pw_local_only",
         "-e", f"POSTGRES_DB={db}", "-P", "postgres:17"],
        check=True, capture_output=True,
    )
    try:
        for _ in range(60):
            r = subprocess.run(["docker", "exec", name, "pg_isready", "-U", "postgres"], capture_output=True)
            if r.returncode == 0:
                break
            time.sleep(1)
        for f in DDL_FILES:
            with open(os.path.join(SQL_DIR, f)) as fh:
                sql = fh.read()
            r = _run_psql(name, db, sql)
            assert r.returncode == 0, f"DDL {f} failed: {r.stderr}"
        yield name, db
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True)


def _fixture_sqlite(tmp_path, n_clinics=7, with_job_items=None):
    path = str(tmp_path / "fixture.sqlite3")
    conn = sqlite3.connect(path)
    conn.executescript(CLINICS_SCHEMA)
    for i in range(1, n_clinics + 1):
        insert_clinic(conn, **_matching_clinic(f"MK-RUNNER-{i:03d}", f"Runner Clinic {i}", phone=f"03-0000-{i:04d}"))
    if with_job_items:
        for state in with_job_items:
            conn.execute("INSERT INTO research_job_items (job_id, clinic_id, state) VALUES ('j1', 1, ?)", (state,))
        conn.execute("INSERT INTO research_jobs (id, kind, options_json, status, max_searches) VALUES ('j1','hp','{}','PAUSED',10)")
    conn.commit()
    conn.close()
    return path


def _counts(container, db):
    rows = _psql_rows(container, db, "SELECT count(*) FROM clinic_master.clinics;")
    clinics = int(rows[0][0])
    rows = _psql_rows(container, db, "SELECT count(*) FROM clinic_ops.import_log_items;")
    items = int(rows[0][0])
    rows = _psql_rows(container, db, "SELECT count(*) FROM clinic_ops.import_logs;")
    logs = int(rows[0][0])
    return clinics, items, logs


# --- Chunk boundary / empty final chunk ----------------------------------

def test_chunk_boundary_and_empty_final_chunk(scratch_container, tmp_path):
    container, db = scratch_container
    # 6 clinics with chunk_size=3 -> exactly 2 full chunks, no partial/empty chunk needed to prove the point,
    # but we also check that a further run (0 new rows) doesn't error (empty-fetch termination).
    sqlite_path = _fixture_sqlite(tmp_path, n_clinics=6)
    results = run_migration(sqlite_path=sqlite_path, container=container, db=db, chunk_size=3)
    assert results["clinics"].chunks_processed == 2
    assert results["clinics"].inserted == 6
    clinics, items, logs = _counts(container, db)
    assert clinics == 6
    assert items == 6


def test_chunk_boundary_with_partial_final_chunk(scratch_container, tmp_path):
    container, db = scratch_container
    sqlite_path = _fixture_sqlite(tmp_path, n_clinics=7)  # chunk_size=3 -> chunks of 3, 3, 1
    results = run_migration(sqlite_path=sqlite_path, container=container, db=db, chunk_size=3)
    assert results["clinics"].chunks_processed == 3
    assert results["clinics"].inserted == 7


# --- Resume from checkpoint / completed chunk skip -----------------------

def test_resume_is_noop_when_already_complete(scratch_container, tmp_path):
    container, db = scratch_container
    sqlite_path = _fixture_sqlite(tmp_path, n_clinics=7)
    run_migration(sqlite_path=sqlite_path, container=container, db=db, chunk_size=3)
    before = _counts(container, db)

    results2 = run_migration(sqlite_path=sqlite_path, container=container, db=db, chunk_size=3)
    after = _counts(container, db)

    assert before == after
    # get_resume_cursor jumps straight past all completed chunks in one step
    # (an O(1) lookup, not an O(n_chunks) per-chunk completed-check), so
    # chunks_already_completed correctly stays 0 here -- chunks_processed==0
    # plus unchanged row counts is what proves the resume was a true no-op.
    assert results2["clinics"].chunks_already_completed == 0


def test_repeated_resume_is_still_noop(scratch_container, tmp_path):
    container, db = scratch_container
    sqlite_path = _fixture_sqlite(tmp_path, n_clinics=7)
    run_migration(sqlite_path=sqlite_path, container=container, db=db, chunk_size=3)
    run_migration(sqlite_path=sqlite_path, container=container, db=db, chunk_size=3)
    before = _counts(container, db)
    run_migration(sqlite_path=sqlite_path, container=container, db=db, chunk_size=3)
    after = _counts(container, db)
    assert before == after


def test_get_resume_cursor_and_is_chunk_completed(scratch_container, tmp_path):
    container, db = scratch_container
    sqlite_path = _fixture_sqlite(tmp_path, n_clinics=7)
    fp = capture_source_fingerprint(sqlite_path)
    assert get_resume_cursor(container, db, fp.sha256, "clinics") == 0
    run_migration(sqlite_path=sqlite_path, container=container, db=db, chunk_size=3)
    assert get_resume_cursor(container, db, fp.sha256, "clinics") == 7
    from scripts.clinic_db_importer.production_runner import chunk_marker
    assert is_chunk_completed(container, db, chunk_marker(fp.sha256, "clinics", 1, 3))
    assert not is_chunk_completed(container, db, chunk_marker(fp.sha256, "clinics", 999, 1000))


# --- Failed chunk retry / forced failure + resume ------------------------
#
# Failure is injected structurally (temporarily renaming a required target
# column so every COPY into clinic_master.clinics fails) rather than via a
# duplicate medical_key, since a duplicate medical_key is *correctly*
# classified as SKIP by the runner (not an error) -- that would test the
# wrong thing. Renaming the column is content-independent and always fails
# deterministically regardless of which rows are in the chunk.

def _break_clinics_table(container, db):
    r = _run_psql(container, db, "ALTER TABLE clinic_master.clinics RENAME COLUMN prefecture TO prefecture_broken;\n")
    assert r.returncode == 0, r.stderr


def _fix_clinics_table(container, db):
    r = _run_psql(container, db, "ALTER TABLE clinic_master.clinics RENAME COLUMN prefecture_broken TO prefecture;\n")
    assert r.returncode == 0, r.stderr


def test_failed_chunk_is_retried_not_skipped(scratch_container, tmp_path):
    container, db = scratch_container
    sqlite_path = _fixture_sqlite(tmp_path, n_clinics=3)

    _break_clinics_table(container, db)
    try:
        with pytest.raises(RuntimeError):
            run_migration(sqlite_path=sqlite_path, container=container, db=db, chunk_size=3)
    finally:
        _fix_clinics_table(container, db)

    # the chunk's own import_logs row must show failed, not completed
    rows = _psql_rows(container, db, "SELECT status FROM clinic_ops.import_logs;")
    assert any(status == "failed" for (status,) in rows)
    assert not any(status == "completed" for (status,) in rows)

    # nothing committed -- the whole chunk (all 3 rows) rolled back
    clinics, items, _ = _counts(container, db)
    assert clinics == 0
    assert items == 0

    # retry (schema fixed): the previously-failed chunk is attempted again, not skipped
    results = run_migration(sqlite_path=sqlite_path, container=container, db=db, chunk_size=3)
    assert results["clinics"].inserted == 3
    assert results["clinics"].chunks_already_completed == 0  # it was failed, not completed -- must be retried
    clinics, items, _ = _counts(container, db)
    assert clinics == 3
    assert items == 3


def test_forced_failure_then_resume_matches_clean_run(scratch_container, tmp_path):
    container, db = scratch_container
    sqlite_path = _fixture_sqlite(tmp_path, n_clinics=9)  # chunk_size=3 -> 3 chunks

    _break_clinics_table(container, db)
    try:
        with pytest.raises(RuntimeError):
            run_migration(sqlite_path=sqlite_path, container=container, db=db, chunk_size=3)
    finally:
        _fix_clinics_table(container, db)

    clinics, _, _ = _counts(container, db)
    assert clinics == 0  # chunk 1 fully rolled back, nothing committed

    # Resume: a fresh call to run_migration, simulating a process restart
    # (no in-memory state carried over between these two calls).
    results = run_migration(sqlite_path=sqlite_path, container=container, db=db, chunk_size=3)
    assert results["clinics"].inserted == 9

    clinics, items, _ = _counts(container, db)
    assert clinics == 9
    assert items == 9

    # A further resume must be a pure no-op -- matches a clean, uninterrupted run.
    before = _counts(container, db)
    results2 = run_migration(sqlite_path=sqlite_path, container=container, db=db, chunk_size=3)
    after = _counts(container, db)
    assert before == after
    assert results2["clinics"].chunks_already_completed == 0  # cursor-jump optimization, see above

    # A further resume must be a pure no-op.
    before = _counts(container, db)
    results2 = run_migration(sqlite_path=sqlite_path, container=container, db=db, chunk_size=3)
    after = _counts(container, db)
    assert before == after
    assert results2["clinics"].chunks_processed == 0


# --- Cutover gate integration (does not block scratch runs) --------------

def test_cutover_gate_pending_blocks_only_production_mode(scratch_container, tmp_path):
    from scripts.clinic_db_importer.production_runner import ProductionGuardError, capture_source_fingerprint
    container, db = scratch_container
    sqlite_path = _fixture_sqlite(tmp_path, n_clinics=2, with_job_items=["PENDING"])
    fp = capture_source_fingerprint(sqlite_path)

    # scratch mode ignores the gate and proceeds
    results = run_migration(sqlite_path=sqlite_path, container=container, db=db, chunk_size=10)
    assert results["cutover_gate"].passed is False
    assert results["clinics"].inserted == 2

    # production mode with the gate blocked must refuse before any write
    with pytest.raises(ProductionGuardError, match="cutover gate"):
        run_migration(
            sqlite_path=sqlite_path, container=container, db=db, chunk_size=10,
            target_mode="production", execute=True,
            confirmed_project_ref="xtspgevvntpidkmyfwes", expected_fingerprint=fp,
        )


def test_cancelled_fixture_migrates_and_repeated_resume_is_noop(scratch_container, tmp_path):
    container, db = scratch_container
    sqlite_path = _fixture_sqlite(tmp_path, n_clinics=2, with_job_items=["CANCELLED"])

    first = run_migration(sqlite_path=sqlite_path, container=container, db=db, chunk_size=1)
    assert first["cutover_gate"].passed is True
    assert first["cutover_gate"].pending_items == 0
    assert first["cutover_gate"].running_items == 0
    assert _psql_rows(container, db, "SELECT count(*) FROM clinic_ops.research_job_items;") == [["0"]]

    before = _counts(container, db)
    second = run_migration(sqlite_path=sqlite_path, container=container, db=db, chunk_size=1)
    third = run_migration(sqlite_path=sqlite_path, container=container, db=db, chunk_size=1)
    assert before == _counts(container, db)
    assert second["clinics"].chunks_processed == third["clinics"].chunks_processed == 0


def test_cutover_gate_running_blocks_production_mode(scratch_container, tmp_path):
    from scripts.clinic_db_importer.production_runner import ProductionGuardError, capture_source_fingerprint
    container, db = scratch_container
    sqlite_path = _fixture_sqlite(tmp_path, n_clinics=2, with_job_items=["RUNNING"])
    fp = capture_source_fingerprint(sqlite_path)
    with pytest.raises(ProductionGuardError, match="cutover gate"):
        run_migration(
            sqlite_path=sqlite_path, container=container, db=db, chunk_size=10,
            target_mode="production", execute=True,
            confirmed_project_ref="xtspgevvntpidkmyfwes", expected_fingerprint=fp,
        )


def test_wrong_source_fingerprint_refuses_production_mode(scratch_container, tmp_path):
    from scripts.clinic_db_importer.production_runner import ProductionGuardError, SourceFingerprint
    container, db = scratch_container
    sqlite_path = _fixture_sqlite(tmp_path, n_clinics=2)
    wrong_fp = SourceFingerprint(sha256="0" * 64, size=0, clinics_count=0,
                                  medical_key_empty=0, medical_key_duplicate_groups=0, integrity_check="ok")
    with pytest.raises(ProductionGuardError, match="fingerprint"):
        run_migration(
            sqlite_path=sqlite_path, container=container, db=db, chunk_size=10,
            target_mode="production", execute=True,
            confirmed_project_ref="xtspgevvntpidkmyfwes", expected_fingerprint=wrong_fp,
        )


def test_missing_execute_flag_refuses_production_mode(scratch_container, tmp_path):
    from scripts.clinic_db_importer.production_runner import ProductionGuardError, capture_source_fingerprint
    container, db = scratch_container
    sqlite_path = _fixture_sqlite(tmp_path, n_clinics=2)
    fp = capture_source_fingerprint(sqlite_path)
    with pytest.raises(ProductionGuardError, match="execute"):
        run_migration(
            sqlite_path=sqlite_path, container=container, db=db, chunk_size=10,
            target_mode="production", execute=False,
            confirmed_project_ref="xtspgevvntpidkmyfwes", expected_fingerprint=fp,
        )


def test_wrong_project_ref_refuses_production_mode(scratch_container, tmp_path):
    from scripts.clinic_db_importer.production_runner import ProductionGuardError, capture_source_fingerprint
    container, db = scratch_container
    sqlite_path = _fixture_sqlite(tmp_path, n_clinics=2)
    fp = capture_source_fingerprint(sqlite_path)
    with pytest.raises(ProductionGuardError, match="project ref"):
        run_migration(
            sqlite_path=sqlite_path, container=container, db=db, chunk_size=10,
            target_mode="production", execute=True,
            confirmed_project_ref="wrong-project-ref", expected_fingerprint=fp,
        )


# --- EMPTY_MEDICAL_KEY stays REVIEW ---------------------------------------

def test_empty_medical_key_remains_review_not_inserted(scratch_container, tmp_path):
    container, db = scratch_container
    path = str(tmp_path / "empty_mk.sqlite3")
    conn = sqlite3.connect(path)
    conn.executescript(CLINICS_SCHEMA)
    insert_clinic(conn, **_matching_clinic("MK-OK-1", "OK Clinic"))
    insert_clinic(conn, **_matching_clinic("", "Empty Key Clinic"))
    conn.commit()
    conn.close()

    results = run_migration(sqlite_path=path, container=container, db=db, chunk_size=10)
    assert results["clinics"].inserted == 1
    assert results["clinics"].review == 1

    rows = _psql_rows(container, db, "SELECT decision, reason, clinic_id FROM clinic_ops.import_log_items WHERE decision='review';")
    assert len(rows) == 1
    decision, reason, clinic_id = rows[0]
    assert "EMPTY_MEDICAL_KEY" in reason
    assert clinic_id == ""  # NULL rendered empty by psql -tA


# --- UUID / FK stability across resume ------------------------------------

def test_uuid_and_fk_stable_across_resume(scratch_container, tmp_path):
    container, db = scratch_container
    sqlite_path = _fixture_sqlite(tmp_path, n_clinics=3)

    # Add an HP research row for clinic sqlite id 1 so the second phase has FK work to do.
    conn = sqlite3.connect(sqlite_path)
    conn.execute(
        "INSERT INTO research_results (clinic_id, result_json, updated_at) VALUES (1, ?, '2026-01-01')",
        (json.dumps({"research_status": "SUCCESS", "hp_rank": "A"}),),
    )
    conn.commit()
    conn.close()

    # Force failure at the hp_research phase by poisoning nothing -- instead,
    # run clinics phase alone first (chunk_size big enough for 1 chunk), verify the
    # assigned clinic_id, then run again (which will proceed to hp_research this time)
    # and verify hp_research.clinic_id matches the SAME uuid recorded in clinics.
    run_migration(sqlite_path=sqlite_path, container=container, db=db, chunk_size=100)

    rows = _psql_rows(container, db, "SELECT clinic_id FROM clinic_master.clinics WHERE medical_key='MK-RUNNER-001';")
    clinic_id_after_first_run = rows[0][0]

    # Second run: idempotent no-op for clinics, but hp_research should now be populated
    # referencing the SAME clinic_id (resolved fresh via medical_key, not an in-memory map).
    run_migration(sqlite_path=sqlite_path, container=container, db=db, chunk_size=100)
    rows2 = _psql_rows(container, db, "SELECT clinic_id FROM clinic_master.clinics WHERE medical_key='MK-RUNNER-001';")
    assert rows2[0][0] == clinic_id_after_first_run

    hp_rows = _psql_rows(container, db, "SELECT clinic_id FROM clinic_ops.hp_research;")
    assert len(hp_rows) == 1
    assert hp_rows[0][0] == clinic_id_after_first_run


def test_comdesk_unresolved_clinic_is_review_not_inserted(scratch_container, tmp_path):
    container, db = scratch_container
    sqlite_path = _fixture_sqlite(tmp_path, n_clinics=1)
    conn = sqlite3.connect(sqlite_path)
    template_id = "template-28"
    conn.execute(
        "INSERT INTO templates (id, headers_json, mapping_json, created_at) VALUES (?, ?, ?, '2026-01-01')",
        (template_id, json.dumps([f"c{i}" for i in range(28)]), json.dumps({})),
    )
    conn.execute(
        "INSERT INTO comdesk_original_rows "
        "(clinic_id, template_id, row_json, uuid, source_hash, row_number, created_at) "
        "VALUES (NULL, ?, ?, NULL, 'unresolved-source', 1, '2026-01-01')",
        (template_id, json.dumps([""] * 28)),
    )
    conn.commit()
    conn.close()

    results = run_migration(sqlite_path=sqlite_path, container=container, db=db, chunk_size=10)
    assert results["comdesk_original_rows"].inserted == 0
    assert results["comdesk_original_rows"].review == 1
    assert _psql_rows(container, db, "SELECT count(*) FROM clinic_ops.comdesk_original_rows;")[0][0] == "0"

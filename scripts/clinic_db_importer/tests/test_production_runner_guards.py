import sqlite3

import pytest

from scripts.clinic_db_importer.jobs_report import read_job_cutover_status
from scripts.clinic_db_importer.production_runner import (
    PRODUCTION_SUPABASE_PROJECT_REF,
    ProductionGuardError,
    SourceFingerprint,
    _assert_local_host,
    check_cutover_gate,
    chunk_marker,
    fingerprint_mismatches,
    guard_production_execute,
    CutoverGateResult,
    SOURCE_MARKER_RE,
)

FP = SourceFingerprint(
    sha256="a" * 64, size=1000, clinics_count=100, medical_key_empty=1,
    medical_key_duplicate_groups=0, integrity_check="ok",
)


def test_fingerprint_matches_itself():
    assert fingerprint_mismatches(FP, FP) == []


def test_fingerprint_detects_sha_mismatch():
    other = SourceFingerprint(sha256="b" * 64, size=FP.size, clinics_count=FP.clinics_count,
                               medical_key_empty=FP.medical_key_empty,
                               medical_key_duplicate_groups=FP.medical_key_duplicate_groups,
                               integrity_check=FP.integrity_check)
    mismatches = fingerprint_mismatches(other, FP)
    assert any("sha256" in m for m in mismatches)


def test_fingerprint_detects_count_mismatch():
    other = SourceFingerprint(sha256=FP.sha256, size=FP.size, clinics_count=999,
                               medical_key_empty=FP.medical_key_empty,
                               medical_key_duplicate_groups=FP.medical_key_duplicate_groups,
                               integrity_check=FP.integrity_check)
    mismatches = fingerprint_mismatches(other, FP)
    assert any("clinics_count" in m for m in mismatches)


def test_chunk_marker_roundtrip():
    marker = chunk_marker("f" * 64, "hp_research", 1, 999)
    m = SOURCE_MARKER_RE.match(marker)
    assert m is not None
    assert m.group(1) == "f" * 64
    assert m.group(2) == "hp_research"
    assert m.group(3) == "1"
    assert m.group(4) == "999"


def test_assert_local_host_allows_localhost():
    _assert_local_host("127.0.0.1")
    _assert_local_host("localhost")


def test_assert_local_host_refuses_other_hosts():
    with pytest.raises(ProductionGuardError):
        _assert_local_host("db.supabase.co")
    with pytest.raises(ProductionGuardError):
        _assert_local_host("xtspgevvntpidkmyfwes.supabase.co")


# --- Cutover gate -------------------------------------------------------

def _job_items_db(pending=0, running=0, running_jobs=0, cancelled=0):
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE research_job_items(state TEXT)")
    conn.execute("CREATE TABLE research_jobs(status TEXT)")
    for _ in range(pending):
        conn.execute("INSERT INTO research_job_items VALUES ('PENDING')")
    for _ in range(running):
        conn.execute("INSERT INTO research_job_items VALUES ('RUNNING')")
    for _ in range(running_jobs):
        conn.execute("INSERT INTO research_jobs VALUES ('RUNNING')")
    for _ in range(cancelled):
        conn.execute("INSERT INTO research_job_items VALUES ('CANCELLED')")
    conn.execute("INSERT INTO research_job_items VALUES ('DONE')")  # noise row
    conn.commit()
    return conn


def test_cutover_gate_passes_when_clear():
    gate = check_cutover_gate(_job_items_db())
    assert gate.passed is True


def test_cutover_gate_cancelled_is_terminal_and_does_not_block():
    gate = check_cutover_gate(_job_items_db(cancelled=103))
    assert gate.passed is True
    assert gate.pending_items == gate.running_items == gate.running_jobs == 0


def test_cutover_gate_blocks_on_pending():
    gate = check_cutover_gate(_job_items_db(pending=202))
    assert gate.passed is False
    assert gate.pending_items == 202


def test_cutover_gate_blocks_on_running():
    gate = check_cutover_gate(_job_items_db(running=1))
    assert gate.passed is False
    assert gate.running_items == 1


def test_cutover_gate_blocks_on_running_job():
    gate = check_cutover_gate(_job_items_db(running_jobs=1))
    assert gate.passed is False
    assert gate.running_jobs == 1


def test_jobs_report_recognizes_cancelled_and_full_gate_contract():
    conn = _job_items_db(cancelled=103)
    status = read_job_cutover_status(conn)
    assert status.cancelled_items == 103
    assert status.other_item_states == {}
    assert status.gate_clear is True

    blocked = read_job_cutover_status(_job_items_db(pending=1))
    assert blocked.gate_clear is False


# --- Production guard ----------------------------------------------------

CLEAR_GATE = CutoverGateResult(pending_items=0, running_items=0, running_jobs=0)
BLOCKED_GATE = CutoverGateResult(pending_items=202, running_items=0, running_jobs=0)


def test_guard_noop_for_scratch_mode():
    # scratch mode never enforces any of this, even with every flag wrong
    guard_production_execute(
        target_mode="scratch", execute=False, confirmed_project_ref=None,
        source_fingerprint=FP, expected_fingerprint=SourceFingerprint(
            sha256="mismatch", size=0, clinics_count=0, medical_key_empty=0,
            medical_key_duplicate_groups=0, integrity_check="bad"),
        cutover=BLOCKED_GATE,
    )


def test_guard_refuses_without_execute_flag():
    with pytest.raises(ProductionGuardError, match="execute"):
        guard_production_execute(
            target_mode="production", execute=False, confirmed_project_ref=PRODUCTION_SUPABASE_PROJECT_REF,
            source_fingerprint=FP, expected_fingerprint=FP, cutover=CLEAR_GATE,
        )


def test_guard_refuses_wrong_project_ref():
    with pytest.raises(ProductionGuardError, match="project ref"):
        guard_production_execute(
            target_mode="production", execute=True, confirmed_project_ref="wrong-ref",
            source_fingerprint=FP, expected_fingerprint=FP, cutover=CLEAR_GATE,
        )


def test_guard_refuses_missing_project_ref():
    with pytest.raises(ProductionGuardError, match="project ref"):
        guard_production_execute(
            target_mode="production", execute=True, confirmed_project_ref=None,
            source_fingerprint=FP, expected_fingerprint=FP, cutover=CLEAR_GATE,
        )


def test_guard_refuses_fingerprint_mismatch():
    other = SourceFingerprint(sha256="c" * 64, size=FP.size, clinics_count=FP.clinics_count,
                               medical_key_empty=FP.medical_key_empty,
                               medical_key_duplicate_groups=FP.medical_key_duplicate_groups,
                               integrity_check=FP.integrity_check)
    with pytest.raises(ProductionGuardError, match="fingerprint"):
        guard_production_execute(
            target_mode="production", execute=True, confirmed_project_ref=PRODUCTION_SUPABASE_PROJECT_REF,
            source_fingerprint=other, expected_fingerprint=FP, cutover=CLEAR_GATE,
        )


def test_guard_refuses_when_cutover_gate_blocked():
    with pytest.raises(ProductionGuardError, match="cutover gate"):
        guard_production_execute(
            target_mode="production", execute=True, confirmed_project_ref=PRODUCTION_SUPABASE_PROJECT_REF,
            source_fingerprint=FP, expected_fingerprint=FP, cutover=BLOCKED_GATE,
        )


def test_guard_passes_when_everything_is_correct():
    guard_production_execute(
        target_mode="production", execute=True, confirmed_project_ref=PRODUCTION_SUPABASE_PROJECT_REF,
        source_fingerprint=FP, expected_fingerprint=FP, cutover=CLEAR_GATE,
    )

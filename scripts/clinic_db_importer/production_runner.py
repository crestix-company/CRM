"""Chunked, resumable, fail-closed migration runner for Schema v1.

Design rationale (docs/clinic-db-production-migration-runner-v1.md section
"Schema review"): durable per-chunk checkpointing is achieved WITHOUT any new
tables or columns. Each chunk becomes its own `clinic_ops.import_logs` row
(instead of one row for the whole migration, as the PR #9 rehearsal did), and
`source_file` encodes a structured marker:

    clinic_sqlite:<source sha256>:<phase>:<range_start>:<range_end>

`range_start`/`range_end` are the source table's own integer primary key
values covering that chunk (keyset pagination -- `WHERE id > :cursor ORDER BY
id LIMIT :chunk_size` -- never OFFSET, which is fragile under concurrent
change). Resuming after a process restart means: for each phase, find the
MAX range_end among 'completed' rows whose source_file matches this exact
source's SHA-256 and phase, and continue from there. A chunk is only ever
attempted once per (source, phase, range) triple -- checked BEFORE doing any
work -- so re-running the whole migration, or resuming after a crash
mid-chunk, is a pure no-op for everything already committed.

Cross-process/restart FK stability: HP/Maps/Comdesk rows resolve their
`clinic_id` by joining the source row's SQLite integer clinic id back to its
`medical_key` (a small, chunk-bounded lookup against the SQLite source), then
querying clinic_master.clinics in the TARGET by that medical_key (also
chunk-bounded). clinic_master.clinics is the durable SSOT for
medical_key -> clinic_id; nothing here ever depends on an in-process
dictionary surviving a restart (unlike the PR #9 rehearsal importer, which
built a full sqlite_id -> clinic_id map in memory for a single run only).
"""
from __future__ import annotations

import io
import os
import re
import sqlite3
import subprocess
import sys
import time
import uuid as uuid_mod
from dataclasses import dataclass, field

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from scripts.clinic_db_importer import pg_csv, transform  # noqa: E402
from scripts.clinic_db_importer.classify import classify_clinic_row  # noqa: E402
from scripts.clinic_db_importer.comdesk_mapping import EXPECTED_COLUMN_COUNT  # noqa: E402
from scripts.clinic_db_importer.hp_mapping import ALLOWED_MACHINE_RANK, evaluate_hp_research_row  # noqa: E402
from scripts.clinic_db_importer.maps_mapping import evaluate_maps_row, is_synthetic_seed_candidate  # noqa: E402
from scripts.clinic_db_importer.normalizer_bridge import load_normalizers  # noqa: E402
from scripts.clinic_db_importer.run_dry_run import build_row_issues  # noqa: E402
from scripts.clinic_db_importer.sqlite_reader import capture_baseline, readonly_connection  # noqa: E402
from scripts.clinic_db_importer.uuid7 import uuid7  # noqa: E402

# This is a project *identifier*, not a secret -- used only as an explicit
# confirmation string the caller must type to enable production mode. No
# password, connection string, or service key is ever read, stored, or
# committed by this module.
PRODUCTION_SUPABASE_PROJECT_REF = "xtspgevvntpidkmyfwes"

SOURCE_MARKER_RE = re.compile(r"^clinic_sqlite:([0-9a-f]{64}):([a-z_]+):(\S+):(\S+)$")


# ============================================================
# Source preflight / fingerprint
# ============================================================

@dataclass(frozen=True)
class SourceFingerprint:
    sha256: str
    size: int
    clinics_count: int
    medical_key_empty: int
    medical_key_duplicate_groups: int
    integrity_check: str


def capture_source_fingerprint(sqlite_path: str) -> SourceFingerprint:
    b = capture_baseline(sqlite_path)
    return SourceFingerprint(
        sha256=b.sha256, size=b.size, clinics_count=b.clinics_count,
        medical_key_empty=b.medical_key_empty,
        medical_key_duplicate_groups=b.medical_key_duplicate_groups,
        integrity_check=b.integrity_check,
    )


def fingerprint_mismatches(actual: SourceFingerprint, expected: SourceFingerprint) -> list[str]:
    mismatches = []
    for f in actual.__dataclass_fields__:
        a, e = getattr(actual, f), getattr(expected, f)
        if a != e:
            mismatches.append(f"{f}: expected={e!r} actual={a!r}")
    return mismatches


# ============================================================
# Cutover gate (read-only against the SQLite source)
# ============================================================

@dataclass(frozen=True)
class CutoverGateResult:
    pending_items: int
    running_items: int
    running_jobs: int

    @property
    def passed(self) -> bool:
        return self.pending_items == 0 and self.running_items == 0


def check_cutover_gate(conn: sqlite3.Connection) -> CutoverGateResult:
    item_counts = dict(conn.execute(
        "SELECT state, COUNT(*) FROM research_job_items GROUP BY state;"
    ).fetchall())
    job_counts = dict(conn.execute(
        "SELECT status, COUNT(*) FROM research_jobs GROUP BY status;"
    ).fetchall())
    return CutoverGateResult(
        pending_items=item_counts.get("PENDING", 0),
        running_items=item_counts.get("RUNNING", 0),
        running_jobs=job_counts.get("RUNNING", 0),
    )


# ============================================================
# Production execution guard (fail-closed)
# ============================================================

class ProductionGuardError(RuntimeError):
    pass


def guard_production_execute(
    *,
    target_mode: str,
    execute: bool,
    confirmed_project_ref: str | None,
    source_fingerprint: SourceFingerprint,
    expected_fingerprint: SourceFingerprint,
    cutover: CutoverGateResult,
) -> None:
    """Raises ProductionGuardError with a specific reason on any failed check.
    A single mistaken flag can never be enough to reach a write: execute mode,
    the exact project ref, an unchanged source, and a clear cutover gate must
    ALL be satisfied simultaneously. Does not connect to anything -- this is
    a pure pre-flight check the caller must pass before construction of any
    database connection to a production target.
    """
    if target_mode != "production":
        return  # guard only applies when explicitly targeting production
    if not execute:
        raise ProductionGuardError("Refusing: --execute was not passed (plan/dry-run mode only).")
    if confirmed_project_ref != PRODUCTION_SUPABASE_PROJECT_REF:
        raise ProductionGuardError(
            f"Refusing: confirmed_project_ref does not match expected production project ref."
        )
    mismatches = fingerprint_mismatches(source_fingerprint, expected_fingerprint)
    if mismatches:
        raise ProductionGuardError(f"Refusing: source fingerprint mismatch: {mismatches}")
    if not cutover.passed:
        raise ProductionGuardError(
            f"Refusing: cutover gate not clear (pending_items={cutover.pending_items}, "
            f"running_items={cutover.running_items}, running_jobs={cutover.running_jobs})."
        )


def _assert_local_host(host: str) -> None:
    if host not in ("127.0.0.1", "localhost"):
        raise ProductionGuardError(f"Refusing to run against non-local host: {host!r}")


# ============================================================
# psql helpers (same pattern as apply_migration.py)
# ============================================================

def _run_psql(container: str, db: str, sql_text: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["docker", "exec", "-i", container, "psql", "-U", "postgres", "-d", db, "-v", "ON_ERROR_STOP=1"],
        input=sql_text, capture_output=True, text=True,
    )


def _psql_rows(container: str, db: str, sql: str, sep: str = "\x01") -> list[list[str]]:
    result = subprocess.run(
        ["docker", "exec", "-i", container, "psql", "-U", "postgres", "-d", db, "-tA", "-F", sep, "-c", sql],
        capture_output=True, text=True,
    )
    return [line.split(sep) for line in result.stdout.splitlines() if line]


def _sql_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


# ============================================================
# Chunk source-file marker
# ============================================================

def chunk_marker(sha256: str, phase: str, range_start, range_end) -> str:
    return f"clinic_sqlite:{sha256}:{phase}:{range_start}:{range_end}"


def get_resume_cursor(container: str, db: str, sha256: str, phase: str) -> int:
    """Returns the highest completed range_end for this (source, phase), or 0
    if no chunk has completed yet. Durable across process restarts: derived
    entirely from clinic_ops.import_logs, never from in-memory state."""
    prefix = f"clinic_sqlite:{sha256}:{phase}:"
    rows = _psql_rows(
        container, db,
        f"SELECT source_file FROM clinic_ops.import_logs "
        f"WHERE status = 'completed' AND source_file LIKE {_sql_quote(prefix + '%')};",
    )
    max_end = 0
    for (source_file,) in rows:
        m = SOURCE_MARKER_RE.match(source_file)
        if not m:
            continue
        try:
            end = int(m.group(4))
        except ValueError:
            continue
        max_end = max(max_end, end)
    return max_end


def is_chunk_completed(container: str, db: str, marker: str) -> bool:
    rows = _psql_rows(
        container, db,
        f"SELECT 1 FROM clinic_ops.import_logs WHERE source_file = {_sql_quote(marker)} "
        f"AND status = 'completed';",
    )
    return len(rows) > 0


@dataclass
class ChunkOutcome:
    marker: str
    attempted: int
    inserted: int
    skipped: int
    review: int
    already_completed: bool = False
    failed: bool = False
    error: str | None = None


def _open_chunk(container: str, db: str, batch_id: str, marker: str, rows_total: int) -> None:
    r = _run_psql(
        container, db,
        f"INSERT INTO clinic_ops.import_logs (batch_id, source_file, status, rows_total) "
        f"VALUES ('{batch_id}', {_sql_quote(marker)}, 'running', {rows_total});\n",
    )
    if r.returncode != 0:
        raise RuntimeError(f"failed to open chunk header: {r.stderr}")


def _fail_chunk(container: str, db: str, batch_id: str, error: str) -> None:
    safe_error = error.replace("'", "''")[:2000]
    _run_psql(
        container, db,
        f"UPDATE clinic_ops.import_logs SET status='failed', finished_at=now(), "
        f"error_detail={_sql_quote(safe_error)} WHERE batch_id='{batch_id}';\n",
    )


def _copy_sql(schema: str, table: str, columns: list[str], rows: list[list[str]]) -> str:
    buf = io.StringIO()
    pg_csv.write_copy_block(buf, schema, table, columns, rows)
    return buf.getvalue()


def _complete_chunk(container: str, db: str, batch_id: str, counts: dict) -> None:
    _run_psql(
        container, db,
        f"UPDATE clinic_ops.import_logs SET status='completed', finished_at=now(), "
        f"rows_inserted={counts.get('inserted', 0)}, rows_skipped={counts.get('skipped', 0)}, "
        f"rows_review={counts.get('review', 0)} WHERE batch_id='{batch_id}';\n",
    )


def _complete_chunk_sql(batch_id: str, *, inserted: int, skipped: int, review: int) -> str:
    """SQL fragment appended to the chunk's data transaction.

    The data COPY and completed checkpoint must commit atomically. Otherwise a
    process exit after the data COMMIT but before the checkpoint UPDATE could
    replay append-only history on resume.
    """
    return (
        "UPDATE clinic_ops.import_logs SET status='completed', finished_at=now(), "
        f"rows_inserted={inserted}, rows_skipped={skipped}, rows_review={review} "
        f"WHERE batch_id='{batch_id}';\n"
    )


# ============================================================
# Cross-restart clinic_id resolution (target is the SSOT, never an in-memory map)
# ============================================================

def resolve_clinic_ids(container: str, db: str, sqlite_conn: sqlite3.Connection, sqlite_ids: set[int]) -> dict[int, str]:
    """Resolves SQLite integer clinic ids to target clinic_id (UUID) via the
    stable medical_key bridge. Bounded to len(sqlite_ids) (i.e. to one
    chunk's worth), regardless of total migration progress so far -- this is
    what makes resume safe without any in-memory sqlite_id->clinic_id map
    surviving a process restart.
    """
    if not sqlite_ids:
        return {}
    id_list = ",".join(str(i) for i in sqlite_ids)
    id_to_mk: dict[int, str | None] = {}
    for row in sqlite_conn.execute(f"SELECT id, medical_key FROM clinics WHERE id IN ({id_list});"):
        id_to_mk[row["id"]] = transform.to_optional_text(row["medical_key"])
    mks = [mk for mk in id_to_mk.values() if mk]
    if not mks:
        return {}
    in_list = ",".join(_sql_quote(mk) for mk in mks)
    mk_to_cid = {}
    for mk, cid in _psql_rows(
        container, db, f"SELECT medical_key, clinic_id FROM clinic_master.clinics WHERE medical_key IN ({in_list});"
    ):
        mk_to_cid[mk] = cid
    return {sid: mk_to_cid[mk] for sid, mk in id_to_mk.items() if mk and mk in mk_to_cid}


# ============================================================
# Generic chunked-phase driver
# ============================================================

@dataclass
class PhaseResult:
    phase: str
    attempted: int = 0
    inserted: int = 0
    skipped: int = 0
    review: int = 0
    chunks_processed: int = 0
    chunks_already_completed: int = 0


def run_chunked_phase(
    container: str, db: str, *, phase: str, sha256: str, chunk_size: int,
    fetch_chunk, process_chunk, cursor_of,
) -> PhaseResult:
    """fetch_chunk(cursor:int, size:int) -> list[dict] (rows with id > cursor, ORDER BY id, LIMIT size).
    process_chunk(rows, container, db, batch_id) -> dict with attempted/inserted/skipped/review.
    cursor_of(row) -> int, a stable, monotonically increasing source key (never OFFSET-based).
    Never holds more than one chunk's rows in memory -- bounded regardless of dataset size.
    """
    result = PhaseResult(phase=phase)
    cursor = get_resume_cursor(container, db, sha256, phase)
    while True:
        rows = fetch_chunk(cursor, chunk_size)
        if not rows:
            break
        range_start, range_end = cursor_of(rows[0]), cursor_of(rows[-1])
        marker = chunk_marker(sha256, phase, range_start, range_end)
        if is_chunk_completed(container, db, marker):
            cursor = range_end
            result.chunks_already_completed += 1
            continue
        batch_id = str(uuid_mod.uuid4())
        _open_chunk(container, db, batch_id, marker, len(rows))
        try:
            counts = process_chunk(rows, container, db, batch_id)
        except Exception as exc:
            _fail_chunk(container, db, batch_id, str(exc))
            raise
        result.attempted += counts.get("attempted", 0)
        result.inserted += counts.get("inserted", 0)
        result.skipped += counts.get("skipped", 0)
        result.review += counts.get("review", 0)
        result.chunks_processed += 1
        cursor = range_end
    return result


# ============================================================
# Per-phase chunk processors
# ============================================================

def _clinic_columns_and_row_csv():
    from scripts.clinic_db_importer.apply_migration import _clinic_columns, _clinic_row_csv
    return _clinic_columns, _clinic_row_csv


def process_clinics_chunk(rows: list[dict], container: str, db: str, batch_id: str, normalizers: dict, normalizer_version: str) -> dict:
    clinic_columns, clinic_row_csv = _clinic_columns_and_row_csv()

    medical_keys = [mk for mk in (transform.to_optional_text(r["medical_key"]) for r in rows) if mk]
    existing: set[str] = set()
    if medical_keys:
        in_list = ",".join(_sql_quote(mk) for mk in medical_keys)
        existing = {row[0] for row in _psql_rows(container, db, f"SELECT medical_key FROM clinic_master.clinics WHERE medical_key IN ({in_list});")}

    dup_counts: dict[str, int] = {}
    for mk in medical_keys:
        dup_counts[mk] = dup_counts.get(mk, 0) + 1

    # Duplicate legacy_uuid within this chunk (bounded, chunk-local check --
    # mirrors run_dry_run.py's global pass, scoped down to one chunk since a
    # global in-memory count across the whole 162k-row dataset would defeat
    # the bounded-memory goal). Cross-chunk duplicates are still caught by
    # the clinics_legacy_uuid_key UNIQUE constraint at the database level.
    legacy_uuid_counts: dict[str, int] = {}
    for r in rows:
        val, ok = transform.parse_uuid(r["uuid"])
        if ok and val is not None:
            legacy_uuid_counts[val] = legacy_uuid_counts.get(val, 0) + 1

    clinic_rows_csv, item_rows_csv = [], []
    inserted = skipped = review = 0
    for r in rows:
        issues = build_row_issues(r, medical_key_counts=dup_counts, normalizers=normalizers)
        uuid_val, _ = transform.parse_uuid(r["uuid"])
        if uuid_val is not None and legacy_uuid_counts.get(uuid_val, 0) > 1:
            issues.legacy_uuid_duplicate = True
        result = classify_clinic_row(issues, target_mode="existing_key", existing_medical_keys=existing)
        if result.decision == "INSERT":
            clinic_id = str(uuid7())
            clinic_rows_csv.append(clinic_row_csv(r, clinic_id=clinic_id, normalizers=normalizers,
                                                   normalizer_version=normalizer_version, batch_id=batch_id))
            item_rows_csv.append([pg_csv.field(batch_id), pg_csv.field(issues.medical_key), pg_csv.field(clinic_id),
                                   pg_csv.field("insert"), pg_csv.field(None)])
            inserted += 1
        elif result.decision == "SKIP":
            existing_rows = _psql_rows(container, db, f"SELECT clinic_id FROM clinic_master.clinics WHERE medical_key={_sql_quote(issues.medical_key)};")
            existing_clinic_id = existing_rows[0][0] if existing_rows else None
            item_rows_csv.append([pg_csv.field(batch_id), pg_csv.field(issues.medical_key), pg_csv.field(existing_clinic_id),
                                   pg_csv.field("skip"), pg_csv.field(None)])
            skipped += 1
        else:
            audit_mk = issues.medical_key if issues.medical_key is not None else (r["medical_key"] or "")
            item_rows_csv.append([pg_csv.field(batch_id), pg_csv.field(audit_mk), pg_csv.field(None),
                                   pg_csv.field("review"), pg_csv.field(",".join(x.value for x in result.reasons))])
            review += 1

    script = "BEGIN;\n"
    if clinic_rows_csv:
        script += _copy_sql("clinic_master", "clinics", clinic_columns(), clinic_rows_csv)
    if item_rows_csv:
        script += _copy_sql("clinic_ops", "import_log_items", ["batch_id", "medical_key", "clinic_id", "decision", "reason"], item_rows_csv)
    script += _complete_chunk_sql(batch_id, inserted=inserted, skipped=skipped, review=review)
    script += "COMMIT;\n"
    result = _run_psql(container, db, script)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return {"attempted": len(rows), "inserted": inserted, "skipped": skipped, "review": review}


HP_RESEARCH_COLUMNS = ["clinic_id", "url", "fetch_status", "fetched_at", "error_detail",
                       "machine_rank", "machine_score", "model_version", "features", "created_at"]


def process_hp_chunk(rows: list[dict], container: str, db: str, batch_id: str, sqlite_conn: sqlite3.Connection) -> dict:
    sqlite_ids = {r["clinic_id"] for r in rows}
    id_to_clinic = resolve_clinic_ids(container, db, sqlite_conn, sqlite_ids)
    known_ids = set(sqlite_ids)

    hp_rows_csv = []
    inserted = review = 0
    for r in rows:
        clinic_id = id_to_clinic.get(r["clinic_id"])
        hp_eval = evaluate_hp_research_row(r, known_clinic_ids=known_ids)
        if clinic_id is None or hp_eval.decision != "INSERT":
            review += 1
            continue
        payload, _ = transform.parse_json(r["result_json"])
        payload = payload if isinstance(payload, dict) else {}
        hp_rank_raw = payload.get("hp_rank")
        machine_rank = hp_rank_raw if hp_rank_raw in ALLOWED_MACHINE_RANK else None
        fetched_at, _ = transform.parse_timestamp(payload.get("hp_checked_at"))
        created_at, ok_ts = transform.parse_timestamp(r["updated_at"])
        hp_rows_csv.append([
            pg_csv.field(clinic_id), pg_csv.field(transform.to_optional_text(payload.get("hp_url"))),
            pg_csv.field(payload.get("research_status")), pg_csv.field(fetched_at),
            pg_csv.field(transform.to_optional_text(payload.get("research_error"))),
            pg_csv.field(machine_rank), pg_csv.field(payload.get("hp_score")),
            pg_csv.field(transform.to_optional_text(payload.get("hp_rank_version"))),
            pg_csv.json_field(payload), pg_csv.field(created_at if ok_ts else None),
        ])
        inserted += 1

    script = "BEGIN;\n"
    if hp_rows_csv:
        script += _copy_sql("clinic_ops", "hp_research", HP_RESEARCH_COLUMNS, hp_rows_csv)
    script += _complete_chunk_sql(batch_id, inserted=inserted, skipped=0, review=review)
    script += "COMMIT;\n"
    result = _run_psql(container, db, script)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return {"attempted": len(rows), "inserted": inserted, "skipped": 0, "review": review}


MAPS_RESULTS_COLUMNS = ["clinic_id", "place_id", "maps_status", "maps_profile_url", "maps_website_url",
                        "maps_match_method", "latitude", "longitude", "rating", "review_count",
                        "raw_result", "source_batch_id", "source_row_number", "fetched_at", "created_at"]
MAPS_RESULTS_COLUMNS_NO_CREATED_AT = MAPS_RESULTS_COLUMNS[:-1]


def process_maps_raw_chunk(rows: list[dict], container: str, db: str, batch_id: str, sqlite_conn: sqlite3.Connection) -> dict:
    sqlite_ids = {r["clinic_id"] for r in rows}
    id_to_clinic = resolve_clinic_ids(container, db, sqlite_conn, sqlite_ids)
    known_ids = set(sqlite_ids)

    maps_rows_csv = []
    inserted = review = 0
    for r in rows:
        clinic_id = id_to_clinic.get(r["clinic_id"])
        maps_eval = evaluate_maps_row(r, known_clinic_ids=known_ids)
        if clinic_id is None or maps_eval.decision != "INSERT":
            review += 1
            continue
        payload, _ = transform.parse_json(r["result_json"])
        fetched_at, _ = transform.parse_timestamp(r["scraped_at"])
        created_at, ok_ts = transform.parse_timestamp(r["created_at"])
        maps_rows_csv.append([
            pg_csv.field(clinic_id), pg_csv.field(None), pg_csv.field(r["maps_match_status"]),
            pg_csv.field(transform.to_optional_text(r["maps_profile_url"])),
            pg_csv.field(transform.to_optional_text(r["maps_website_url"])),
            pg_csv.field(transform.to_optional_text(r["maps_match_method"])),
            pg_csv.field(None), pg_csv.field(None), pg_csv.field(None), pg_csv.field(None),
            pg_csv.json_field(payload if isinstance(payload, dict) else None),
            pg_csv.field(transform.to_optional_text(r["batch_id"])), pg_csv.field(r["row_number"]),
            pg_csv.field(fetched_at), pg_csv.field(created_at if ok_ts else None),
        ])
        inserted += 1

    script = "BEGIN;\n"
    if maps_rows_csv:
        script += _copy_sql("clinic_ops", "maps_results", MAPS_RESULTS_COLUMNS, maps_rows_csv)
    script += _complete_chunk_sql(batch_id, inserted=inserted, skipped=0, review=review)
    script += "COMMIT;\n"
    result = _run_psql(container, db, script)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return {"attempted": len(rows), "inserted": inserted, "skipped": 0, "review": review}


def process_maps_seed_chunk(rows: list[dict], container: str, db: str, batch_id: str, sqlite_conn: sqlite3.Connection) -> dict:
    """`rows` are raw `clinics` rows for this id range (the cursor walks the
    whole clinics table under the independent 'maps_seed' phase namespace);
    only rows matching is_synthetic_seed_candidate produce a seed event."""
    candidates = [r for r in rows if is_synthetic_seed_candidate(r)]
    sqlite_ids = {r["id"] for r in candidates}
    id_to_clinic = resolve_clinic_ids(container, db, sqlite_conn, sqlite_ids)

    seed_rows_csv = []
    inserted = review = 0
    for r in candidates:
        clinic_id = id_to_clinic.get(r["id"])
        if clinic_id is None:
            review += 1
            continue
        seed_rows_csv.append([
            pg_csv.field(clinic_id), pg_csv.field(None),
            pg_csv.field(transform.to_optional_text(r["maps_presence_status"]) or "UNKNOWN"),
            pg_csv.field(transform.to_optional_text(r["maps_profile_url"])),
            pg_csv.field(transform.to_optional_text(r["maps_website_url"])),
            pg_csv.field(transform.to_optional_text(r["maps_match_method"])),
            pg_csv.field(None), pg_csv.field(None), pg_csv.field(None), pg_csv.field(None),
            pg_csv.json_field({"seed": True, "source": "clinics.maps_* cutover seed"}),
            pg_csv.field(None), pg_csv.field(None),
            pg_csv.field(None),  # fetched_at unknown for the seed
        ])
        inserted += 1

    script = "BEGIN;\n"
    if seed_rows_csv:
        script += _copy_sql("clinic_ops", "maps_results", MAPS_RESULTS_COLUMNS_NO_CREATED_AT, seed_rows_csv)
    script += _complete_chunk_sql(batch_id, inserted=inserted, skipped=0, review=review)
    script += "COMMIT;\n"
    result = _run_psql(container, db, script)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return {"attempted": len(candidates), "inserted": inserted, "skipped": 0, "review": review}


def process_comdesk_templates(container: str, db: str, sqlite_conn: sqlite3.Connection, sha256: str) -> PhaseResult:
    """Only ever 1-2 rows in practice; handled as a single checkpointed chunk
    rather than a real paginated loop."""
    phase = "comdesk_templates"
    marker = chunk_marker(sha256, phase, "all", "all")
    if is_chunk_completed(container, db, marker):
        return PhaseResult(phase=phase, chunks_already_completed=1)

    rows = [dict(r) for r in sqlite_conn.execute("SELECT * FROM templates;")]
    template_rows_csv = []
    inserted = review = 0
    for r in rows:
        headers, hok = transform.parse_json(r["headers_json"])
        mapping, mok = transform.parse_json(r["mapping_json"])
        if not (hok and mok and isinstance(headers, list) and len(headers) == EXPECTED_COLUMN_COUNT):
            review += 1
            continue
        created_at, ok_ts = transform.parse_timestamp(r["created_at"])
        template_rows_csv.append([pg_csv.field(r["id"]), pg_csv.json_field(headers), pg_csv.json_field(mapping),
                                   pg_csv.field(created_at if ok_ts else None)])
        inserted += 1

    batch_id = str(uuid_mod.uuid4())
    _open_chunk(container, db, batch_id, marker, len(rows))
    try:
        script = "BEGIN;\n"
        if template_rows_csv:
            script += _copy_sql("clinic_ops", "comdesk_templates", ["template_id", "headers", "field_mapping", "created_at"], template_rows_csv)
        script += _complete_chunk_sql(batch_id, inserted=inserted, skipped=0, review=review)
        script += "COMMIT;\n"
        result = _run_psql(container, db, script)
        if result.returncode != 0:
            raise RuntimeError(result.stderr)
    except Exception as exc:
        _fail_chunk(container, db, batch_id, str(exc))
        raise
    return PhaseResult(phase=phase, attempted=len(rows), inserted=inserted, review=review, chunks_processed=1)


def process_comdesk_original_chunk(rows: list[dict], container: str, db: str, batch_id: str,
                                    sqlite_conn: sqlite3.Connection, known_template_ids: set[str]) -> dict:
    sqlite_ids = {r["clinic_id"] for r in rows if r["clinic_id"] is not None}
    id_to_clinic = resolve_clinic_ids(container, db, sqlite_conn, sqlite_ids)

    original_rows_csv = []
    inserted = review = 0
    for r in rows:
        values, vok = transform.parse_json(r["row_json"])
        length_ok = vok and isinstance(values, list) and len(values) == EXPECTED_COLUMN_COUNT
        clinic_id = id_to_clinic.get(r["clinic_id"]) if r["clinic_id"] is not None else None
        # Nullable target storage exists for an explicitly reviewed future
        # preservation flow. Automatic migration requires a resolved clinic;
        # unresolved rows are also excluded from export by contract.
        clinic_fk_ok = r["clinic_id"] is not None and clinic_id is not None
        template_fk_ok = r["template_id"] in known_template_ids
        if not (length_ok and clinic_fk_ok and template_fk_ok):
            review += 1
            continue
        legacy_uuid, _ = transform.parse_uuid(r["uuid"])
        created_at, ok_ts = transform.parse_timestamp(r["created_at"])
        original_rows_csv.append([
            pg_csv.field(clinic_id), pg_csv.field(r["template_id"]), pg_csv.json_field(values),
            pg_csv.field(legacy_uuid), pg_csv.field(r["source_hash"]), pg_csv.field(r["row_number"]),
            pg_csv.field(batch_id), pg_csv.field(created_at if ok_ts else None),
        ])
        inserted += 1

    script = "BEGIN;\n"
    if original_rows_csv:
        script += _copy_sql("clinic_ops", "comdesk_original_rows",
                             ["clinic_id", "template_id", "original_values", "legacy_uuid", "source_hash",
                              "source_row_number", "imported_batch_id", "created_at"],
                             original_rows_csv)
    script += _complete_chunk_sql(batch_id, inserted=inserted, skipped=0, review=review)
    script += "COMMIT;\n"
    result = _run_psql(container, db, script)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return {"attempted": len(rows), "inserted": inserted, "skipped": 0, "review": review}


def _normalizer_version_tag() -> str:
    from scripts.clinic_db_importer.apply_migration import _normalizer_version_tag as _tag
    from scripts.clinic_db_importer.normalizer_bridge import CLINIC_LEAD_REPO
    return _tag(CLINIC_LEAD_REPO)


# ============================================================
# Top-level orchestration
# ============================================================

def run_migration(
    *, sqlite_path: str, container: str, db: str, host: str = "127.0.0.1", chunk_size: int = 1000,
    target_mode: str = "scratch", execute: bool = False, confirmed_project_ref: str | None = None,
    expected_fingerprint: SourceFingerprint | None = None,
) -> dict:
    """Runs (or resumes) the full chunked migration. Safe to call repeatedly:
    already-completed chunks are detected and skipped before any row is
    touched. target_mode='production' additionally requires passing every
    guard in guard_production_execute() before a single query is issued.

    Note: this repository's actual network connection code only ever talks
    to `host` via `docker exec <container> psql` -- there is no code path
    here that can reach a real Supabase endpoint. target_mode='production' is
    exercised in this task only as a guard-logic test against a second
    localhost scratch instance, never against real production infrastructure.
    """
    _assert_local_host(host)

    with readonly_connection(sqlite_path) as sconn:
        fingerprint = capture_source_fingerprint(sqlite_path)
        cutover = check_cutover_gate(sconn)

        if target_mode == "production":
            if expected_fingerprint is None:
                raise ProductionGuardError("expected_fingerprint is required for target_mode='production'")
            guard_production_execute(
                target_mode=target_mode, execute=execute, confirmed_project_ref=confirmed_project_ref,
                source_fingerprint=fingerprint, expected_fingerprint=expected_fingerprint, cutover=cutover,
            )

        normalizers = load_normalizers()
        normalizer_version = _normalizer_version_tag()
        sha = fingerprint.sha256

        results: dict[str, object] = {"source_fingerprint": fingerprint, "cutover_gate": cutover}

        results["clinics"] = run_chunked_phase(
            container, db, phase="clinics", sha256=sha, chunk_size=chunk_size,
            fetch_chunk=lambda cursor, size: [dict(r) for r in sconn.execute(
                "SELECT * FROM clinics WHERE id > ? ORDER BY id LIMIT ?", (cursor, size))],
            process_chunk=lambda rows, c, d, bid: process_clinics_chunk(rows, c, d, bid, normalizers, normalizer_version),
            cursor_of=lambda r: r["id"],
        )

        results["hp_research"] = run_chunked_phase(
            container, db, phase="hp_research", sha256=sha, chunk_size=chunk_size,
            fetch_chunk=lambda cursor, size: [dict(r) for r in sconn.execute(
                "SELECT * FROM research_results WHERE clinic_id > ? ORDER BY clinic_id LIMIT ?", (cursor, size))],
            process_chunk=lambda rows, c, d, bid: process_hp_chunk(rows, c, d, bid, sconn),
            cursor_of=lambda r: r["clinic_id"],
        )

        results["maps_raw"] = run_chunked_phase(
            container, db, phase="maps_raw", sha256=sha, chunk_size=chunk_size,
            fetch_chunk=lambda cursor, size: [dict(r) for r in sconn.execute(
                "SELECT * FROM google_maps_results WHERE id > ? ORDER BY id LIMIT ?", (cursor, size))],
            process_chunk=lambda rows, c, d, bid: process_maps_raw_chunk(rows, c, d, bid, sconn),
            cursor_of=lambda r: r["id"],
        )

        results["maps_seed"] = run_chunked_phase(
            container, db, phase="maps_seed", sha256=sha, chunk_size=chunk_size,
            fetch_chunk=lambda cursor, size: [dict(r) for r in sconn.execute(
                "SELECT * FROM clinics WHERE id > ? ORDER BY id LIMIT ?", (cursor, size))],
            process_chunk=lambda rows, c, d, bid: process_maps_seed_chunk(rows, c, d, bid, sconn),
            cursor_of=lambda r: r["id"],
        )

        results["comdesk_templates"] = process_comdesk_templates(container, db, sconn, sha)

        known_template_ids = {row[0] for row in _psql_rows(container, db, "SELECT template_id FROM clinic_ops.comdesk_templates;")}

        results["comdesk_original_rows"] = run_chunked_phase(
            container, db, phase="comdesk_original_rows", sha256=sha, chunk_size=chunk_size,
            fetch_chunk=lambda cursor, size: [dict(r) for r in sconn.execute(
                "SELECT * FROM comdesk_original_rows WHERE id > ? ORDER BY id LIMIT ?", (cursor, size))],
            process_chunk=lambda rows, c, d, bid: process_comdesk_original_chunk(rows, c, d, bid, sconn, known_template_ids),
            cursor_of=lambda r: r["id"],
        )

    return results

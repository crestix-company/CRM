"""Applies the Clinic SQLite -> Schema v1 migration to a SCRATCH PostgreSQL only.

Reuses the exact classify/transform/normalizer logic from run_dry_run.py so
the apply path and the dry-run path can never silently diverge. Never
connects to anything but 127.0.0.1/localhost (fail-closed guard below), and
never touches Production SQLite beyond a read-only connection.

Idempotency design: a migration "batch" is identified by the source SQLite's
SHA-256 (its content identity). Before doing any INSERT, this checks
clinic_ops.import_logs for a `status='completed'` row whose `source_file`
already encodes that SHA-256. If found, the whole append-only-history INSERT
step (hp_research / maps_results / comdesk) is skipped entirely -- re-running
against unchanged source content must not create duplicate history rows.
clinic_master.clinics additionally gets its own per-row guard (existing
medical_key -> SKIP), as defense in depth even within a single batch.
"""
from __future__ import annotations

import json
import os
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

NORMALIZER_VERSION_PREFIX = "clinic-list-filter-complete@"


class UnsafeTargetHost(RuntimeError):
    pass


def _assert_local_host(host: str) -> None:
    if host not in ("127.0.0.1", "localhost"):
        raise UnsafeTargetHost(f"Refusing to run migration against non-local host: {host!r}")


def _run_psql(container: str, db: str, sql_text: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["docker", "exec", "-i", container, "psql", "-U", "postgres", "-d", db, "-v", "ON_ERROR_STOP=1"],
        input=sql_text,
        capture_output=True,
        text=True,
    )


def _psql_scalar(container: str, db: str, sql: str) -> str | None:
    result = subprocess.run(
        ["docker", "exec", "-i", container, "psql", "-U", "postgres", "-d", db, "-tA"],
        input=sql,
        capture_output=True,
        text=True,
    )
    out = result.stdout.strip()
    return out if out else None


def _existing_medical_keys(container: str, db: str) -> set[str]:
    result = subprocess.run(
        ["docker", "exec", "-i", container, "psql", "-U", "postgres", "-d", db, "-tA",
         "-c", "SELECT medical_key FROM clinic_master.clinics;"],
        capture_output=True, text=True,
    )
    return {line for line in result.stdout.splitlines() if line}


def _completed_batch_id_for_source(container: str, db: str, source_marker: str) -> str | None:
    return _psql_scalar(
        container, db,
        f"SELECT batch_id FROM clinic_ops.import_logs WHERE source_file = '{source_marker}' "
        f"AND status = 'completed' LIMIT 1;",
    )


@dataclass
class ApplyResult:
    idempotent_skip: bool
    batch_id: str
    counts: dict = field(default_factory=dict)
    success: bool = True
    error: str | None = None
    elapsed_seconds: float = 0.0


def _clinic_columns() -> list[str]:
    return [
        "clinic_id", "medical_key", "legacy_uuid", "clinic_name", "clinic_name_kana",
        "medical_type", "prefecture", "postal_code", "address", "phone",
        "designation_date", "registration_reason", "owner_equal", "age_probability", "departments",
        "active", "is_new", "source_as_of_date", "merge_hold", "merged_into_clinic_id", "exclude_reason",
        "source_payload", "first_seen_at", "last_seen_at",
        "name_norm", "name_prefix", "phone_norm", "address_norm", "tel_match_key", "search_projection_version",
        "source", "imported_batch_id",
    ]


def _clinic_row_csv(row: dict, *, clinic_id: str, normalizers: dict, normalizer_version: str, batch_id: str) -> list[str]:
    legacy_uuid, _ = transform.parse_uuid(row["uuid"])
    designation_date, _ = transform.parse_date(row["designation_date"])
    source_as_of_date, _ = transform.parse_date(row["source_as_of_date"])
    first_seen_at, ok1 = transform.parse_timestamp(row["first_seen_at"])
    if not ok1 or first_seen_at is None:
        first_seen_at, _ = transform.parse_date(row["first_seen_at"])
    last_seen_at, ok2 = transform.parse_timestamp(row["last_seen_at"])
    if not ok2 or last_seen_at is None:
        last_seen_at, _ = transform.parse_date(row["last_seen_at"])
    owner_equal, _ = transform.parse_bool(row["owner_equal"])
    age_probability, _ = transform.parse_numeric(row["age_probability"])
    active, _ = transform.parse_bool(row["active"])
    is_new, _ = transform.parse_bool(row["is_new"])
    merge_hold, _ = transform.parse_bool(row["merge_hold"])
    base_payload, _ = transform.parse_json(row["base_json"])
    departments_raw, _ = transform.parse_json(row["departments_json"])
    departments = departments_raw if isinstance(departments_raw, list) else None
    postal_code = None
    if isinstance(base_payload, dict):
        postal_code = transform.to_optional_text(base_payload.get("postal_code"))

    return [
        pg_csv.field(clinic_id),
        pg_csv.field(transform.to_optional_text(row["medical_key"])),
        pg_csv.field(legacy_uuid),
        pg_csv.field(row["clinic_name"]),
        pg_csv.field(None),  # clinic_name_kana: no source column (docs/clinic-db-schema-v1.md)
        pg_csv.field(transform.to_optional_text(row["medical_type"])),
        pg_csv.field(transform.to_optional_text(row["prefecture"])),
        pg_csv.field(postal_code),
        pg_csv.field(transform.to_optional_text(row["address"])),
        pg_csv.field(transform.to_optional_text(row["phone"])),
        pg_csv.field(designation_date),
        pg_csv.field(transform.to_optional_text(row["registration_reason"])),
        pg_csv.field(owner_equal if owner_equal is not None else None),
        pg_csv.field(age_probability),
        pg_csv.text_array_field(departments),
        pg_csv.field(bool(active) if active is not None else True),
        pg_csv.field(bool(is_new) if is_new is not None else False),
        pg_csv.field(source_as_of_date),
        pg_csv.field(bool(merge_hold) if merge_hold is not None else False),
        pg_csv.field(None),  # merged_into_clinic_id: 0 rows need resolution in current source data
        pg_csv.field(transform.to_optional_text(row["exclude_reason"])),
        pg_csv.json_field(base_payload if isinstance(base_payload, dict) else None),
        pg_csv.field(first_seen_at),
        pg_csv.field(last_seen_at),
        pg_csv.field(normalizers["name_norm"](row["clinic_name"])),
        pg_csv.field(normalizers["name_prefix"](row["clinic_name"])),
        pg_csv.field(normalizers["phone_norm"](row["phone"])),
        pg_csv.field(normalizers["address_norm"](row["address"])),
        pg_csv.field(normalizers["tel_match_key"](row["phone"])),
        pg_csv.field(normalizer_version),
        pg_csv.field("legacy_sqlite"),
        pg_csv.field(batch_id),
    ]


def run_apply(sqlite_path: str, *, container: str, db: str, host: str = "127.0.0.1") -> ApplyResult:
    _assert_local_host(host)
    started = time.monotonic()

    baseline_before = capture_baseline(sqlite_path)
    source_marker = f"clinic_sqlite:{baseline_before.sha256}"

    existing_batch = _completed_batch_id_for_source(container, db, source_marker)

    normalizers = load_normalizers()
    from scripts.clinic_db_importer.normalizer_bridge import CLINIC_LEAD_REPO  # noqa: E402
    normalizer_version = _normalizer_version_tag(CLINIC_LEAD_REPO)

    with readonly_connection(sqlite_path) as conn:
        clinic_rows = [dict(r) for r in conn.execute("SELECT * FROM clinics;")]

        medical_key_counts: dict[str, int] = {}
        for r in clinic_rows:
            mk = transform.to_optional_text(r["medical_key"])
            if mk is not None:
                medical_key_counts[mk] = medical_key_counts.get(mk, 0) + 1

        existing_keys = _existing_medical_keys(container, db)

        decisions = {}
        for r in clinic_rows:
            issues = build_row_issues(r, medical_key_counts=medical_key_counts, normalizers=normalizers)
            result = classify_clinic_row(
                issues,
                target_mode="existing_key" if existing_keys else "target_empty",
                existing_medical_keys=existing_keys,
            )
            decisions[r["id"]] = (result.decision, [x.value for x in result.reasons], issues.medical_key)

        if existing_batch:
            counts = {"insert": 0, "skip": sum(1 for d, _, _ in decisions.values() if d == "SKIP"),
                      "review": sum(1 for d, _, _ in decisions.values() if d == "REVIEW"), "error": 0}
            return ApplyResult(idempotent_skip=True, batch_id=existing_batch, counts=counts,
                                elapsed_seconds=time.monotonic() - started)

        batch_id = str(uuid_mod.uuid4())
        known_clinic_sqlite_ids = {r["id"] for r in clinic_rows}

        clinic_id_map: dict[int, str] = {}
        clinic_csv_rows = []
        import_log_item_rows = []
        for r in clinic_rows:
            decision, reasons, medical_key = decisions[r["id"]]
            if decision == "INSERT":
                clinic_id = str(uuid7())
                clinic_id_map[r["id"]] = clinic_id
                clinic_csv_rows.append(_clinic_row_csv(r, clinic_id=clinic_id, normalizers=normalizers,
                                                        normalizer_version=normalizer_version, batch_id=batch_id))
                import_log_item_rows.append([
                    pg_csv.field(batch_id), pg_csv.field(medical_key), pg_csv.field(clinic_id),
                    pg_csv.field("insert"), pg_csv.field(None),
                ])
            elif decision == "SKIP":
                existing_clinic_id = _psql_scalar(
                    container, db, f"SELECT clinic_id FROM clinic_master.clinics WHERE medical_key = '{medical_key}';"
                )
                import_log_item_rows.append([
                    pg_csv.field(batch_id), pg_csv.field(medical_key), pg_csv.field(existing_clinic_id),
                    pg_csv.field("skip"), pg_csv.field(None),
                ])
            else:  # REVIEW
                # medical_key may be None here (EMPTY_MEDICAL_KEY case). import_log_items.medical_key
                # is NOT NULL -- it's an audit snapshot, so an empty source value is preserved as ''
                # rather than as NULL (docs/clinic-db-architecture.md 3.5 exception rationale).
                audit_medical_key = medical_key if medical_key is not None else (r["medical_key"] or "")
                import_log_item_rows.append([
                    pg_csv.field(batch_id), pg_csv.field(audit_medical_key), pg_csv.field(None),
                    pg_csv.field("review"), pg_csv.field(",".join(reasons)),
                ])

        hp_rows = []
        hp_review_count = 0
        for r in conn.execute("SELECT * FROM research_results;"):
            r = dict(r)
            clinic_id = clinic_id_map.get(r["clinic_id"])
            # Same evaluator the dry-run used (docs/clinic-db-importer-dry-run-v1.md found 0
            # review/error across all 814 rows) -- applied again here defensively so a NULL or
            # unmapped fetch_status can never reach the NOT NULL + CHECK constrained column.
            hp_eval = evaluate_hp_research_row(r, known_clinic_ids=known_clinic_sqlite_ids)
            if clinic_id is None or hp_eval.decision != "INSERT":
                hp_review_count += 1
                continue
            payload, ok = transform.parse_json(r["result_json"])
            payload = payload if isinstance(payload, dict) else {}
            hp_rank_raw = payload.get("hp_rank")
            machine_rank = hp_rank_raw if hp_rank_raw in ALLOWED_MACHINE_RANK else None
            fetched_at, _ = transform.parse_timestamp(payload.get("hp_checked_at"))
            created_at, ok_ts = transform.parse_timestamp(r["updated_at"])
            hp_rows.append([
                pg_csv.field(clinic_id),
                pg_csv.field(transform.to_optional_text(payload.get("hp_url"))),
                pg_csv.field(payload.get("research_status")),
                pg_csv.field(fetched_at),
                pg_csv.field(transform.to_optional_text(payload.get("research_error"))),
                pg_csv.field(machine_rank),
                pg_csv.field(payload.get("hp_score")),
                pg_csv.field(transform.to_optional_text(payload.get("hp_rank_version"))),
                pg_csv.json_field(payload),
                pg_csv.field(created_at if ok_ts else None),
            ])

        maps_rows = []
        maps_review_count = 0
        for r in conn.execute("SELECT * FROM google_maps_results;"):
            r = dict(r)
            clinic_id = clinic_id_map.get(r["clinic_id"])
            maps_eval = evaluate_maps_row(r, known_clinic_ids=known_clinic_sqlite_ids)
            if clinic_id is None or maps_eval.decision != "INSERT":
                maps_review_count += 1
                continue
            payload, _ = transform.parse_json(r["result_json"])
            fetched_at, _ = transform.parse_timestamp(r["scraped_at"])
            created_at, ok_ts = transform.parse_timestamp(r["created_at"])
            maps_rows.append([
                pg_csv.field(clinic_id),
                pg_csv.field(None),  # place_id: not present in legacy source
                pg_csv.field(r["maps_match_status"]),
                pg_csv.field(transform.to_optional_text(r["maps_profile_url"])),
                pg_csv.field(transform.to_optional_text(r["maps_website_url"])),
                pg_csv.field(transform.to_optional_text(r["maps_match_method"])),
                pg_csv.field(None), pg_csv.field(None), pg_csv.field(None), pg_csv.field(None),  # lat/lng/rating/review_count
                pg_csv.json_field(payload if isinstance(payload, dict) else None),
                pg_csv.field(transform.to_optional_text(r["batch_id"])),
                pg_csv.field(r["row_number"]),
                pg_csv.field(fetched_at),
                pg_csv.field(created_at if ok_ts else None),
            ])

        seed_rows = []
        for r in clinic_rows:
            clinic_id = clinic_id_map.get(r["id"])
            if clinic_id is None or not is_synthetic_seed_candidate(r):
                continue
            seed_rows.append([
                pg_csv.field(clinic_id),
                pg_csv.field(None),
                pg_csv.field(transform.to_optional_text(r["maps_presence_status"]) or "UNKNOWN"),
                pg_csv.field(transform.to_optional_text(r["maps_profile_url"])),
                pg_csv.field(transform.to_optional_text(r["maps_website_url"])),
                pg_csv.field(transform.to_optional_text(r["maps_match_method"])),
                pg_csv.field(None), pg_csv.field(None), pg_csv.field(None), pg_csv.field(None),
                pg_csv.json_field({"seed": True, "source": "clinics.maps_* cutover seed"}),
                pg_csv.field(None), pg_csv.field(None),
                pg_csv.field(None),  # fetched_at unknown for the seed
                pg_csv.field(None),  # created_at set to now() in SQL (must sort after all raw history)
            ])

        template_rows = []
        known_template_ids = set()
        for r in conn.execute("SELECT * FROM templates;"):
            r = dict(r)
            headers, hok = transform.parse_json(r["headers_json"])
            mapping, mok = transform.parse_json(r["mapping_json"])
            if not (hok and mok and isinstance(headers, list) and len(headers) == EXPECTED_COLUMN_COUNT):
                continue
            known_template_ids.add(r["id"])
            created_at, ok_ts = transform.parse_timestamp(r["created_at"])
            template_rows.append([
                pg_csv.field(r["id"]), pg_csv.json_field(headers), pg_csv.json_field(mapping),
                pg_csv.field(created_at if ok_ts else None),
            ])

        original_rows = []
        for r in conn.execute("SELECT * FROM comdesk_original_rows;"):
            r = dict(r)
            values, vok = transform.parse_json(r["row_json"])
            if not (vok and isinstance(values, list) and len(values) == EXPECTED_COLUMN_COUNT):
                continue
            if r["template_id"] not in known_template_ids:
                continue
            clinic_id = clinic_id_map.get(r["clinic_id"]) if r["clinic_id"] is not None else None
            legacy_uuid, _ = transform.parse_uuid(r["uuid"])
            created_at, ok_ts = transform.parse_timestamp(r["created_at"])
            original_rows.append([
                pg_csv.field(clinic_id), pg_csv.field(r["template_id"]), pg_csv.json_field(values),
                pg_csv.field(legacy_uuid), pg_csv.field(r["source_hash"]), pg_csv.field(r["row_number"]),
                pg_csv.field(batch_id), pg_csv.field(created_at if ok_ts else None),
            ])

    # --- Step 1: batch header, own short transaction, survives even if step 2 fails ---
    header_sql = (
        f"INSERT INTO clinic_ops.import_logs (batch_id, source_file, status, rows_total) "
        f"VALUES ('{batch_id}', '{source_marker}', 'running', {len(clinic_rows)});\n"
    )
    header_result = _run_psql(container, db, header_sql)
    if header_result.returncode != 0:
        return ApplyResult(idempotent_skip=False, batch_id=batch_id, success=False,
                            error=header_result.stderr, elapsed_seconds=time.monotonic() - started)

    # --- Step 2: the actual data load, one transaction, all-or-nothing ---
    script_lines = ["BEGIN;\n"]
    script_lines.append(_copy_sql("clinic_master", "clinics", _clinic_columns(), clinic_csv_rows))
    script_lines.append(_copy_sql("clinic_ops", "hp_research",
                                   ["clinic_id", "url", "fetch_status", "fetched_at", "error_detail",
                                    "machine_rank", "machine_score", "model_version", "features", "created_at"],
                                   hp_rows))
    script_lines.append(_copy_sql("clinic_ops", "maps_results",
                                   ["clinic_id", "place_id", "maps_status", "maps_profile_url", "maps_website_url",
                                    "maps_match_method", "latitude", "longitude", "rating", "review_count",
                                    "raw_result", "source_batch_id", "source_row_number", "fetched_at", "created_at"],
                                   maps_rows))
    if seed_rows:
        seed_rows_now = [r[:-1] for r in seed_rows]  # drop placeholder created_at; SQL default now() applies
        script_lines.append(_copy_sql("clinic_ops", "maps_results",
                                       ["clinic_id", "place_id", "maps_status", "maps_profile_url", "maps_website_url",
                                        "maps_match_method", "latitude", "longitude", "rating", "review_count",
                                        "raw_result", "source_batch_id", "source_row_number", "fetched_at"],
                                       seed_rows_now))
    script_lines.append(_copy_sql("clinic_ops", "comdesk_templates", ["template_id", "headers", "field_mapping", "created_at"], template_rows))
    script_lines.append(_copy_sql("clinic_ops", "comdesk_original_rows",
                                   ["clinic_id", "template_id", "original_values", "legacy_uuid", "source_hash",
                                    "source_row_number", "imported_batch_id", "created_at"],
                                   original_rows))
    script_lines.append(_copy_sql("clinic_ops", "import_log_items",
                                   ["batch_id", "medical_key", "clinic_id", "decision", "reason"],
                                   import_log_item_rows))

    counts = {
        "clinics_insert": len(clinic_csv_rows),
        "clinics_skip": sum(1 for d, _, _ in decisions.values() if d == "SKIP"),
        "clinics_review": sum(1 for d, _, _ in decisions.values() if d == "REVIEW"),
        "hp_research": len(hp_rows),
        "hp_research_review": hp_review_count,
        "maps_raw": len(maps_rows),
        "maps_review": maps_review_count,
        "maps_seed": len(seed_rows),
        "comdesk_templates": len(template_rows),
        "comdesk_original_rows": len(original_rows),
        "import_log_items": len(import_log_item_rows),
    }
    script_lines.append(
        f"UPDATE clinic_ops.import_logs SET status='completed', finished_at=now(), "
        f"rows_inserted={counts['clinics_insert']}, rows_skipped={counts['clinics_skip']}, "
        f"rows_review={counts['clinics_review']} WHERE batch_id='{batch_id}';\n"
    )
    script_lines.append("COMMIT;\n")

    data_result = _run_psql(container, db, "".join(script_lines))
    elapsed = time.monotonic() - started

    if data_result.returncode != 0:
        fail_sql = (
            f"UPDATE clinic_ops.import_logs SET status='failed', finished_at=now(), "
            f"error_detail='migration script failed, see rehearsal logs' WHERE batch_id='{batch_id}';\n"
        )
        _run_psql(container, db, fail_sql)
        return ApplyResult(idempotent_skip=False, batch_id=batch_id, counts=counts, success=False,
                            error=data_result.stderr, elapsed_seconds=elapsed)

    return ApplyResult(idempotent_skip=False, batch_id=batch_id, counts=counts, success=True, elapsed_seconds=elapsed)


def _copy_sql(schema: str, table: str, columns: list[str], rows: list[list[str]]) -> str:
    import io
    buf = io.StringIO()
    pg_csv.write_copy_block(buf, schema, table, columns, rows)
    return buf.getvalue()


def _normalizer_version_tag(clinic_lead_repo: str) -> str:
    try:
        sha = subprocess.run(
            ["git", "-C", clinic_lead_repo, "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return NORMALIZER_VERSION_PREFIX + sha[:12]
    except Exception:
        return NORMALIZER_VERSION_PREFIX + "unknown"

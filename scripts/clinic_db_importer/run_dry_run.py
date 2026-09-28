#!/usr/bin/env python3
"""Entry point: dry-run classify all Clinic Production SQLite rows against
Schema v1, writing NOTHING to SQLite, Scratch Postgres, or Supabase.

Usage:
    python3 -m scripts.clinic_db_importer.run_dry_run \
        --sqlite ~/CrestixData/clinic-lead/clinics.sqlite3 \
        --summary-out docs/clinic-db-importer-dry-run-v1.summary.json \
        --detail-dir /tmp/clinic-dry-run-detail

The summary JSON contains counts only (safe for git). The detail dir
contains one JSONL file per category with per-row reason codes and enough
identifying information (medical_key, SQLite row id) to look the row up
later; it MUST NOT be committed (report.write_detail_rows refuses to write
inside the repo tree as a safety net).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from scripts.clinic_db_importer import transform  # noqa: E402
from scripts.clinic_db_importer.classify import RowIssues, classify_clinic_row  # noqa: E402
from scripts.clinic_db_importer.comdesk_mapping import (  # noqa: E402
    evaluate_original_row,
    evaluate_template_row,
)
from scripts.clinic_db_importer.hp_mapping import evaluate_hp_research_row  # noqa: E402
from scripts.clinic_db_importer.jobs_report import read_job_cutover_status  # noqa: E402
from scripts.clinic_db_importer.maps_mapping import (  # noqa: E402
    evaluate_maps_row,
    is_synthetic_seed_candidate,
)
from scripts.clinic_db_importer.normalizer_bridge import (  # noqa: E402
    NormalizerUnavailable,
    load_normalizers,
)
from scripts.clinic_db_importer.report import Tally, write_detail_rows  # noqa: E402
from scripts.clinic_db_importer.sqlite_reader import (  # noqa: E402
    capture_baseline,
    readonly_connection,
)

CLINIC_JSON_FIELDS = {
    "base_json": dict,
    "effective_json": dict,
    "departments_json": list,
    "treatments_json": list,
    "signals_json": list,
}
CLINIC_DATE_FIELDS = ["designation_date", "source_as_of_date", "first_seen_at", "last_seen_at"]


def legacy_uuid_summary(rows: list[dict], legacy_uuid_counts: dict[str, int]) -> dict:
    empty = valid = invalid = 0
    for row in rows:
        val, ok = transform.parse_uuid(row["uuid"])
        if not ok:
            invalid += 1
        elif val is None:
            empty += 1
        else:
            valid += 1
    return {
        "empty": empty,
        "non_empty_valid": valid,
        "invalid": invalid,
        "duplicate_groups": sum(1 for c in legacy_uuid_counts.values() if c > 1),
    }


def build_row_issues(row: dict, *, medical_key_counts: dict, normalizers: dict | None) -> RowIssues:
    medical_key = transform.to_optional_text(row["medical_key"])
    issues = RowIssues(medical_key=medical_key)

    if medical_key is not None:
        issues.medical_key_duplicate_in_source = medical_key_counts.get(medical_key, 0) > 1

    issues.merge_hold = bool(row["merge_hold"])
    issues.merged_into_set = row["merged_into"] is not None

    _, uuid_ok = transform.parse_uuid(row["uuid"])
    issues.legacy_uuid_invalid = not uuid_ok

    if normalizers is not None:
        mismatches = []
        checks = [
            ("name_norm", normalizers["name_norm"](row["clinic_name"])),
            ("name_prefix", normalizers["name_prefix"](row["clinic_name"])),
            ("phone_norm", normalizers["phone_norm"](row["phone"])),
            ("tel_match_key", normalizers["tel_match_key"](row["phone"])),
            ("address_norm", normalizers["address_norm"](row["address"])),
        ]
        for field, regenerated in checks:
            if regenerated != row[field]:
                mismatches.append(field)
        issues.normalizer_mismatch_fields = mismatches

    for field, expected_type in CLINIC_JSON_FIELDS.items():
        parsed, ok = transform.parse_json(row[field])
        if not ok or (parsed is not None and not isinstance(parsed, expected_type)):
            issues.invalid_json_fields.append(field)

    for field in CLINIC_DATE_FIELDS:
        _, ok = transform.parse_date(row[field])
        if not ok:
            _, ts_ok = transform.parse_timestamp(row[field])
            if not ts_ok:
                issues.invalid_date_fields.append(field)

    for field in ("age_probability",):
        _, ok = transform.parse_numeric(row[field])
        if not ok:
            issues.invalid_numeric_fields.append(field)

    for field in ("owner_equal", "active", "is_new", "merge_hold"):
        _, ok = transform.parse_bool(row[field])
        if not ok:
            issues.other_errors.append(f"invalid_boolean:{field}")

    return issues


def run(sqlite_path: str, summary_out: str | None, detail_dir: str | None) -> dict:
    baseline_before = capture_baseline(sqlite_path)

    try:
        normalizers = load_normalizers()
        normalizer_status = "loaded"
    except NormalizerUnavailable as exc:
        normalizers = None
        normalizer_status = f"unavailable: {exc}"

    with readonly_connection(sqlite_path) as conn:
        rows = [dict(r) for r in conn.execute("SELECT * FROM clinics;")]

        medical_key_counts: dict[str, int] = {}
        for row in rows:
            mk = transform.to_optional_text(row["medical_key"])
            if mk is not None:
                medical_key_counts[mk] = medical_key_counts.get(mk, 0) + 1

        legacy_uuid_counts: dict[str, int] = {}
        for row in rows:
            val, ok = transform.parse_uuid(row["uuid"])
            if ok and val is not None:
                legacy_uuid_counts[val] = legacy_uuid_counts.get(val, 0) + 1

        clinic_tally = Tally()
        review_detail: list[dict] = []
        normalizer_mismatch_field_counts: dict[str, int] = {}
        known_clinic_ids = {row["id"] for row in rows}

        for row in rows:
            issues = build_row_issues(row, medical_key_counts=medical_key_counts, normalizers=normalizers)
            uuid_val, _ = transform.parse_uuid(row["uuid"])
            if uuid_val is not None and legacy_uuid_counts.get(uuid_val, 0) > 1:
                issues.legacy_uuid_duplicate = True

            for f in issues.normalizer_mismatch_fields:
                normalizer_mismatch_field_counts[f] = normalizer_mismatch_field_counts.get(f, 0) + 1

            result = classify_clinic_row(issues, target_mode="target_empty")
            clinic_tally.add(result.decision, [r.value for r in result.reasons])
            if result.decision != "INSERT":
                review_detail.append(
                    {
                        "sqlite_id": row["id"],
                        "medical_key": issues.medical_key,
                        "decision": result.decision,
                        "reasons": [r.value for r in result.reasons],
                    }
                )

        # --- HP research dry-run ---
        hp_tally = Tally()
        hp_detail: list[dict] = []
        for row in conn.execute("SELECT * FROM research_results;"):
            row = dict(row)
            hp_result = evaluate_hp_research_row(row, known_clinic_ids=known_clinic_ids)
            hp_tally.add(hp_result.decision, hp_result.reasons)
            if hp_result.decision != "INSERT":
                hp_detail.append({"clinic_sqlite_id": hp_result.clinic_sqlite_id, "reasons": hp_result.reasons})

        # --- Maps dry-run ---
        maps_tally = Tally()
        maps_detail: list[dict] = []
        seed_candidates = 0
        for row in conn.execute("SELECT * FROM google_maps_results;"):
            row = dict(row)
            maps_result = evaluate_maps_row(row, known_clinic_ids=known_clinic_ids)
            maps_tally.add(maps_result.decision, maps_result.reasons)
            if maps_result.decision != "INSERT":
                maps_detail.append({"clinic_sqlite_id": row["clinic_id"], "reasons": maps_result.reasons})
        for row in rows:
            if is_synthetic_seed_candidate(row):
                seed_candidates += 1

        # --- Comdesk dry-run ---
        comdesk_tally = Tally()
        known_template_ids = set()
        for row in conn.execute("SELECT * FROM templates;"):
            row = dict(row)
            known_template_ids.add(row["id"])
            t_result = evaluate_template_row(row)
            comdesk_tally.add(f"template:{t_result.decision}", t_result.reasons)
        for row in conn.execute("SELECT * FROM comdesk_original_rows;"):
            row = dict(row)
            o_result = evaluate_original_row(row, known_clinic_ids=known_clinic_ids, known_template_ids=known_template_ids)
            comdesk_tally.add(f"original_row:{o_result.decision}", o_result.reasons)

        # --- Manual overrides (legacy) ---
        manual_override_count = conn.execute("SELECT COUNT(*) FROM manual_overrides;").fetchone()[0]

        # --- Job cutover status ---
        job_status = read_job_cutover_status(conn)

    baseline_after = capture_baseline(sqlite_path)
    baseline_diff = baseline_before.matches(baseline_after)

    summary = {
        "source_protection": {
            "before": baseline_before.__dict__,
            "after": baseline_after.__dict__,
            "identical": baseline_diff == [],
            "diff": baseline_diff,
        },
        "normalizer_status": normalizer_status,
        "clinics": clinic_tally.as_dict(),
        "clinics_fingerprint": clinic_tally.fingerprint(),
        "normalizer_mismatch_by_field": dict(sorted(normalizer_mismatch_field_counts.items())),
        "legacy_uuid": legacy_uuid_summary(rows, legacy_uuid_counts),
        "hp_research": hp_tally.as_dict(),
        "hp_research_fingerprint": hp_tally.fingerprint(),
        "maps_results": maps_tally.as_dict(),
        "maps_results_fingerprint": maps_tally.fingerprint(),
        "maps_synthetic_seed_candidates": seed_candidates,
        "comdesk": comdesk_tally.as_dict(),
        "comdesk_fingerprint": comdesk_tally.fingerprint(),
        "manual_overrides_legacy_count": manual_override_count,
        "job_cutover": job_status.__dict__,
    }

    if summary_out:
        os.makedirs(os.path.dirname(summary_out) or ".", exist_ok=True)
        with open(summary_out, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)

    if detail_dir:
        write_detail_rows(os.path.join(detail_dir, "clinics_review.jsonl"), review_detail)
        write_detail_rows(os.path.join(detail_dir, "hp_research_review.jsonl"), hp_detail)
        write_detail_rows(os.path.join(detail_dir, "maps_review.jsonl"), maps_detail)

    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sqlite", required=True)
    parser.add_argument("--summary-out", default=None)
    parser.add_argument("--detail-dir", default=None)
    args = parser.parse_args()

    summary = run(os.path.expanduser(args.sqlite), args.summary_out, args.detail_dir)
    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()

"""Dry-run mapping for templates (1 row) / comdesk_original_rows (21 rows)
-> clinic_ops.comdesk_templates / comdesk_original_rows.

Per docs/clinic-db-review-resolution.md section 2.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import transform
from .classify import classify_comdesk_row

EXPECTED_COLUMN_COUNT = 28


@dataclass
class ComdeskRowResult:
    decision: str
    reasons: list[str]


def evaluate_template_row(row: dict) -> ComdeskRowResult:
    headers, headers_ok = transform.parse_json(row["headers_json"])
    mapping, mapping_ok = transform.parse_json(row["mapping_json"])
    json_ok = headers_ok and mapping_ok and isinstance(headers, list) and isinstance(mapping, dict)
    length_ok = json_ok and len(headers) == EXPECTED_COLUMN_COUNT
    result = classify_comdesk_row(
        clinic_fk_resolved=True,  # templates have no clinic FK
        template_fk_resolved=True,  # templates are the FK target, not a referrer
        values_len_ok=length_ok,
        json_valid=json_ok,
    )
    return ComdeskRowResult(decision=result.decision, reasons=[r.value for r in result.reasons])


def evaluate_original_row(row: dict, *, known_clinic_ids: set[int], known_template_ids: set[str]) -> ComdeskRowResult:
    # The target column is nullable so a separately reviewed unresolved source
    # can be retained later, but unresolved rows are not eligible for automatic
    # migration or export (clinic-db-review-resolution.md section 2.3).
    clinic_fk_ok = row["clinic_id"] is not None and row["clinic_id"] in known_clinic_ids
    template_fk_ok = row["template_id"] in known_template_ids

    values, json_ok = transform.parse_json(row["row_json"])
    length_ok = json_ok and isinstance(values, list) and len(values) == EXPECTED_COLUMN_COUNT

    result = classify_comdesk_row(
        clinic_fk_resolved=clinic_fk_ok,
        template_fk_resolved=template_fk_ok,
        values_len_ok=length_ok,
        json_valid=json_ok,
    )
    return ComdeskRowResult(decision=result.decision, reasons=[r.value for r in result.reasons])

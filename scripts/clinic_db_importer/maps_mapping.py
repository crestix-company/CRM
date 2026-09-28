"""Dry-run mapping for google_maps_results (15,339 rows) -> clinic_ops.maps_results,
plus the legacy clinics.maps_* -> synthetic current-seed candidate count.

Per docs/clinic-db-review-resolution.md section 3.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import transform
from .classify import classify_maps_row


@dataclass
class MapsRowResult:
    decision: str
    reasons: list[str]


def evaluate_maps_row(row: dict, *, known_clinic_ids: set[int]) -> MapsRowResult:
    clinic_id = row["clinic_id"]
    fk_ok = clinic_id in known_clinic_ids
    _, json_ok = transform.parse_json(row["result_json"])
    result = classify_maps_row(clinic_fk_resolved=fk_ok, json_valid=json_ok)
    return MapsRowResult(decision=result.decision, reasons=[r.value for r in result.reasons])


def is_synthetic_seed_candidate(clinic_row: dict) -> bool:
    """A legacy clinic whose *current* Maps summary columns carry information
    that would otherwise have no corresponding row in clinic_ops.maps_results
    once we stop trusting `clinics.maps_*` as the source of truth. Per
    review-resolution 3.2, this needs exactly one synthetic "current-seed"
    event so the protected-current VIEW logic has something to protect from
    day one.
    """
    status = transform.to_optional_text(clinic_row.get("maps_presence_status"))
    url = transform.to_optional_text(clinic_row.get("maps_website_url"))
    return status is not None or url is not None

"""Decision rules: for each clinic row, decide INSERT / SKIP / REVIEW / ERROR.

`ERROR` is reserved for rows that could not even be evaluated (an unexpected
exception while computing RowIssues -- see run_dry_run.py's per-row try/except).
Every row that *can* be evaluated ends up INSERT, SKIP, or REVIEW; classify.py
itself never raises.

Precedence: any issue -> REVIEW (never auto-INSERT). With zero issues, the
target-simulation mode decides INSERT vs SKIP. "target_empty" simulates
migrating into an empty clinic_master.clinics (everything with a clean row is
a new INSERT). "existing_key" simulates a second/incremental run against a
target that already has some medical_keys (those become SKIP).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .reason_codes import ReasonCode


@dataclass
class RowIssues:
    medical_key: str | None
    medical_key_duplicate_in_source: bool = False
    merge_hold: bool = False
    merged_into_set: bool = False
    legacy_uuid_invalid: bool = False
    legacy_uuid_duplicate: bool = False
    normalizer_mismatch_fields: list[str] = field(default_factory=list)
    invalid_json_fields: list[str] = field(default_factory=list)
    invalid_date_fields: list[str] = field(default_factory=list)
    invalid_numeric_fields: list[str] = field(default_factory=list)
    other_errors: list[str] = field(default_factory=list)


@dataclass
class ClassificationResult:
    decision: str  # "INSERT" | "SKIP" | "REVIEW" | "ERROR"
    reasons: list[ReasonCode]


def classify_clinic_row(
    issues: RowIssues,
    *,
    target_mode: str = "target_empty",
    existing_medical_keys: set[str] | None = None,
) -> ClassificationResult:
    if target_mode not in ("target_empty", "existing_key"):
        raise ValueError(f"unknown target_mode: {target_mode}")

    reasons: list[ReasonCode] = []
    if issues.medical_key is None:
        reasons.append(ReasonCode.EMPTY_MEDICAL_KEY)
    if issues.medical_key_duplicate_in_source:
        reasons.append(ReasonCode.DUPLICATE_MEDICAL_KEY)
    if issues.merge_hold:
        reasons.append(ReasonCode.MERGE_HOLD)
    if issues.merged_into_set:
        reasons.append(ReasonCode.UNRESOLVED_MERGE)
    if issues.legacy_uuid_invalid or issues.legacy_uuid_duplicate:
        reasons.append(ReasonCode.INVALID_UUID)
    if issues.normalizer_mismatch_fields:
        reasons.append(ReasonCode.NORMALIZER_MISMATCH)
    if issues.invalid_json_fields:
        reasons.append(ReasonCode.INVALID_JSON)
    if issues.invalid_date_fields:
        reasons.append(ReasonCode.INVALID_DATE)
    if issues.invalid_numeric_fields:
        reasons.append(ReasonCode.INVALID_NUMERIC)
    if issues.other_errors:
        reasons.append(ReasonCode.OTHER_VALIDATION_ERROR)

    if reasons:
        # De-duplicate while preserving first-seen order (stable, deterministic).
        seen = set()
        ordered = [r for r in reasons if not (r in seen or seen.add(r))]
        return ClassificationResult(decision="REVIEW", reasons=ordered)

    if (
        target_mode == "existing_key"
        and existing_medical_keys is not None
        and issues.medical_key in existing_medical_keys
    ):
        return ClassificationResult(decision="SKIP", reasons=[])

    return ClassificationResult(decision="INSERT", reasons=[])


def classify_hp_research_row(*, fetch_status_valid: bool, json_valid: bool, clinic_fk_resolved: bool) -> ClassificationResult:
    reasons: list[ReasonCode] = []
    if not clinic_fk_resolved:
        reasons.append(ReasonCode.MISSING_FK)
    if not json_valid:
        reasons.append(ReasonCode.INVALID_JSON)
    if not fetch_status_valid:
        reasons.append(ReasonCode.UNMAPPED_ENUM)
    if reasons:
        return ClassificationResult(decision="REVIEW", reasons=reasons)
    return ClassificationResult(decision="INSERT", reasons=[])


def classify_maps_row(*, clinic_fk_resolved: bool, json_valid: bool) -> ClassificationResult:
    reasons: list[ReasonCode] = []
    if not clinic_fk_resolved:
        reasons.append(ReasonCode.MISSING_FK)
    if not json_valid:
        reasons.append(ReasonCode.INVALID_JSON)
    if reasons:
        return ClassificationResult(decision="REVIEW", reasons=reasons)
    return ClassificationResult(decision="INSERT", reasons=[])


def classify_comdesk_row(*, clinic_fk_resolved: bool, template_fk_resolved: bool, values_len_ok: bool, json_valid: bool) -> ClassificationResult:
    reasons: list[ReasonCode] = []
    if not template_fk_resolved:
        reasons.append(ReasonCode.MISSING_FK)
    if not clinic_fk_resolved:
        reasons.append(ReasonCode.MISSING_FK)
    if not json_valid:
        reasons.append(ReasonCode.INVALID_JSON)
    elif not values_len_ok:
        reasons.append(ReasonCode.OTHER_VALIDATION_ERROR)
    if reasons:
        return ClassificationResult(decision="REVIEW", reasons=reasons)
    return ClassificationResult(decision="INSERT", reasons=[])

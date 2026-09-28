"""Dry-run mapping for research_results (814 rows) -> clinic_ops.hp_research.

Per docs/clinic-sqlite-to-postgres-mapping.md section 2 and
docs/clinic-db-runtime-vocab-v1.md "HP fetch status".
"""
from __future__ import annotations

from dataclasses import dataclass

from . import transform
from .classify import classify_hp_research_row

ALLOWED_FETCH_STATUS = {"SUCCESS", "REVIEW", "ERROR", "NOT_FOUND"}
ALLOWED_MACHINE_RANK = {"A", "B", "C", "D"}
# UNKNOWN / NO_HP are valid *source* hp_rank values but must map to NULL, not
# be treated as an error -- see docs/clinic-sqlite-to-postgres-mapping.md.
RANK_MAPS_TO_NULL = {"UNKNOWN", "NO_HP"}


@dataclass
class HpResearchRowResult:
    clinic_sqlite_id: int
    decision: str
    reasons: list[str]
    machine_rank: str | None


def evaluate_hp_research_row(row: dict, *, known_clinic_ids: set[int]) -> HpResearchRowResult:
    clinic_id = row["clinic_id"]
    fk_ok = clinic_id in known_clinic_ids

    payload, json_ok = transform.parse_json(row["result_json"])
    payload = payload if isinstance(payload, dict) else {}

    fetch_status_raw = payload.get("research_status")
    fetch_status_ok = fetch_status_raw in ALLOWED_FETCH_STATUS if json_ok else False

    hp_rank_raw = payload.get("hp_rank")
    machine_rank: str | None
    if hp_rank_raw in ALLOWED_MACHINE_RANK:
        machine_rank = hp_rank_raw
    elif hp_rank_raw in RANK_MAPS_TO_NULL or hp_rank_raw is None:
        machine_rank = None
    else:
        machine_rank = None
        fetch_status_ok = False  # unrecognized rank value: flag for review too

    result = classify_hp_research_row(
        fetch_status_valid=fetch_status_ok, json_valid=json_ok, clinic_fk_resolved=fk_ok
    )
    return HpResearchRowResult(
        clinic_sqlite_id=clinic_id,
        decision=result.decision,
        reasons=[r.value for r in result.reasons],
        machine_rank=machine_rank,
    )

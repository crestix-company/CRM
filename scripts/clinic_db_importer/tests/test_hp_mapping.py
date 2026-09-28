import json

from scripts.clinic_db_importer.hp_mapping import evaluate_hp_research_row


def _row(clinic_id, payload):
    return {"clinic_id": clinic_id, "result_json": json.dumps(payload), "updated_at": "2026-01-01T00:00:00"}


def test_success_row_is_insert_with_rank():
    row = _row(1, {"research_status": "SUCCESS", "hp_rank": "A"})
    result = evaluate_hp_research_row(row, known_clinic_ids={1})
    assert result.decision == "INSERT"
    assert result.machine_rank == "A"


def test_unknown_rank_maps_to_null_not_review():
    row = _row(1, {"research_status": "SUCCESS", "hp_rank": "UNKNOWN"})
    result = evaluate_hp_research_row(row, known_clinic_ids={1})
    assert result.decision == "INSERT"
    assert result.machine_rank is None


def test_no_hp_rank_maps_to_null_not_review():
    row = _row(1, {"research_status": "NOT_FOUND", "hp_rank": "NO_HP"})
    result = evaluate_hp_research_row(row, known_clinic_ids={1})
    assert result.decision == "INSERT"
    assert result.machine_rank is None


def test_unrecognized_rank_value_is_review():
    row = _row(1, {"research_status": "SUCCESS", "hp_rank": "SOMETHING_ELSE"})
    result = evaluate_hp_research_row(row, known_clinic_ids={1})
    assert result.decision == "REVIEW"


def test_invalid_fetch_status_is_review():
    row = _row(1, {"research_status": "VERIFIED"})  # not a valid fetch_status value
    result = evaluate_hp_research_row(row, known_clinic_ids={1})
    assert result.decision == "REVIEW"
    assert "UNMAPPED_ENUM" in result.reasons


def test_missing_fk_is_review():
    row = _row(999, {"research_status": "SUCCESS"})
    result = evaluate_hp_research_row(row, known_clinic_ids={1})
    assert result.decision == "REVIEW"
    assert "MISSING_FK" in result.reasons


def test_invalid_json_is_review():
    row = {"clinic_id": 1, "result_json": "{not json", "updated_at": ""}
    result = evaluate_hp_research_row(row, known_clinic_ids={1})
    assert result.decision == "REVIEW"
    assert "INVALID_JSON" in result.reasons

from scripts.clinic_db_importer.maps_mapping import evaluate_maps_row, is_synthetic_seed_candidate


def test_valid_row_is_insert():
    row = {"clinic_id": 1, "result_json": "{}"}
    result = evaluate_maps_row(row, known_clinic_ids={1})
    assert result.decision == "INSERT"


def test_missing_fk_is_review():
    row = {"clinic_id": 999, "result_json": "{}"}
    result = evaluate_maps_row(row, known_clinic_ids={1})
    assert result.decision == "REVIEW"
    assert "MISSING_FK" in result.reasons


def test_invalid_json_is_review():
    row = {"clinic_id": 1, "result_json": "{broken"}
    result = evaluate_maps_row(row, known_clinic_ids={1})
    assert result.decision == "REVIEW"
    assert "INVALID_JSON" in result.reasons


def test_seed_candidate_when_status_present():
    assert is_synthetic_seed_candidate({"maps_presence_status": "MAPS_MATCHED_WEBSITE", "maps_website_url": ""}) is True


def test_seed_candidate_when_url_present():
    assert is_synthetic_seed_candidate({"maps_presence_status": "", "maps_website_url": "https://x.example.com"}) is True


def test_not_seed_candidate_when_both_empty():
    assert is_synthetic_seed_candidate({"maps_presence_status": "", "maps_website_url": ""}) is False

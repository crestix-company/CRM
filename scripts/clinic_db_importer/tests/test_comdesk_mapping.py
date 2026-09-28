import json

from scripts.clinic_db_importer.comdesk_mapping import evaluate_original_row, evaluate_template_row


def test_template_with_28_headers_is_insert():
    row = {"headers_json": json.dumps(list(range(28))), "mapping_json": json.dumps({"a": 1})}
    assert evaluate_template_row(row).decision == "INSERT"


def test_template_with_27_headers_is_review():
    row = {"headers_json": json.dumps(list(range(27))), "mapping_json": json.dumps({"a": 1})}
    assert evaluate_template_row(row).decision == "REVIEW"


def test_original_row_with_28_values_is_insert():
    row = {
        "clinic_id": 1,
        "template_id": "tmpl-1",
        "row_json": json.dumps(list(range(28))),
        "uuid": "",
        "source_hash": "h1",
        "row_number": 1,
    }
    result = evaluate_original_row(row, known_clinic_ids={1}, known_template_ids={"tmpl-1"})
    assert result.decision == "INSERT"


def test_original_row_with_29_values_is_review():
    row = {
        "clinic_id": 1,
        "template_id": "tmpl-1",
        "row_json": json.dumps(list(range(29))),
        "uuid": "",
        "source_hash": "h1",
        "row_number": 1,
    }
    result = evaluate_original_row(row, known_clinic_ids={1}, known_template_ids={"tmpl-1"})
    assert result.decision == "REVIEW"


def test_original_row_unresolved_template_is_review():
    row = {
        "clinic_id": 1,
        "template_id": "unknown-template",
        "row_json": json.dumps(list(range(28))),
        "uuid": "",
        "source_hash": "h1",
        "row_number": 1,
    }
    result = evaluate_original_row(row, known_clinic_ids={1}, known_template_ids={"tmpl-1"})
    assert result.decision == "REVIEW"
    assert "MISSING_FK" in result.reasons


def test_original_row_null_clinic_is_allowed():
    row = {
        "clinic_id": None,
        "template_id": "tmpl-1",
        "row_json": json.dumps(list(range(28))),
        "uuid": "",
        "source_hash": "h1",
        "row_number": 1,
    }
    result = evaluate_original_row(row, known_clinic_ids={1}, known_template_ids={"tmpl-1"})
    assert result.decision == "INSERT"

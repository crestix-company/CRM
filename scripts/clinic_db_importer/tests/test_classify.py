from scripts.clinic_db_importer.classify import RowIssues, classify_clinic_row
from scripts.clinic_db_importer.reason_codes import ReasonCode


def test_clean_row_target_empty_is_insert():
    issues = RowIssues(medical_key="MK-1")
    result = classify_clinic_row(issues, target_mode="target_empty")
    assert result.decision == "INSERT"
    assert result.reasons == []


def test_empty_medical_key_is_review():
    issues = RowIssues(medical_key=None)
    result = classify_clinic_row(issues)
    assert result.decision == "REVIEW"
    assert ReasonCode.EMPTY_MEDICAL_KEY in result.reasons


def test_duplicate_medical_key_is_review():
    issues = RowIssues(medical_key="MK-1", medical_key_duplicate_in_source=True)
    result = classify_clinic_row(issues)
    assert result.decision == "REVIEW"
    assert ReasonCode.DUPLICATE_MEDICAL_KEY in result.reasons


def test_merge_hold_is_review():
    issues = RowIssues(medical_key="MK-1", merge_hold=True)
    result = classify_clinic_row(issues)
    assert result.decision == "REVIEW"
    assert ReasonCode.MERGE_HOLD in result.reasons


def test_unresolved_merge_is_review():
    issues = RowIssues(medical_key="MK-1", merged_into_set=True)
    result = classify_clinic_row(issues)
    assert result.decision == "REVIEW"
    assert ReasonCode.UNRESOLVED_MERGE in result.reasons


def test_invalid_uuid_is_review():
    issues = RowIssues(medical_key="MK-1", legacy_uuid_invalid=True)
    result = classify_clinic_row(issues)
    assert result.decision == "REVIEW"
    assert ReasonCode.INVALID_UUID in result.reasons


def test_duplicate_legacy_uuid_is_review():
    issues = RowIssues(medical_key="MK-1", legacy_uuid_duplicate=True)
    result = classify_clinic_row(issues)
    assert result.decision == "REVIEW"
    assert ReasonCode.INVALID_UUID in result.reasons


def test_normalizer_mismatch_is_review():
    issues = RowIssues(medical_key="MK-1", normalizer_mismatch_fields=["name_norm"])
    result = classify_clinic_row(issues)
    assert result.decision == "REVIEW"
    assert ReasonCode.NORMALIZER_MISMATCH in result.reasons


def test_invalid_json_is_review():
    issues = RowIssues(medical_key="MK-1", invalid_json_fields=["base_json"])
    result = classify_clinic_row(issues)
    assert result.decision == "REVIEW"
    assert ReasonCode.INVALID_JSON in result.reasons


def test_invalid_date_is_review():
    issues = RowIssues(medical_key="MK-1", invalid_date_fields=["designation_date"])
    result = classify_clinic_row(issues)
    assert result.decision == "REVIEW"
    assert ReasonCode.INVALID_DATE in result.reasons


def test_invalid_numeric_is_review():
    issues = RowIssues(medical_key="MK-1", invalid_numeric_fields=["age_probability"])
    result = classify_clinic_row(issues)
    assert result.decision == "REVIEW"
    assert ReasonCode.INVALID_NUMERIC in result.reasons


def test_other_error_is_review():
    issues = RowIssues(medical_key="MK-1", other_errors=["invalid_boolean:active"])
    result = classify_clinic_row(issues)
    assert result.decision == "REVIEW"
    assert ReasonCode.OTHER_VALIDATION_ERROR in result.reasons


def test_existing_key_simulation_is_skip():
    issues = RowIssues(medical_key="MK-1")
    result = classify_clinic_row(issues, target_mode="existing_key", existing_medical_keys={"MK-1"})
    assert result.decision == "SKIP"


def test_existing_key_simulation_new_key_is_insert():
    issues = RowIssues(medical_key="MK-NEW")
    result = classify_clinic_row(issues, target_mode="existing_key", existing_medical_keys={"MK-1"})
    assert result.decision == "INSERT"


def test_issues_never_produce_skip_even_if_key_exists():
    """An issue must always win over SKIP -- a row with a problem is never
    silently treated as 'already there, nothing to do'."""
    issues = RowIssues(medical_key="MK-1", merge_hold=True)
    result = classify_clinic_row(issues, target_mode="existing_key", existing_medical_keys={"MK-1"})
    assert result.decision == "REVIEW"

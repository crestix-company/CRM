from scripts.clinic_db_importer.reason_codes import ReasonCode

EXPECTED = {
    "EMPTY_MEDICAL_KEY",
    "DUPLICATE_MEDICAL_KEY",
    "MERGE_HOLD",
    "UNRESOLVED_MERGE",
    "NORMALIZER_MISMATCH",
    "INVALID_UUID",
    "INVALID_JSON",
    "INVALID_DATE",
    "INVALID_NUMERIC",
    "UNMAPPED_ENUM",
    "MISSING_FK",
    "OTHER_VALIDATION_ERROR",
}


def test_reason_code_is_closed_set():
    assert {code.value for code in ReasonCode} == EXPECTED


def test_reason_code_values_are_strings():
    for code in ReasonCode:
        assert isinstance(code.value, str)
        assert code.value == code.value.upper()

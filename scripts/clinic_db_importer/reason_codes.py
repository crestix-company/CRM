"""Fixed vocabulary for why a row was not classified as a plain INSERT candidate.

Kept as a closed set (not free-text) so that summary counts are stable and
comparable across dry-run executions (see determinism tests).
"""
from enum import Enum


class ReasonCode(str, Enum):
    EMPTY_MEDICAL_KEY = "EMPTY_MEDICAL_KEY"
    DUPLICATE_MEDICAL_KEY = "DUPLICATE_MEDICAL_KEY"
    MERGE_HOLD = "MERGE_HOLD"
    UNRESOLVED_MERGE = "UNRESOLVED_MERGE"
    NORMALIZER_MISMATCH = "NORMALIZER_MISMATCH"
    INVALID_UUID = "INVALID_UUID"
    INVALID_JSON = "INVALID_JSON"
    INVALID_DATE = "INVALID_DATE"
    INVALID_NUMERIC = "INVALID_NUMERIC"
    UNMAPPED_ENUM = "UNMAPPED_ENUM"
    MISSING_FK = "MISSING_FK"
    OTHER_VALIDATION_ERROR = "OTHER_VALIDATION_ERROR"

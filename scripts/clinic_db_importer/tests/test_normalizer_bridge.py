import pytest

from scripts.clinic_db_importer.normalizer_bridge import NormalizerUnavailable, load_normalizers

try:
    NORMALIZERS = load_normalizers()
except NormalizerUnavailable:
    NORMALIZERS = None

pytestmark = pytest.mark.skipif(
    NORMALIZERS is None, reason="Clinic Lead repo not available in this environment"
)


def test_name_norm_matches_clinic_lead_behavior():
    # Known behavior per src/normalizer/clinic_name.py: strips a leading
    # 医療法人-style prefix and casefolds.
    assert NORMALIZERS["name_norm"]("医療法人社団健康会サンプルクリニック") == "サンプルクリニック"


def test_name_prefix_is_first_two_chars_of_name_norm():
    name_norm = NORMALIZERS["name_norm"]("テストクリニック")
    assert NORMALIZERS["name_prefix"]("テストクリニック") == name_norm[:2]


def test_phone_norm_strips_non_digits():
    assert NORMALIZERS["phone_norm"]("03-1234-5678") == "0312345678"


def test_tel_match_key_drops_leading_zero():
    assert NORMALIZERS["tel_match_key"]("03-1234-5678") == "312345678"


def test_address_norm_converts_kanji_numerals():
    result = NORMALIZERS["address_norm"]("東京都千代田区三丁目一番")
    assert "3" in result and "1" in result


def test_normalizers_are_deterministic():
    a = NORMALIZERS["name_norm"]("同じ医院名クリニック")
    b = NORMALIZERS["name_norm"]("同じ医院名クリニック")
    assert a == b

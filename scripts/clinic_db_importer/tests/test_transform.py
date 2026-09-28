from scripts.clinic_db_importer import transform


def test_to_optional_text():
    assert transform.to_optional_text("") is None
    assert transform.to_optional_text("   ") is None
    assert transform.to_optional_text(None) is None
    assert transform.to_optional_text("x") == "x"


def test_parse_bool():
    assert transform.parse_bool(0) == (False, True)
    assert transform.parse_bool(1) == (True, True)
    assert transform.parse_bool(None) == (None, True)
    assert transform.parse_bool(2) == (None, False)


def test_parse_numeric():
    assert transform.parse_numeric(None) == (None, True)
    assert transform.parse_numeric("") == (None, True)
    assert transform.parse_numeric("0.42") == (0.42, True)
    assert transform.parse_numeric("not-a-number") == (None, False)


def test_parse_date_valid():
    value, ok = transform.parse_date("2024-04-01")
    assert ok is True
    assert value.isoformat() == "2024-04-01"


def test_parse_date_empty_is_ok_none():
    assert transform.parse_date("") == (None, True)
    assert transform.parse_date(None) == (None, True)


def test_parse_date_invalid():
    value, ok = transform.parse_date("not-a-date")
    assert ok is False
    assert value is None


def test_parse_json_valid():
    value, ok = transform.parse_json('{"a": 1}')
    assert ok is True
    assert value == {"a": 1}


def test_parse_json_empty_is_ok_none():
    assert transform.parse_json("") == (None, True)


def test_parse_json_invalid():
    value, ok = transform.parse_json("{not json")
    assert ok is False
    assert value is None


def test_parse_uuid_empty_is_none():
    assert transform.parse_uuid("") == (None, True)


def test_parse_uuid_valid():
    value, ok = transform.parse_uuid("11111111-1111-1111-1111-111111111111")
    assert ok is True
    assert value == "11111111-1111-1111-1111-111111111111"


def test_parse_uuid_invalid():
    value, ok = transform.parse_uuid("not-a-uuid")
    assert ok is False
    assert value is None


def test_strip_nul_removes_null_bytes():
    assert transform.strip_nul("abc\x00def") == "abcdef"


def test_to_optional_text_strips_nul():
    assert transform.to_optional_text("https://example.com/\x00broken") == "https://example.com/broken"


def test_sanitize_json_value_strips_nested_nul():
    value = {"a": "x\x00y", "b": ["p\x00q", 1, None], "c": {"d": "e\x00f"}}
    sanitized = transform.sanitize_json_value(value)
    assert sanitized == {"a": "xy", "b": ["pq", 1, None], "c": {"d": "ef"}}

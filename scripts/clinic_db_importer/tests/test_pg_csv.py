from scripts.clinic_db_importer import pg_csv


def test_field_none_is_empty_unquoted():
    assert pg_csv.field(None) == ""


def test_field_string_is_quoted():
    assert pg_csv.field("hello") == '"hello"'


def test_field_empty_string_is_quoted_empty():
    """Distinguishes an intentional empty string from NULL (COPY FORMAT csv semantics)."""
    assert pg_csv.field("") == '""'


def test_field_escapes_embedded_quotes():
    assert pg_csv.field('he said "hi"') == '"he said ""hi"""'


def test_field_bool():
    assert pg_csv.field(True) == "true"
    assert pg_csv.field(False) == "false"


def test_field_number_unquoted():
    assert pg_csv.field(42) == "42"
    assert pg_csv.field(0.5) == "0.5"


def test_field_strips_nul_bytes():
    assert pg_csv.field("a\x00b") == '"ab"'


def test_json_field_none():
    assert pg_csv.json_field(None) == ""


def test_json_field_sanitizes_nested_nul():
    result = pg_csv.json_field({"url": "https://example.com/\x00page"})
    assert "\\u0000" not in result
    assert "\x00" not in result


def test_text_array_field_none():
    assert pg_csv.text_array_field(None) == ""


def test_text_array_field_basic():
    result = pg_csv.text_array_field(["内科", "外科"])
    assert result == '"{""内科"",""外科""}"'


def test_text_array_field_with_none_element():
    result = pg_csv.text_array_field(["a", None])
    assert result == '"{""a"",NULL}"'


def test_write_copy_block_format():
    import io
    buf = io.StringIO()
    pg_csv.write_copy_block(buf, "clinic_master", "clinics", ["clinic_id", "medical_key"],
                             [["\"x\"", "\"MK-1\""]])
    output = buf.getvalue()
    assert output.startswith("COPY clinic_master.clinics (clinic_id, medical_key) FROM STDIN WITH (FORMAT csv);\n")
    assert '"x","MK-1"' in output
    assert output.rstrip().endswith("\\.")

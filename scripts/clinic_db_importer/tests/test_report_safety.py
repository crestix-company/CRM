import pytest

from scripts.clinic_db_importer.report import REPO_ROOT, write_detail_rows


def test_refuses_to_write_inside_repo():
    with pytest.raises(ValueError, match="Refusing to write"):
        write_detail_rows(f"{REPO_ROOT}/docs/should-not-exist.jsonl", [{"a": 1}])


def test_allows_writing_outside_repo(tmp_path):
    target = tmp_path / "outside" / "detail.jsonl"
    write_detail_rows(str(target), [{"a": 1}, {"b": 2}])
    lines = target.read_text().strip().splitlines()
    assert len(lines) == 2

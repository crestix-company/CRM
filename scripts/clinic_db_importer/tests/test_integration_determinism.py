import json

from scripts.clinic_db_importer.run_dry_run import run
from scripts.clinic_db_importer.tests.conftest import insert_clinic

import sqlite3


def _populate(path: str):
    conn = sqlite3.connect(path)
    # address/address_norm left at conftest defaults ("東京都千代田区1-1" both raw and
    # normalized -- no kanji numerals or unicode dashes to convert, so normalize_address
    # is a no-op here and the stored value already matches what regeneration would produce).
    insert_clinic(conn, medical_key="MK-CLEAN-1", clinic_name="正常クリニック", phone="03-1111-2222",
                  name_norm="正常クリニック".casefold(), name_prefix="正常クリニック".casefold()[:2],
                  phone_norm="0311112222", tel_match_key="311112222")
    insert_clinic(conn, medical_key="", clinic_name="空キー医院")
    insert_clinic(conn, medical_key="MK-MERGEHOLD", clinic_name="保留中医院", merge_hold=1)
    insert_clinic(conn, medical_key="MK-BADUUID", clinic_name="不正UUID医院", uuid="not-a-uuid")
    insert_clinic(conn, medical_key="MK-BADJSON", clinic_name="不正JSON医院", base_json="{not valid")
    conn.execute(
        "INSERT INTO research_results (clinic_id, result_json, updated_at) VALUES (1, ?, '2026-01-01')",
        (json.dumps({"research_status": "SUCCESS", "hp_rank": "A"}),),
    )
    conn.commit()
    conn.close()


def test_dry_run_produces_expected_decisions(fixture_db_path, tmp_path):
    _populate(fixture_db_path)
    summary_path = str(tmp_path / "summary.json")
    detail_dir = str(tmp_path / "detail")

    summary = run(fixture_db_path, summary_path, detail_dir)

    decisions = summary["clinics"]["decisions"]
    assert decisions.get("INSERT", 0) == 1
    assert decisions.get("REVIEW", 0) == 4
    reasons = summary["clinics"]["reasons"]
    assert reasons.get("EMPTY_MEDICAL_KEY", 0) == 1
    assert reasons.get("MERGE_HOLD", 0) == 1
    assert reasons.get("INVALID_UUID", 0) == 1
    assert reasons.get("INVALID_JSON", 0) == 1

    with open(summary_path) as f:
        assert json.load(f) == summary

    assert summary["source_protection"]["identical"] is True


def test_dry_run_is_deterministic_across_two_runs(fixture_db_path, tmp_path):
    _populate(fixture_db_path)

    summary1 = run(fixture_db_path, str(tmp_path / "s1.json"), str(tmp_path / "d1"))
    summary2 = run(fixture_db_path, str(tmp_path / "s2.json"), str(tmp_path / "d2"))

    assert summary1["clinics_fingerprint"] == summary2["clinics_fingerprint"]
    assert summary1["clinics"] == summary2["clinics"]
    assert summary1["hp_research_fingerprint"] == summary2["hp_research_fingerprint"]

import json
import sqlite3

import pytest

CLINICS_SCHEMA = """
CREATE TABLE clinics(
  id INTEGER PRIMARY KEY, uuid TEXT NOT NULL DEFAULT '', clinic_name TEXT NOT NULL DEFAULT '',
  phone TEXT NOT NULL DEFAULT '', address TEXT NOT NULL DEFAULT '',
  phone_norm TEXT NOT NULL DEFAULT '', name_norm TEXT NOT NULL DEFAULT '',
  name_prefix TEXT NOT NULL DEFAULT '', address_norm TEXT NOT NULL DEFAULT '',
  medical_key TEXT NOT NULL DEFAULT '', prefecture TEXT NOT NULL DEFAULT '',
  medical_type TEXT NOT NULL DEFAULT '', base_json TEXT NOT NULL DEFAULT '{}',
  effective_json TEXT NOT NULL DEFAULT '{}', active INTEGER NOT NULL DEFAULT 0,
  designation_date TEXT NOT NULL DEFAULT '', recent_until TEXT NOT NULL DEFAULT '',
  registration_reason TEXT NOT NULL DEFAULT '', owner_equal INTEGER,
  age_probability REAL, hp_status TEXT NOT NULL DEFAULT 'UNRESEARCHED',
  hp_url TEXT NOT NULL DEFAULT '', hp_rank TEXT NOT NULL DEFAULT 'UNKNOWN',
  signal_count INTEGER NOT NULL DEFAULT 0, hot_status TEXT NOT NULL DEFAULT '通常',
  departments_json TEXT NOT NULL DEFAULT '[]', treatments_json TEXT NOT NULL DEFAULT '[]',
  signals_json TEXT NOT NULL DEFAULT '[]', first_seen_at TEXT NOT NULL DEFAULT '',
  last_seen_at TEXT NOT NULL DEFAULT '', source_as_of_date TEXT NOT NULL DEFAULT '',
  is_new INTEGER NOT NULL DEFAULT 0, merged_into INTEGER, tel_match_key TEXT NOT NULL DEFAULT '',
  merge_hold INTEGER NOT NULL DEFAULT 0, maps_presence_status TEXT NOT NULL DEFAULT '',
  maps_profile_url TEXT NOT NULL DEFAULT '', maps_website_url TEXT NOT NULL DEFAULT '',
  maps_match_method TEXT NOT NULL DEFAULT '', maps_checked_at TEXT NOT NULL DEFAULT '',
  exclude_reason TEXT NOT NULL DEFAULT ''
);
CREATE TABLE research_results(clinic_id INTEGER PRIMARY KEY, result_json TEXT NOT NULL, updated_at TEXT);
CREATE TABLE hp_pages(clinic_id INTEGER, url TEXT, page_json TEXT, checked_at TEXT);
CREATE TABLE google_maps_results(
  id INTEGER PRIMARY KEY, clinic_id INTEGER, batch_id TEXT, row_number INTEGER,
  result_json TEXT NOT NULL, maps_match_status TEXT, maps_match_method TEXT,
  maps_profile_url TEXT, maps_website_url TEXT, scraped_at TEXT, created_at TEXT
);
CREATE TABLE manual_overrides(clinic_id INTEGER, field TEXT, value_json TEXT, source TEXT, note TEXT, updated_at TEXT);
CREATE TABLE templates(id TEXT PRIMARY KEY, headers_json TEXT NOT NULL, mapping_json TEXT NOT NULL, created_at TEXT);
CREATE TABLE comdesk_original_rows(
  id INTEGER PRIMARY KEY, clinic_id INTEGER, template_id TEXT, row_json TEXT NOT NULL,
  uuid TEXT, source_hash TEXT, row_number INTEGER, created_at TEXT
);
CREATE TABLE research_jobs(id TEXT PRIMARY KEY, kind TEXT, options_json TEXT, status TEXT NOT NULL DEFAULT 'PAUSED', max_searches INTEGER, search_count INTEGER NOT NULL DEFAULT 0, created_at TEXT, updated_at TEXT);
CREATE TABLE research_job_items(job_id TEXT, clinic_id INTEGER, state TEXT NOT NULL DEFAULT 'PENDING', result TEXT NOT NULL DEFAULT '', note TEXT NOT NULL DEFAULT '', lease_until TEXT NOT NULL DEFAULT '', PRIMARY KEY(job_id, clinic_id));
"""


@pytest.fixture
def fixture_db_path(tmp_path):
    path = tmp_path / "clinics_fixture.sqlite3"
    conn = sqlite3.connect(str(path))
    conn.executescript(CLINICS_SCHEMA)
    conn.commit()
    conn.close()
    return str(path)


def insert_clinic(conn: sqlite3.Connection, **overrides):
    base = dict(
        uuid="", clinic_name="Fixture Clinic", phone="03-1234-5678", address="東京都千代田区1-1",
        phone_norm="0312345678", name_norm="fixtureclinic", name_prefix="fi", address_norm="東京都千代田区1-1",
        medical_key="MK-0001", prefecture="東京都", medical_type="医科",
        base_json="{}", effective_json="{}", active=1,
        designation_date="", recent_until="", registration_reason="",
        owner_equal=None, age_probability=None, hp_status="UNRESEARCHED", hp_url="", hp_rank="UNKNOWN",
        signal_count=0, hot_status="通常", departments_json="[]", treatments_json="[]", signals_json="[]",
        first_seen_at="", last_seen_at="", source_as_of_date="", is_new=0, merged_into=None,
        tel_match_key="12345678", merge_hold=0, maps_presence_status="", maps_profile_url="",
        maps_website_url="", maps_match_method="", maps_checked_at="", exclude_reason="",
    )
    base.update(overrides)
    cols = ",".join(base.keys())
    placeholders = ",".join("?" for _ in base)
    cur = conn.execute(f"INSERT INTO clinics ({cols}) VALUES ({placeholders})", list(base.values()))
    return cur.lastrowid

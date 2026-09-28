# Clinic Production SQLite Read-only Audit

> 実測日: 2026-09-28 (Asia/Tokyo)  
> 対象: `/Users/maekawahiroyuki/CrestixData/clinic-lead/clinics.sqlite3`  
> 方法: `sqlite3 -readonly 'file:...?mode=ro'` + `PRAGMA query_only=ON`。DDL/DMLは実行していない。  
> この文書は調査結果であり、SupabaseへのDDL/DML、SQLite import、package installを伴わない。

## 1. Read-only safety baseline

| 項目 | 調査前 |
|---|---|
| SHA-256 | `5b8c37838006545498ec132e09e333dd6200ceccfce09b3b094af75899265c40` |
| mtime (epoch) | `1790563202` |
| mtime (JST) | `2026-09-28T11:40:02+0900` |
| file size | `1,090,035,712 bytes` |
| `clinics` row count | `162,258` |
| `PRAGMA integrity_check` | `ok` |

調査完了後にも同じ5項目を再取得し、本文末尾の「調査後検証」に記録する。

## 2. `clinics` schema

### 2.1 Columns

SQLiteの`notnull=0`はDDL上NULL可能、`notnull=1`はNOT NULLを表す。`id`は`INTEGER PRIMARY KEY`。

| cid | column | SQLite type | nullable | default | PK |
|---:|---|---|---|---|---:|
| 0 | id | INTEGER | yes (PK semantics) | — | 1 |
| 1 | uuid | TEXT | no | `''` | 0 |
| 2 | clinic_name | TEXT | no | `''` | 0 |
| 3 | phone | TEXT | no | `''` | 0 |
| 4 | address | TEXT | no | `''` | 0 |
| 5 | phone_norm | TEXT | no | `''` | 0 |
| 6 | name_norm | TEXT | no | `''` | 0 |
| 7 | name_prefix | TEXT | no | `''` | 0 |
| 8 | address_norm | TEXT | no | `''` | 0 |
| 9 | medical_key | TEXT | no | `''` | 0 |
| 10 | prefecture | TEXT | no | `''` | 0 |
| 11 | medical_type | TEXT | no | `''` | 0 |
| 12 | base_json | TEXT | no | `'{}'` | 0 |
| 13 | effective_json | TEXT | no | `'{}'` | 0 |
| 14 | active | INTEGER | no | `0` | 0 |
| 15 | designation_date | TEXT | no | `''` | 0 |
| 16 | recent_until | TEXT | no | `''` | 0 |
| 17 | registration_reason | TEXT | no | `''` | 0 |
| 18 | owner_equal | INTEGER | yes | — | 0 |
| 19 | age_probability | REAL | yes | — | 0 |
| 20 | hp_status | TEXT | no | `'UNRESEARCHED'` | 0 |
| 21 | hp_url | TEXT | no | `''` | 0 |
| 22 | hp_rank | TEXT | no | `'UNKNOWN'` | 0 |
| 23 | signal_count | INTEGER | no | `0` | 0 |
| 24 | hot_status | TEXT | no | `'通常'` | 0 |
| 25 | departments_json | TEXT | no | `'[]'` | 0 |
| 26 | treatments_json | TEXT | no | `'[]'` | 0 |
| 27 | signals_json | TEXT | no | `'[]'` | 0 |
| 28 | first_seen_at | TEXT | no | — | 0 |
| 29 | last_seen_at | TEXT | no | — | 0 |
| 30 | source_as_of_date | TEXT | no | `''` | 0 |
| 31 | is_new | INTEGER | no | `0` | 0 |
| 32 | merged_into | INTEGER | yes | — | 0 |
| 33 | tel_match_key | TEXT | no | `''` | 0 |
| 34 | merge_hold | INTEGER | no | `0` | 0 |
| 35 | maps_presence_status | TEXT | no | `''` | 0 |
| 36 | maps_profile_url | TEXT | no | `''` | 0 |
| 37 | maps_website_url | TEXT | no | `''` | 0 |
| 38 | maps_match_method | TEXT | no | `''` | 0 |
| 39 | maps_checked_at | TEXT | no | `''` | 0 |
| 40 | exclude_reason | TEXT | no | `''` | 0 |

### 2.2 Indexes, uniqueness, foreign keys

- Unique: partial unique index `idx_clinic_uuid ON clinics(uuid) WHERE uuid<>'' AND merged_into IS NULL`。
- Non-unique: `idx_clinic_med(medical_key)`, `idx_clinic_phone(phone_norm)`,
  `idx_clinic_name_address(name_norm,address_norm)`, `idx_clinic_prefix(name_prefix,prefecture)`,
  `idx_clinic_filter(hp_status,prefecture,hp_rank,signal_count)`, `idx_clinic_hot(hot_status)`,
  `idx_clinic_tel_match(tel_match_key)`。
- Foreign key: `merged_into -> clinics.id`, `ON UPDATE NO ACTION`, `ON DELETE NO ACTION`。
- `medical_key`にSQLite UNIQUE制約はない。実データの非空値は重複0だが、PostgreSQL側UNIQUEは必須。

## 3. `medical_key` profile

| metric | count |
|---|---:|
| total | 162,258 |
| NULL | 0 |
| empty string | 16 |
| non-empty | 162,242 |
| distinct non-empty | 162,242 |
| duplicate groups (non-empty) | 0 |
| duplicate extra rows (non-empty) | 0 |

空文字16件は自動migrationしない。`clinic_ops.import_log_items`の`decision='review'`候補とし、
`clinic_master.clinics`へは有効な`medical_key`が確定するまでINSERTしない。

## 4. Legacy UUID profile

既存UUID相当列は`clinics.uuid TEXT NOT NULL DEFAULT ''`。
valid判定はcanonicalな36文字、ハイフン位置`8-4-4-4-12`、16進文字のみで実測した。

| metric | count |
|---|---:|
| total | 162,258 |
| NULL | 0 |
| empty string | 162,237 |
| non-empty / distinct | 21 / 21 |
| valid UUID | 21 |
| invalid UUID | 0 |
| duplicate groups / extra rows | 0 / 0 |

invalid/duplicate例は該当なし。現時点の実測では非空21件は一意だが、移行DDLで
`legacy_uuid UNIQUE`を有効にする判断は別工程とし、今回は制約を追加しない。空文字はNULLへ変換する。

## 5. HP data found in SQLite

実在するHP関連格納先のみを列挙する。

- `clinics`: `hp_status`, `hp_url`, `hp_rank`, `signal_count`, `hot_status`,
  `treatments_json`, `signals_json`。
- `research_results` (814 rows): `clinic_id`, `result_json`, `updated_at`。
  `result_json`には`hp_url`, `hp_status`, `hp_rank`, `hp_score`, `hp_checked_at`,
  `hp_match_score`, `hp_rank_version`, `research_status`, `research_error`, `crawl_errors`,
  `hp_candidates`, `hp_identity_pages`, `hp_match_reason`, `hp_rank_reasons`等が存在する。
- `hp_pages` (9,944 rows): `clinic_id`, `url`, `page_json`, `checked_at`。
  `page_json`の実キーは`url`, `title`, `headings`, `text`。
- `research_job_items` (2,838 rows): `job_id`, `clinic_id`, `state`, `result`, `note`,
  `lease_until`。`research_jobs`は57 rowsでjobのkind/status/options/timestampsを保持。
- `manual_overrides`は`clinic_id`, `field`, `value_json`, `source`, `note`, `updated_at`を持つが、
  現在0 rows。したがって人間によるHP rank訂正履歴は実データとして確認できなかった。

`clinics.hp_rank`分布: `UNKNOWN=161,619`, `B=266`, `C=211`, `A=127`, `D=32`, `NO_HP=3`。
PostgreSQLのmachine rank許可値はA/B/C/Dのみなので、`UNKNOWN`/`NO_HP`はrankへCOPYしない。
`clinics.hp_status`分布: `UNRESEARCHED=161,444`, `VERIFIED=643`, `REVIEW=146`,
`ERROR=22`, `NOT_FOUND=3`。HP URL非空は643件。

## 6. Maps data found in SQLite

- `clinics`: `maps_presence_status`, `maps_profile_url`, `maps_website_url`,
  `maps_match_method`, `maps_checked_at`, `exclude_reason`。
- `google_maps_results` (15,339 rows): `id`, `clinic_id`, `batch_id`, `row_number`,
  `result_json`, `maps_match_status`, `maps_match_method`, `maps_profile_url`,
  `maps_website_url`, `scraped_at`, `created_at`。
- `google_maps_results.result_json`には上記に加え、`maps_name`, `maps_address`, `maps_phone`,
  `address_match`, `name_match`, `phone_match`, `scrape_status`, `website_status`,
  `診療日`, `午前始`, `午前終`, `午後始`, `午後終`, `休診日`, `営業時間原文`が存在する。

`place_id`, `rating`, `review_count`, `latitude`, `longitude`は、調査対象schema/JSONキーのいずれにも
存在しなかった。存在しない値を推測・生成しない。`clinics`のMaps集約値がある行は13,954件、
履歴側`google_maps_results`は15,339件であり、migration元は履歴側を優先して別行として扱う。

## 7. Python UUIDv7 runtime

| check | result |
|---|---|
| `python --version` | command not found |
| `python3 --version` | Python 3.9.6 |
| executable | `/Library/Developer/CommandLineTools/usr/bin/python3` |
| stdlib `uuid.uuid7()` | unavailable |
| installed `uuid6` package | unavailable |
| `pyproject.toml` | not found under the DB directory |
| `requirements*.txt` | not found under the DB directory |
| `.python-version` / `runtime.txt` / Pipfile / lockfile | not found under the DB directory |

現在確認できるruntimeではstdlib `uuid.uuid7()`も`uuid6`も使用できない。package install禁止の今回の
範囲では、`docs/clinic-uuid-strategy.md`記載の**依存ゼロRFC 9562 UUIDv7 fallback**を採用候補とする。
Clinic Leadアプリ本体のruntime設定はDB配置ディレクトリに存在しないため、実装時にはアプリrepoで再確認する。

## 8. 調査後検証

この節は全queryとdocs作成後に再取得し、調査前と一致した値を記録する。

- SHA-256: `5b8c37838006545498ec132e09e333dd6200ceccfce09b3b094af75899265c40` (調査前と一致)
- mtime: epoch `1790563202` / `2026-09-28T11:40:02+0900` (調査前と一致)
- `clinics` count: `162,258` (調査前と一致)
- integrity: `ok`
- non-empty `medical_key` duplicate groups: `0`

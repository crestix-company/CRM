# Clinic SQLite → PostgreSQL Mapping

> Source audit: `docs/clinic-db-readonly-audit.md`  
> Target drafts: `clinic_master.clinics`, `clinic_ops.hp_research`,
> `clinic_ops.hp_rank_feedback`, `clinic_ops.maps_results`。  
> 本表はmapping設計のみ。DDL/DML/importは実行しない。

Migration actionは`COPY`, `TRANSFORM`, `DERIVE`, `REVIEW`, `DO_NOT_MIGRATE`のいずれか。
`nullable`はPostgreSQL targetの許容性を示す。`—`は現在のtarget列がないことを示す。

## 1. Clinic master mapping

| SQLite column | SQLite type | Postgres schema | Postgres table | Postgres column | Postgres type | transform | nullable | migration action | notes |
|---|---|---|---|---|---|---|---|---|---|
| `clinics.id` | INTEGER | — | — | — | — | importer内のjoin keyとしてのみ使用 | — | DO_NOT_MIGRATE | PostgreSQL PKには流用しない |
| — | — | clinic_master | clinics | clinic_id | uuid | PythonでUUIDv7生成 | no | DERIVE | DB defaultなし |
| `clinics.medical_key` | TEXT | clinic_master | clinics | medical_key | text | 非空のみtrim/同一性確認後COPY | no | REVIEW | 空文字16件はINSERTせずREVIEW |
| `clinics.uuid` | TEXT | clinic_master | clinics | legacy_uuid | uuid | `'' -> NULL`; canonical UUIDをcast | yes | TRANSFORM | 非空21件valid/unique。まだUNIQUE制約は付けない |
| `clinics.clinic_name` | TEXT | clinic_master | clinics | clinic_name | text | identity | no | COPY | 空文字品質はpromotion前検証対象 |
| `clinics.name_norm` | TEXT | clinic_master | generated/search projection | name_norm | text | raw nameから現normalizerで再生成 | no | DERIVE | matching consumerあり。algorithm version固定必須 |
| `clinics.name_prefix` | TEXT | clinic_master | generated/search projection | name_prefix | text | name_norm先頭2文字 | no | DERIVE | matching/index consumer |
| `clinics.phone` | TEXT | clinic_master | clinics | phone | text | `'' -> NULL` | yes | TRANSFORM | raw phoneを保持 |
| `clinics.phone_norm` | TEXT | clinic_master | generated/search projection | phone_norm | text | raw phoneから現normalizerで再生成 | no | DERIVE | search consumer |
| `clinics.tel_match_key` | TEXT | clinic_master | generated/search projection | tel_match_key | text | raw phoneから現normalizerで再生成 | no | DERIVE | Maps matching consumer |
| `clinics.address` | TEXT | clinic_master | clinics | address | text | `'' -> NULL` | yes | TRANSFORM | raw addressを保持 |
| `clinics.address_norm` | TEXT | clinic_master | generated/search projection | address_norm | text | raw addressから現normalizerで再生成 | no | DERIVE | Maps matching consumer |
| `clinics.prefecture` | TEXT | clinic_master | clinics | prefecture | text | `'' -> NULL`; 表記検証 | yes | TRANSFORM | JISコード化は未決定 |
| `base_json.postal_code` | JSON text | clinic_master | clinics | postal_code | text | JSON extract; `'' -> NULL` | yes | TRANSFORM | 実在21件のみ |
| `clinics.hp_url` | TEXT | clinic_ops | current HP projection | current_hp_website | text | manual SET→verified machine HPの順で解決 | yes | DERIVE | 単一master websiteへ統合しない。consumer別priorityはreview-resolution参照 |
| `clinics.active` | INTEGER | clinic_master | clinics | active (proposed) | boolean | 0/1→boolean | no | TRANSFORM | MUST_MIGRATE: default filter/job/metrics |
| `clinics.first_seen_at` | TEXT | clinic_master | clinics | first_seen_at (proposed) | timestamptz | timestamp parse | no | TRANSFORM | SHOULD_MIGRATE: DB created_atとは意味が異なる |
| `clinics.last_seen_at` | TEXT | clinic_master | clinics | last_seen_at (proposed) | timestamptz | timestamp parse | no | TRANSFORM | SHOULD_MIGRATE: DB updated_atとは意味が異なる |
| constant | — | clinic_master | clinics | source | text | `'legacy_sqlite'` | no | DERIVE | target defaultと一致 |
| migration batch | — | clinic_master | clinics | imported_batch_id | uuid | current batch ID | yes | DERIVE | rollback attribution |
| `clinics.medical_type` | TEXT | clinic_master | clinics | medical_type (proposed) | text | identity | yes | COPY | MUST_MIGRATE: filter/job/source importで使用 |
| `clinics.designation_date` | TEXT | clinic_master | clinics | designation_date (proposed) | date | empty→NULL; date parse | yes | TRANSFORM | MUST_MIGRATE: 指定日/新規開業filterとexport |
| `clinics.recent_until` | TEXT | clinic_master | clinics/view | recent_until (derived) | date | designation_date + 10 years | yes | DERIVE | consumerあり。正本から安全に再生成 |
| `clinics.registration_reason` | TEXT | clinic_master | clinics | registration_reason (proposed) | text | empty→NULL | yes | TRANSFORM | MUST_MIGRATE: 新規指定filter |
| `clinics.owner_equal` | INTEGER | clinic_master | clinics | owner_equal (proposed) | boolean | 0/1→boolean | yes | TRANSFORM | MUST_MIGRATE: 営業filter |
| `clinics.age_probability` | REAL | clinic_master | clinics | age_probability (proposed) | numeric | numeric cast | yes | TRANSFORM | MUST_MIGRATE: filter/UI/metrics |
| `clinics.departments_json` | TEXT/JSON | clinic_master | clinics/child | departments (proposed) | text[]/rows | JSON array decode | yes | TRANSFORM | MUST_MIGRATE: 診療科filter |
| `clinics.source_as_of_date` | TEXT | clinic_master | clinics | source_as_of_date (proposed) | date | empty→NULL; date parse | yes | TRANSFORM | MUST_MIGRATE: stale import防止 |
| `clinics.base_json` | TEXT/JSON | clinic_master | clinics | source_payload (proposed) | jsonb | valid JSON→jsonb | yes | TRANSFORM | MUST_MIGRATE: projection/import/mergeの入力 |
| `clinics.effective_json` | TEXT/JSON | clinic_master | view/projection | current clinic projection | jsonb | base+research+manualから再生成 | yes | DERIVE | consumerあり。blobのblind copyではなく再projection |
| `clinics.is_new` | INTEGER | clinic_master | clinics | is_new (proposed) | boolean | 0/1→boolean | no | TRANSFORM | MUST_MIGRATE: filter/job priority |
| `clinics.merged_into` | INTEGER | clinic_master | clinics | merged_into_clinic_id (proposed) | uuid | SQLite id→new UUIDv7 lookup | yes | TRANSFORM | MUST_MIGRATE: canonical dereference/merge audit |
| `clinics.merge_hold` | INTEGER | clinic_master | clinics | merge_hold (proposed) | boolean | 0/1→boolean | no | TRANSFORM | MUST_MIGRATE: 誤営業・誤調査防止 |

`clinic_name_kana`は対応するSQLite列が存在しないためNULL。`postal_code`は`clinics`の物理列ではなく、
`base_json`内に21件だけ存在する。

## 2. HP machine history mapping

`research_results`は814行の現在スナップショットであり、過去の全実行履歴ではない。1 source rowから
`hp_research` 1行を生成できるが、存在しない履歴を復元しない。

| SQLite column | SQLite type | Postgres schema | Postgres table | Postgres column | Postgres type | transform | nullable | migration action | notes |
|---|---|---|---|---|---|---|---|---|---|
| `research_results.clinic_id` | INTEGER | clinic_ops | hp_research | clinic_id | uuid | SQLite id→新UUIDv7 lookup | no | TRANSFORM | FK解決必須 |
| `result_json.hp_url` | JSON text | clinic_ops | hp_research | url | text | JSON extract; empty→NULL | yes | TRANSFORM | `clinics.hp_url`より詳細sourceを優先 |
| `result_json.research_status` | JSON text | clinic_ops | hp_research | fetch_status | text | JSON extract/語彙map | no | TRANSFORM | 実値の許可語彙をpromotion前に固定 |
| `result_json.hp_checked_at` | JSON text | clinic_ops | hp_research | fetched_at | timestamptz | timestamp parse | yes | TRANSFORM | 814件に存在 |
| `result_json.research_error` | JSON text | clinic_ops | hp_research | error_detail | text | empty→NULL | yes | TRANSFORM | crawl_errorsはfeaturesへ |
| `result_json.hp_rank` | JSON text | clinic_ops | hp_research | machine_rank | text | A/B/C/Dのみ; UNKNOWN/NO_HP→NULL | yes | TRANSFORM | target CHECKを遵守 |
| `result_json.hp_score` | JSON integer | clinic_ops | hp_research | machine_score | numeric | numeric cast | yes | TRANSFORM | 実キーあり |
| `result_json.hp_rank_version` | JSON text | clinic_ops | hp_research | model_version | text | empty→NULL | yes | TRANSFORM | 638/814件に存在 |
| `research_results.result_json` | TEXT/JSON | clinic_ops | hp_research | features | jsonb | valid JSONをjsonb化 | yes | TRANSFORM | 814/814 valid |
| `research_results.updated_at` | TEXT | clinic_ops | hp_research | created_at | timestamptz | timestamp parse | no | TRANSFORM | source snapshot timestamp |
| `hp_pages.page_json` | TEXT/JSON | clinic_ops | hp_research | content_ref | text | 外部保存先へ書いた場合のみ参照を生成 | yes | REVIEW | 本文をcontent_refへ直接COPYしない; 今回外部書込なし |
| `hp_pages.url` | TEXT | clinic_ops | hp_research | features | jsonb | page metadataとして関連付け | yes | REVIEW | 1医院複数page。格納形態未確定 |
| `clinics.hp_status` | TEXT | clinic_ops | hp_research | fetch_status | text | `research_results`欠落時のsummary候補 | no | REVIEW | append-only event時刻がないため自動行生成しない |
| `clinics.hp_rank` | TEXT | clinic_ops | hp_research | machine_rank | text | A/B/C/Dのみ | yes | REVIEW | summaryを履歴と誤認しない |
| `clinics.signal_count` | INTEGER | clinic_ops | hp_research | features | jsonb | named JSON key | yes | TRANSFORM | research rowに紐づく場合のみ |
| `clinics.hot_status` | TEXT | clinic_ops | current HP projection | hot_status (proposed) | text | research/manualから再計算 | yes | DERIVE | consumerあり。scoring version固定必須 |
| `clinics.treatments_json` | TEXT/JSON | clinic_ops | current HP projection | treatment_categories (proposed) | text[]/jsonb | JSON array decode | yes | TRANSFORM | MUST_MIGRATE: 治療カテゴリfilter。162,258/162,258 valid |
| `clinics.signals_json` | TEXT/JSON | clinic_ops | current HP projection | confirmed_signals (proposed) | text[]/jsonb | JSON array decode | yes | TRANSFORM | MUST_MIGRATE: 広告/signals filter。162,258/162,258 valid |
| `hp_pages.clinic_id` | INTEGER | clinic_ops | hp_research | clinic_id | uuid | SQLite id→new UUIDv7 lookup | no | REVIEW | pageとresearch snapshotの関連付け方式を確定後に使用 |
| `hp_pages.checked_at` | TEXT | clinic_ops | hp_research | fetched_at | timestamptz | timestamp parse | yes | REVIEW | page単位時刻をresearch実行時刻と同一視しない |
| `research_job_items.*` | mixed | runtime | research_job_items (future) | runtime state | mixed | legacy in-flight rowsはcutover前に停止/完了 | — | DO_NOT_MIGRATE | RUNTIME_ONLY: 新Postgres runtimeには同等queue必須 |
| `research_jobs.*` | mixed | runtime | research_jobs (future) | runtime state | mixed | legacy in-flight rowsはcutover前に停止/完了 | — | DO_NOT_MIGRATE | RUNTIME_ONLY: pause/resume UIに必要 |

## 3. Human feedback mapping

| SQLite column | SQLite type | Postgres schema | Postgres table | Postgres column | Postgres type | transform | nullable | migration action | notes |
|---|---|---|---|---|---|---|---|---|---|
| `manual_overrides.clinic_id` | INTEGER | clinic_ops | manual_override_events | clinic_id | uuid | SQLite id→new UUIDv7 lookup | no | TRANSFORM | generic override target確定。source tableは現在0 rows |
| `manual_overrides.field` | TEXT | clinic_ops | manual_override_events | field | text | allowed field語彙を検証 | no | COPY | rank以外のURL/status/treatment/signalsも保持 |
| `manual_overrides.value_json` | TEXT/JSON | clinic_ops | manual_override_events | value | jsonb | valid JSON→jsonb; legacy rowはSET | yes | TRANSFORM | CLEARは将来eventとしてvalue NULL |
| `manual_overrides.source` | TEXT | clinic_ops | manual_override_events | source / reviewer | text | sourceを保持; reviewer未分離なら同値seed | no | TRANSFORM | 実装後はreviewerを明示入力 |
| `manual_overrides.note` | TEXT | clinic_ops | manual_override_events | reason | text | empty→NULL | yes | TRANSFORM | audit reason |
| `manual_overrides.updated_at` | TEXT | clinic_ops | manual_override_events | reviewed_at / created_at | timestamptz | timestamp parse | no | TRANSFORM | deterministic current ordering |
| latest machine snapshot | derived | clinic_ops | hp_rank_feedback | machine_*_at_review / features_snapshot | mixed | review時点machine行から取得 | yes | DERIVE | legacy sourceに確定スナップショットなし |

現在0 rowsなので`hp_rank_feedback`へ自動INSERTするlegacy human historyはない。`clinics.hp_rank`を
manual rankと推測してはならない。

## 4. Maps history mapping

| SQLite column | SQLite type | Postgres schema | Postgres table | Postgres column | Postgres type | transform | nullable | migration action | notes |
|---|---|---|---|---|---|---|---|---|---|
| `google_maps_results.id` | INTEGER | — | — | — | — | importer内のsource row keyとしてのみ使用 | — | DO_NOT_MIGRATE | PostgreSQL row UUIDへ流用しない |
| `google_maps_results.clinic_id` | INTEGER | clinic_ops | maps_results | clinic_id | uuid | SQLite id→new UUIDv7 lookup | no | TRANSFORM | NULL source rowはREVIEW |
| — | — | clinic_ops | maps_results | id | uuid | DB row surrogate default | no | DERIVE | clinic identityではない |
| `google_maps_results.maps_match_status` | TEXT | clinic_ops | maps_results | maps_status | text | source語彙map | no | TRANSFORM | 空値はREVIEW |
| `google_maps_results.scraped_at` | TEXT | clinic_ops | maps_results | fetched_at | timestamptz | empty→NULL; timestamp parse | yes | TRANSFORM | 実列あり |
| `google_maps_results.created_at` | TEXT | clinic_ops | maps_results | created_at / updated_at | timestamptz | timestamp parse | no | TRANSFORM | immutable legacy rowでは同値使用候補 |
| `result_json.place_id` | absent | clinic_ops | maps_results | place_id | text | NULL | yes | DERIVE | source schema/JSONに存在しない |
| `result_json.latitude` | absent | clinic_ops | maps_results | latitude | numeric | NULL | yes | DERIVE | sourceに存在しない |
| `result_json.longitude` | absent | clinic_ops | maps_results | longitude | numeric | NULL | yes | DERIVE | sourceに存在しない |
| `result_json.rating` | absent | clinic_ops | maps_results | rating | numeric | NULL | yes | DERIVE | sourceに存在しない |
| `result_json.review_count` | absent | clinic_ops | maps_results | review_count | int | NULL | yes | DERIVE | sourceに存在しない |
| `google_maps_results.maps_profile_url` | TEXT | clinic_ops | maps_results | maps_profile_url (proposed) | text | empty→NULL | yes | TRANSFORM | SHOULD_MIGRATE: Maps UI/evidence |
| `google_maps_results.maps_website_url` | TEXT | clinic_ops | maps_results | maps_website_url (proposed) | text | empty→NULL | yes | TRANSFORM | SHOULD_MIGRATE: confirmed HP evidence |
| `google_maps_results.maps_match_method` | TEXT | clinic_ops | maps_results | maps_match_method (proposed) | text | empty→NULL | yes | TRANSFORM | SHOULD_MIGRATE: match audit |
| `google_maps_results.result_json` | TEXT/JSON | clinic_ops | maps_results | raw_result (proposed) | jsonb | valid JSON→jsonb | yes | TRANSFORM | SHOULD_MIGRATE: 営業時間等のraw evidence |
| `google_maps_results.batch_id` | TEXT | clinic_ops | maps_results | source_batch_id (proposed) | text | identity | yes | COPY | SHOULD_MIGRATE: import provenance |
| `google_maps_results.row_number` | INTEGER | clinic_ops | maps_results | source_row_number (proposed) | int | identity | yes | COPY | SHOULD_MIGRATE: source row追跡 |
| `clinics.maps_presence_status` | TEXT | clinic_ops | current Maps projection | maps_status | text | protected current snapshotとして移行 | no | TRANSFORM | MUST_MIGRATE: filter/job/UI。latest rawだけからderiveしない |
| `clinics.maps_checked_at` | TEXT | clinic_ops | current Maps projection | fetched_at | timestamptz | timestamp parse | yes | TRANSFORM | MUST_MIGRATE: current snapshot時点 |
| `clinics.maps_profile_url` | TEXT | clinic_ops | current Maps projection | maps_profile_url (proposed) | text | empty→NULL | yes | TRANSFORM | MUST_MIGRATE: detail UI |
| `clinics.maps_website_url` | TEXT | clinic_ops | current Maps projection | maps_website_url (proposed) | text | empty→NULL | yes | TRANSFORM | MUST_MIGRATE: filter/research/Comdesk export |
| `clinics.maps_match_method` | TEXT | clinic_ops | current Maps projection | maps_match_method (proposed) | text | empty→NULL | yes | TRANSFORM | current protected snapshotの根拠 |
| `clinics.exclude_reason` | TEXT | clinic_master | clinics | exclude_reason (proposed) | text | empty→NULL | yes | TRANSFORM | MUST_MIGRATE: Comdesk営業対象除外 |

## 5. Promotion gates

1. `medical_key=''`の16件はREVIEW。UUIDv7をproduction insertに使わない。
2. merged/merge-hold行は関係解決までREVIEW。
3. HP rankはA/B/C/Dだけをmachine/manual rank列へ入れる。`UNKNOWN`/`NO_HP`はNULLまたはstatus/features。
4. `manual_overrides`は0件なのでmanual historyを推測生成しない。
5. Mapsに存在しないplace/rating/coordinatesを生成しない。
6. `google_maps_results`履歴と`clinics`集約列を二重投入しない。
7. import apply前には別途dry-runを必須とする。今回はapplyしない。

## 6. Comdesk export contract

| SQLite column | SQLite type | Postgres schema | Postgres table | Postgres column | Postgres type | transform | nullable | migration action | notes |
|---|---|---|---|---|---|---|---|---|---|
| `templates.id` | TEXT | clinic_ops | comdesk_templates | template_id | text | identity | no | COPY | template hash identity |
| `templates.headers_json` | TEXT/JSON | clinic_ops | comdesk_templates | headers | jsonb | ordered array; 28要素検証 | no | TRANSFORM | 実データ1/1 valid |
| `templates.mapping_json` | TEXT/JSON | clinic_ops | comdesk_templates | field_mapping | jsonb | objectとしてcast | no | TRANSFORM | 実データ1/1 valid、10 mapping keys |
| `templates.created_at` | TEXT | clinic_ops | comdesk_templates | created_at | timestamptz | timestamp parse | no | TRANSFORM | audit timestamp |
| `comdesk_original_rows.id` | INTEGER | — | — | — | — | source row surrogateとしてのみ使用 | — | DO_NOT_MIGRATE | targetは新規row UUID |
| `comdesk_original_rows.clinic_id` | INTEGER | clinic_ops | comdesk_original_rows | clinic_id | uuid | SQLite id→new UUIDv7 lookup | yes | TRANSFORM | 21/21 linked、orphan 0 |
| `comdesk_original_rows.template_id` | TEXT | clinic_ops | comdesk_original_rows | template_id | text | identity | no | COPY | template FK |
| `comdesk_original_rows.row_json` | TEXT/JSON | clinic_ops | comdesk_original_rows | original_values | jsonb | ordered array; 28要素検証 | no | TRANSFORM | 元値は空欄も含め上書き保護 |
| `comdesk_original_rows.uuid` | TEXT | clinic_ops | comdesk_original_rows | legacy_uuid | uuid | canonical UUID cast | yes | TRANSFORM | source snapshot |
| `comdesk_original_rows.source_hash` | TEXT | clinic_ops | comdesk_original_rows | source_hash | text | identity | no | COPY | row provenance/unique key |
| `comdesk_original_rows.row_number` | INTEGER | clinic_ops | comdesk_original_rows | source_row_number | int | identity | no | COPY | `UNIQUE(source_hash,source_row_number)` |
| `comdesk_original_rows.created_at` | TEXT | clinic_ops | comdesk_original_rows | created_at | timestamptz | timestamp parse | no | TRANSFORM | import timestamp |

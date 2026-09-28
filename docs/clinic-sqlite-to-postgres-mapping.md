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
| `clinics.name_norm` | TEXT | — | — | — | — | — | — | DO_NOT_MIGRATE | target列なし。再生成可能な正規化値 |
| `clinics.name_prefix` | TEXT | — | — | — | — | — | — | DO_NOT_MIGRATE | target列なし |
| `clinics.phone` | TEXT | clinic_master | clinics | phone | text | `'' -> NULL` | yes | TRANSFORM | raw phoneを保持 |
| `clinics.phone_norm` | TEXT | — | — | — | — | — | — | DO_NOT_MIGRATE | target列なし。派生値 |
| `clinics.tel_match_key` | TEXT | — | — | — | — | — | — | DO_NOT_MIGRATE | target列なし。派生値 |
| `clinics.address` | TEXT | clinic_master | clinics | address | text | `'' -> NULL` | yes | TRANSFORM | raw addressを保持 |
| `clinics.address_norm` | TEXT | — | — | — | — | — | — | DO_NOT_MIGRATE | target列なし。派生値 |
| `clinics.prefecture` | TEXT | clinic_master | clinics | prefecture | text | `'' -> NULL`; 表記検証 | yes | TRANSFORM | JISコード化は未決定 |
| `base_json.postal_code` | JSON text | clinic_master | clinics | postal_code | text | JSON extract; `'' -> NULL` | yes | TRANSFORM | 実在21件のみ |
| `clinics.hp_url` | TEXT | clinic_master | clinics | website | text | VERIFIEDかつ非空を候補化 | yes | REVIEW | Maps websiteとの優先規則をpromotion前に確定 |
| `clinics.active` | INTEGER | clinic_master | clinics | status | text | booleanと`effective_json.status`から状態語彙へ変換 | yes | DERIVE | status語彙未確定のため要レビュー |
| `clinics.first_seen_at` | TEXT | clinic_master | clinics | created_at | timestamptz | timestamp parse | no | REVIEW | first_seenとDB登録日時の意味差を承認後のみ使用 |
| `clinics.last_seen_at` | TEXT | clinic_master | clinics | updated_at | timestamptz | timestamp parse | no | REVIEW | last_seenとrow更新日時の意味差あり |
| constant | — | clinic_master | clinics | source | text | `'legacy_sqlite'` | no | DERIVE | target defaultと一致 |
| migration batch | — | clinic_master | clinics | imported_batch_id | uuid | current batch ID | yes | DERIVE | rollback attribution |
| `clinics.medical_type` | TEXT | — | — | — | — | — | — | DO_NOT_MIGRATE | current target列なし |
| `clinics.designation_date` | TEXT | — | — | — | — | — | — | DO_NOT_MIGRATE | current target列なし |
| `clinics.recent_until` | TEXT | — | — | — | — | — | — | DO_NOT_MIGRATE | current target列なし |
| `clinics.registration_reason` | TEXT | — | — | — | — | — | — | DO_NOT_MIGRATE | current target列なし |
| `clinics.owner_equal` | INTEGER | — | — | — | — | — | — | DO_NOT_MIGRATE | current target列なし |
| `clinics.age_probability` | REAL | — | — | — | — | — | — | DO_NOT_MIGRATE | current target列なし |
| `clinics.departments_json` | TEXT/JSON | — | — | — | — | — | — | DO_NOT_MIGRATE | current target列なし; valid JSON |
| `clinics.source_as_of_date` | TEXT | — | — | — | — | — | — | DO_NOT_MIGRATE | source provenance; current target列なし |
| `clinics.base_json` | TEXT/JSON | — | — | — | — | 必要な正本列のみ個別extract | — | DO_NOT_MIGRATE | blob全体は移さない |
| `clinics.effective_json` | TEXT/JSON | — | — | — | — | HP/Mapsの実キーのみ個別extract | — | DO_NOT_MIGRATE | blob全体は移さない |
| `clinics.is_new` | INTEGER | — | — | — | — | — | — | DO_NOT_MIGRATE | current target列なし |
| `clinics.merged_into` | INTEGER | — | — | — | — | merge関係をpromotion前に解決 | — | REVIEW | merged rowを自動INSERTしない |
| `clinics.merge_hold` | INTEGER | — | — | — | — | hold対象をpromotionから除外 | — | REVIEW | migration controlとして利用 |

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
| `clinics.hot_status` | TEXT | clinic_ops | hp_research | features | jsonb | named JSON key | yes | TRANSFORM | research rowに紐づく場合のみ |
| `clinics.treatments_json` | TEXT/JSON | clinic_ops | hp_research | features | jsonb | named JSON key | yes | TRANSFORM | 162,258/162,258 valid |
| `clinics.signals_json` | TEXT/JSON | clinic_ops | hp_research | features | jsonb | named JSON key | yes | TRANSFORM | 162,258/162,258 valid |
| `hp_pages.clinic_id` | INTEGER | clinic_ops | hp_research | clinic_id | uuid | SQLite id→new UUIDv7 lookup | no | REVIEW | pageとresearch snapshotの関連付け方式を確定後に使用 |
| `hp_pages.checked_at` | TEXT | clinic_ops | hp_research | fetched_at | timestamptz | timestamp parse | yes | REVIEW | page単位時刻をresearch実行時刻と同一視しない |
| `research_job_items.*` | mixed | — | — | — | — | — | — | DO_NOT_MIGRATE | queue/lease runtime状態; target表なし |
| `research_jobs.*` | mixed | — | — | — | — | — | — | DO_NOT_MIGRATE | job control; target表なし |

## 3. Human feedback mapping

| SQLite column | SQLite type | Postgres schema | Postgres table | Postgres column | Postgres type | transform | nullable | migration action | notes |
|---|---|---|---|---|---|---|---|---|---|
| `manual_overrides.clinic_id` | INTEGER | clinic_ops | hp_rank_feedback | clinic_id | uuid | SQLite id→new UUIDv7 lookup | no | REVIEW | source tableは現在0 rows |
| `manual_overrides.field` | TEXT | clinic_ops | hp_rank_feedback | manual_rank | text | `field='hp_rank'`だけを候補化 | no | REVIEW | 実データ0件で語彙未検証 |
| `manual_overrides.value_json` when `field='hp_rank'` | TEXT/JSON | clinic_ops | hp_rank_feedback | manual_rank | text | A/B/C/Dのみextract | no | REVIEW | 実データ0件。field/value形式を実例で検証不能 |
| `manual_overrides.source` | TEXT | clinic_ops | hp_rank_feedback | reviewer | text | reviewer identity mapping | no | REVIEW | sourceと人間identityが同義か未確認 |
| `manual_overrides.note` | TEXT | clinic_ops | hp_rank_feedback | reason | text | empty→NULL | yes | REVIEW | 実データ0件 |
| `manual_overrides.updated_at` | TEXT | clinic_ops | hp_rank_feedback | reviewed_at / created_at | timestamptz | timestamp parse | no | REVIEW | 実データ0件 |
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
| `google_maps_results.maps_profile_url` | TEXT | — | — | — | — | — | — | DO_NOT_MIGRATE | current maps target列なし |
| `google_maps_results.maps_website_url` | TEXT | clinic_master | clinics | website | text | HP URLとの優先判定 | yes | REVIEW | target maps列なし。自動上書き禁止 |
| `google_maps_results.maps_match_method` | TEXT | — | — | — | — | — | — | DO_NOT_MIGRATE | current target列なし |
| `google_maps_results.result_json` | TEXT/JSON | — | — | — | — | 必要なら将来専用features列を設計 | — | DO_NOT_MIGRATE | 15,339/15,339 validだがcurrent targetにjsonb列なし |
| `google_maps_results.batch_id` | TEXT | — | — | — | — | — | — | DO_NOT_MIGRATE | maps targetにlegacy batch列なし |
| `google_maps_results.row_number` | INTEGER | — | — | — | — | — | — | DO_NOT_MIGRATE | import provenance; target列なし |
| `clinics.maps_presence_status` | TEXT | clinic_ops | maps_results | maps_status | text | summary fallback候補 | no | REVIEW | 履歴15,339行を優先; summaryの二重投入禁止 |
| `clinics.maps_checked_at` | TEXT | clinic_ops | maps_results | fetched_at | timestamptz | timestamp parse | yes | REVIEW | summary行を作る場合のみ |
| `clinics.maps_profile_url` | TEXT | — | — | — | — | — | — | DO_NOT_MIGRATE | current target列なし |
| `clinics.maps_website_url` | TEXT | clinic_master | clinics | website | text | HP URLとの優先判定 | yes | REVIEW | current masterにwebsiteは1列のみ |
| `clinics.maps_match_method` | TEXT | — | — | — | — | — | — | DO_NOT_MIGRATE | current target列なし |
| `clinics.exclude_reason` | TEXT | — | — | — | — | — | — | DO_NOT_MIGRATE | current target列なし; 削除せずsource snapshotで保持 |

## 5. Promotion gates

1. `medical_key=''`の16件はREVIEW。UUIDv7をproduction insertに使わない。
2. merged/merge-hold行は関係解決までREVIEW。
3. HP rankはA/B/C/Dだけをmachine/manual rank列へ入れる。`UNKNOWN`/`NO_HP`はNULLまたはstatus/features。
4. `manual_overrides`は0件なのでmanual historyを推測生成しない。
5. Mapsに存在しないplace/rating/coordinatesを生成しない。
6. `google_maps_results`履歴と`clinics`集約列を二重投入しない。
7. import apply前には別途dry-runを必須とする。今回はapplyしない。

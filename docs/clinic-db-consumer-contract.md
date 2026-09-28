# Clinic DB Consumer Contract

> 調査対象: `/Users/maekawahiroyuki/Desktop/clinic-list-filter-complete` (read-only)  
> 調査日: 2026-09-28  
> 目的: SQLiteからPostgreSQLへ切替後も、現在のClinic Lead機能を欠落させないためのconsumer契約。  
> この文書は設計のみ。Clinic Lead repo、Production SQLite、Supabase、CRM public/Prismaは変更していない。

## 1. Runtime and dependency decision

実アプリの`.venv/bin/python`はPython 3.12.14、実行ファイルは
`/Users/maekawahiroyuki/Desktop/clinic-list-filter-complete/.venv/bin/python`。
stdlib `uuid.uuid7()`は存在せず、`uuid6`も未導入。依存管理は`requirements.txt`と固定版の
`requirements-lock.txt`で、`pyproject.toml`はpytest設定のみである。

したがって現runtimeでUUIDv7を実装する選択は **`uuid6` dependency**。実装工程で両requirementsへ
明示追加し、lockを更新する必要がある。今回package install・依存変更は実施していない。

## 2. Classification rules

- **MUST_MIGRATE**: Supabase切替後に現在機能を維持するため必須。
- **SHOULD_MIGRATE**: 現在の履歴・監査・再現性または将来運用のため保持推奨。
- **DERIVABLE**: 保持する正本から同じ規則で安全に再生成可能。
- **RUNTIME_ONLY**: queue/lease等の一時状態。legacy値の移行は不要だが、新runtimeには同等機構が必要。
- **LEGACY_ONLY**: 現runtimeのread/query/UI/exportに依存せず、履歴保持価値もない。
- **REVIEW**: consumerはあるが、正本・意味・移行先をコードだけでは確定できない。

## 3. `clinics` field consumers

| SQLite field | current consumer | usage location | business purpose | classification | target proposal | reason |
|---|---|---|---|---|---|---|
| `medical_type` | filter, Maps/HP job, source import | `src/master/filters.py:49`, `app_v2.py:368`, `src/master/store.py:331` | 医科/歯科filterと調査母集団 | MUST_MIGRATE | `clinic_master.clinics.medical_type text` | 現targetに欠落するとfilter/job対象が変わる |
| `designation_date` | filter, UI, export | `filters.py:43,63`, `app_v2.py:132`, `export_*` | 指定日・10年以内・新規開業候補 | MUST_MIGRATE | `designation_date date` | 業務filterの正本 |
| `recent_until` | filter | `filters.py:43`; generated at `store.py:214-230` | 指定日から10年以内 | DERIVABLE | VIEW/generated query from `designation_date` | 同じ10年加算規則で再生成可能 |
| `registration_reason` | filter | `filters.py:63`; projected at `store.py:230` | 新規指定判定 | MUST_MIGRATE | `registration_reason text` | 新規開業候補filterに必要 |
| `owner_equal` | filter | `filters.py:60`; projected at `store.py:207-230` | 開設者＝管理者filter | MUST_MIGRATE | `owner_equal boolean` | owner/manager原文を移さない限り安全に再生成不能 |
| `age_probability` | filter, detail UI, metrics | `filters.py:44`, `app_v2.py:127,156`, `store.py:426` | 59歳以下確率 | MUST_MIGRATE | `clinic_master.clinics.age_probability numeric` | 営業filterに直接使用 |
| `departments_json` | filter | `filters.py:52-54`; projected at `store.py:234` | 診療科filter | MUST_MIGRATE | `departments text[]`または正規化child table | 現機能のmulti-select条件 |
| `treatments_json` | filter | `filters.py:52-54`; projected at `store.py:234` | 治療カテゴリfilter | MUST_MIGRATE | `clinic_ops.hp_research.features` + current projection | HP調査由来の営業filter |
| `signals_json` | filter | `filters.py:5,58`; projected at `store.py:235` | 広告・集客施策filter/件数 | MUST_MIGRATE | current signal projectionまたは正規化child table | signal_countだけでは選択内容を復元不能 |
| `signal_count` | filter, sort, metrics | `filters.py:55`, `store.py:408,426` | 集客投資シグナル数・優先順 | DERIVABLE | signals/current HP featuresから計算 | confirmed signal集合から再生成可能 |
| `hot_status` | filter | `filters.py:48-50`; projected at `store.py:232` | アツさfilter | DERIVABLE | current HP featuresから計算 | scoring結果から再生成可能だがversion固定が必要 |
| `source_as_of_date` | source import, merge | `store.py:249,339-345`, `reintegration.py:44,76` | 古い公式データの上書き防止 | MUST_MIGRATE | `clinic_master.clinics.source_as_of_date date` | 増分importの安全条件 |
| `active` | default filter, jobs, metrics | `filters.py:39`, `app_v2.py:360`, `store.py:425` | 現存医院だけを営業・調査対象化 | MUST_MIGRATE | `active boolean` | current `status text`だけでは語彙変換が未定 |
| `is_new` | filter, job order | `filters.py:61`, `jobs.py:34`, `app_v2.py:380` | 前回更新から追加・優先調査 | MUST_MIGRATE | `is_new boolean` | import cycle stateとして現役 |
| `merged_into` | every query, dereference, merge | `filters.py:74`, `store.py:185`, `reintegration.py:75` | canonical clinicへの統合 | MUST_MIGRATE | `merged_into_clinic_id uuid` self-FK | 行を捨てるだけではmerge監査と参照解決を失う |
| `merge_hold` | every query/job, review | `filters.py:74`, `app_v2.py:359`, `reintegration.py:101-177` | 重複確認中レコードの除外 | MUST_MIGRATE | `merge_hold boolean` | 誤営業・誤調査防止 |
| `maps_presence_status` | filter, UI, metrics, jobs | `filters.py:65-68`, `app_v2.py:133,361`, `store.py:432-434` | Maps掲載状態とHP取得母集団 | MUST_MIGRATE | current Maps projection/view | 履歴だけでなく保護済みcurrent状態が必要 |
| `maps_profile_url` | detail UI | `app_v2.py:144-145` | Mapsページを開く | MUST_MIGRATE | `clinic_ops.maps_results.maps_profile_url text` | 再取得なしでは復元不能 |
| `maps_website_url` | filter, UI, HP research, Comdesk export | `filters.py:68`, `app_v2.py:146`, `researcher.py:80`, `fixed_export.py:60` | confirmed HP URLと再調査入力 | MUST_MIGRATE | `clinic_ops.maps_results.maps_website_url text` + current view | 中核consumerが複数 |
| `maps_match_method` | import/audit, preserved current state | `google_maps.py:117,142-166`, `store.py:237` | match根拠 | SHOULD_MIGRATE | `clinic_ops.maps_results.maps_match_method text` | 誤紐付け調査に必要 |
| `maps_checked_at` | current Maps state | `google_maps.py:142`, `store.py:238` | current値の観測時刻 | MUST_MIGRATE | `maps_results.fetched_at` | current selectionと鮮度判定 |
| `exclude_reason` | Comdesk export, Maps import | `fixed_export.py:98`, `google_maps.py:17,147` | 病院/センターの営業除外 | MUST_MIGRATE | `clinic_master.clinics.exclude_reason text` | exportから除外する直接条件 |
| `base_json` | projection, import, merge, Maps update | `store.py:201,246`, `google_maps.py:120`, `reintegration.py:43` | source正本と再projection | MUST_MIGRATE | `source_payload jsonb`または正規化済み全正本列 | 現アプリはこれを再計算の入力にする |
| `effective_json` | UI/query object, production-company filter | `store.py:188`, `filters.py:57` | 現在値projection | DERIVABLE | current VIEW/materialized projection | base+research+manualから生成可能 |
| `first_seen_at` / `last_seen_at` | management export/get | `store.py:188` | 初回/最終観測 | SHOULD_MIGRATE | `first_seen_at`, `last_seen_at` | DB row作成/更新日時とは意味が異なる |
| `uuid` | search, ordering, Comdesk identity/export | `filters.py:62,70`, `jobs.py:34`, `fixed_export.py:14,58` | legacy identity | MUST_MIGRATE | `legacy_uuid uuid UNIQUE NULL` | 非空21件valid/unique |
| `phone_norm`, `name_norm`, `address_norm`, `name_prefix`, `tel_match_key` | matching/search | `filters.py:70`, `google_maps.py:69-88` | fuzzy/exact matching | DERIVABLE | application normalizationまたはgenerated/search columns | raw name/phone/addressから再生成可能。algorithm version固定必須 |
| `hp_url`と`maps_website_url`のmaster `website`優先値 | UI/export/research | `fixed_export.py:60`, `researcher.py:80` | canonical website選択 | DERIVABLE | source別URLを保持し、consumer別VIEWで優先解決 | 解決済み。単一列へ不可逆統合しない。詳細はreview-resolution参照 |

都道府県filterは既存`prefecture`、HP Rank/statusは`hp_rank`/`hp_status`、医科/歯科は`medical_type`に
直接依存する。既存mappingでmaster/HP対象としていた前者に加え、`medical_type`をtargetへ追加する必要がある。

## 4. Related table consumers

| SQLite field/table | current consumer | usage location | business purpose | classification | target proposal | reason |
|---|---|---|---|---|---|---|
| `research_results.result_json` | projection, UI/filter/export, rerun | `store.py:203,358,538`, `jobs.py:179`, `export_*` | HP rank/status/score、年齢、治療、signalsのmachine result | MUST_MIGRATE | `hp_research.features`とtyped columns | 現機能のmachine正本 |
| `research_results.updated_at` | merge/latest snapshot | `reintegration.py:49-62` | machine result時点 | MUST_MIGRATE | `hp_research.created_at/fetched_at` | 最新判定・履歴順 |
| `hp_pages.url/page_json/checked_at` | save, merge; raw page evidence | `store.py:363-365`, `reintegration.py:64` | research evidence再確認 | SHOULD_MIGRATE | object storage + `content_ref`,または`hp_research_pages` | current codeは保持・mergeする。安易な破棄不可 |
| `manual_overrides.field/value_json` | projection and override UI | `store.py:205,394-398` | manual correction | MUST_MIGRATE | typed feedback + generic override support | hp_rank以外にURL/status/treatment/signalsも許可 |
| `manual_overrides.source/note/updated_at` | audit/history | `store.py:398`, `reintegration.py:22-23` | reviewer、理由、時点 | MUST_MIGRATE | feedback reviewer/reason/reviewed_at | 人手判断の監査契約 |
| `google_maps_results.maps_match_status` | append audit | `google_maps.py:105-118` | 各取得結果 | SHOULD_MIGRATE | `maps_results.maps_status` | current snapshotとは別に履歴保持 |
| `google_maps_results.maps_profile_url/maps_website_url` | append audit/current reconstruction | `google_maps.py:117,125-166` | URL evidenceと確定HP保護 | SHOULD_MIGRATE | maps targetへ同名列追加 | 再取得なしでは復元不能 |
| `google_maps_results.maps_match_method` | append audit | `google_maps.py:117` | match根拠 | SHOULD_MIGRATE | maps targetへ追加 | 誤match調査 |
| `google_maps_results.result_json` | immutable raw evidence | `google_maps.py:116-118,125` | 全Maps結果と営業時間 | SHOULD_MIGRATE | `raw_result jsonb` | typed targetにない値を保持 |
| `google_maps_results.batch_id/row_number` | import provenance/idempotency | `google_maps.py:99-118` | 元batchと行追跡 | SHOULD_MIGRATE | `source_batch_id text`, `source_row_number int` | 再現・監査に必要 |
| `google_maps_results.scraped_at/created_at` | observation/audit time | `google_maps.py:117` | 取得時点/取込時点 | MUST_MIGRATE | `fetched_at`, `created_at` | ordering/current解決 |
| `research_jobs.*` | job UI, pause/resume/budget | `jobs.py:29-99`, `app_v2.py:503-526,724-753` | durable research job | RUNTIME_ONLY | PostgreSQL runtime job table | legacy job移行は不要。cutover時に停止/完了を確認 |
| `research_job_items.job_id/clinic_id/state/result/note` | worker and progress UI | `jobs.py:42-203` | queue、result、retry | RUNTIME_ONLY | PostgreSQL job item table | 新runtimeには必須、legacy in-flightは移さない |
| `research_job_items.lease_until` | schema/merge only | `store.py:92-95`, `reintegration.py:65-74` | 旧lease予約 | LEGACY_ONLY | omit unless worker reintroduces leases | current workerのclaimでreadされていない |
| Comdesk `templates` / `comdesk_original_rows` | fixed export | `fixed_export.py:87-119` | 元28列を原文保持して再出力 | MUST_MIGRATE | `clinic_ops.comdesk_templates` / `comdesk_original_rows` | 解決済み。元値優先と空URL時だけMaps補完を維持 |

## 5. Functional contract

| feature | required source contract |
|---|---|
| 都道府県filter | `prefecture` |
| 医科/歯科 | `medical_type` |
| HP Rank / status | latest machine result + manual overrides + current projection |
| 治療カテゴリ | `treatment_categories` (research/manual) |
| 開業・指定日 | `designation_date`, `registration_reason`; `recent_until`はderive |
| 院長/年齢 | base manager/owner data、research age evidence、`age_probability` current projection |
| 広告・signals | named confirmed signals。countだけでは不足 |
| Maps status/URL/match | current protected snapshot + append-only raw history |
| 除外理由 | `exclude_reason` |
| merge処理 | `merged_into`, `merge_hold`, source payload、manual/research/pagesの引継ぎ |
| Comdesk export | legacy UUID、基本属性、confirmed Maps/HP URL、営業時間、exclude reason、original rows/templates |
| 再調査 | current clinic filters、research result、Maps confirmed website、job runtime tables |
| pause/resume | research job/job item runtime state |

Comdesk exportを完全維持するため、`clinic_ops.comdesk_original_rows`と`comdesk_templates`をSchema v1
target候補に含める。元行を空欄も含めて優先し、元URLが空欄の場合だけprotected Maps URLを補完する。
詳細は`docs/clinic-db-review-resolution.md`を参照。

## 6. Constraint candidates

### `medical_key`

実測はNULL 0、empty 16、非空重複0。PostgreSQL targetは次をschema-finalize候補とする。

```sql
medical_key text NOT NULL,
CONSTRAINT clinics_medical_key_key UNIQUE (medical_key),
CONSTRAINT clinics_medical_key_nonblank CHECK (btrim(medical_key) <> '')
```

空文字16件は制約を緩めずREVIEWへ送り、有効key確定までinsertしない。空白だけの値も同じく拒否する。

### `legacy_uuid`

空文字をNULLへ変換し、非空21件はvalid・重複0。PostgreSQL UNIQUEは複数NULLを許容するため、
`legacy_uuid uuid NULL UNIQUE`をschema-finalize候補として有効化して問題ない。promotion dry-runで
cast成功・重複0を再確認してから適用する。

## 7. Target gaps

### `clinic_master.clinics`

追加必須候補: `medical_type`, `designation_date`, `registration_reason`, `owner_equal`, `age_probability`,
`active`, `is_new`, `source_as_of_date`, `merged_into_clinic_id`, `merge_hold`, `exclude_reason`,
診療科projection、source payload、first/last seen。`recent_until`と正規化検索keyはderive候補。

### `clinic_ops.hp_research` / feedback

HP machine typed columnsは概ね足りるが、named treatment/signals/current projection契約、page evidenceの
保存先、hp_rank以外のgeneric manual overrideを設計する必要がある。`hp_rank_feedback`だけでは
manual URL/status/treatment/signalsを保持できないため、append-only `manual_override_events`とcurrent VIEWを
追加する。詳細はreview-resolution参照。

### `clinic_ops.maps_results`

追加推奨: `maps_profile_url`, `maps_website_url`, `maps_match_method`, `raw_result jsonb`,
`source_batch_id`, `source_row_number`。また「最新raw」ではなく、confirmed websiteを低品質な後続結果から
保護する現ロジックを維持したcurrent Maps VIEW/projectionが必要。legacy sourceに存在しない
`place_id/latitude/longitude/rating/review_count`はNULLのままにする。

## 7.1 Review resolution

Website priority、Comdesk target、Maps protected current、generic manual override、runtime jobsの主要REVIEWは
`docs/clinic-db-review-resolution.md`で解消済み。残る作業はSchema v1 DDLでの具体化であり、ownership判断は0件。

## 8. Safety result

- Clinic Production SQLite DDL/INSERT/UPDATE/DELETE: 0/0/0/0
- Supabase DDL/INSERT/UPDATE/DELETE: 0/0/0/0
- Clinic Lead repo code modification: 0
- CRM public/Prisma modification: 0

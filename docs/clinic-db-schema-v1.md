# Clinic DB Schema v1(確定版)

> 作成日: 2026-09-28
> ステータス: **設計確定。Supabaseへは未適用。162,258件のimportも未実行。**
> 本文書は以下を統合した最終参照(single source of truth)である:
> `docs/clinic-db-readonly-audit.md`(SQLite実測)、`docs/clinic-sqlite-to-postgres-mapping.md`(列単位mapping)、
> `docs/clinic-db-consumer-contract.md`(現機能の契約)、`docs/clinic-db-review-resolution.md`(REVIEW解消)、
> `docs/clinic-db-architecture.md` / `docs/clinic-db-migration-plan.md` / `docs/clinic-uuid-strategy.md`(先行設計)。
>
> Clinic Lead repo (`/Users/maekawahiroyuki/Desktop/clinic-list-filter-complete`)・Production SQLite
> (`~/CrestixData/clinic-lead/clinics.sqlite3`) は読み取り専用でのみ参照済み。DDL/DML/importは
> 一切実行していない。CRM `public` schema / Prisma migrationsへの変更も0件。

---

## 1. Schema ownership

| schema | 所有 | migration手段 |
|---|---|---|
| `public` | CRM repo / Prisma | `prisma/migrations/`(`docs/clinic-db-architecture.md` STEP1) |
| `clinic_master` | Clinic Master SSOT | Clinic専用SQL migration(本文書4節) |
| `clinic_ops` | HP / Maps / manual correction / jobs / Comdesk / import audit | 同上 |

CRM Prismaの`schema.prisma`は`multiSchema`を使わず`public`単一schemaしか認識しないため、
`clinic_master`/`clinic_ops`は`prisma migrate deploy`/`db push`の対象に構造的に入らない
(`docs/clinic-db-architecture.md` STEP1参照、変更なし)。

---

## 2. Table catalog

### 2.1 master tables(`clinic_master`)

| table | 役割 | 備考 |
|---|---|---|
| `clinics` | 医院Master SSOT | Schema v1で列を大幅拡張(2.4節)。DDL: `001_create_clinic_master.sql` |

### 2.2 ops tables(`clinic_ops`)

| table | append-only? | 役割 | DDL |
|---|---|---|---|
| `hp_research` | Yes | machine側HP調査・スコア履歴 | `002_create_clinic_ops.sql` |
| `hp_rank_feedback` | Yes | 人間によるHP rank(A/B/C/D)レビュー履歴 | `002_create_clinic_ops.sql` |
| `manual_override_events` | Yes | HP rank以外のfield(URL/status/治療/signals等)の人手訂正履歴 | `005_create_clinic_ops_extended.sql` |
| `maps_results` | Yes | Maps調査raw履歴 | `002_create_clinic_ops.sql`(Schema v1で列拡張) |
| `comdesk_templates` | No(参照専用) | Comdesk export用template(headers/mapping) | `005_create_clinic_ops_extended.sql` |
| `comdesk_original_rows` | No(元行保護のため上書きしない運用) | Comdesk元28列の原文保持 | `005_create_clinic_ops_extended.sql` |
| `research_jobs` | No(runtime state) | HP/Maps調査jobのpause/resume/budget管理 | `005_create_clinic_ops_extended.sql` |
| `research_job_items` | No(runtime state) | job内の医院単位進捗 | `005_create_clinic_ops_extended.sql` |
| `import_logs` | No(runtime state) | 162,258件移行等のbatch監査 | `002_create_clinic_ops.sql` |
| `import_log_items` | Yes(rollbackでclinic_idのみNULL化) | batch内の行単位監査(SKIP/INSERT/REVIEW) | `002_create_clinic_ops.sql` |
| `_clinic_schema_migrations` | — | Clinic側migration追跡(`_prisma_migrations`とは別) | `002_create_clinic_ops.sql` |

### 2.3 runtime tables

`research_jobs` / `research_job_items` が該当(2.2節に記載)。legacy SQLiteのin-flight job/job item行は
移行しない。cutover gate(3.6節)を満たしてから新runtimeを空の状態で開始する。

### 2.4 `clinic_master.clinics` 全列(Schema v1確定)

| column | type | 分類 | 由来/根拠 |
|---|---|---|---|
| `clinic_id` | uuid PK | — | UUIDv7、Python生成、DB defaultなし(`docs/clinic-uuid-strategy.md`) |
| `medical_key` | text NOT NULL UNIQUE | — | dedup正本。CHECK非空 |
| `legacy_uuid` | uuid UNIQUE | MUST_MIGRATE | SQLite `uuid`。非空21/valid21/重複0実測済み |
| `clinic_name` | text NOT NULL | MUST_MIGRATE | |
| `clinic_name_kana` | text | — | SQLite側に対応列なし(常にNULL、将来予約) |
| `medical_type` | text | MUST_MIGRATE | 医科/歯科filter |
| `prefecture` | text | MUST_MIGRATE | |
| `postal_code` | text | REVIEW | `base_json`内、実在21件のみ |
| `address` | text | MUST_MIGRATE | |
| `phone` | text | MUST_MIGRATE | |
| `designation_date` | date | MUST_MIGRATE | 指定日/新規開業filter |
| `recent_until` | date GENERATED | DERIVABLE | `designation_date + 10年`の生成カラム |
| `registration_reason` | text | MUST_MIGRATE | |
| `owner_equal` | boolean | MUST_MIGRATE | |
| `age_probability` | numeric | MUST_MIGRATE | |
| `departments` | text[] | MUST_MIGRATE | 診療科 |
| `active` | boolean NOT NULL DEFAULT true | MUST_MIGRATE | 現存医院filter |
| `is_new` | boolean NOT NULL DEFAULT false | MUST_MIGRATE | |
| `source_as_of_date` | date | MUST_MIGRATE | 増分import安全条件 |
| `merge_hold` | boolean NOT NULL DEFAULT false | MUST_MIGRATE | |
| `merged_into_clinic_id` | uuid, self FK RESTRICT | MUST_MIGRATE | canonical医院への統合。CASCADE禁止 |
| `exclude_reason` | text | MUST_MIGRATE | Comdesk営業除外 |
| `source_payload` | jsonb | MUST_MIGRATE | SQLite `base_json` |
| `first_seen_at` | timestamptz | SHOULD_MIGRATE | |
| `last_seen_at` | timestamptz | SHOULD_MIGRATE | |
| `name_norm` / `name_prefix` / `phone_norm` / `address_norm` / `tel_match_key` | text | DERIVABLE | アプリ側normalizerが生成。**DBは値の生成ロジックを持たない**(matching algorithm自体はSchema v1の対象外) |
| `search_projection_version` | text | — | 上記normalizerのalgorithm versionタグ。再現性確保のため必須 |
| `source` | text NOT NULL DEFAULT 'legacy_sqlite' | — | |
| `imported_batch_id` | uuid | — | rollback追跡 |
| `created_at` / `updated_at` | timestamptz | — | |

**明示的に置かない列**: `website`(理由: 1.3節/review-resolution 1.3節)、汎用`status`
(理由: `active`/`exclude_reason`/`merge_hold`で意味が分かれるため)。

---

## 3. Contract coverage

### 3.1 Clinic filters

`medical_type`, `designation_date`, `registration_reason`, `owner_equal`, `age_probability`,
`departments`, `active`, `is_new`, `merged_into_clinic_id`, `merge_hold`, `exclude_reason`,
`prefecture` を`clinic_master.clinics`へ反映済み。`recent_until`は生成カラムでderive。
`hot_status`のみ未実装(3.7節「Remaining unknowns」参照)。

### 3.2 HP

- `hp_research`(machine, append-only) + `hp_rank_feedback`(human rank, append-only) +
  `manual_override_events`(rank以外のHP関連field, append-only)。
- `current_hp_rank` VIEW(`004_current_hp_rank_view.sql`): 最新manual rank、なければ最新machine rank。
  同VIEWで`treatment_categories`/`confirmed_signals`もmachine featuresから投影。
- `current_hp_website` VIEW(`006_create_current_views.sql`): manual `hp_url` SET優先、なければ
  最新verified machine URL。
- machine再計算は`hp_research`へのINSERTのみで完結し、`hp_rank_feedback`/`manual_override_events`の
  過去行には一切触れないため、人間の訂正が構造的に消えない。

### 3.3 Maps

- `maps_results`(append-only raw history)に`maps_profile_url`/`maps_website_url`/`maps_match_method`/
  `raw_result`/`source_batch_id`/`source_row_number`を追加。
- `maps_current` VIEW: confirmed website eventがあれば最新confirmed、なければ全eventの最新。
  confirmed採用後の後続NOT_FOUND/AMBIGUOUS/ERROR/空URLでcurrentを格下げしない
  (`docs/clinic-db-review-resolution.md` 3.2節のロジックをそのままVIEW化)。

### 3.4 Manual

`manual_override_events`(append-only, SET/CLEAR) + `manual_overrides_current` VIEW
(`clinic_id, field`ごとの最新イベント解決)。許可fieldはCHECK制約で列挙
(`hp_url`, `hp_status`, `hp_rank`, `epark_url`, `epark_contract`, `google_ads_status`,
`treatment_categories`, `marketing_signals`)。

### 3.5 Comdesk

`comdesk_templates`(1 row実測) + `comdesk_original_rows`(21 rows実測、28列JSON配列、
`UNIQUE(source_hash, source_row_number)`)。元28列を空欄も含め原文保持し、元URL空欄時のみ
`maps_current`で補完する現行`fixed_row()`規則をSchema v1でも維持する設計。

### 3.6 Jobs

`research_jobs` + `research_job_items`(runtime state、legacy in-flight行は移行しない)。
Cutover gate:

- `research_jobs.status = 'RUNNING'` の件数 = 0
- `research_job_items.state IN ('PENDING','RUNNING')` の件数 = 0
- app workerが停止し、research lockが解放されていること
- 完了結果が`research_results`(legacy)へ反映済みであることを照合済み

これらを全て満たしてから、新runtimeを空の状態で開始する。

### 3.7 Import audit

`import_logs`(batch集計) + `import_log_items`(行単位監査、SKIP/INSERT/REVIEW)。
`clinic_id`の値ルール: `insert`→新規clinic_id、`skip`→既存clinic_id、`review`→NULL、
rollback済み`insert`行→`ON DELETE SET NULL`で事後NULL化(`docs/clinic-db-architecture.md` 3.5節)。

---

## 4. Migration ownership

| schema | 責任 | ツール |
|---|---|---|
| `public` | CRM repo | Prisma |
| `clinic_master` / `clinic_ops` | Clinic Lead側 | 専用SQL migration(素のファイル + `clinic_ops._clinic_schema_migrations`によるトラッキング) |

CRM Prismaの`migrate deploy`/`db push`は`clinic_master`/`clinic_ops`の存在を認識しないため構造的に
触れない(`docs/clinic-db-architecture.md` STEP1/5節、変更なし)。Clinic側migrationロールには
`public`への`CREATE`/`ALTER`/`DROP`権限を一切付与しない(5節参照)。

---

## 5. RLS / GRANT 方針

**public CRM tableのRLS問題(Supabase Security Advisorが指摘した80 tableのRLS disabled)とは
完全に別問題として扱う。** Clinic schemasは最初から「private/server-sideのみ」を前提に設計する。

### 5.1 ロール分離(方針。実role名は未確認のためplaceholder)

| ロール(placeholder名) | 用途 | 権限方針 |
|---|---|---|
| `clinic_migration_role` | Clinic側DDL migration実行専用 | `clinic_master`/`clinic_ops`へのCREATE/ALTER/DROP。`public`への権限は一切付与しない |
| `clinic_app_role` | Clinic Leadアプリのruntime接続(server-side) | `clinic_master`/`clinic_ops`へのSELECT/INSERT/UPDATE(append-onlyテーブルはUPDATE/DELETE権限を与えない、またはアプリ層で禁止を徹底) |
| `clinic_readonly_role` | 監査/BI等の読み取り専用アクセス | `clinic_master`/`clinic_ops`へのSELECTのみ |

実際のSupabase production DB roleが未確認の状態で広いGRANTを推測実行しない。上記はSchema v1時点では
**設計方針のみ**であり、実role名・実際の`GRANT`文はDB管理者が実環境を確認してから確定する。

### 5.2 anon / authenticated

`clinic_master`/`clinic_ops`は**Supabase Data APIのexposed schemasに含めない**方針を維持
(`docs/clinic-db-architecture.md` STEP6節、変更なし)。したがって`anon`/`authenticated`ロールからの
HTTPアクセス経路自体が存在しない。ブラウザ・フロントエンドからSupabaseクライアント経由でこれら
schemaに触れる経路は作らない。

### 5.3 security definer / security invoker

新規VIEW(`maps_current`, `manual_overrides_current`, `current_hp_website`,
`current_official_website`, `current_hp_rank`)はすべて`security_invoker = true`を設定済み
(`004_current_hp_rank_view.sql`, `006_create_current_views.sql`)。`SECURITY DEFINER`関数は
原則使用しない。将来これらのVIEWをData APIへ公開する場合のみ、対象tableへのRLS + 適切なpolicyを
併せて有効化する(exposeだけを先行させない、`docs/clinic-db-architecture.md` STEP6節と同じ原則)。

---

## 6. SQL ordering

既存ファイル番号(001〜004)の互換性を優先し、新規は005・006として追加した。実際の適用順序は
`docs/clinic-db-sql-drafts/README.md` の表を正とする(ファイル番号順とは一致しない)。

```
001 (clinic_master + clinics)
  → 002 (clinic_ops base: hp_research / hp_rank_feedback / maps_results / import_logs / import_log_items)
    → 005 (clinic_ops extended: manual_override_events / comdesk / research jobs)
      → 004 (view: current_hp_rank)
      → 006 (views: maps_current / manual_overrides_current / current_hp_website / current_official_website)
003 (promotion example, DDLではないためいつでも参考可)
```

---

## 7. 静的検証(手動レビュー、Supabaseへは未実行)

ローカルにpsql/Postgres/Dockerデーモンが利用できなかったため(`which psql/postgres/initdb`は
not found、`docker`はインストール済みだがdaemon未起動)、実DB/ローカル使い捨てDBでの実行検証は
行っていない。以下は全SQL draftの目視レビュー結果。

| 観点 | 結果 |
|---|---|
| dependency ordering | 6節の順序で全FK・VIEW参照先が事前に存在する。self FK(`merged_into_clinic_id`)は同一`CREATE TABLE`内でのforward referenceとして有効 |
| FK target existence | 全FKの参照先table/column(`clinic_master.clinics.clinic_id`, `clinic_ops.import_logs.batch_id`, `clinic_ops.comdesk_templates.template_id`, `clinic_ops.research_jobs.id`)が定義順で存在することを確認 |
| duplicate object | table名・VIEW名・index名・constraint名の重複なしを`grep`で確認 |
| VIEW dependency | `current_hp_rank`は`hp_research`/`hp_rank_feedback`、`maps_current`は`maps_results`、`manual_overrides_current`は`manual_override_events`、`current_hp_website`は`manual_overrides_current`+`hp_research`、`current_official_website`は`current_hp_website`+`maps_current`に依存。全て6節の順序内で解決可能 |
| CHECK consistency | `manual_override_events`のSET/CLEAR CHECKは相互排他。rank系CHECK(A/B/C/D)はhp_research/hp_rank_feedback間で値域一致。矛盾するCHECKなし |
| index target | 追加index列はすべて対応tableの実列名と一致(`grep`で列定義と索引定義を突合) |
| syntax sanity | 括弧・カンマの対応を目視確認。ただし実際のPostgresパーサによる検証ではない点に注意 |

---

## 8. Remaining unknowns

| # | 項目 | 内容 |
|---|---|---|
| 1 | `hot_status`のscoring algorithm/version | 未確定のため列・VIEWを追加していない。確定後に`current_hp_rank`拡張 |
| 2 | `hp_research.fetch_status`の正式許可語彙 | `current_hp_website`のWHERE句は実測分布(`VERIFIED`等)からの暫定値。promotion前に確定要 |
| 3 | `research_jobs.status` / `research_job_items.state`の正式語彙 | `jobs.py`実装の最終確認が必要。CHECK制約は暫定値 |
| 4 | 実Supabase DB roleの構成 | 5.1節のロール名はplaceholder。実環境確認後にGRANT文を確定 |
| 5 | `postal_code` / `clinic_name_kana`の実運用要否 | 実在件数が僅少(postal_code 21件、kana 0件)。将来入力経路の要否を業務側で判断 |
| 6 | `name_norm`等のnormalizer実装移植 | アルゴリズム自体はClinic Lead既存コード(`filters.py`, `google_maps.py`)からの移植が必要。Schema v1はstorageのみ定義 |

---

## 9. Safety

- Supabase: DDL 0 / INSERT 0 / UPDATE 0 / DELETE 0
- Clinic Production SQLite: DDL 0 / INSERT 0 / UPDATE 0 / DELETE 0
- Clinic Lead repo code変更: 0
- CRM `public` schema変更: 0
- Prisma migrations変更: 0
- 162,258件import実行: 0

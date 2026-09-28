# Clinic DB Review Resolution

> 調査日: 2026-09-28  
> Clinic Lead source: `/Users/maekawahiroyuki/Desktop/clinic-list-filter-complete` (read-only)  
> Production SQLite: `/Users/maekawahiroyuki/CrestixData/clinic-lead/clinics.sqlite3` (read-only URI)  
> 本文はSchema v1 finalize前の設計確定候補。Supabase DDL/DMLは実行しない。

## 1. Website priority contract

### 1.1 Source ownership

- `google_maps_results.maps_website_url`: Maps import 1回ごとのappend-only raw evidence。
- `clinics.maps_website_url`: confirmed websiteを低品質な後続結果から保護したcurrent Maps state。
- `research_results.result_json.hp_url`: machine researchの最新HP URL。
- `manual_overrides(field='hp_url')`: 人間が確認したHP URL。`_project()`でmachine resultより後に適用される。
- `clinics.hp_url`: base + machine + manualをprojectしたcurrent HP URL。独立した正本ではない。

### 1.2 Actual runtime priorities

| consumer | priority 1 | priority 2 | fallback | manual protection | overwrite rule |
|---|---|---|---|---|---|
| UI detail | Maps URLとHP URLを別ボタン表示 | — | — | manual `hp_url`はproject済みHP欄に表示 | 2 sourceを統合しない (`app_v2.py:144-149`) |
| HP research input | protected Maps URL (`MAPS_MATCHED_WEBSITE`) | current `hp_url` | `hp_candidate_url`, then search | manual `hp_url`はexisting候補だがMaps confirmedが先 | successful researchはmachine resultへ追記。project時にmanualが再優先 (`researcher.py:80-92`, `store.py:201-206`) |
| forced/re-research | protected Maps URL | current projected HP URL | search | recompute後もmanual overrideを最後に適用 | machine rowだけ更新、manual rowは保持 |
| new-row Comdesk export | protected Maps URL | VERIFIED HP URL | blank | manual HPはproject済みHP URLとしてpriority 2 | `fixed_export.py:73-74` |
| original-row Comdesk export | original 28-column URL | protected Maps URL only when original URL blank | blank | manual HPでoriginal URLを上書きしない | raw original valuesがcomputed valuesを上書き (`fixed_export.py:87-119`) |
| Maps import | incoming confirmed Maps URL | existing protected confirmed Maps URL | incoming non-confirmed state if no protected URL | HP manual overrideには触れない | confirmed→non-confirmed downgradeは禁止。次のconfirmedだけ置換 (`google_maps.py:125-166`) |
| manual override | latest SET `hp_url` | machine HP URL after CLEAR | base/default | latest manual event wins | machine recomputeで上書きしない (`store.py:201-206,369-398`) |

### 1.3 PostgreSQL resolution

`clinic_master.clinics.website`へ不可逆統合しない。Schema v1ではsource-specific stateを保持する。

1. `clinic_ops.maps_results.maps_website_url`: Maps raw event URL。
2. `clinic_ops.maps_current`: protected current Maps eventを解決するVIEW。
3. `clinic_ops.hp_research.url`: machine HP URL history。
4. `clinic_ops.manual_overrides_current`: latest manual SET/CLEARを解決するVIEW。
5. `clinic_ops.current_hp_website`: latest manual `hp_url` SET、なければlatest verified machine HP URL。

汎用表示用の`current_official_website`が必要な場合だけ、
`current_hp_website` → `maps_current.maps_website_url`の順でVIEWにより解決する。ただしHP research inputと
Comdesk exportは上表の固有規則を使い、この汎用VIEWで置き換えない。VIEWはprivate schema内に置き、
将来Data APIへ公開する場合はPostgres 15+の`security_invoker=true`と適切なRLS/GRANTを必須とする。

## 2. Comdesk data contract

### 2.1 Production facts

| table | rows | key / join | data quality |
|---|---:|---|---|
| `templates` | 1 | `id TEXT PK` | headers/mapping JSONともvalid。header数28、mapping key数10 |
| `comdesk_original_rows` | 21 | `clinic_id -> clinics.id`, `template_id -> templates.id` | clinic/template NULL 0、orphan 0、row JSON 21/21 valid、全行28列 |
| `import_batches` | 8 | `id TEXT PK` | result JSON 8/8 valid。Comdesk batch 1件 |

`comdesk_original_rows`は`UNIQUE(source_hash,row_number)`、`idx_original_clinic(clinic_id)`を持つ。
21行は21医院・非空UUID 21個に1対1で、clinic/UUID/source row重複は0。

### 2.2 Export protection rule

`fixed_row()`はまずcurrent dataから28列を組み立てるが、original rowがある場合はtemplate mappingで
対応する元セルを**空欄を含めて上書き復元**する。元URLが空欄の場合だけprotected Maps websiteを補完する。
元URLをmachine HPや別sourceで上書きしない。この規則をPostgreSQL移行後も維持する。

### 2.3 PostgreSQL target candidate

`clinic_ops.comdesk_templates`

- `template_id text PRIMARY KEY` (現hash identityを保持)
- `headers jsonb NOT NULL` (array、Schema v1では28要素CHECK候補)
- `field_mapping jsonb NOT NULL`
- `created_at timestamptz NOT NULL`

`clinic_ops.comdesk_original_rows`

- `id uuid PRIMARY KEY DEFAULT gen_random_uuid()` (row surrogate)
- `clinic_id uuid NULL REFERENCES clinic_master.clinics ON DELETE RESTRICT`
- `template_id text NOT NULL REFERENCES clinic_ops.comdesk_templates ON DELETE RESTRICT`
- `original_values jsonb NOT NULL` (ordered JSON array、28要素CHECK候補)
- `legacy_uuid uuid NULL` (source snapshot)
- `source_hash text NOT NULL`
- `source_row_number int NOT NULL`
- `imported_batch_id uuid NULL` (import audit link)
- `created_at timestamptz NOT NULL`
- `UNIQUE(source_hash, source_row_number)`、index `(clinic_id)`

`clinic_id`は既存21件では全て非NULL。将来REVIEW source rowを保持する場合に備えてnullableとし、未解決行は
export対象にしない。元28列は順序付きarrayで保持し、templateのheaders/mappingと同じsnapshotから解決する。
これによりSQLiteなしでも現行28列exportを完全再現できる。

## 3. Maps raw/current contract

### 3.1 History

`clinic_ops.maps_results`はappend-only raw history。次を保持する。

- typed: `maps_status`, `maps_profile_url`, `maps_website_url`, `maps_match_method`, `fetched_at`
- raw/audit: `raw_result jsonb`, `source_batch_id`, `source_row_number`, `created_at`
- legacy sourceにない`place_id`, coordinates, rating/review countはNULL

### 3.2 Protected current projection

`clinic_ops.maps_current`は**tableではなくVIEW**を採用する。理由:

- raw eventを唯一の正本にし、mutable current tableとの二重書込み・driftを避ける。
- 現行保護規則を決定的に再現できる。
- current stateを再build可能にする。

医院ごとの選択規則:

1. confirmed website eventが1件以上なら、その中の最新を選ぶ。
2. confirmed website eventがなければ全eventの最新を選ぶ。
3. event順はimport到着順を表す`created_at DESC, id DESC`。`fetched_at`は観測時刻として表示するが、
   out-of-order importでも現行コードと同じ「後から受理したconfirmedが置換」を守るため選択順には使わない。
4. confirmed判定は`maps_status='MAPS_MATCHED_WEBSITE'`、URL非空、raw `website_status`が
   AMBIGUOUS/NO_WEBSITE/ERRORでないこと。

これによりconfirmed event後のNOT_FOUND/AMBIGUOUS/ERROR/URL空欄はcurrentを格下げせず、次のconfirmedだけが
置換する。legacy `clinics.maps_*`は初期cutoverでsynthetic current-seed eventとして1件投入し、raw historyに
欠落があっても現行protected stateを失わない。実際の投入は将来のdry-run/apply工程で行い、今回は行わない。

## 4. Generic manual override contract

`hp_rank_feedback`はHP rank専用のまま維持し、generic correctionは別のappend-only tableとする。

`clinic_ops.manual_override_events` candidate:

- `id uuid PRIMARY KEY DEFAULT gen_random_uuid()`
- `clinic_id uuid NOT NULL REFERENCES clinic_master.clinics ON DELETE RESTRICT`
- `field text NOT NULL`
- `operation text NOT NULL CHECK (operation IN ('SET','CLEAR'))`
- `value jsonb NULL` (`SET`はnon-NULL、`CLEAR`はNULLのCHECK)
- `reviewer text NOT NULL`
- `source text NOT NULL`
- `reason text NULL`
- `reviewed_at timestamptz NOT NULL`
- `automatic_value_at_review jsonb NULL`
- `context_snapshot jsonb NULL`
- `created_at timestamptz NOT NULL DEFAULT now()`

許可field:
`hp_url`, `hp_status`, `hp_rank`, `epark_url`, `epark_contract`, `google_ads_status`,
`treatment_categories`, `marketing_signals`。

`manual_overrides_current` VIEWは`clinic_id,field`ごとに
`ORDER BY reviewed_at DESC, id DESC`の最新eventを選び、CLEARならmanual値なしとして扱う。
current clinic projectionはbase → latest machine → latest manual SETの順で合成するため、machine recomputeは
manual値を上書きできない。snapshotは必須ではないが、review時点のautomatic値と判断contextを監査できるため
Schema v1候補に含める。

## 5. Runtime jobs contract

legacy job rowsは移行しないが、PostgreSQL runtimeに同等tableが必要。

`clinic_ops.research_jobs`:

- `id uuid PK`, `kind text`, `options jsonb`, `status text`
- `max_searches int`, `search_count int`
- `created_at`, `updated_at` timestamptz

`clinic_ops.research_job_items`:

- `job_id uuid FK`, `clinic_id uuid FK`, composite PK
- `state text`, `result text`, `note text`
- `lease_until timestamptz NULL`はcurrent workerでは未使用。将来claim方式で必要な場合のみ採用

pause/resumeに必要なstatus/state transition、budget count、result/noteは維持する。複数worker対応時は
`SELECT ... FOR UPDATE SKIP LOCKED`等のatomic claimをSchema v1実装工程で設計する。

Cutover条件:

- `research_jobs.status='RUNNING'` = 0
- `research_job_items.state IN ('PENDING','RUNNING')` = 0
- app worker停止とresearch lock解放を確認
- 必要な完了結果が`research_results`へ反映済みであることを照合
- legacy job/job item rowsそのものはmigrationしない

## 6. Resolution status

今回対象の主要REVIEWは全て解消した。

- Website: source別保持 + consumer別priority + current VIEWで確定
- Comdesk: 2 target tables + original-first export規則で確定
- Maps: append-only history + deterministic protected VIEWで確定
- Generic manual override: append-only event + latest/current VIEWで確定
- Jobs: legacy non-migration + new runtime contract + cutover gateで確定

Schema v1 DDL工程へ渡す実装詳細として、CHECK語彙、index、RLS/GRANT、VIEWのSQL、job claim transactionを
最終化する必要はあるが、データownership/priorityに未解決REVIEWはない。

## 7. Production protection

### Before

- SHA-256: `5b8c37838006545498ec132e09e333dd6200ceccfce09b3b094af75899265c40`
- mtime: epoch `1790563202` / `2026-09-28T11:40:02+0900`
- `clinics` count: 162,258
- integrity: `ok`
- non-empty medical_key duplicate groups: 0

### After

- SHA-256: `5b8c37838006545498ec132e09e333dd6200ceccfce09b3b094af75899265c40` (beforeと一致)
- mtime: epoch `1790563202` / `2026-09-28T11:40:02+0900` (beforeと一致)
- `clinics` count: 162,258
- integrity: `ok`
- non-empty medical_key duplicate groups: 0

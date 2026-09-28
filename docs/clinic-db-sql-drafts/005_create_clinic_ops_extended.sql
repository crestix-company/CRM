-- DRAFT ONLY. 未適用。
-- 対象: Schema v1で追加した clinic_ops 拡張テーブル(generic manual override / Comdesk / research jobs)。
-- 前提: 001_create_clinic_master.sql, 002_create_clinic_ops.sql(hp_research/hp_rank_feedback/
-- maps_results/import_logs/import_log_items含む)適用後。
-- 根拠: docs/clinic-db-review-resolution.md 4節(manual override) / 2節(Comdesk) / 5節(jobs)、
-- docs/clinic-db-consumer-contract.md、docs/clinic-db-schema-v1.md。

-- ============================================================
-- Generic manual override(hp_rank_feedback以外のフィールド訂正)
-- ============================================================
-- append-only。hp_rank_feedbackはHP rank専用のまま維持し、それ以外(URL/status/治療/signals等)の
-- 人手訂正はこちらに記録する。CLEARはvalueをNULLにして「訂正を取り消す/未設定に戻す」ことを表す
-- (行はDELETEしない。CLEARも1つのイベントとしてappendする)。
CREATE TABLE IF NOT EXISTS clinic_ops.manual_override_events (
  id                          uuid        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,  -- row surrogate key、Identity設計の対象外
  clinic_id                   uuid        NOT NULL,
  field                       text        NOT NULL,
  operation                   text        NOT NULL,   -- 'SET' | 'CLEAR'
  value                       jsonb       NULL,        -- SET時のみ非NULL
  reviewer                    text        NOT NULL,
  source                      text        NOT NULL,
  reason                      text        NULL,
  reviewed_at                 timestamptz NOT NULL,
  automatic_value_at_review   jsonb       NULL,        -- レビュー時点のmachine/自動値スナップショット
  context_snapshot            jsonb       NULL,
  created_at                  timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT fk_manual_override_events_clinic
    FOREIGN KEY (clinic_id) REFERENCES clinic_master.clinics (clinic_id) ON DELETE RESTRICT,
  CONSTRAINT chk_manual_override_events_operation
    CHECK (operation IN ('SET', 'CLEAR')),
  CONSTRAINT chk_manual_override_events_value
    CHECK (
      (operation = 'SET' AND value IS NOT NULL) OR
      (operation = 'CLEAR' AND value IS NULL)
    ),
  -- 許可fieldはdocs/clinic-db-review-resolution.md 4節の語彙。新規field追加時はこのCHECKも更新する。
  CONSTRAINT chk_manual_override_events_field
    CHECK (field IN (
      'hp_url', 'hp_status', 'hp_rank', 'epark_url', 'epark_contract',
      'google_ads_status', 'treatment_categories', 'marketing_signals'
    ))
);
CREATE INDEX IF NOT EXISTS idx_manual_override_events_clinic_field_reviewed
  ON clinic_ops.manual_override_events (clinic_id, field, reviewed_at DESC, id DESC);

-- ============================================================
-- Comdesk export contract(元28列の原文保持)
-- ============================================================
-- 現Production実測: templates 1 row、comdesk_original_rows 21 rows、全行28列。
-- fixed_row()の「元セルを空欄含めて優先復元し、元URL空欄時のみMaps補完」規則を維持するための
-- 正本保持テーブル(docs/clinic-db-review-resolution.md 2節)。
CREATE TABLE IF NOT EXISTS clinic_ops.comdesk_templates (
  template_id    text        NOT NULL PRIMARY KEY,  -- 現行hash identityを保持
  headers        jsonb       NOT NULL,               -- ordered array, 28要素
  field_mapping  jsonb       NOT NULL,
  created_at     timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT chk_comdesk_templates_headers_length
    CHECK (jsonb_typeof(headers) = 'array' AND jsonb_array_length(headers) = 28)
);

CREATE TABLE IF NOT EXISTS clinic_ops.comdesk_original_rows (
  id                  uuid        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,  -- row surrogate key、Identity設計の対象外
  clinic_id           uuid        NULL,       -- 未解決REVIEW sourceを許容するためnullable。既存21件は全て非NULL
  template_id         text        NOT NULL,
  original_values     jsonb       NOT NULL,   -- ordered array, 28要素。空欄セルも含め原文を保持
  legacy_uuid         uuid        NULL,       -- source snapshot(clinic_master.clinics.legacy_uuidと別に保持)
  source_hash         text        NOT NULL,
  source_row_number   int         NOT NULL,
  imported_batch_id   uuid        NULL,
  created_at          timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT fk_comdesk_original_rows_clinic
    FOREIGN KEY (clinic_id) REFERENCES clinic_master.clinics (clinic_id) ON DELETE RESTRICT,
  CONSTRAINT fk_comdesk_original_rows_template
    FOREIGN KEY (template_id) REFERENCES clinic_ops.comdesk_templates (template_id) ON DELETE RESTRICT,
  CONSTRAINT fk_comdesk_original_rows_batch
    FOREIGN KEY (imported_batch_id) REFERENCES clinic_ops.import_logs (batch_id) ON DELETE SET NULL,
  CONSTRAINT chk_comdesk_original_rows_values_length
    CHECK (jsonb_typeof(original_values) = 'array' AND jsonb_array_length(original_values) = 28),
  CONSTRAINT uq_comdesk_original_rows_source
    UNIQUE (source_hash, source_row_number)
);
CREATE INDEX IF NOT EXISTS idx_comdesk_original_rows_clinic
  ON clinic_ops.comdesk_original_rows (clinic_id);

-- ============================================================
-- Research jobs runtime(pause/resume/budget/progress)
-- ============================================================
-- legacy in-flight job/job itemは移行しない(docs/clinic-db-review-resolution.md 5節のcutover gate:
-- RUNNING jobs=0、PENDING/RUNNING items=0、worker停止、lock解放、完了結果反映済みを確認してから
-- 新runtimeを空の状態で開始する)。status/state語彙は暫定値であり、Clinic Lead実装(jobs.py)の
-- 実際の遷移を最終確認してからこのCHECKを固定する(要確認)。
CREATE TABLE IF NOT EXISTS clinic_ops.research_jobs (
  id             uuid        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,  -- row surrogate key、Identity設計の対象外
  kind           text        NOT NULL,
  options        jsonb       NULL,
  status         text        NOT NULL,
  max_searches   int         NULL,
  search_count   int         NOT NULL DEFAULT 0,
  created_at     timestamptz NOT NULL DEFAULT now(),
  updated_at     timestamptz NOT NULL DEFAULT now(),

  -- 要確認: 暫定vocab。jobs.py実装確認後に確定する。
  CONSTRAINT chk_research_jobs_status
    CHECK (status IN ('PENDING', 'RUNNING', 'PAUSED', 'COMPLETED', 'FAILED', 'CANCELLED'))
);
CREATE INDEX IF NOT EXISTS idx_research_jobs_status ON clinic_ops.research_jobs (status);

CREATE TABLE IF NOT EXISTS clinic_ops.research_job_items (
  job_id         uuid        NOT NULL,
  clinic_id      uuid        NOT NULL,
  state          text        NOT NULL,
  result         text        NULL,
  note           text        NULL,
  lease_until    timestamptz NULL,   -- current workerでは未使用。将来claim方式導入時のみ利用(要確認)
  created_at     timestamptz NOT NULL DEFAULT now(),
  updated_at     timestamptz NOT NULL DEFAULT now(),

  PRIMARY KEY (job_id, clinic_id),
  CONSTRAINT fk_research_job_items_job
    FOREIGN KEY (job_id) REFERENCES clinic_ops.research_jobs (id) ON DELETE RESTRICT,
  CONSTRAINT fk_research_job_items_clinic
    FOREIGN KEY (clinic_id) REFERENCES clinic_master.clinics (clinic_id) ON DELETE RESTRICT,
  -- 要確認: 暫定vocab。jobs.py実装確認後に確定する。
  CONSTRAINT chk_research_job_items_state
    CHECK (state IN ('PENDING', 'RUNNING', 'DONE', 'ERROR', 'SKIPPED'))
);
CREATE INDEX IF NOT EXISTS idx_research_job_items_job_state
  ON clinic_ops.research_job_items (job_id, state);
CREATE INDEX IF NOT EXISTS idx_research_job_items_clinic
  ON clinic_ops.research_job_items (clinic_id);

-- 複数worker対応時の atomic claim は実装工程で設計する。想定パターン(未適用、参考コメントのみ):
-- SELECT job_id, clinic_id FROM clinic_ops.research_job_items
--   WHERE job_id = :job_id AND state = 'PENDING'
--   ORDER BY clinic_id
--   FOR UPDATE SKIP LOCKED
--   LIMIT :batch_size;

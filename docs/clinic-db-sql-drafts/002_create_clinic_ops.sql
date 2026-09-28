-- DRAFT ONLY. 未適用。
-- 対象: clinic_ops スキーマ(HP調査・ランクfeedback・Maps調査・importログ)
--
-- 正式決定: clinic_master.clinics(clinic_id) への cross-schema FOREIGN KEY を張る
-- (前リビジョンの「FKなし」方針から変更。docs/clinic-db-architecture.md STEP3参照)。
-- ON DELETE は RESTRICT で統一(CASCADE禁止)。001実行後(clinic_master.clinicsが存在する状態)に本ファイルを適用する。
--
-- 注記: このファイル内の `id`(hp_research/hp_rank_feedback/maps_results)や `batch_id`(import_logs)は
-- 「clinic_id」とは別概念の行サロゲートキーであり、Identity設計(UUIDv7/Python生成)の対象外。
-- これらはops側の内部row識別子に過ぎないため、DB側 `gen_random_uuid()`(UUIDv4)のままでよい
-- (docs/clinic-uuid-strategy.md「適用範囲」参照)。

CREATE SCHEMA IF NOT EXISTS clinic_ops;

CREATE TABLE IF NOT EXISTS clinic_ops.hp_research (
  id             uuid        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,  -- row surrogate key、Identity設計の対象外
  clinic_id      uuid        NOT NULL,
  url            text        NULL,
  fetch_status   text        NOT NULL,
  fetched_at     timestamptz NULL,
  content_ref    text        NULL,
  error_detail   text        NULL,
  created_at     timestamptz NOT NULL DEFAULT now(),
  updated_at     timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT fk_hp_research_clinic
    FOREIGN KEY (clinic_id) REFERENCES clinic_master.clinics (clinic_id) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_hp_research_clinic_id ON clinic_ops.hp_research (clinic_id);

CREATE TABLE IF NOT EXISTS clinic_ops.hp_rank_feedback (
  id              uuid        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  clinic_id       uuid        NOT NULL,
  machine_rank    int         NULL,
  machine_score   numeric     NULL,
  manual_rank     int         NULL,   -- 人手上書き。machine再計算バッチは絶対にこの列をUPDATEしない
  model_version   text        NULL,
  features        jsonb       NULL,
  reviewed_at     timestamptz NULL,
  reviewer        text        NULL,
  reason          text        NULL,
  -- final_rank: manual優先の生成カラム。machine再計算UPDATEでも自動的に正しい値になる。
  final_rank      int         GENERATED ALWAYS AS (COALESCE(manual_rank, machine_rank)) STORED,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT hp_rank_feedback_clinic_id_key UNIQUE (clinic_id),
  CONSTRAINT fk_hp_rank_feedback_clinic
    FOREIGN KEY (clinic_id) REFERENCES clinic_master.clinics (clinic_id) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_hp_rank_feedback_final_rank ON clinic_ops.hp_rank_feedback (final_rank);
CREATE INDEX IF NOT EXISTS idx_hp_rank_feedback_manual_reviewed
  ON clinic_ops.hp_rank_feedback (clinic_id) WHERE manual_rank IS NOT NULL;

-- machine再計算バッチが使う想定のUPDATE例(manual系カラムに触れないことを明示):
-- UPDATE clinic_ops.hp_rank_feedback
-- SET machine_rank = :machine_rank,
--     machine_score = :machine_score,
--     model_version = :model_version,
--     features = :features,
--     updated_at = now()
-- WHERE clinic_id = :clinic_id;

CREATE TABLE IF NOT EXISTS clinic_ops.maps_results (
  id             uuid        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  clinic_id      uuid        NOT NULL,
  place_id       text        NULL,
  maps_status    text        NOT NULL,
  latitude       numeric     NULL,
  longitude      numeric     NULL,
  rating         numeric     NULL,
  review_count   int         NULL,
  fetched_at     timestamptz NULL,
  created_at     timestamptz NOT NULL DEFAULT now(),
  updated_at     timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT fk_maps_results_clinic
    FOREIGN KEY (clinic_id) REFERENCES clinic_master.clinics (clinic_id) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_maps_results_clinic_id ON clinic_ops.maps_results (clinic_id);
CREATE INDEX IF NOT EXISTS idx_maps_results_status ON clinic_ops.maps_results (maps_status);

CREATE TABLE IF NOT EXISTS clinic_ops.import_logs (
  batch_id       uuid        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  source_file    text        NOT NULL,
  started_at     timestamptz NOT NULL DEFAULT now(),
  finished_at    timestamptz NULL,
  status         text        NOT NULL,
  rows_total     int         NULL,
  rows_inserted  int         NULL,
  rows_skipped   int         NULL,
  rows_review    int         NULL,
  rows_error     int         NULL,
  error_detail   text        NULL
);
CREATE INDEX IF NOT EXISTS idx_import_logs_started_at ON clinic_ops.import_logs (started_at);

-- SKIP/INSERT/REVIEW の行単位監査(docs/clinic-db-architecture.md 3.5節)
-- medical_key を例外的にスナップショット保持する(REVIEW行はclinic_idがまだ存在しないため)。
CREATE TABLE IF NOT EXISTS clinic_ops.import_log_items (
  id           uuid        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,  -- row surrogate key、Identity設計の対象外
  batch_id     uuid        NOT NULL,   -- clinic_ops.import_logs.batch_id と対応(FKなし、値参照のみ)
  medical_key  text        NOT NULL,
  clinic_id    uuid        NULL,       -- INSERT確定行のみ非NULL。SKIP/REVIEWはNULL
  decision     text        NOT NULL,   -- 'skip' | 'insert' | 'review'
  reason       text        NULL,
  created_at   timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT fk_import_log_items_clinic
    FOREIGN KEY (clinic_id) REFERENCES clinic_master.clinics (clinic_id) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_import_log_items_batch_id ON clinic_ops.import_log_items (batch_id);
CREATE INDEX IF NOT EXISTS idx_import_log_items_clinic_id ON clinic_ops.import_log_items (clinic_id);

-- Clinic側専用のmigration履歴テーブル(_prisma_migrationsとは完全別、publicにも置かない)
CREATE TABLE IF NOT EXISTS clinic_ops._clinic_schema_migrations (
  version      text        NOT NULL PRIMARY KEY,
  applied_at   timestamptz NOT NULL DEFAULT now()
);

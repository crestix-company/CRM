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

-- machine側の調査・スコア履歴。append-only(UPDATE/DELETEしない)。1医院につき複数行。
-- 「現在のmachineランク」は idx_hp_research_clinic_created の (clinic_id, created_at DESC) を使い、
-- clinic_ops.current_hp_rank VIEW(004参照)経由で「最新行」として解決する。
CREATE TABLE IF NOT EXISTS clinic_ops.hp_research (
  id             uuid        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,  -- row surrogate key、Identity設計の対象外
  clinic_id      uuid        NOT NULL,
  url            text        NULL,
  fetch_status   text        NOT NULL,
  fetched_at     timestamptz NULL,
  content_ref    text        NULL,
  error_detail   text        NULL,
  machine_rank   int         NULL,
  machine_score  numeric     NULL,
  model_version  text        NULL,
  features       jsonb       NULL,
  created_at     timestamptz NOT NULL DEFAULT now(),
  -- updated_at は持たない(append-onlyのため行は作成後に変更しない)

  CONSTRAINT fk_hp_research_clinic
    FOREIGN KEY (clinic_id) REFERENCES clinic_master.clinics (clinic_id) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_hp_research_clinic_created
  ON clinic_ops.hp_research (clinic_id, created_at DESC);

-- 人間レビューのappend-only履歴(正式決定、前リビジョンから変更)。
-- UNIQUE(clinic_id) は削除済み。レビューのたびに新しい行をINSERTし、過去行はDELETE/UPDATEしない。
-- machine_*_at_review 系は「レビュー実施時点のhp_research最新値」の不変スナップショット。
CREATE TABLE IF NOT EXISTS clinic_ops.hp_rank_feedback (
  id                          uuid        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  clinic_id                   uuid        NOT NULL,
  manual_rank                 int         NOT NULL,
  reviewer                    text        NOT NULL,
  reason                      text        NULL,
  reviewed_at                 timestamptz NOT NULL DEFAULT now(),
  machine_rank_at_review      int         NULL,
  machine_score_at_review     numeric     NULL,
  model_version_at_review     text        NULL,
  features_snapshot           jsonb       NULL,
  created_at                  timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT fk_hp_rank_feedback_clinic
    FOREIGN KEY (clinic_id) REFERENCES clinic_master.clinics (clinic_id) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_hp_rank_feedback_clinic_reviewed
  ON clinic_ops.hp_rank_feedback (clinic_id, reviewed_at DESC);

-- machine側の再計算は hp_research への INSERT のみで完結し、hp_rank_feedback には一切触れない。
-- UPDATE文自体が存在しないため、「manual系カラムを上書きしないよう注意深く書く」運用は不要
-- (append-onlyであること自体が保護になる)。
-- 「今のランク」の解決は 004_current_hp_rank_view.sql の VIEW を参照。

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
-- medical_key を例外的にスナップショット保持する(REVIEW行・rollback後はclinic_idがNULLになるため)。
--
-- FK設計(正式決定、前リビジョンから変更):
-- - batch_id は import_logs へ RESTRICT のFKを新規に張る(batch監査ログを恒久保持するため)。
-- - clinic_id は RESTRICT ではなく SET NULL を採用。rollbackで clinic_master.clinics 側の
--   新規行を削除しても、この監査行自体は消えず clinic_id だけがNULLになる
--   (docs/clinic-db-migration-plan.md STEP[11]参照)。
CREATE TABLE IF NOT EXISTS clinic_ops.import_log_items (
  id           uuid        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,  -- row surrogate key、Identity設計の対象外
  batch_id     uuid        NOT NULL,
  medical_key  text        NOT NULL,
  clinic_id    uuid        NULL,       -- INSERT確定行のみ非NULL。SKIP/REVIEW、rollback後はNULL
  decision     text        NOT NULL,   -- 'skip' | 'insert' | 'review'
  reason       text        NULL,
  created_at   timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT fk_import_log_items_batch
    FOREIGN KEY (batch_id) REFERENCES clinic_ops.import_logs (batch_id) ON DELETE RESTRICT,
  CONSTRAINT fk_import_log_items_clinic
    FOREIGN KEY (clinic_id) REFERENCES clinic_master.clinics (clinic_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_import_log_items_batch_id ON clinic_ops.import_log_items (batch_id);
CREATE INDEX IF NOT EXISTS idx_import_log_items_clinic_id ON clinic_ops.import_log_items (clinic_id);

-- Clinic側専用のmigration履歴テーブル(_prisma_migrationsとは完全別、publicにも置かない)
CREATE TABLE IF NOT EXISTS clinic_ops._clinic_schema_migrations (
  version      text        NOT NULL PRIMARY KEY,
  applied_at   timestamptz NOT NULL DEFAULT now()
);

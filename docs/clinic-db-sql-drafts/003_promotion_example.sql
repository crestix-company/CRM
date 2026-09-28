-- DRAFT ONLY. 未適用。単体で流す想定ではなく、Python側バッチ処理のロジック例として提示。
-- 前提: clinic_staging.clinics_raw に staging import 済み(docs/clinic-db-migration-plan.md STEP3参照)。
-- clinic_staging スキーマ自体の作成DDLは、Clinic側の実際のstagingツールに合わせて別途用意する。
--
-- UUID方針(正式確定): clinic_id は UUIDv7、Python側で生成してから渡す。本ファイルにDB側UUID生成
-- (gen_random_uuid()等)は一切含めない。生成実装は docs/clinic-uuid-strategy.md 参照。

-- [4] medical_key 重複再検証(staging側)
-- SELECT medical_key, COUNT(*) FROM clinic_staging.clinics_raw GROUP BY medical_key HAVING COUNT(*) > 1;

-- (a) 新規対象の抽出。Pythonがこれを実行し、結果行ごとにUUIDv7を生成してから (b) へ渡す。
-- 既存medical_keyの行はここでLEFT JOINにより自然に除外される(= SKIP。新しいUUIDv7は発行しない)。
SELECT s.*
FROM clinic_staging.clinics_raw s
LEFT JOIN clinic_master.clinics c ON c.medical_key = s.medical_key
WHERE c.medical_key IS NULL                      -- 新規のみ(既存はSKIP)
  AND s.medical_key IS NOT NULL                   -- キー欠落はREVIEW対象、ここでは弾く
  AND COALESCE(s.review_flag, false) IS NOT TRUE; -- 内容不整合フラグが立っていない行のみ

-- (b) [9] promotion: Pythonが (a) の各行に対して clinic_id = uuidv7() を生成した上でINSERT。
-- 実運用は execute_values 等でバッチ化する。DB側は値を受け取るだけで一切生成しない。
-- 列は簡略化のため一部のみ例示。Schema v1確定の全列(medical_type/designation_date/owner_equal/
-- active/is_new/merge_hold/exclude_reason/source_payload等)は docs/clinic-db-schema-v1.md 2.4節、
-- 実装時のINSERT対象列は docs/clinic-db-sql-drafts/001_create_clinic_master.sql を正とする。
-- `website`列は存在しない(clinic_master.clinicsへ単一websiteを持たせない設計。
-- docs/clinic-db-review-resolution.md 1.3節)。
INSERT INTO clinic_master.clinics
  (clinic_id, medical_key, legacy_uuid, clinic_name, prefecture, address, phone,
   source, imported_batch_id, created_at, updated_at)
VALUES
  (:clinic_id, :medical_key, :legacy_uuid, :clinic_name, :prefecture, :address, :phone,
   'legacy_sqlite', :batch_id, now(), now());

-- (c) 行単位監査ログ(SKIP/INSERT/REVIEWそれぞれについてPythonが1行ずつ記録する)
-- 注: import_log_items.batch_id は clinic_ops.import_logs(batch_id) への RESTRICT FKを持つため、
-- 事前に clinic_ops.import_logs へ当該batchの行(status='running'等)が作成済みである必要がある。
-- INSERT確定行: clinic_id を記録
INSERT INTO clinic_ops.import_log_items (batch_id, medical_key, clinic_id, decision, reason)
VALUES (:batch_id, :medical_key, :clinic_id, 'insert', NULL);

-- REVIEW行: UUIDv7を発行していても production へは未INSERTのため clinic_id は NULL のまま記録
-- (発行だけして使われないUUIDは orphan として無害に破棄してよい。後始末は不要)
INSERT INTO clinic_ops.import_log_items (batch_id, medical_key, clinic_id, decision, reason)
VALUES (:batch_id, :medical_key, NULL, 'review', :reason);

-- SKIP行: 既存clinic_idをそのまま参照して記録(新規UUIDv7は発行しない)
INSERT INTO clinic_ops.import_log_items (batch_id, medical_key, clinic_id, decision, reason)
VALUES (:batch_id, :medical_key, :existing_clinic_id, 'skip', NULL);

-- [10] retry-safe / idempotent: 同一batch_idで再実行しても (a) のLEFT JOINにより
-- 既にINSERT済みのmedical_keyは自然に対象外となるため、途中失敗からの再実行が安全。

-- [11] rollback(正式決定、前リビジョンから変更): import_log_items は一切DELETEしない。
-- PRECONDITION (両方必須):
--   1. PRE-CUTOVERであること。
--   2. 対象医院についてhp_research / hp_rank_feedback / maps_results等のops業務データが
--      まだ1行も生成されていないこと。
-- この条件を満たす期間だけ、imported_batch_id単位のhard DELETE rollbackを許可する。
-- POST-CUTOVERまたはops業務データ生成後はhard DELETE rollback禁止。通常のops FKは
-- ON DELETE RESTRICTのためDELETEを拒否する。ops/監査履歴を消して強制rollbackしてはならない。
-- 復旧はprevious SQLite backup、DB backup / PITR、corrective migration、status / deactivationを使う。
-- clinic_id は ON DELETE SET NULL のFKに変更済みのため、以下のDELETEを実行すると
-- import_log_items 側は行ごと残り、対応する clinic_id 列だけが自動的にNULLになる
-- (batch_id/medical_key/decision/reason/created_at は保持される。監査履歴を消さない)。
-- 対象は「当該batchで新規INSERTされた行」のみ(imported_batch_idはSKIP行では更新されないため、
-- 既存行・他batchの行はこの条件に一致せず絶対にDELETEされない)。
DELETE FROM clinic_master.clinics WHERE imported_batch_id = :batch_id;

-- rollback後、batch自体のstatusを更新する場合(今回は実行しない。将来のrunbook例):
-- UPDATE clinic_ops.import_logs SET status = 'rolled_back', finished_at = now() WHERE batch_id = :batch_id;

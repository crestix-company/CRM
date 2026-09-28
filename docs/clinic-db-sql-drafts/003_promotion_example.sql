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
INSERT INTO clinic_master.clinics
  (clinic_id, medical_key, legacy_uuid, clinic_name, prefecture, address, phone, website,
   source, imported_batch_id, created_at, updated_at)
VALUES
  (:clinic_id, :medical_key, :legacy_uuid, :clinic_name, :prefecture, :address, :phone, :website,
   'legacy_sqlite', :batch_id, now(), now());

-- (c) 行単位監査ログ(SKIP/INSERT/REVIEWそれぞれについてPythonが1行ずつ記録する)
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

-- [11] rollback(当該batchのみ、他batch・既存データに影響なし)
-- import_log_items が clinic_id へ ON DELETE RESTRICT のFKを持つため、
-- clinic_master.clinics を削除する前に import_log_items 側の対応行を先に削除する。
-- DELETE FROM clinic_ops.import_log_items WHERE batch_id = :batch_id;
-- DELETE FROM clinic_master.clinics WHERE imported_batch_id = :batch_id;

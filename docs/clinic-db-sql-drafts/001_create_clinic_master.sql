-- DRAFT ONLY. 未適用。CREATE SCHEMA等はSupabaseへ実行していない。
-- 対象: clinic_master スキーマの新規作成(Prisma管理領域 public とは完全に独立)
--
-- UUID方針(正式確定): clinic_id は UUIDv7、Clinic Lead側Pythonアプリケーションで生成し、
-- INSERT時に値として渡す。DB側の DEFAULT gen_random_uuid() は使用しない
-- (gen_random_uuid() は UUIDv4 を返すため、UUIDv4混在防止のためあえて外している)。
-- 生成実装・ライブラリ選定・テスト設計は docs/clinic-uuid-strategy.md を参照。

CREATE SCHEMA IF NOT EXISTS clinic_master;

CREATE TABLE IF NOT EXISTS clinic_master.clinics (
  clinic_id           uuid        NOT NULL PRIMARY KEY,  -- 値は必ずアプリ側(UUIDv7)から渡す。DB defaultなし
  medical_key         text        NOT NULL,
  legacy_uuid         uuid        NULL,
  clinic_name         text        NOT NULL,
  clinic_name_kana    text        NULL,       -- 要確認: SQLite側に存在するか未確定
  prefecture          text        NULL,
  postal_code         text        NULL,       -- 要確認
  address             text        NULL,
  phone               text        NULL,
  website             text        NULL,
  status              text        NULL,       -- 要確認: 休廃業等のフラグの有無
  source              text        NOT NULL DEFAULT 'legacy_sqlite',
  imported_batch_id   uuid        NULL,
  created_at          timestamptz NOT NULL DEFAULT now(),
  updated_at          timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT clinics_medical_key_key UNIQUE (medical_key)
);

-- legacy_uuid の一意性は STEP8 のバリデーション結果を見てから確定する(暫定で外している)。
-- 確定後、以下を有効化:
-- ALTER TABLE clinic_master.clinics ADD CONSTRAINT clinics_legacy_uuid_key UNIQUE (legacy_uuid);

CREATE INDEX IF NOT EXISTS idx_clinics_prefecture ON clinic_master.clinics (prefecture);

COMMENT ON TABLE clinic_master.clinics IS
  'Clinic Master SSOT. Owned by Clinic Lead migration tooling, NOT by CRM Prisma. See docs/clinic-db-architecture.md';

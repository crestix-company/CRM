-- DRAFT ONLY. 未適用。CREATE SCHEMA等はSupabaseへ実行していない。
-- 対象: clinic_master スキーマの新規作成(Prisma管理領域 public とは完全に独立)
-- Schema v1確定版。フィールド一覧・分類根拠は docs/clinic-db-schema-v1.md、
-- SQLite→PostgreSQLの列単位mappingは docs/clinic-sqlite-to-postgres-mapping.md を正とする。
--
-- UUID方針(正式確定): clinic_id は UUIDv7、Clinic Lead側Pythonアプリケーションで生成し、
-- INSERT時に値として渡す。DB側の DEFAULT gen_random_uuid() は使用しない
-- (gen_random_uuid() は UUIDv4 を返すため、UUIDv4混在防止のためあえて外している)。
-- 生成実装・ライブラリ選定・テスト設計は docs/clinic-uuid-strategy.md を参照。
--
-- website方針(正式確定、docs/clinic-db-review-resolution.md 1.3節): このtableに単一`website`列は
-- 置かない。Maps確定URL/machine HP URL/manual HP URLはsource別に clinic_ops 側で保持し、
-- consumer別priorityをVIEWで解決する(clinic_ops.current_hp_website / maps_current /
-- current_official_website。006_create_current_views.sql参照)。

CREATE SCHEMA IF NOT EXISTS clinic_master;

CREATE TABLE IF NOT EXISTS clinic_master.clinics (
  clinic_id                 uuid        NOT NULL PRIMARY KEY,  -- 値は必ずアプリ側(UUIDv7)から渡す。DB defaultなし
  medical_key               text        NOT NULL,
  legacy_uuid               uuid        NULL,       -- SQLite `clinics.uuid`。非空21件はvalid/unique実測済み

  -- 基本属性(MUST_MIGRATE)
  clinic_name               text        NOT NULL,
  clinic_name_kana          text        NULL,       -- SQLite側に対応列なし。常にNULLで移行(将来入力用に予約)
  medical_type              text        NULL,       -- 医科/歯科。filter/調査母集団のMUST_MIGRATE
  prefecture                text        NULL,
  postal_code               text        NULL,       -- SQLite `base_json`内のみ(実在21件)。原則NULL
  address                   text        NULL,
  phone                     text        NULL,

  -- 開業・指定/属性フィルタ(MUST_MIGRATE)
  designation_date          date        NULL,
  recent_until              date        GENERATED ALWAYS AS (
                                           (designation_date + INTERVAL '10 years')::date
                                         ) STORED,               -- DERIVABLE。designation_date + 10年の固定regenerate
  registration_reason       text        NULL,
  owner_equal               boolean     NULL,
  age_probability           numeric     NULL,
  departments               text[]      NULL,       -- 診療科(SQLite departments_json由来)

  -- ライフサイクル/運用フィルタ(MUST_MIGRATE)
  active                    boolean     NOT NULL DEFAULT true,
  is_new                    boolean     NOT NULL DEFAULT false,
  source_as_of_date         date        NULL,
  merge_hold                boolean     NOT NULL DEFAULT false,
  merged_into_clinic_id     uuid        NULL,       -- self FK。canonical医院への統合先(下記CONSTRAINT参照)
  exclude_reason            text        NULL,       -- Comdesk営業対象除外理由

  -- 正本payload/観測時刻(MUST_MIGRATE/SHOULD_MIGRATE)
  source_payload            jsonb       NULL,       -- SQLite base_json。projection/import/mergeの入力
  first_seen_at             timestamptz NULL,
  last_seen_at              timestamptz NULL,

  -- 検索/matching投影(DERIVABLE。algorithmはアプリ側、DBはstorageのみ)
  name_norm                 text        NULL,
  name_prefix               text        NULL,
  phone_norm                text        NULL,
  address_norm              text        NULL,
  tel_match_key             text        NULL,
  search_projection_version text        NULL,       -- name_norm等を生成したnormalizerのversion tag(再現性のため必須)

  -- migration/監査
  source                    text        NOT NULL DEFAULT 'legacy_sqlite',
  imported_batch_id         uuid        NULL,
  created_at                timestamptz NOT NULL DEFAULT now(),
  updated_at                timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT clinics_medical_key_key UNIQUE (medical_key),
  CONSTRAINT clinics_medical_key_nonblank CHECK (btrim(medical_key) <> ''),
  -- legacy_uuid UNIQUE: readonly-audit実測(非空21件、valid 21、重複0)により有効化。
  -- promotion dry-runでcast成功・重複0を再確認してから実DBへ適用すること。
  CONSTRAINT clinics_legacy_uuid_key UNIQUE (legacy_uuid),
  -- merged_into_clinic_id: self FK。CASCADE禁止(統合先の医院を誤って連鎖削除しない)。
  -- 統合先を削除したい場合は、先に参照している行のmerged_into_clinic_idを解除してから行う。
  CONSTRAINT fk_clinics_merged_into
    FOREIGN KEY (merged_into_clinic_id) REFERENCES clinic_master.clinics (clinic_id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_clinics_prefecture ON clinic_master.clinics (prefecture);
CREATE INDEX IF NOT EXISTS idx_clinics_medical_type ON clinic_master.clinics (medical_type);
CREATE INDEX IF NOT EXISTS idx_clinics_active ON clinic_master.clinics (active);
CREATE INDEX IF NOT EXISTS idx_clinics_merge_state ON clinic_master.clinics (merge_hold, merged_into_clinic_id);
CREATE INDEX IF NOT EXISTS idx_clinics_name_norm ON clinic_master.clinics (name_norm);
CREATE INDEX IF NOT EXISTS idx_clinics_phone_norm ON clinic_master.clinics (phone_norm);
CREATE INDEX IF NOT EXISTS idx_clinics_tel_match_key ON clinic_master.clinics (tel_match_key);

COMMENT ON TABLE clinic_master.clinics IS
  'Clinic Master SSOT. Owned by Clinic Lead migration tooling, NOT by CRM Prisma. See docs/clinic-db-schema-v1.md';

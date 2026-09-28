-- DRAFT ONLY. 未適用。
-- 対象: website/Maps/manual overrideの「現在値」を解決するVIEW群。
-- 前提: 001, 002, 005 適用後(maps_results, manual_override_events, hp_research等が存在すること)。
-- 方針(docs/clinic-db-review-resolution.md 1.3節): clinic_master.clinics に単一websiteへ
-- 不可逆統合しない。source別状態を保持し、consumer別priorityをVIEWで解決する。
--
-- すべてのVIEWに security_invoker = true を設定する。現時点でこれらのschemaはSupabase Data API
-- へ公開していないため実害はないが、将来Data API公開を検討する際にRLSを呼び出し元ロールの権限で
-- 正しく評価させるための既定姿勢としてあらかじめ設定する(docs/clinic-db-review-resolution.md 1.3節)。

-- ============================================================
-- Maps: 保護されたcurrent projection(単純なlatest rowではない)
-- ============================================================
-- 選択規則(docs/clinic-db-review-resolution.md 3.2節):
--   1. confirmed website event(maps_status='MAPS_MATCHED_WEBSITE' かつ URL非空)が1件以上あれば、
--      その中の最新(created_at DESC, id DESC)を採用する。
--   2. confirmed eventが無ければ、全eventの最新を採用する。
--   3. confirmed採用後にNOT_FOUND/AMBIGUOUS/ERROR/URL空欄の後続eventが来てもcurrentを格下げしない。
CREATE OR REPLACE VIEW clinic_ops.maps_current AS
SELECT
  c.clinic_id,
  chosen.maps_status,
  chosen.maps_profile_url,
  chosen.maps_website_url,
  chosen.maps_match_method,
  chosen.fetched_at,
  chosen.created_at AS event_created_at,
  chosen.is_confirmed
FROM clinic_master.clinics c
LEFT JOIN LATERAL (
  (
    SELECT m.maps_status, m.maps_profile_url, m.maps_website_url, m.maps_match_method,
           m.fetched_at, m.created_at, true AS is_confirmed, m.id
    FROM clinic_ops.maps_results m
    WHERE m.clinic_id = c.clinic_id
      AND m.maps_status = 'MAPS_MATCHED_WEBSITE'
      AND m.maps_website_url IS NOT NULL
    ORDER BY m.created_at DESC, m.id DESC
    LIMIT 1
  )
  UNION ALL
  (
    SELECT m.maps_status, m.maps_profile_url, m.maps_website_url, m.maps_match_method,
           m.fetched_at, m.created_at, false AS is_confirmed, m.id
    FROM clinic_ops.maps_results m
    WHERE m.clinic_id = c.clinic_id
    ORDER BY m.created_at DESC, m.id DESC
    LIMIT 1
  )
  ORDER BY is_confirmed DESC, created_at DESC, id DESC
  LIMIT 1
) chosen ON true;

ALTER VIEW clinic_ops.maps_current SET (security_invoker = true);

COMMENT ON VIEW clinic_ops.maps_current IS
  'Protected current Maps state: confirmed website event wins over any later NOT_FOUND/AMBIGUOUS/ERROR event. See docs/clinic-db-review-resolution.md 3.2';

-- ============================================================
-- Generic manual override: フィールドごとの最新イベント
-- ============================================================
-- CLEARの場合はvalueをNULLとして扱う(訂正の取り消し/未設定への復帰)。
CREATE OR REPLACE VIEW clinic_ops.manual_overrides_current AS
SELECT DISTINCT ON (e.clinic_id, e.field)
  e.clinic_id,
  e.field,
  e.operation,
  CASE WHEN e.operation = 'SET' THEN e.value ELSE NULL END AS value,
  e.reviewer,
  e.reason,
  e.reviewed_at
FROM clinic_ops.manual_override_events e
ORDER BY e.clinic_id, e.field, e.reviewed_at DESC, e.id DESC;

ALTER VIEW clinic_ops.manual_overrides_current SET (security_invoker = true);

COMMENT ON VIEW clinic_ops.manual_overrides_current IS
  'Latest SET/CLEAR per (clinic_id, field). CLEAR resolves to NULL value. See docs/clinic-db-review-resolution.md 4';

-- ============================================================
-- HP website: manual優先、なければ最新verified machine URL
-- ============================================================
-- 要確認: fetch_status='VERIFIED' はreadonly-audit実測(clinics.hp_status分布)を参照した暫定値。
-- hp_research.fetch_statusの正式な許可語彙が確定次第、このWHERE条件を更新する。
CREATE OR REPLACE VIEW clinic_ops.current_hp_website AS
SELECT
  c.clinic_id,
  COALESCE(manual.value #>> '{}', machine.url) AS website,
  (manual.value IS NOT NULL) AS is_manual
FROM clinic_master.clinics c
LEFT JOIN clinic_ops.manual_overrides_current manual
  ON manual.clinic_id = c.clinic_id AND manual.field = 'hp_url'
LEFT JOIN LATERAL (
  SELECT hr.url
  FROM clinic_ops.hp_research hr
  WHERE hr.clinic_id = c.clinic_id
    AND hr.fetch_status = 'VERIFIED'
    AND hr.url IS NOT NULL
  ORDER BY hr.created_at DESC, hr.id DESC
  LIMIT 1
) machine ON true;

ALTER VIEW clinic_ops.current_hp_website SET (security_invoker = true);

COMMENT ON VIEW clinic_ops.current_hp_website IS
  'Latest manual hp_url SET, otherwise latest verified machine HP URL. See docs/clinic-db-review-resolution.md 1.3';

-- ============================================================
-- 汎用website表示(必要な場合のみ使用。HP research inputとComdesk exportは
-- 固有のpriority規則を使うため、このVIEWで置き換えない)
-- ============================================================
CREATE OR REPLACE VIEW clinic_ops.current_official_website AS
SELECT
  c.clinic_id,
  COALESCE(hp.website, maps.maps_website_url) AS website
FROM clinic_master.clinics c
LEFT JOIN clinic_ops.current_hp_website hp ON hp.clinic_id = c.clinic_id
LEFT JOIN clinic_ops.maps_current maps ON maps.clinic_id = c.clinic_id;

ALTER VIEW clinic_ops.current_official_website SET (security_invoker = true);

COMMENT ON VIEW clinic_ops.current_official_website IS
  'Generic display-only website resolution (current_hp_website falling back to maps_current). Do not use for HP research input or Comdesk export — those follow source-specific priority rules. See docs/clinic-db-review-resolution.md 1.3';

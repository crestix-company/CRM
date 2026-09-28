-- DRAFT ONLY. 未適用。
-- 目的: hp_research(machine側append-only履歴) と hp_rank_feedback(人間レビューappend-only履歴) から
-- 「医院ごとの現在のランク」を解決するVIEW。final_rankをテーブルに固定保存せず、常にクエリで解決する
-- (docs/clinic-db-architecture.md 3.2.1節参照)。
--
-- 前提: 001_create_clinic_master.sql, 002_create_clinic_ops.sql(hp_research/hp_rank_feedback含む)適用後。
--
-- ロジック:
--   final_rank = 最新manual_rankがあればそれ、なければ最新machine_rank(いずれもtext、'A'|'B'|'C'|'D')
-- machine側が新しい調査行を追加しても、hp_rank_feedbackの過去レビューは一切変更されないため、
-- machine再計算によって過去のmanual reviewが消える・上書きされることは構造上ない。
--
-- 決定性: 同一timestamp(created_at/reviewed_at)が複数行に付く可能性があるため、
-- id をtie-breakerに追加してORDER BYを完全に決定的にする(id DESC自体に意味はなく、
-- 「同点なら常に同じ1行が選ばれる」ことだけを保証する)。

-- treatment_categories / confirmed_signals: docs/clinic-db-consumer-contract.md で
-- DERIVABLE(HP調査由来のfilter)と分類された投影。hp_research.features jsonb内に
-- 同名keyで格納されている前提で最新行から抽出する(格納key名は実装確定後に要調整、要確認)。
-- hot_status: scoring algorithmとversion固定が未確定のため、Schema v1では列を追加しない
-- (docs/clinic-db-consumer-contract.md 7節「Target gaps」参照。確定後にこのVIEWへ追加する)。
CREATE OR REPLACE VIEW clinic_ops.current_hp_rank AS
SELECT
  c.clinic_id,
  latest_machine.machine_rank,
  latest_machine.machine_score,
  latest_machine.model_version,
  latest_machine.created_at   AS machine_computed_at,
  latest_machine.features -> 'treatment_categories' AS treatment_categories,
  latest_machine.features -> 'confirmed_signals'    AS confirmed_signals,
  latest_manual.manual_rank,
  latest_manual.reviewer,
  latest_manual.reason,
  latest_manual.reviewed_at,
  COALESCE(latest_manual.manual_rank, latest_machine.machine_rank) AS final_rank
FROM clinic_master.clinics c
LEFT JOIN LATERAL (
  SELECT hr.machine_rank, hr.machine_score, hr.model_version, hr.created_at, hr.features
  FROM clinic_ops.hp_research hr
  WHERE hr.clinic_id = c.clinic_id
    AND hr.machine_rank IS NOT NULL
  ORDER BY hr.created_at DESC, hr.id DESC
  LIMIT 1
) latest_machine ON true
LEFT JOIN LATERAL (
  SELECT f.manual_rank, f.reviewer, f.reason, f.reviewed_at
  FROM clinic_ops.hp_rank_feedback f
  WHERE f.clinic_id = c.clinic_id
  ORDER BY f.reviewed_at DESC, f.id DESC
  LIMIT 1
) latest_manual ON true;

ALTER VIEW clinic_ops.current_hp_rank SET (security_invoker = true);

COMMENT ON VIEW clinic_ops.current_hp_rank IS
  'Resolves current HP rank per clinic from append-only hp_research/hp_rank_feedback history. manual review always wins over machine when present. See docs/clinic-db-architecture.md 3.2.1';

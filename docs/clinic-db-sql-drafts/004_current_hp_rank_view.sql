-- DRAFT ONLY. 未適用。
-- 目的: hp_research(machine側append-only履歴) と hp_rank_feedback(人間レビューappend-only履歴) から
-- 「医院ごとの現在のランク」を解決するVIEW。final_rankをテーブルに固定保存せず、常にクエリで解決する
-- (docs/clinic-db-architecture.md 3.2.1節参照)。
--
-- 前提: 001_create_clinic_master.sql, 002_create_clinic_ops.sql(hp_research/hp_rank_feedback含む)適用後。
--
-- ロジック:
--   final_rank = 最新manual_rankがあればそれ、なければ最新machine_rank
-- machine側が新しい調査行を追加しても、hp_rank_feedbackの過去レビューは一切変更されないため、
-- machine再計算によって過去のmanual reviewが消える・上書きされることは構造上ない。

CREATE OR REPLACE VIEW clinic_ops.current_hp_rank AS
SELECT
  c.clinic_id,
  latest_machine.machine_rank,
  latest_machine.machine_score,
  latest_machine.model_version,
  latest_machine.created_at   AS machine_computed_at,
  latest_manual.manual_rank,
  latest_manual.reviewer,
  latest_manual.reason,
  latest_manual.reviewed_at,
  COALESCE(latest_manual.manual_rank, latest_machine.machine_rank) AS final_rank
FROM clinic_master.clinics c
LEFT JOIN LATERAL (
  SELECT hr.machine_rank, hr.machine_score, hr.model_version, hr.created_at
  FROM clinic_ops.hp_research hr
  WHERE hr.clinic_id = c.clinic_id
    AND hr.machine_rank IS NOT NULL
  ORDER BY hr.created_at DESC
  LIMIT 1
) latest_machine ON true
LEFT JOIN LATERAL (
  SELECT f.manual_rank, f.reviewer, f.reason, f.reviewed_at
  FROM clinic_ops.hp_rank_feedback f
  WHERE f.clinic_id = c.clinic_id
  ORDER BY f.reviewed_at DESC
  LIMIT 1
) latest_manual ON true;

COMMENT ON VIEW clinic_ops.current_hp_rank IS
  'Resolves current HP rank per clinic from append-only hp_research/hp_rank_feedback history. manual review always wins over machine when present. See docs/clinic-db-architecture.md 3.2.1';

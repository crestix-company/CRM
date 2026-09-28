# Clinic DB SQL Drafts — 未適用

**このディレクトリのSQLはすべてドラフトであり、Supabaseへ一度も実行されていない。**

- `prisma/migrations/` とは完全に別のディレクトリ。Prismaのmigrate diff/履歴には一切含まれない。
- CRM Prisma管理領域 (`public`) には触れない。すべて `clinic_master` / `clinic_ops` / `clinic_staging` を対象とする。
- 実際にClinic Lead側で採用するmigrationツール(Alembic / 素のSQLランナー等、`docs/clinic-db-schema-v1.md`
  Migration ownership節参照)にあわせて、番号体系やファイル分割は変更してよい。ここではレビュー用の
  叩き台として提示する。
- Schema v1の全体像・フィールド分類根拠・RLS/GRANT方針は `docs/clinic-db-schema-v1.md` を正とする。

## ファイルと実行順序

既存番号(001〜004)の互換性を優先し、新規ファイルは005・006として追加した。**ファイル番号の並びと
実際の依存順序は一致しない**ため、適用時は以下の順序に従うこと。

| 順序 | ファイル | 内容 |
|---|---|---|
| 1 | `001_create_clinic_master.sql` | `clinic_master` schema + `clinics` table(Schema v1全列、self FK含む) |
| 2 | `002_create_clinic_ops.sql` | `clinic_ops` schema + `hp_research` / `hp_rank_feedback` / `maps_results` / `import_logs` / `import_log_items` / `_clinic_schema_migrations` |
| 3 | `005_create_clinic_ops_extended.sql` | `manual_override_events` / `comdesk_templates` / `comdesk_original_rows` / `research_jobs` / `research_job_items`(001, 002のtableに依存) |
| 4 | `004_current_hp_rank_view.sql` | VIEW `current_hp_rank`(002の`hp_research`/`hp_rank_feedback`に依存) |
| 5 | `006_create_current_views.sql` | VIEW `maps_current` / `manual_overrides_current` / `current_hp_website` / `current_official_website`(002, 005に依存) |
| — | `003_promotion_example.sql` | データ移行ロジックの例示(INSERT文サンプル)。DDLではないため、001・002適用後ならいつでも参考にしてよい。単体のSQLとしてそのまま流す想定ではなく、実データ移行時はPython側のバッチ処理に組み込む |

## 設計方針の要点

- `hp_research` / `hp_rank_feedback` / `maps_results` は **append-only**(UPDATE/DELETEしない)。
  「現在の状態」は004・006のVIEWで解決し、テーブルに`final_rank`やcurrent website列を固定保存しない。
- `clinic_master.clinics` に単一`website`列は置かない(source別にclinic_ops側で保持し、VIEWで
  consumer別priorityを解決する。理由は`docs/clinic-db-review-resolution.md` 1.3節)。
- 通常のFKは`ON DELETE RESTRICT`(CASCADE禁止)。`import_log_items.clinic_id`のみ監査履歴保護のため
  `ON DELETE SET NULL`(`docs/clinic-db-architecture.md` 3.5節)。
- hard DELETE rollbackは PRE-CUTOVER かつ ops業務データ生成前のみ許可
  (`docs/clinic-db-migration-plan.md` STEP[11])。

適用時のチェックリストは `docs/clinic-db-migration-plan.md` を、Schema v1の完全な一覧・contract対応は
`docs/clinic-db-schema-v1.md` を参照。

# Clinic DB SQL Drafts — 未適用

**このディレクトリのSQLはすべてドラフトであり、Supabaseへ一度も実行されていない。**

- `prisma/migrations/` とは完全に別のディレクトリ。Prismaのmigrate diff/履歴には一切含まれない。
- CRM Prisma管理領域 (`public`) には触れない。すべて `clinic_master` / `clinic_ops` / `clinic_staging` を対象とする。
- 実際にClinic Lead側で採用するmigrationツール(Alembic / 素のSQLランナー等、`docs/clinic-db-architecture.md`
  STEP5参照)にあわせて、番号体系やファイル分割は変更してよい。ここではレビュー用の叩き台として提示する。
- 実行順序: 001 → 002 → 003(003は一部INSERT文の設計例であり、実データ移行時はPython側の
  バッチ処理に組み込む想定。単体のSQLとしてそのまま流す想定ではない)。

適用時のチェックリストは `docs/clinic-db-migration-plan.md` を参照。

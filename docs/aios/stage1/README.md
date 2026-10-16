# Crestix AIOS Stage1 Audit

## Outcome

Stage A〜DのREAD ONLY監査を実施した。production DBは80 public tables / Company 1,419 / Deal 4,898 / Contact 1,378 / Activity 4,231 / Task 323。Crestix「第一事業部」は医療候補が集中し、飲食候補は主にHD事業部に集中する。

最大のblockerは、80/80 public tablesでRLS無効、`anon`/`authenticated`に全権限があること。production hot-fixは行わず、runtime roleとData API利用を確認した上でpreview cloneから修正する。

## Read order

1. [Scope / sources](00_scope_and_sources.md)
2. [Risks / decisions / gates](12_risks_decisions_release_gates.md)
3. [Runtime / deployment](01_runtime_and_deployment_inventory.md)
4. [UI / API / auth](02_crm_ui_api_inventory.md)
5. [DB schema / relations](03_db_schema_relations.md)
6. [Data quality / counts](04_data_quality_counts.md)
7. [Security / RLS](05_security_grants_rls.md)
8. [First sales mapping](06_first_sales_department_mapping.md)
9. [Restaurant candidates](07_restaurant_cleanup_candidates.md)
10. [Cleanup dry-run](08_data_cleanup_dry_run_plan.md)
11. [Requirements matrix](09_requirements_traceability_matrix.md)
12. [Target architecture delta](10_target_architecture_delta.md)
13. [Performance / proposed SLO](11_performance_baseline_and_slo.md)
14. [Open PR plan](13_open_pr_inventory_and_merge_plan.md)
15. [Official requirements conformance](14_official_requirements_conformance.md)
16. [Requirements tracking update proposal](15_requirements_tracking_update_proposal.md)
17. [Stage1 completion approval gates](16_stage1_completion_approval_gates.md)
18. [Preview RLS / GRANT / Data API test design](17_preview_rls_grant_data_api_test_design.md)

## Key facts

- Inputs: expected 15, observed 15. Official 00〜12をSource of Truthとして全文照合済み。
- Supabase: `xtspgevvntpidkmyfwes`, PostgreSQL 17.6, active healthy, inspected read-only.
- Schema: 79 Prisma models + `_prisma_migrations` = 80 public base tables; 21 successful distinct migrations.
- Security: RLS ON 0/80, policy 0, anon/auth SELECT 80 and write grants 80.
- Organization: exact「第一営業部」absent; Crestix「第一事業部」is inferred mapping and needs approval.
- Classification: active Company medical 246 / restaurant candidate 235 / unknown 924; active Deal restaurant candidate 375.
- Cleanup dependencies: 80 WON candidate deals, 145 money-bearing line items, 997 participants; no deletion authorized.
- Calendar: 2 connected v1 records, refresh token missing 0; #18 stays Draft.
- PRs: #1〜#11 SUPERSEDED recommendation; #12/#13 MERGE_CANDIDATE; #14/#18 HOLD; #15〜#17 REBASE_REQUIRED. No merge/close performed.
- Formal correction: Clinic Leadは現行bridge/供給元としてLINKするが、正式要件上の医院・法人・担当者の最終SOTはCRM。authority/cutoverはStage2 gate。

## What is not complete

- Vercel old/new environment and production SHA comparison due team access.
- Browser/E2E latency and Calendar OAuth cutover rehearsal.
- Business-owner review of candidate rows and unknown categories.
- 情報区分の詳細と30日Trash後の長期保持方針（質問管理表で未回答）。
- External API/Workspace実環境可否と正式Acceptance Criteriaの実装・受入。
- Any production remediation, cleanup, migration, seed or deploy.
- Stage1 formal completion and Stage2 readiness approval; see [approval gates](16_stage1_completion_approval_gates.md) and [Preview security test design](17_preview_rls_grant_data_api_test_design.md).

## Repository validation

- `npm run db:generate`: PASS（ローカルPrisma Client生成のみ。DB接続・Migrationなし）
- `npm run typecheck`: PASS
- `npm run lint`: PASS
- `npm test`: PASS（30 files / 187 tests）
- `npm run build`: PASS（Prisma Client生成とNext.js buildのみ。Migration/Seedなし）
- `npm ci`: FAIL（既存`package-lock.json`が`fsevents@2.3.2`を欠くため）。監査ブランチではlockfileを変更せず、検証用依存は`npm install --package-lock=false --ignore-scripts`でローカル導入した。
- Build warning: repository外の上位`package-lock.json`も検出され、Next.jsのworkspace root推定が不安定。`outputFileTracingRoot`の明示はStage2候補。

## Recommended next work

Approve the first-division mapping and Clinic Lead→CRM authority/cutover; answer information classification/retention questions; grant read-only Vercel viewer access; design and rehearse least-privilege DB/RLS on a clone; validate PR #13 then #12; keep #18 Draft; defer #14〜#17 until authority requirements and the P0 security boundary are resolved.

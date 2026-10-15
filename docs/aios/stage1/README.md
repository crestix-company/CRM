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

## Key facts

- Inputs: expected 15, observed 1. Official 00〜12 and question xlsx are missing; full traceability is blocked.
- Supabase: `xtspgevvntpidkmyfwes`, PostgreSQL 17.6, active healthy, inspected read-only.
- Schema: 79 Prisma models + `_prisma_migrations` = 80 public base tables; 21 successful distinct migrations.
- Security: RLS ON 0/80, policy 0, anon/auth SELECT 80 and write grants 80.
- Organization: exact「第一営業部」absent; Crestix「第一事業部」is inferred mapping and needs approval.
- Classification: active Company medical 246 / restaurant candidate 235 / unknown 924; active Deal restaurant candidate 375.
- Cleanup dependencies: 80 WON candidate deals, 145 money-bearing line items, 997 participants; no deletion authorized.
- Calendar: 2 connected v1 records, refresh token missing 0; #18 stays Draft.
- PRs: #1〜#11 SUPERSEDED recommendation; #12/#13 MERGE_CANDIDATE; #14/#18 HOLD; #15〜#17 REBASE_REQUIRED. No merge/close performed.

## What is not complete

- Official source-by-source quotation/acceptance matrix.
- Vercel old/new environment and production SHA comparison due team access.
- Browser/E2E latency and Calendar OAuth cutover rehearsal.
- Business-owner review of candidate rows and unknown categories.
- Any production remediation, cleanup, migration, seed or deploy.

## Repository validation

- `npm run db:generate`: PASS（ローカルPrisma Client生成のみ。DB接続・Migrationなし）
- `npm run typecheck`: PASS
- `npm run lint`: PASS
- `npm test`: PASS（30 files / 187 tests）
- `BOOTSTRAP_DATABASE_ON_BUILD=false BOOTSTRAP_SEED_ON_BUILD=false npm run build`: PASS
- `npm ci`: FAIL（既存`package-lock.json`が`fsevents@2.3.2`を欠くため）。監査ブランチではlockfileを変更せず、検証用依存は`npm install --package-lock=false --ignore-scripts`でローカル導入した。
- Build warning: repository外の上位`package-lock.json`も検出され、Next.jsのworkspace root推定が不安定。`outputFileTracingRoot`の明示はStage2候補。

## Recommended next work

Provide the 14 missing inputs; grant read-only Vercel viewer access; approve the first-division mapping; design and rehearse least-privilege DB/RLS on a clone; validate PR #13 then #12; keep #18 Draft; defer #14〜#17 until authority requirements and the P0 security boundary are resolved.

# Open PR Inventory and Merge Plan (#1–#18)

## Snapshot and safety

- Observed: 2026-10-15, GitHub read-only.
- 18 open PRs; no merge/close/rebase/push performed.
- GitHub reports all heads MERGEABLE at observation time. #14/#17 are UNSTABLE; #17 Vercel `crm` failed. Other visible checks are primarily Vercel deployment/comments, not a full typecheck/lint/unit/build suite.
- Classification is recommendation, not authorization.

## Dependency graph

```text
main -> #1 -> #2 -> #3 -> #4 -> #5 -> #6 -> #7 -> #8 -> #9 -> #10 -> #11
main -> #12
main -> #13
main -> #14 -> #15 -> #16 -> #17
main -> #18 (independent Draft; keep Draft)
```

## Per-PR decision

| PR | Purpose / changed scope | Schema / migration | Base → head / CI-conflict | Requirements & operational impact | Recommendation / next action |
|---:|---|---|---|---|---|
| #1 | Clinic DB coexistence docs, SQL drafts, UUID test (9 files) | draft `clinic_master`/`clinic_ops`; no Prisma migration | main→`docs/clinic-db-design`; CLEAN; Vercel green | clinic-first intent aligns, but targets CRM Supabase and obsolete schema | **SUPERSEDED**. Preserve useful history; compare current Clinic Lead architecture, then close only with approval |
| #2 | read-only SQLite audit/mapping (2 docs) | none | #1→readonly-mapping; CLEAN | evidence was useful but 2026-09 snapshot | **SUPERSEDED** by current Clinic Lead Supabase runtime/evidence |
| #3 | consumer contract/mapping (2 docs) | none | #2→consumer-contract; CLEAN | source-specific URL/Comdesk ideas remain relevant | **SUPERSEDED**; salvage concepts into connector ADR only |
| #4 | review resolution (3 docs) | none | #3→review-resolution; CLEAN | append-only/provenance aligns | **SUPERSEDED** by current operational implementation |
| #5 | finalized Schema v1 docs/SQL (12 files) | draft schemas/views; no Prisma migration | #4→schema-v1; CLEAN | explicit no anon grants good; physical shape no longer current | **SUPERSEDED**; do not apply drafts |
| #6 | runtime vocab correction (6 files) | SQL drafts amended | #5→runtime-contract; CLEAN | vocab findings may be historical reference | **SUPERSEDED**; current main must be source |
| #7 | scratch PostgreSQL 17 validation script (3 files) | applies draft schema only to localhost | #6→schema-validation; CLEAN | testing pattern reusable | **SUPERSEDED**; port test ideas, not schema |
| #8 | write-zero importer + 58 tests (25 files) | none; reads 162,258 SQLite rows | #7→importer-dry-run; CLEAN | dry-run-first aligns | **SUPERSEDED**; current Clinic Lead already cut over, do not rerun against CRM DB |
| #9 | scratch apply/rehearsal (7 files) | scratch loader, no CRM migration | #8→rehearsal; CLEAN | historical rehearsal; high memory limitation | **SUPERSEDED** |
| #10 | resumable production migration runner (7 files) | can write target schema when invoked | #9→production-runner; CLEAN | highest accidental-apply risk; current system already migrated elsewhere | **SUPERSEDED**; never run against `xtsp...` |
| #11 | CANCELLED job contract (14 files) | draft CHECK changes | #10→cancelled-contract; CLEAN | current Clinic Lead has later job/runtime contract | **SUPERSEDED** |
| #12 | UUIDv7 helper/test/policy + AGENTS (4 files) | none | main→uuid policy; CLEAN; Vercel green | preserves existing IDs; aligns Stage1 | **MERGE_CANDIDATE** after full repo commands; coordinate duplicate helper in #16 |
| #13 | CRM Relation/FK audit doc (1 file) | none | main→relation audit; CLEAN; Vercel green | directly supports Stage1; production facts added by this audit | **MERGE_CANDIDATE**. Integrate doc after reconciling production evidence |
| #14 | OrgNode/Role/HospitalProfile/Approval schema + doc (3 files) | `20261002090000_stage3_core_foundation` | main→core-foundation; UNSTABLE, one pending | Human Gate/Hospital aligns, but official sources missing and DB security blocker unresolved | **HOLD**. Isolated preview migration/rollback + authority review first |
| #15 | effective permission resolver/tests (3 files) | none, depends #14 models | #14→permission-resolver; CLEAN | individual allow/deny useful; must preserve all-active-BU read rule | **REBASE_REQUIRED** after #14 decision; tenant/BU regression tests |
| #16 | approval service/policies/SLA + enum migration (11 files) | `20261002110000_stage3_approval_operational_events` | #15→approval-service; CLEAN | Human Gate aligned; hardcoded people/SLA require official approval; duplicate UUID helper | **REBASE_REQUIRED** after #12/#14/#15; preview DB and stale-target tests |
| #17 | approval UI/API (9 files) | none directly; needs #14/#16 DB | #16→approval-ui; UNSTABLE; Vercel `crm` FAILURE | useful UI, but non-draft despite dependency and failing deployment | **REBASE_REQUIRED**; return to Draft recommended, fix CI, E2E permission tests |
| #18 | v1 token version guard (3 files) | none | main→calendar guard; CLEAN; both Vercel green | directly mitigates existing two v1 connections but cutover remains untested | **HOLD** and keep **Draft** exactly as requested; test on isolated clone, no enable/deploy |

## PR #13 evidence incorporated

PR #13 correctly separates physical FK from loose logical IDs. Production verification adds:

- `object_associations`: 5,838 rows; Deal→Company 2,105, Deal→Contact 2,104.
- Company/Contact/Deal core links are polymorphic; cleanup cannot rely only on FK cascade/restrict.
- High-priority loose IDs: MeetingBooking company/deal/businessUnit; DeliveryProject company/contact/sourceDeal/businessUnit; Deal origin; DealParticipant user; SalesPerformanceEvent sources.
- All current public tables have RLS off/full anon grants—a production fact outside #13’s code-only scope.

Therefore #13 is sound as a code inventory but should merge only with an addendum or cross-link to this production audit.

## Clinic Lead System vs #1–#11

Current `crestix-company/crestix-clinic-lead-system` main is `e543249` (2026-10-15). Its own current documentation shows:

- Production runtime has already cut READ/WRITE to Supabase project `hwdvyhunozporfuefteb` (`clinic-lead-shadow`).
- Current SoT uses `public.clinics`, `provenance.*`, `research.*`, `treatment.*`, `hp_research.*`, not PR #1–#11’s `clinic_master/clinic_ops` on CRM project `xtspgevvntpidkmyfwes`.
- `clinic_runtime` is least-privilege with RLS; anon/auth unintended writes 0; 162,258 clinics and 632,903 rows across 19 tables were reconciled.
- Stage5 code/runtime closure exists; Windows/two-PC external acceptance remains pending.

Thus applying #1–#11 would duplicate or fork the current Clinic Lead SoT and create conflicting schema/identity/migration paths. The safe AIOS relationship is an explicit connector/link from CRM to current Clinic Lead, not replaying the old chain.

## #14–#17 stack review

Order must remain #14 schema → #15 permissions → #16 service/migration → #17 UI. Do not squash the decision boundaries before review. Before any merge:

1. Obtain official 00–12 authority/SLA wording.
2. Rebase #14 on current main and apply migration only to isolated preview DB.
3. Validate schema rollback/recreate, partial unique constraints, RLS/Data API interaction.
4. Rebase #15 and prove BusinessUnitMembership is not a read ACL.
5. Merge/reuse #12 UUID helper, then rebase #16; verify idempotency, stale-target and audit.
6. Rebase #17, restore Draft status, fix failed Vercel check, run UI/API tenant E2E.

## Safe review / integration sequence

1. **#13**: review production addendum; docs-only merge candidate.
2. **#12**: run full repo validation; merge candidate if policy accepted.
3. **#1–#11**: owner confirms superseded status; archive useful docs externally, then separate close decision (not in this task).
4. **#18**: keep Draft; isolated v1/v2 test and dual-deployment ownership plan. Do not merge merely because Preview is green.
5. Resolve Stage1 P0 DB exposure and official source gaps.
6. **#14**, then **#15**, **#16**, **#17** in order, each rebased and independently gated.

No current PR should be batch-merged. No PR should execute production migrations as part of review.

## Exact changed-file inventory

2026-10-15に`gh pr diff --name-only`で再取得した。積み上げPRはbaseからheadまでの差分であり、前段PRから継承したファイルを含む。

| PR | Changed files |
|---:|---|
| #1 | `docs/clinic-db-architecture.md`; `docs/clinic-db-migration-plan.md`; `docs/clinic-db-sql-drafts/{001_create_clinic_master.sql,002_create_clinic_ops.sql,003_promotion_example.sql,004_current_hp_rank_view.sql,README.md}`; `docs/clinic-uuid-strategy.md`; `docs/clinic-uuid-tests/test_uuid7_strategy.py` |
| #2 | `docs/clinic-db-readonly-audit.md`; `docs/clinic-sqlite-to-postgres-mapping.md` |
| #3 | `docs/clinic-db-consumer-contract.md`; `docs/clinic-sqlite-to-postgres-mapping.md` |
| #4 | `docs/clinic-db-consumer-contract.md`; `docs/clinic-db-review-resolution.md`; `docs/clinic-sqlite-to-postgres-mapping.md` |
| #5 | `docs/clinic-db-{architecture,migration-plan,readonly-audit,schema-v1}.md`; `docs/clinic-db-sql-drafts/{001_create_clinic_master.sql,002_create_clinic_ops.sql,003_promotion_example.sql,004_current_hp_rank_view.sql,005_create_clinic_ops_extended.sql,006_create_current_views.sql,README.md}`; `docs/clinic-uuid-strategy.md` |
| #6 | `docs/clinic-db-migration-plan.md`; `docs/clinic-db-runtime-vocab-v1.md`; `docs/clinic-db-schema-v1.md`; `docs/clinic-db-sql-drafts/{002_create_clinic_ops.sql,005_create_clinic_ops_extended.sql,006_create_current_views.sql}` |
| #7 | `docs/clinic-db-schema-v1-validation.md`; `docs/clinic-db-sql-drafts/006_create_current_views.sql`; `scripts/validate-clinic-schema-v1.sh` |
| #8 | `docs/clinic-db-importer-dry-run-v1.{md,summary.json}`; `scripts/clinic_db_importer/{__init__,classify,comdesk_mapping,hp_mapping,jobs_report,maps_mapping,normalizer_bridge,reason_codes,report,run_dry_run,sqlite_reader,transform}.py`; `scripts/clinic_db_importer/tests/{__init__,conftest,test_classify,test_comdesk_mapping,test_hp_mapping,test_integration_determinism,test_maps_mapping,test_normalizer_bridge,test_reason_codes,test_report_safety,test_transform}.py` |
| #9 | `docs/clinic-db-migration-rehearsal-v1.md`; `scripts/clinic_db_importer/{apply_migration,pg_csv,transform,uuid7}.py`; `scripts/clinic_db_importer/tests/{test_pg_csv,test_transform}.py` |
| #10 | `docs/clinic-db-production-migration-runner-v1.md`; `scripts/clinic_db_importer/{comdesk_mapping,production_runner,sqlite_reader}.py`; `scripts/clinic_db_importer/tests/{test_comdesk_mapping,test_production_runner_guards,test_production_runner_integration}.py` |
| #11 | `docs/clinic-db-importer-dry-run-v1.{md,summary.json}`; `docs/clinic-db-{migration-plan,migration-rehearsal-v1,production-migration-runner-v1,runtime-vocab-v1,schema-v1-validation,schema-v1}.md`; `docs/clinic-db-sql-drafts/005_create_clinic_ops_extended.sql`; `scripts/clinic_db_importer/{jobs_report,production_runner}.py`; `scripts/clinic_db_importer/tests/{test_production_runner_guards,test_production_runner_integration}.py`; `scripts/validate-clinic-schema-v1.sh` |
| #12 | `AGENTS.md`; `docs/uuidv7-id-policy.md`; `src/lib/server/uuidv7.{test.ts,ts}` |
| #13 | `docs/crm-db-02-relation-audit.md` |
| #14 | `docs/stage3-core-foundation-schema.md`; `prisma/migrations/20261002090000_stage3_core_foundation/migration.sql`; `prisma/schema.prisma` |
| #15 | `src/lib/effective-permissions.ts`; `src/lib/permissions.test.ts`; `src/lib/permissions.ts` |
| #16 | `prisma/migrations/20261002110000_stage3_approval_operational_events/migration.sql`; `prisma/schema.prisma`; `src/lib/approvals/{notifications,policies,process-sla,service,sla.test,sla,types}.ts`; `src/lib/server/uuidv7.{test.ts,ts}` |
| #17 | `src/app/(app)/approvals/{page.tsx,[id]/page.tsx}`; `src/app/api/approvals/{route.ts,[id]/steps/[stepId]/[action]/route.ts}`; `src/components/approvals/approval-actions.tsx`; `src/components/layout/{app-header,sidebar}.tsx`; `src/lib/approvals/queries.ts`; `src/lib/server/uuidv7.ts` |
| #18 | `src/lib/google-calendar.ts`; `src/lib/security.test.ts`; `src/lib/security.ts` |

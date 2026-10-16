# Open PR Inventory and Merge Plan (#1–#18)

## Snapshot and safety

- Observed: 2026-10-16, GitHub read-only (`gh pr list/view/diff`).
- PR #1–#18 are OPEN; no merge/close/rebase/PR branch update performed. PR #19 is this audit PR and is outside the 18-PR inventory.
- GitHub currently reports all 18 as `MERGEABLE`. This only reports the observed Git mergeability; it does not validate an unmerged parent PR or the compatibility of a stacked branch after rebasing.
- Visible checks: #1–#13 and #15–#16 show Vercel Preview/deployment success; #14 has one Vercel check PENDING and `Vercel – crm` SUCCESS; #17 `Vercel – crm` FAILURE; #18 has both Vercel deployments SUCCESS. These checks are not a full typecheck/lint/unit/build suite; PR #18 explicitly says its code checks have not yet run.
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

| PR / Priority | Purpose and files changed | Schema / Migration | Current base → head; GitHub state / checks | Formal requirements and operational impact | Classification; evidence; next action |
|---|---|---|---|---|---|
| #1 / P2 | Clinic coexistence design, SQL drafts, UUID test (9 files; +1,263) | Draft `clinic_master` / `clinic_ops` SQL; no Prisma migration | `main` → `docs/clinic-db-design`; MERGEABLE; Vercel PASS | Clinic-first direction is relevant, but formal docs set CRM as final clinic/company/contact SOT; proposal puts a second master in the CRM Supabase project | **SUPERSEDED** — current Clinic Lead system uses a separate project/schema. Retain only relevant design history; owner approval required before any closure |
| #2 / P2 | Read-only SQLite audit and mapping (2 docs; +310) | None | #1 branch → `feature/clinic-db-readonly-mapping`; MERGEABLE; Vercel PASS | Historical 2026-09 source snapshot, not the current production CRM relation inventory | **SUPERSEDED** — preserve only source facts still useful to an approved connector/migration ADR |
| #3 / P2 | Consumer contract and mapping corrections (2 files; +189/−38) | None | #2 branch → `feature/clinic-db-consumer-contract`; MERGEABLE; Vercel PASS | Source-specific URL, Maps, research and Comdesk concepts may inform a connector boundary; does not satisfy CRM-final-SOT requirement | **SUPERSEDED** — salvage useful contracts into Stage2 design, do not integrate this branch |
| #4 / P2 | Review resolutions and append-only provenance (3 files; +242/−13) | None | #3 branch → `feature/clinic-db-review-resolution`; MERGEABLE; Vercel PASS | Append-only history aligns with audit needs, but implementation belongs in the current Clinic Lead source or an approved CRM link design | **SUPERSEDED** — archive useful decisions; no branch integration |
| #5 / P2 | Consolidated Clinic Schema v1 design and SQL (12 files; +713/−94) | Draft schemas/views/RLS SQL; no Prisma migration | #4 branch → `feature/clinic-db-schema-v1`; MERGEABLE; Vercel PASS | Draft excludes anon/auth grants, but physical design targets the superseded second-master direction | **SUPERSEDED** — do not apply the SQL drafts |
| #6 / P2 | Runtime vocabulary corrections (6 files; +294/−27) | Draft SQL amendments only | #5 branch → `feature/clinic-db-runtime-contract-v1`; MERGEABLE; Vercel PASS | Useful historical vocabulary; current production Clinic Lead code is the authority for source behavior | **SUPERSEDED** — keep only as historical reference |
| #7 / P2 | PostgreSQL 17 scratch schema validation (3 files; +470/−1) | Validation script applies the draft schema to localhost only when invoked | #6 branch → `feature/clinic-db-schema-validation-v1`; MERGEABLE; Vercel PASS | Local validation method may be reused after an approved target design; it does not validate the current CRM schema | **SUPERSEDED** — reuse test ideas only; do not run against production |
| #8 / P2 | Write-zero SQLite importer and 58 tests (25 files; +1,919) | No DB migration; reads source SQLite | #7 branch → `feature/clinic-db-importer-dry-run-v1`; MERGEABLE; Vercel PASS | Dry-run-first aligns with formal rules; importing the already-cut-over dataset into CRM would duplicate clinics and history | **SUPERSEDED** — do not run against the CRM database; only reconsider for an approved reconciliation/cutover plan |
| #9 / P2 | Scratch PostgreSQL migration rehearsal (7 files; +1,027/−1) | Scratch loader/apply code; no CRM Prisma migration | #8 branch → `feature/clinic-db-migration-rehearsal-v1`; MERGEABLE; Vercel PASS | Evidence is tied to the former target schema and includes documented resource limits | **SUPERSEDED** — no production execution; retain only as historical rehearsal evidence |
| #10 / P0 risk; P2 review | Resumable production migration runner (7 files; +1,441/−5) | No Prisma migration file; runner can write its target when explicitly invoked | #9 branch → `feature/clinic-db-production-migration-runner-v1`; MERGEABLE; Vercel PASS | Highest accidental-write risk in #1–#11; target/schema differs from the current Clinic Lead production project | **SUPERSEDED** — do not invoke against CRM/Supabase; retain runner only if a separately approved future migration is needed |
| #11 / P2 | CANCELLED job contract/schema draft (14 files; +132/−14) | Draft CHECK/schema SQL amendments; no Prisma migration | #10 branch → `feature/clinic-db-cancelled-contract-v1`; MERGEABLE; Vercel PASS | Historical job contract; current Clinic Lead implementation advanced beyond this proposal | **SUPERSEDED** — archive useful contract notes; owner approval required before closure |
| #12 / P1 | UUIDv7 helper, policy, test and AGENTS rule (4 files; +154) | None | `main` → `chore/uuidv7-id-policy`; MERGEABLE; Vercel PASS | Compatible as a new-ID policy if existing IDs and external ID mappings remain unchanged; helper duplicates a copy in #16 | **MERGE_CANDIDATE** — run the full repository suite on this head and decide helper ownership before #16 is rebased |
| #13 / P0 audit evidence | CRM Relation/FK audit (1 doc; +358) | None | `main` → `docs/crm-db-02-relation-audit`; MERGEABLE; Vercel PASS | Directly supports Stage1 DB inventory; its own scope is code/schema based and explicitly says production was not queried | **MERGE_CANDIDATE** — review the document and cross-link this Stage1 production addendum; do not represent its source audit as production evidence |
| #14 / P0 blocker; P1 review | OrgNode, RoleDefinition, HospitalProfile, approval schema and design (3 files; +668/−5) | `20261002090000_stage3_core_foundation` | `main` → `feat/stage3-core-foundation-schema`; MERGEABLE; one Vercel check PENDING, `crm` PASS | New hierarchy, permissions, clinic profile and approval entities align in direction. Hard-coded org/approval assumptions need owner review; migration leaves current RLS/grants unchanged while P0 security remains open | **HOLD** — no merge until business authority and least-privilege design are approved and migration rollback/CRM smoke tests pass on isolated preview DB |
| #15 / P1 | Effective permission resolver and tests (3 files; +258/−2) | None; depends on #14 schema | #14 branch → `feat/stage3-permission-resolver`; MERGEABLE; Vercel PASS | Role + org-node + individual override is directionally aligned; must not use `BusinessUnitMembership` as read ACL and must preserve tenant context from `getAuthContext()` | **REBASE_REQUIRED** — rebase after #14 decision; add/test allow-deny, cross-tenant, and all-active-BU visibility cases |
| #16 / P1 | Approval policy/service/SLA/notifications and tests (11 files; +1,024) | `20261002110000_stage3_approval_operational_events` (enum/schema migration) | #15 branch → `feat/stage3-approval-service`; MERGEABLE; Vercel PASS | Human Gate mechanism aligns. Named approvers, SLA values and role behavior are business decisions/configuration, not safe AI defaults; UUID helper duplicates #12 | **REBASE_REQUIRED** — after #12/#14/#15 decisions, replace unapproved fixed authority with approved configurable policy; validate idempotency, stale target, audit and isolated migration |
| #17 / P1 | Approval inbox/detail/API and navigation (9 files; +470/−4) | No migration in this PR; requires #14/#16 models | #16 branch → `feat/stage3-approval-ui`; MERGEABLE; `crm` FAILURE; PR is not Draft | Approval UI is useful after authority is approved; page/API access needs tenant/role/step-level tests | **REBASE_REQUIRED** — return to Draft, fix failed deployment check, rebase after #14–#16, and pass UI/API permission E2E |
| #18 / P0 operational protection | Google Calendar token-version guard and tests (3 files; +85) | None | `main` → `fix/google-calendar-legacy-token-guard`; MERGEABLE; both Vercel projects PASS; Draft | Protects two existing v1 connections against v2-key operations; no OAuth cutover, real v1 DB exercise or full code suite yet | **HOLD; KEEP DRAFT** — preserve the old connection; run unit/full-suite and isolated v1/v2 regression review, then approve a separate cutover plan |

“Priority” is review sequencing, not permission to merge. P0 entries are immediate safety/evidence gates; P1 are Stage2 foundations; P2 are cleanup/history candidates.

## PR #13 evidence incorporated

PR #13 correctly separates physical FK from loose logical IDs. Independent read-only production verification adds:

- The catalog inventory found 106 physical foreign-key constraints; 0 were `NOT VALID`.
- 23 sampled high-priority loose-reference integrity checks returned 0 orphan rows. These point-in-time checks do not prove every logical reference is constrained or immutable.
- `object_associations`: 5,838 rows; Deal→Company 2,105, Deal→Contact 2,104.
- Company/Contact/Deal core links are polymorphic; cleanup cannot rely only on FK cascade/restrict.
- High-priority loose IDs: MeetingBooking company/deal/businessUnit; DeliveryProject company/contact/sourceDeal/businessUnit; Deal origin; DealParticipant user; SalesPerformanceEvent sources.
- Production security inventory separately observed public-schema tables with RLS disabled and broad anon grants. Treat this as a P0 exposure requiring authenticated-access validation and owner-approved remediation; this finding is outside #13’s code-only scope. No privilege/policy change was made.

Therefore #13 is sound as a code inventory but should merge only with an addendum or cross-link to this production audit.

## Clinic Lead System vs #1–#11

Current `crestix-company/crestix-clinic-lead-system` main is `e543249` (2026-10-15). Its own current documentation shows:

- Production runtime has already cut READ/WRITE to Supabase project `hwdvyhunozporfuefteb` (`clinic-lead-shadow`).
- Current SoT uses `public.clinics`, `provenance.*`, `research.*`, `treatment.*`, `hp_research.*`, not PR #1–#11’s `clinic_master/clinic_ops` on CRM project `xtspgevvntpidkmyfwes`.
- `clinic_runtime` is least-privilege with RLS; anon/auth unintended writes 0; 162,258 clinics and 632,903 rows across 19 tables were reconciled.
- Stage5 code/runtime closure exists; Windows/two-PC external acceptance remains pending.

Thus applying #1–#11 would duplicate or fork the current Clinic Lead implementation and create conflicting schema/identity/migration paths. The safe transitional relationship is an explicit connector/link, not replaying the old chain. However, official_01/02 define clinic/company/contact data as CRM SOT: Clinic Lead cannot remain an indefinite second SOT. Stage2 must approve field authority, ID/provenance mapping, reconciliation, cutover and rollback before any write path.

## #14–#17 stack review

Order must remain #14 schema → #15 permissions → #16 service/migration → #17 UI. Do not squash the decision boundaries before review. Before any merge:

1. Use official 00–12 authority/Human Gate/master化 wording now recorded in this audit.
2. Rebase #14 on current main and apply migration only to isolated preview DB.
3. Validate schema rollback/recreate, partial unique constraints, RLS/Data API interaction.
4. Rebase #15 and prove BusinessUnitMembership is not a read ACL.
5. Reuse #12 UUID helper only as an internal technical choice, then rebase #16; verify idempotency, stale-target, audit and configurable approvers/SLA.
6. Rebase #17, restore Draft status, fix failed Vercel check, run UI/API tenant E2E.

## Safe review / integration sequence

1. **#13**: review production addendum; docs-only merge candidate.
2. **#12**: run full repo validation; merge candidate if policy accepted.
3. **#1–#11**: owner confirms superseded status; archive useful docs externally, then separate close decision (not in this task).
4. **#18**: keep Draft; isolated v1/v2 test and dual-deployment ownership plan. Do not merge merely because Preview is green.
5. Resolve Stage1 P0 DB exposure, Clinic Lead→CRM authority and unanswered information-classification/retention decisions.
6. **#14**, then **#15**, **#16**, **#17** in order, each rebased and independently gated.

No current PR should be batch-merged. No PR should execute production migrations as part of review.

## Exact changed-file inventory

2026-10-16に`gh pr diff --name-only`で再取得した。積み上げPRはbaseからheadまでの差分であり、前段PRから継承したファイルを含む。

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

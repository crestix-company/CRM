# P0 Security Verification — Execution Readiness and Results

## Status

**First isolated local execution unit completed on 2026-10-16; Production and hosted services untouched.** The approved local PostgreSQL bootstrap, all 21 repository migrations, synthetic fixture insertion, local CRM API checks, and local regression/build checks are recorded in [19_p0_security_local_execution_report.md](19_p0_security_local_execution_report.md). No Production database/Vercel/Calendar operation, hosted Supabase project operation, Production migration, deployment, or PR #1–#18 operation was performed. PR #19 remains OPEN/Draft; only this docs-only result is proposed for it.

This runbook refines [the Preview test design](17_preview_rls_grant_data_api_test_design.md) using CRM source code as inspected on branch `audit/aios-stage1-db-inventory`. Source inspection is not a live validation of Production Vercel configuration, Supabase API settings, runtime roles, or external consumers.

## 1. Source-verified authentication, database, API, tenant boundary

| Area | Confirmed from source | Implication / limitation |
|---|---|---|
| Application authentication | [src/lib/auth.ts](../../../src/lib/auth.ts) issues an opaque token in an HttpOnly, SameSite=Lax cookie (Secure in production); DB stores `hashToken(token)` in `auth_sessions`. `getAuthContext()` looks up the session, expiry, user, active organization and ACTIVE `organization_members` membership. This is a custom CRM session, not Supabase Auth. | Supabase `auth.uid()`/JWT claims do not represent CRM users and cannot be assumed to work for app RLS. Cookie never goes straight to Postgres. |
| Prisma DB connection | [src/lib/prisma.ts](../../../src/lib/prisma.ts) creates a singleton `PrismaClient` from `DATABASE_URL`; when hostname contains `pooler.supabase.com`, it adds `pgbouncer=true`. [prisma/schema.prisma](../../../prisma/schema.prisma) is PostgreSQL and reads `DATABASE_URL`. | Actual runtime DB username/role, BYPASSRLS, ownership, pool mode, Vercel environment value and TLS settings are **UNVERIFIED**. `.env.example` uses only a local `postgres:postgres` example and is not evidence about production. |
| Supabase Data API | Source/dependency search found no `@supabase/supabase-js`, `@supabase/ssr`, REST `/rest/v1`, GraphQL `/graphql/v1`, Supabase client initialization, or direct Data API HTTP call in the inspected app source/dependencies. CRM persistence observed in code is Prisma direct Postgres. | No in-repo Data API consumer found. This does **not** establish that Data API is disabled or unused by external scripts, dashboards, integrations, or other deployed code. Supabase API settings and external consumer inventory remain required before disabling it or revoking grants. |
| Tenant identity | `getAuthContext()` derives `organization.id` from stored `AuthSession.activeOrganizationId`; membership status must be ACTIVE. Example [companies route](../../../src/app/api/companies/route.ts) scopes select/count/create to `context.organization.id` and ignores client organization ID on create. [deals route](../../../src/app/api/deals/route.ts) similarly scopes tenant and verifies linked objects/stage/unit. | Source shows application-layer tenant predicates; this is not DB RLS enforcement, and this sample is not a proof that every route is safe. Automated cross-tenant tests/source audit across all APIs remain needed. |
| Business Unit visibility | [src/lib/business-units.ts](../../../src/lib/business-units.ts) loads every ACTIVE BusinessUnit under `context.organization.id`; a selected unit is a view/filter setting. | RLS must not reduce same-organization reads to BusinessUnitMembership. Tests need active-BU-wide visibility, separately from optional UI filtering. |
| Public/server consumers | Public scheduling, form, appointment-capture and Google-Form routes resolve capability links/tokens then use Prisma; Google Calendar webhook validates channel/resource/token and resolves its connection; cron uses `CRON_SECRET` and scans reminders across organizations. | These are not necessarily Supabase Data API callers, but do issue Prisma queries. Under DB RLS they need narrowly scoped capability/tenant context or a separately constrained worker path. Blanket RLS will break them until designed/tested. |
| Existing DB policy | Stage1 READ ONLY production catalog evidence recorded in [05_security_grants_rls.md](05_security_grants_rls.md): 80/80 public base tables have RLS off, policies 0, and anon/authenticated broad grants. | Findings are point-in-time catalog observations, not a live external access proof. Table/object-level privileges and exposed schema settings must be rechecked under authorized read-only access before any change. |

### Critical architecture conclusion

There are two separate boundaries:

1. **Supabase Data API** (`anon` / `authenticated` PostgreSQL roles): source search found no CRM runtime caller. If an authorized inventory confirms no external consumer, disabling Data API or removing those roles' grants from CRM data is the lowest-coupling containment candidate; validate all routes/integrations first.
2. **CRM application → Prisma → Postgres direct connection**: CRM authenticates with its own session cookie and currently has no shared RLS session context. Merely enabling RLS on 80 tables can turn reads into empty sets or writes into policy errors; if the URL role is owner/BYPASSRLS, RLS may not constrain the app at all. A tested design needs a restricted non-owner runtime role and a safe, transaction-scoped context bridge from `getAuthContext()` to every tenant-scoped Prisma operation. The present singleton/client and scattered direct Prisma calls do not prove such a bridge exists.

Do not write `auth.uid()` policies against CRM tables until CRM identity is deliberately integrated with Supabase Auth, which would be a separate design decision. A custom `current_setting('app.organization_id')` policy is only a defense-in-depth pattern if a trusted app transaction sets it; a freely-settable custom GUC is not itself authentication and must not be described as protection against an attacker with DB credentials or arbitrary SQL execution.

## 2. Independent non-production environment — proposed, not created

### Recommended target

First choice: a **local disposable Supabase stack + local Next.js app** on the developer machine, entirely disconnected from Production, with no Google OAuth credentials and synthetic-only records. This permits testing PostgREST roles and CRM's actual cookie/Prisma routes without creating a hosted Supabase project or touching Vercel.

If local PostgREST/Data API parity or pooling role behavior cannot reproduce the relevant managed-project settings, a second option is a new isolated Supabase project in an organization selected and funded by the human owner. No existing production-linked project or Supabase production branch. Project creation, billing, credentials, and any schema migration are explicit approvals required before execution.

### Execution guardrails (used for first unit; retained for follow-up)

1. Confirm Docker/CLI availability and choose a disposable local target. Use a **separate worktree/temp directory** for Supabase CLI files so generated config, local secrets, fixtures, and test output cannot accidentally enter PR #19. Do not run `supabase init` in the audit repository without approval.
2. Pin/report relevant database/API versions. The 21 repository migrations below were applied only to the empty temporary loopback DB. This is not permission to apply them to any other target. Do not use `supabase db pull`/branch/rebase against Production.
3. After approval, apply these migrations to the **empty local DB only**, then separately insert only synthetic fixtures. Do not run application `prisma/seed.ts`; it may create default business data beyond these fixtures.
4. Set local-only `DATABASE_URL`, cookie/security placeholder secrets and disabled external feature flags. Ensure no production hostnames/projects/credentials resolve from the environment. Use fake mail/calendar adapters or disable those outbound integrations.
5. Start the local CRM app against local DB. Validate login/cookie flows using synthetic users. Exercise local Data API REST only if local Supabase stack is enabled and configured with synthetic keys.
6. Save sanitized test output outside versioned paths; tear down disposable volumes only after evidence export and reviewer approval. Do not place `.env`, JWT, API keys, database dumps, or test cookies in Git.

The owner approved the first local execution unit. A native PostgreSQL 17.11 cluster was created in a unique `/private/tmp` directory and bound only to `127.0.0.1`; all 21 migrations and synthetic fixtures ran there. No hosted Supabase environment was started. PostgREST/Data API parity and any RLS/GRANT mutation remain outside that approval and require a separate exact-target approval.

### Repository migration order and data effects

All `prisma/migrations/*/migration.sql` in the following exact order (21 files):

1. `20260612000000_init`
2. `20260613000000_phase4`
3. `20260618000000_remove_external_email_accounts`
4. `20260619043656_business_units`
5. `20260619065918_phase2_kpi_foundation`
6. `20260622024137_phase3b_sales_foundation`
7. `20260622025927_phase3b_price_fees`
8. `20260622042427_phase3c_delivery_projects`
9. `20260622055100_phase3d_forms_scheduling_google`
10. `20260622060000_phase3d_booking_overlap_constraint`
11. `20260622062548_phase3e_google_calendar_hardening`
12. `20260622062600_phase3e_unique_idempotency_indexes`
13. `20260623010000_phase3f_appointments_activity_analysis`
14. `20260623020000_meeting_booking_idempotency_unique`
15. `20260623030000_daily_metric_field_configs`
16. `20260623040000_appointment_capture_links`
17. `20260623050000_task_reminders_notifications`
18. `20260623060000_delivery_project_company_backfill`
19. `20260625043000_backfill_deal_stage_required_fields`
20. `20260729010000_deal_line_item_workflow`
21. `20260729010100_deal_line_item_workflow_fields`

Static scan found data-manipulating statements in three migration files: #15 inserts `daily_metric_field_configs` by selecting existing `metric_definitions`/active `business_units`; #18 backfills `delivery_projects.company_id` and `scope_snapshot`; #19 updates `pipeline_stages.required_fields`. On an empty schema these backfill sources should be empty before synthetic fixture insertion, but this expectation must be checked after each migration on the disposable target. If any migration unexpectedly changes a row or accesses external/Production resources, stop. The remaining files still perform DDL/constraints/indexes; this is not a claim that migrations are harmless.

## 3. Synthetic test data (proposed only)

All fixed values below are test-only examples. No production IDs/user rows are copied.

| Fixture | Example ID | Minimum relations / purpose |
|---|---|---|
| Organization A / B | `00000000-0000-4000-8000-0000000000a1` / `00000000-0000-4000-8000-0000000000b1` | Cross-tenant isolation pair |
| Users A / B / suspended-A | `00000000-0000-4000-8000-000000000101` / `00000000-0000-4000-8000-000000000201` / `00000000-0000-4000-8000-000000000102` | ACTIVE members in A/B; suspended member in A |
| BusinessUnit A-1 / A-2 / B-1 | `00000000-0000-4000-8000-00000000a111` / `00000000-0000-4000-8000-00000000a112` / `00000000-0000-4000-8000-00000000b111` | Both A units ACTIVE; create A user with no BusinessUnitMembership and test both visible |
| Companies A / B | `00000000-0000-4000-8000-000000000c01` / `00000000-0000-4000-8000-000000000c02` | Synthetic harmless names; no domain/phone/email needed |
| Contacts A / B | `00000000-0000-4000-8000-000000000d01` / `00000000-0000-4000-8000-000000000d02` | Fake names/addresses only; test association tenant validation |
| Deals A / B + LineItems | `00000000-0000-4000-8000-000000000e01` / `00000000-0000-4000-8000-000000000e02` | Test owner, unit, company and LineItem relations; values are synthetic and tiny |
| Session rows | generated random token hashes only | A active/suspended/expired; raw synthetic cookie emitted only to local test process, never stored in artifacts |
| Public capability | generated local-only MeetingLink/form/capture link with random token hash | Valid, revoked, expired, wrong-tenant and replay cases |
| Calendar | no real connection; optional fake credential placeholder | Test legacy guard/status rendering without OAuth, Google API call or actual v1 connection |

Required invariants: all fixture foreign keys point to fixture tenant; any intentionally cross-tenant ID is a negative-test input only, not persisted. Use deterministic seeded IDs solely within disposable local DB. No credentials from `.env.example` are reused beyond local defaults; replace with test-only random values.

## 4. Proposed GRANT / RLS change sets (non-executable design)

Exact object grants, role ownership and every relation policy are not yet inventoried for a new runtime role. The SQL below is **illustrative only**; it is not a ready migration and must not be pasted into Production or an existing preview database.

### Set A — minimize Data API surface (only after external consumer review)

- Prefer disable Data API for the CRM Supabase project if the owner confirms there are no external PostgREST/GraphQL/supabase-js consumers. Test on local stack first.
- Otherwise revoke `anon`/`authenticated` access from unapproved schemas/objects. Keep only explicit Data API object allowlist; don't grant generic CRUD on CRM base tables. Revoke schema USAGE/function EXECUTE/sequence privileges where not required, including inherited `PUBLIC` access where verified.
- Inspect and correct default privileges for the actual object-creating owner roles so new objects are private by default. Changing defaults does not revoke grants already on existing objects.
- Do not revoke privileges from the actual Prisma/service runtime role until its identity and operation needs are proven. Do not assume `service_role` is or is not used just because repo source lacks Supabase SDK.

Candidate role/object outcome (all entries conditional on consumer/runtime inventory):

| Role / path | Current recorded state | Candidate outcome |
|---|---|---|
| `anon` Data API | Broad table privileges observed; Data API exposure setting unknown | No access to CRM base tables/views/sequences/functions. Any public form/scheduler continues via scoped Next.js server route, not direct table grants |
| `authenticated` Data API | Broad table privileges observed; Supabase Auth not used by CRM | No access to CRM base tables/views unless an external API consumer is identified and gets a deliberately narrow schema/object allowlist |
| `service_role` Data API | In-repo Supabase client not found; external usage unknown | Keep secret server-only; remove Data API/object privileges only if external consumers are ruled out. Never expose key in browser |
| Prisma DB role | `DATABASE_URL` role unknown; direct Prisma access confirmed | Dedicated `crm_runtime`-class non-owner/non-BYPASSRLS role with enumerated CRUD. Existing production role changes wait for separate approval |

Illustrative SQL shapes for review only (not a migration; do not execute):

```sql
-- Data API deny-by-default candidate, only after no external consumers are confirmed.
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM anon, authenticated;
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM anon, authenticated;
-- Review schema USAGE, PUBLIC inheritance, functions, service_role, and default ACLs separately.

-- Example policy shape for a direct-organization table after trusted context is implemented.
ALTER TABLE public.companies ENABLE ROW LEVEL SECURITY;
CREATE POLICY companies_crm_runtime_tenant
  ON public.companies
  FOR ALL TO crm_runtime
  USING (organization_id = NULLIF(current_setting('app.organization_id', true), '')::uuid)
  WITH CHECK (organization_id = NULLIF(current_setting('app.organization_id', true), '')::uuid);

-- Set transaction-local context only from a verified server-side AuthContext,
-- inside the SAME transaction as every protected query:
SELECT set_config('app.organization_id', $1, true);
```

These snippets intentionally do not cover all 80 tables, role inheritance, session bootstrap, child/polymorphic relations, sequences, functions or worker/capability paths. A blank/malformed setting, transaction pool reuse, SQL injection, or using an owner/BYPASSRLS role can invalidate the intended protection. Do not create `crm_runtime`, alter privileges, enable RLS or create policies until a disposable target and application transaction wrapper are approved and tested.

### Set B — RLS for direct Prisma runtime (requires application redesign)

- Create a dedicated runtime database role that is not superuser, not table owner, and lacks `BYPASSRLS`; grant only needed schema usage/object operations. Keep migrations on a separate owner role and secrets server-side.
- Partition tables: (1) direct `organization_id` tables; (2) child tables whose parent enforces tenant; (3) polymorphic `object_associations`/loose UUID links; (4) auth/session/capability secrets; (5) global enums/config/reference; (6) background job/system-event tables. Do not blanket-generate policy for every Prisma model.
- For direct tenant tables, a possible policy predicate is `organization_id = <trusted transaction-local organization context>`, with matching `WITH CHECK` on insert/update. Resolve organization context from the verified CRM session server-side. This is an architecture pattern, not executable policy until context propagation and role semantics are proven.
- For child/polymorphic tables, enforce parent tenant membership using a validated relation path and check both old/new target on updates. `object_associations` must validate source and target objects belong to same org; polymorphic IDs do not get FK protection automatically.
- For `auth_sessions` and login bootstrap, design minimal session verification access separately so tenant RLS does not block `getAuthContext()` before context is established. Public capability routes, webhook and cron need distinct restricted flows; never solve with unrestricted `BYPASSRLS` app credentials.
- Views require explicit review for owner/security-invoker behavior; functions, sequences, `SECURITY DEFINER`, default ACL, and triggers are separate access surfaces. Policies do not grant privileges, and grants do not filter rows.
- Default deny, no blanket `TO authenticated USING(true)`. No `BusinessUnitMembership` read ACL. Do not force RLS on table owners until migration/bootstrap operations are tested.

### Migration packaging and reversibility

If later approved, create a new migration through the repo's normal migration workflow, after a disposable-DB prototype and review. Bundle schema RLS, policies, and explicit grants coherently. A simple `DISABLE ROW LEVEL SECURITY` is not an adequate rollback if grants were also revoked; record exact before-ACL/default-ACL/policy inventory and prepare an explicit compensating migration or recreate the disposable DB. No migration file is created in this preparation step.

## 5. Positive and tenant-boundary test cases

| ID | Request / caller | Expected result |
|---|---|---|
| CRM-AUTH-01 | No cookie to protected CRM API/page | 401/redirect; no DB mutation |
| CRM-AUTH-02 | Valid synthetic A cookie; expired cookie; suspended A member | A permitted; expired/suspended denied; session/hash values absent from logs |
| CRM-TENANT-01 | A list Companies/Contacts/Deals/Tasks/Calendar status; B has matching records | A sees A only; list totals, exports, reports and search totals don't disclose B |
| CRM-TENANT-02 | A requests B UUID directly in detail/update/delete/API relation field | consistent 404/403; B unchanged; no side-effect/audit leakage |
| CRM-TENANT-03 | A creates record while body supplies B `organizationId` | created row uses verified context A or request rejected; never B |
| CRM-TENANT-04 | A changes existing A record `organizationId` to B; attaches B Company/Contact/Deal/LineItem | denied/validation fails; source row and all dependents unchanged |
| CRM-BU-01 | A active org member with no BU memberships selects/view A-1 and A-2 | both active units visible; optional selected-BU filter works only as view scope, not authorization |
| CRM-BU-02 | A supplies B's BU UUID on new Deal/Booking | rejected because BU must belong to A and be active |
| CRM-REL-01 | Polymorphic association source in A + target in B | reject; cannot create or enumerate cross-tenant edge |
| CRM-PRIV-01 | READ_ONLY role runs CRUD/approve/delete/export tests | app permission behavior unchanged; DB role does not bypass it |
| PUBLIC-01 | Valid synthetic public MeetingLink/form/capture token | only scoped booking/submission created in link's organization; no arbitrary org ID accepted |
| PUBLIC-02 | invalid/revoked/expired/wrong-tenant token, duplicate submission/replay | denied or idempotent according to existing contract; no cross-tenant read/write |
| PUBLIC-03 | signup/invitation accept | existing intentional public flow works; invitation applies only to invitation org; signup's new org belongs only to new user |
| WORKER-01 | valid/invalid CRON_SECRET | valid reminders process only scheduled eligible rows; invalid denied; no cross-org leakage in output |
| WORKER-02 | valid/invalid Google channel token/resource/message number | valid webhook limited to resolved connection org; invalid/replay does not trigger unauthorized sync |
| CAL-01 | Synthetic/fake Calendar provider with no real Google credential | old v1 guard/status and disabled path behave as before; no external API call/OAuth mutation |
| DATAAPI-01 | Local PostgREST anon key requests for sensitive tables/views/functions | no table schema/data/read/write; expected permission denial; test actual HTTP, not only SQL `SET ROLE` |
| DATAAPI-02 | Synthetic Supabase Auth `authenticated` JWT (if external API consumer confirmed) | only explicitly approved API surface; do not confuse this identity with CRM custom cookie |
| REG-01 | Company/Deal CRUD, LineItem revenue/gross profit reports, appointments, exports, imports dry-run, audit, reminders, public scheduling | existing flows pass; no real import apply or external integration writes |

Test verification must include DB before/after canary counts, transaction rollback or disposable DB recreation, expected response status, authorization source, and logs scan for PII/secrets. Use integration tests plus actual local REST/PostgREST requests; unit policy tests alone are insufficient.

## 6. Existing CRM impact review before any change

Potential breakage areas requiring explicit tests:

- **Session bootstrap**: `getAuthContext()` reads `auth_sessions`, `users`, and `organization_members` before many request handlers issue scoped queries. RLS could block login/context creation unless a minimal safe bootstrap access design exists.
- **Every normal CRUD/report/API route**: many handlers pass `context.organization.id` into Prisma filters/data; source code uses per-route queries rather than a central DB tenant wrapper. A query omission is precisely where RLS could add defense, but policy integration may require converting the operations to scoped transactions.
- **Direct object relations**: nested Prisma reads, FKs, and polymorphic links need same-tenant validation; query filtering only the parent does not guarantee all included/child rows are safe if policies are incomplete.
- **Business Unit semantics**: same-organization active BU visibility must continue; selected BU can narrow a screen but cannot become a read ACL. Assignment writes still validate that the BU belongs to the caller organization.
- **Public-by-capability routes**: public meeting-link availability/hold/book, public forms, appointment capture, Google Form token, invitation, registration. They lack normal cookie auth by design and derive scope from opaque slug/hash token/invitation. They need endpoint-specific RLS context, not `anon` table privileges.
- **Webhook and cron**: Calendar webhook validates provider capability then queries connection/selection and writes events; cron uses a secret and processes multiple organizations. Need least-privilege, auditable worker role or verified per-tenant iteration.
- **Google Calendar legacy connection**: no real OAuth/Google calls in test. Use fakes/disabled feature flags and synthetic connection rows. Preserve #18 protection and do not touch connected prod tokens.
- **Imports and background processing**: no legacy import apply in tests. Exercise dry-run and authorization only. Multi-tenant queue/cron queries can be unintentionally hidden under RLS.
- **Build/release**: local typecheck/lint/test/build only after any authorized isolated implementation; CI/Vercel preview environment must be isolated from Production variables. A GitHub PR update may trigger Preview automation, but no production deployment is permitted.

## 7. Rollback plan (isolated target first)

1. Before experiment, record schema/migration SHA, exact role membership, object ACL/default ACL, policies, view/function ACL, and synthetic baseline row counts. Store only in restricted run output.
2. Preferred rollback is **drop/recreate disposable local DB or container volume**, then replay reviewed baseline migrations and synthetic fixtures. Verify app tests pass before applying candidate again.
3. If testing on a hosted disposable project after separate approval, use its verified point-in-time/backup mechanism and a tested restore procedure; do not assume Production PITR or backup is available. Project must be dedicated and contain no production data.
4. For transactional policy/grant prototype, use a transaction and `ROLLBACK` only if every operation is transactional and tests prove no side effects. External API calls/sequence increments can be non-transactional; keep integrations mocked.
5. A future production release requires a separately authored compensating migration restoring exact prior ACL/default ACL and policy state, or an approved forward-fix. Do not rely on blanket re-grant. Include staged app rollback because new policies and runtime-role/application release are coupled.
6. On any mismatch, permission regression, changed business row, unexpected outbound call, or restore failure: stop, preserve diagnostics without secrets, discard local environment, and do not promote the change.

## 8. Required access and approvals

| Needed | Minimum access / purpose | Why currently unverified |
|---|---|---|
| Repository | Read access to CRM repo and migrations; already available locally | Source review done for this branch |
| Production Supabase metadata | Dashboard/API settings read-only; PostgreSQL read-only connection for `current_user`, role attributes/membership, object owner, schema exposure, grants/default ACL/RLS/views/functions; no row data needed | Production runtime role and API settings not exposed by repo |
| External consumer inventory | Owners of any scripts, Metabase/BI, integrations, admin tooling, direct REST/GraphQL usage; read-only telemetry/access logs if authorized | Repo search cannot detect clients outside repository |
| Non-production environment | Approval to create local disposable Docker/Supabase stack (recommended) or selected new hosted test project; separate nonprod-only keys | Environment creation has not been approved/executed |
| Migration/seed approval | Explicit approval for exact reviewed CRM schema migration list and synthetic fixture seed to the named nonprod target only | Environment/bootstrap will apply migrations and insert test fixture data |
| Vercel | No Production access needed for first local test. Later, Preview project/env read-only inspection and a guarantee Preview doesn't inherit Production credentials | No Vercel call/setting check in this task |
| Business/security approval | Owner to accept test boundary, public endpoint behavior, exception list, and residual risk | Policies alter runtime assumptions and public flows |

Do not send a Production `DATABASE_URL`, service role key, Supabase secret key, token, or raw data into chat, Git, PR, shell history or test logs. Provide a secret-manager-backed read-only access path or have an authorized human run catalog-only SQL and share sanitized outputs.

## 9. Execution readiness and next human approval

**Completed for the approved local scope**: schema bootstrap and synthetic fixtures on a proven loopback-only temporary DB; custom CRM cookie and tenant-boundary smoke checks; unit tests, typecheck, lint, and build. Detailed results are in [19_p0_security_local_execution_report.md](19_p0_security_local_execution_report.md).

**Still blocked / unverified**: live Production runtime role and `BYPASSRLS`, live Data API exposure and actual `anon`/`authenticated` access, PostgREST authenticated-role behavior, RLS policy enforcement, external Data API consumers, and RLS compatibility for public capability, webhook, and cron paths.

Next approval requests and priority are listed in [19_p0_security_local_execution_report.md](19_p0_security_local_execution_report.md). Any follow-up RLS/GRANT experiment must be separately presented with the exact test-only SQL, disposable target identity, rollback/recreate plan, and API/application regression matrix before approval. Production catalog reads require separately authorized read-only access; no Production writes are recommended or requested.

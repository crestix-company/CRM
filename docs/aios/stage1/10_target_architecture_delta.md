# Stage2 Target Architecture Delta (Proposal)

## Target boundary

```text
Users / public intake
  -> Next.js BFF (session + permission + organization scope)
  -> Command services / Human Gate
  -> CRM public schema (Company, Contact, Deal, LineItem, Task, Delivery)
  -> AIOS additive domains (HospitalProfile, Contract, Payment, MeetingRecord, Artifact)
  -> Event/outbox + immutable attribution/audit
  -> Connectors (Calendar, Drive, CloudSign, Clinic Lead)
```

Clinic Lead remains its own operational SoT for clinic prospect/enrichment. Current Clinic Lead main already uses `hwdvyhunozporfuefteb` with `public.clinics`, `provenance`, `research`, `treatment`, `hp_research`; it must not be recreated inside CRM from obsolete PR #1〜#11 drafts. CRM receives explicit approved links/conversions, not bulk duplication.

## Delta by layer

| Layer | Current | Target delta | Type |
|---|---|---|---|
| Tenant auth | app session + org predicates | central scoped repository/command guard + negative tests | EXTEND |
| DB security | public 80 tables no RLS/full anon grants | least-privilege runtime role, Data API allowlist, RLS on exposed tables | NEW/P0 |
| Organization | BusinessUnit flat | keep BU; optional OrgNode only after official approval | EXTEND |
| Clinic model | Company + associations | CorporateGroup/HospitalProfile + Clinic Lead link | NEW/LINK |
| Sales | Deal/LineItem/Participant/Event | E1/E2/Yomi/lead-time explicit events and required fields | EXTEND |
| Contract/finance | line item workflow only | contract snapshot, CloudSign executed fact, invoice/payment schedule/actual | NEW |
| Meeting | booking + task | MeetingRecord, transcript ref, Minutes, Decision, Task linkage | NEW |
| Approval | absent main | policy/request/step/action/delegation + stale target check | NEW |
| AI | absent | Artifact with fact/inference/proposal/missing, prompt/model/version, approval | NEW |
| Integration | Calendar | connector ownership, outbox/idempotency, Drive/CloudSign/Clinic Lead | EXTEND/NEW |
| Retention | scattered `deleted_at` | Trash/restore/retention class/legal hold | EXTEND |

## Proposed additive data objects

- `HospitalProfile` linked to Company, with clinic identifiers and specialty facts.
- `ExternalEntityLink` for Clinic Lead/Drive/CloudSign IDs and provenance.
- `ContractSnapshot`, `BillingSchedule`, `PaymentReceipt` (names provisional).
- `MeetingRecord`, `Minutes`, `Decision`, `TaskSourceLink`.
- `ApprovalRequest/Step/Action/Delegation` after PR #14 review.
- `AiArtifact` and `AiEvidence` with classification and Human Gate state.
- `OutboxEvent` and connector delivery log for crash-safe integration.

## Migration sequence (not executed)

1. P0 security preview design; no production one-shot RLS.
2. Add link/profile tables with nullable/backward-compatible fields.
3. Backfill mappings in dry-run; keep existing IDs.
4. Add dual-read comparison behind disabled feature flag.
5. Enable role-specific UI on a canary organization.
6. Add contract/meeting/approval domains in separate migrations.
7. Only after acceptance, retire legacy display paths; do not delete records.

## Release / rollback

Every migration must be additive first, preview-applied, catalog-diffed, and have rollback/recreate rehearsal. Runtime activation uses disabled-by-default flags. Rollback disables reads/writes to new domains while retaining additive tables and history. Destructive down migrations are prohibited for production records.

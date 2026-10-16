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

正式要件では医院・法人・担当者の最終SOTはCRMである。Current Clinic Lead mainは`hwdvyhunozporfuefteb`の`public.clinics`, `provenance`, `research`, `treatment`, `hp_research`で稼働しているため、移行期間中のprospect/enrichment供給元・bridgeとして扱う。obsoleteなPR #1〜#11をCRM DBへ再適用せず、source authority、ID mapping、同期方向、conversion、cutover、rollbackを明示して段階的にCRMへ正本を寄せる。恒久的なdual-write/dual-SoTは禁止する。

## Delta by layer

| Layer | Current | Target delta | Type |
|---|---|---|---|
| Tenant auth | app session + org predicates | central scoped repository/command guard + negative tests | EXTEND |
| DB security | public 80 tables no RLS/full anon grants | least-privilege runtime role, Data API allowlist, RLS on exposed tables | NEW/P0 |
| Organization | BusinessUnit flat | keep BU; optional OrgNode only after official approval | EXTEND |
| Clinic model | Company + associations、Clinic Lead別DB | CorporateGroup/HospitalProfile + staged Clinic Lead bridge + CRM authority/cutover | NEW/LINK/P0 decision |
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
3. Define Clinic Lead→CRM field authority and create a read-only comparison connector first.
4. Backfill mappings in dry-run; keep existing IDs and provenance.
5. Add bounded dual-read comparison behind disabled feature flag; do not enable indefinite dual-write.
6. Enable role-specific UI on a canary organization.
7. Add contract/meeting/approval domains in separate migrations.
8. Cut over each authoritative field only after reconciliation/rollback approval; retain source history and do not delete CRM records.

## Release / rollback

Every migration must be additive first, preview-applied, catalog-diffed, and have rollback/recreate rehearsal. Runtime activation uses disabled-by-default flags. Rollback disables reads/writes to new domains while retaining additive tables and history. Destructive down migrations are prohibited for production records.

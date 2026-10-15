# Risks, Decisions and Release Gates

## Top 10 risks

| Rank | Risk | Evidence | Gate |
|---:|---|---|---|
| 1 | public DB exposure | 80/80 RLS off; anon/auth full privileges | BLOCK RELEASE |
| 2 | official sources missing | 13 docx + question xlsx absent | BLOCK requirements sign-off |
| 3 | dual Vercel + Calendar key conflict | v1 connections 2; env/SHA unverified | BLOCK Calendar enablement |
| 4 | restaurant cleanup destroys history | 80 WON, 145 money line items, 997 participants | BLOCK cleanup apply |
| 5 | first department identity ambiguous | no exact「第一営業部」;「第一事業部」inferred | OWNER DECISION |
| 6 | owner/next action data gaps | 2,079 active deals owner null; 1,077 nextAction null | DATA QUALITY GATE |
| 7 | loose UUID orphan risk | PR #13 catalog; polymorphic links | MIGRATION GATE |
| 8 | Clinic Lead PR chain obsolete | current system uses separate shadow schema/runtime | PR CLEANUP DECISION |
| 9 | approval stack unvalidated | #14 pending, #17 Vercel failure; originals missing | HOLD |
| 10 | Vercel config blind spot | target teams inaccessible | ACCESS GATE |

## Decisions required

Representative/business owner:

1. Confirm official source files and resolve contradictions.
2. Confirm「第一営業部」= current Crestix「第一事業部」or approve hierarchy/name change.
3. Approve clinic/restaurant classification policy and retention.
4. Approve authority matrix/Human Gate and final approvers.
5. Confirm contract/WON/finance SoT semantics.

Technical owner:

1. Approve least-privilege DB role/RLS rollout design on clone.
2. Decide ExternalEntityLink vs Clinic-specific link table.
3. Decide index/load-test thresholds.
4. Decide PR #12/#13 integration mechanics and rebase order.

## Ready / blocked

| Item | Status | Reason |
|---|---|---|
| Stage1 facts/data inventory | READY WITH KNOWN LIMITS | production read-only evidence captured |
| Full official traceability | BLOCKED | originals missing |
| Security remediation implementation | READY FOR DESIGN, NOT PROD | runtime role/Vercel config must be verified |
| Restaurant cleanup apply | BLOCKED | human review/retention/backup absent |
| Google enable/cutover | BLOCKED | v1/v2 and dual deployment unresolved |
| Stage3 approval PRs | HOLD | dependency stack, preview migration, official authority review |

## Release gate checklist

- [ ] official 00〜12 and question xlsx ingested
- [ ] Vercel old/new SHA and env key presence verified
- [ ] DB role/Data API/RLS design preview-tested
- [ ] tenant negative tests pass
- [ ] Google v1/v2 cutover rehearsal and rollback pass
- [ ] cleanup secure manifest approved; clone dry-run and restore pass
- [ ] performance/browser E2E meets approved SLO
- [ ] all required CI/test/typecheck/lint/build green on final rebased head
- [ ] no unauthorized migration/seed/deploy

## Recommended next sequence

P1-01 source completion/sign-off → P0 security architecture/rehearsal → department/clinic link decision → Calendar cutover plan → additive Hospital/Link foundation → Deal/Yomi/Event/LeadTime gaps → Hospital Chart/E1/E2 → contract/payment → Meeting/Human Gate. Preserve original backlog numbering after originals are available.

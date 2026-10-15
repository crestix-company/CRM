# Data Cleanup Dry-run Plan

## Current decision

No cleanup apply is authorized. All 235 Company and 375 active Deal restaurant candidates remain `HUMAN_REVIEW` because they include 80 WON deals, 145 money-bearing DealLineItems, 997 participants and historical events/bookings/tasks.

## Classification rules

| Class | Rule | Current use |
|---|---|---|
| KEEP | clinic/medical、shared master、legal/financial/audit/history、mixed | never delete |
| ARCHIVE | inactive legacy business retained for history | preferred for old restaurant records |
| SOFT_DELETE_CANDIDATE | restaurant-only, no unresolved retention/external dependency | after review only |
| HARD_DELETE_EXCEPTION | no business/audit/financial/history value, approved and restorable | expected rare/none |
| HUMAN_REVIEW | mixed, unknown, won, financial, ambiguous links | all current candidates |

## Two-hour comparison

| Option | Estimated effort | Reversible | Risk | Recommendation |
|---|---:|---|---|---|
| UI filter / saved view excludes restaurant | <2h after rule approval | yes | low; underlying data remains | first containment |
| BusinessUnit/status tag + archive view | 2–6h plus review | yes | medium; tagging model needed | preferred durable path |
| Existing `deleted_at` on Company/Deal | >2h because dependencies/reports must be tested | partially | high | only after dry-run |
| Physical delete | far >2h | no without restore | critical | reject except explicit exception |
| ID reassignment | >2h and unnecessary | risky | breaks lineage | do not pursue |

## Dry-run phases

1. Freeze rule version and generate secure row-level manifest in an approved non-Git location.
2. Require two-person classification: business owner + data steward.
3. Traverse both directions of `object_associations` and every loose UUID from PR #13.
4. Mark any WON, line item amount, performance event, booking, task/activity, audit, external ID, Calendar relation as retention-protected.
5. Produce before counts and simulated after visibility counts; no DML.
6. Take Supabase backup/PITR evidence and record restore point.
7. Apply only to preview clone; run count, FK/logical orphan, report/KPI and UI tests.
8. Limited production canary requires representative approval; no batch apply in Stage1.

## Backup / rollback proposal

- Verify PITR/backup availability and retention; do not assume plan capability.
- Export approved manifest with original IDs, timestamps, classification reason and dependency counts to encrypted restricted storage.
- Soft-delete rollback: restore `deleted_at` only for exact manifest IDs and audit the change.
- Archive rollback: re-enable visibility/status by manifest/version.
- Hard-delete rollback: database point-in-time restore or isolated restore + selective re-import; because this is operationally disruptive, hard delete is not recommended.

## ID policy

Existing IDs stay unchanged. If Clinic Lead linkage is needed, add a mapping/provenance record (`source_system`, `source_id`, `crm_company_id`/`hospital_profile_id`, confidence, timestamps). Never renumber Company/Deal or rewrite DealParticipant/SalesPerformanceEvent history merely for sequence aesthetics.

## Acceptance criteria

- Candidate manifest reviewed 100%; mixed/unknown 0 automatically changed.
- Legal/contract/financial/audit/history protected.
- No physical or logical orphans across physical FK and PR #13 loose IDs.
- KPI before/after differences are explained by excluded display scope, not history mutation.
- Rollback rehearsal passes on clone.

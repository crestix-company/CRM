# Requirements Traceability Matrix

## Constraint

`official_00.docx`〜`official_12.docx`は未提供。以下は統合Markdownの原本索引と要約に対するprovisional traceabilityであり、正式原文引用ではない。原本page/section/requirement ID、質問管理sheetとの対応は**UNVERIFIED / BLOCKED**。

## Document-level matrix

| Source | Integrated requirement summary | Current evidence | Class | Gap / acceptance | Priority |
|---|---|---|---|---|---|
| 00 共有ガイド | 既存CRM再利用、要件優先順位 | broad CRM exists | KEEP | official text取得、change control合意 | P0 |
| 01 要件定義 | 経営/営業/契約/CS/AI | sales/KPI/CS一部あり | EXTEND | contract/AI/management acceptance再定義 | P0 |
| 02 構成/データ | CRM SoT、entity、権限 | Prisma 79 models、tenant app boundary | EXTEND | RLS/grants blocker、Hospital/Contract不足 | P0 |
| 03 UI/UX | role Home、医院カルテ、Deal、Review、Meeting/Task | dashboard/Deal/Taskあり | EXTEND + NEW | Hospital Chart/Review/Minutes UI | P1 |
| 04 AI Agent | agent、fact/inference/proposal、禁止 | mainにAI artifact/agentなし | NEW | typed artifact、provenance、Human Gate | P1 |
| 05 Event/Approval | Event Bus、idempotency、approval | operational/performance events一部、approval mainなし | EXTEND + NEW | PR #14〜17を原本照合・preview検証 | P0 |
| 06 External/Migration | Calendar/Drive/CloudSign/Comdesk、保持 | Calendarあり、他なし | EXTEND + LINK | v1/v2 cutover、connector contracts | P0 |
| 07 P1 Backlog | P1-01〜31 | Stage1がP1-01相当 | EXTEND | original backlog IDs未確認 | P0 |
| 08 P2〜4 | CS/Finance/CEO/AI/Talent | Delivery/KPI一部 | EXTEND + NEW | phase orderを維持 | P2 |
| 09 Acceptance | AC/S/R/F/AI/MM/TM | repo tests 31 files | EXTEND | original casesとE2E/nonfunctional不足 | P0 |
| 10 Checklist | production差分、技術判断、代表承認 | 本docsで分離 | KEEP | owner sign-off | P0 |
| 11 References | old CRM/operations/exclusions | PR/docsあり | LINK | official reference inventory不足 | P1 |
| 12 Meeting/Task AI | record→minutes→decision/task→review | booking/taskのみ | NEW | MeetingRecord/Minutes/Decision/notification approval E2E | P1 |

## Cross-cutting requirements

| Requirement | Evidence | Class | Acceptance |
|---|---|---|---|
| Contact internal / UI「担当者」 | Prisma `Contact`、UIにContact naming残存 | EXTEND | domain model維持、customer-facing label統一 |
| active org member sees all active BUs | `getAccessibleBusinessUnits()` ignores membership ACL | KEEP | regression test |
| Deal=1 opportunity | core Deal model | KEEP | KPI query counts distinct Deal |
| revenue/gross profit from DealLineItem | line item fields + KPI code | KEEP | Deal.amountを正式集計に使わないtest |
| historical attribution | DealParticipant 10,676 / events 94 | KEEP | cleanup cannot delete/rewrite |
| legacy import dry-run first | dry-run/apply routes both exist | EXTEND | apply requires signed dry-run fingerprint/gate |
| clinic-first first division | first unit medical 246 / restaurant 0 candidates | LINK/EXTEND | business mapping approval |
| restaurant cleanup | 235 company / 375 active deal candidates | RETIRE_CANDIDATE | all HUMAN_REVIEW; no Stage1 apply |
| logical delete + 30-day Trash | some entities have `deleted_at`; Trash workflow absent | EXTEND | retention policy + restore UI |
| Human Gate | main absent; draft PR stack exists | NEW | no business effect before final approval |
| audit before/after | `audit_logs` exists 79 rows | EXTEND | coverage test for sensitive commands |

## KEEP / EXTEND / LINK / NEW / RETIRE_CANDIDATE totals

These are capability rows, not original requirement counts: KEEP 8, EXTEND 12, LINK 4, NEW 10, RETIRE_CANDIDATE 2. Exact official requirement totals cannot be computed until 13 source documents are present.

## Approval boundary

Representative approval: SoT change, won/contract definition, permission/approval authority, clinic/restaurant business classification, retention/hard delete, phase priority. Technical owner decision: index/query design, DTO shape, migration mechanics, test harness, provided they preserve approved semantics.

# Requirements Traceability Matrix

## Status

`official_00.docx`〜`official_12.docx`の全文照合を完了した。詳細な一次資料register、正式要件ごとの一致/不一致/不足/未確認、AC判定は[Official Requirements Conformance](14_official_requirements_conformance.md)を参照する。

## Document-level traceability

| Source | Formal scope | Stage1 result | Current implementation classification | Residual gate |
|---|---|---|---|---|
| 00 | 読む順番、既存再利用、変更統制 | 一致 | KEEP | 要件意味変更は縞谷承認 |
| 01 | 全体要件、SOT、Human Gate、Phase/DoD | 一部一致・多数不足 | KEEP + EXTEND + NEW | contract/finance/AI/meeting等は未実装 |
| 02 | architecture、SOT、data model、権限 | 一部不一致 | EXTEND + LINK + NEW | clinic SOT cutover、DB security |
| 03 | role UI、Hospital Chart、Review、Meeting/Task | 不足 | EXTEND + NEW | field/permission/mobile E2E |
| 04 | Agent、Artifact、Human Gate、禁止 | 不足 | NEW | 共通AI governanceを先行 |
| 05 | Event、automation、approval、notification | 不足 | EXTEND + NEW | Retry/DLQ/approval/channel |
| 06 | external、migration、retention | 一部一致・未確認 | KEEP + LINK + EXTEND | API実査、retention owner決定 |
| 07 | Phase1 backlog/順序/DoR | 一致 | LINK | P1-01 Stage1完了、実装は未着手 |
| 08 | Phase2〜4/release | 一致する提案 | NEW | phase/release gate維持 |
| 09 | acceptance | 未達 | NEW/EXTEND | ACを実装/受入と誤認しない |
| 10 | 技術確認/承認境界 | 一致 | KEEP | 未確認事項をownerへ返す |
| 11 | 参照資料/旧運用除外 | 一部未確認 | LINK/RETIRE_CANDIDATE | 参照原本の実査は別task |
| 12 | Minutes/Task詳細 | 不足 | EXTEND + NEW | 共通Task拡張＋専用Meeting domain |

## Cross-cutting fixed rules

| Formal rule | Stage1 decision | Class |
|---|---|---|
| CRMを中核に既存機能を再利用 | mainの79 models、53 pages、153 API routesを基礎にする | KEEP |
| 医院/法人/担当者はCRMが最終SOT | Clinic Leadを現行bridge/供給元として接続し、authority/cutoverを設計 | LINK + EXTEND |
| Contact modelを維持し人物表示は「担当者」 | modelを維持し、顧客人物の表示名を「担当者」に統一 | KEEP + EXTEND |
| Dealを1 opportunityとして数える | distinct Dealを案件数にする | KEEP |
| 売上/粗利はDealLineItemから集計 | Deal.amountを正式実績にしない | KEEP |
| DealParticipant/Eventで過去帰属を保持 | cleanup/migrationで削除・上書きしない | KEEP |
| AIは重要判断・外部送信を単独確定しない | Approval/Artifact/Human Gateを共通基盤にする | NEW |
| 正式受注はCloudSign executed | executed eventより前のWONを禁止する | NEW |
| active org memberはactive BUを閲覧 | BusinessUnitMembershipをread ACLにしない | KEEP |
| importはdry-run先行 | applyは承認済みmanifest/fingerprint後 | EXTEND |
| 削除はTrash/論理削除/監査 | 飲食候補はRETIRE_CANDIDATE/HUMAN_REVIEWのみ | EXTEND |

## Capability disposition

| Type | Main capabilities |
|---|---|
| KEEP | tenant-scoped application access、Company/Contact/Deal、LineItem、Participant/Event、Calendar、KPI、Task、Delivery、dry-run import |
| EXTEND | Hospital Chart、Yomi/Event/LeadTime、Task、Product snapshot、Review、Notification、Audit、Retention |
| LINK | Clinic Lead、Drive/Docs/Slides/Meet、CloudSign、Comdesk、決済、Bolt |
| NEW | HospitalProfile/CorporateGroup、Contract/Billing/Payment、Approval、AIArtifact、Meeting/Minutes/Decision、Knowledge、integration delivery |
| RETIRE_CANDIDATE | 飲食候補data/旧表示/旧Clinic DB draft。承認・保持・復旧手順なしに削除しない |

## Approval boundary

縞谷承認が必要: SOT変更、Human Gate削除、正式受注/Yomi/粗利定義、権限方針、Phase優先度、情報公開範囲、retention/hard delete。前川が決定可能: library/framework、index/cache/queue、component構成、monitoring/test tool、ID内部方式。ただし正式要件の意味、既存ID、監査性を変えない。

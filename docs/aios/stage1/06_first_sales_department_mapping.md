# First Sales Department / Clinic Mapping

## Verified organization structure

正式追加要件の「第一営業部」と完全一致するBusinessUnit/Teamはproductionに存在しない。

| Organization | Organization ID | Unit | Unit ID | Active / deleted Deals | Active memberships |
|---|---|---|---|---:|---:|
| 株式会社Crestix | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | 第一事業部 | `8036a665-d413-4857-81cd-a5ad041d0309` | 504 / 448 | 0 |
| 株式会社Crestix | same | HD事業部 | `5beaaff8-d556-4053-81bd-65585d1218b1` | 1,595 / 2,189 | 2 |
| 株式会社Crestix | same | レガシー移行 | `ed520ef2-eae2-41a4-a6bc-959c553d8229` | 0 / 131 | 0 |
| 株式会社サンプル | `588bd30f-5f05-4cfa-9f7f-118a8a8c0a11` | 第1事業部 | `312fe4c1-c4c4-41cd-bb12-46dadeb208d4` | 15 / 0 | 3 |
| 株式会社サンプル | same | HD事業部 | `aba7bbbe-d934-423f-bc69-568554e63fa2` | 15 / 0 | 4 |
| 株式会社サンプル | same | 北斗…案件 | `ce6a43e8-16cd-4263-9191-7b9981b984f9` | 0 / 0 | 0 |

Team tableはsample organizationの「営業チーム」1件のみ。CrestixにはTeamがない。よって「第一営業部」= Crestix「第一事業部」とみなすのは**INFERRED**で、代表/業務owner確認が必要。

## Clinic / restaurant mapping

| Crestix unit | Active Deals | Medical candidate | Restaurant candidate | Unknown/other |
|---|---:|---:|---:|---:|
| 第一事業部 | 504 | 246 | 0 | 258 |
| HD事業部 | 1,595 | 33 | 375 | 1,187 |

Company active 1,405件ではmedical 246、restaurant 235、unknown/other 924。keyword上、医療Dealは第一事業部へ集中し、飲食DealはHD事業部へ集中している。これは追加要件の方向と整合するが、第一事業部のactive membershipが0件である点は運用上の重大Gap。

## Mapping decision

- KEEP: Crestix Organization、既存BusinessUnit ID、Deal ID、DealParticipant、SalesPerformanceEvent。
- LINK: Clinic Leadの`clinic_id/UUID`とCRM Company/HospitalProfileを明示link tableで接続。
- EXTEND: 第一事業部にHospital/Clinic profile、medical classification、担当者roleを付与。
- NEW: 法人→医院の階層、source provenance、conversion service。
- RETIRE_CANDIDATE: 「第一営業部=飲食」表示/初期値がコード・seed・dataに残る場合。現行main codeで明示固定は未検出。

## Required approval

1. 「第一営業部」の正式DB表現を既存「第一事業部」とするか、名称変更/OrgNodeを導入するか。
2. active membership 0件が意図的か、membership backfillが必要か。
3. 258 unknown dealsの分類owner。
4. sample organizationをproductionで保持する目的。

# Data Quality and Counts

## Exact production counts

観測時点は2026-10-15 21:42 JST前後。全80テーブルのexact countは`03_db_schema_relations.md`に記載。

| Entity | Rows | Notes |
|---|---:|---|
| Organization | 2 | Crestix + sample |
| User | 9 | PII非出力 |
| Company | 1,419 | active 1,413 / soft-deleted 6 |
| Contact | 1,378 | active 1,378 / deleted 0 |
| Deal | 4,898 | active 2,129 / soft-deleted 2,769 |
| Activity | 4,231 | soft delete列あり |
| Task | 323 | no soft-delete列 |
| MeetingBooking | 25 | Google logical IDsあり |
| DealLineItem | 1,618 | revenue/gross profit SoT候補 |
| DealParticipant | 10,676 | historical attribution |
| SalesPerformanceEvent | 94 | historical KPI event |
| ObjectAssociation | 5,838 | polymorphic relation |
| DeliveryProject | 491 | CS aggregate |
| AuditLog | 79 | cleanup対象外 |
| GoogleCalendarConnection | 2 | connected/v1 |
| `_prisma_migrations` | 23 | distinct successful migration 21 + rolled-back attempts 2 |

## Main quality findings

| Check | Result | Interpretation |
|---|---:|---|
| active Company industry NULL | 1,383 / 1,413 | 97.9%。industry単独分類は不可 |
| active Company domain NULL | 1,249 / 1,413 | domain matching coverage低 |
| active Company owner NULL | 1,383 / 1,413 | ownership backfill/semantics要確認 |
| duplicate normalized active Company name groups | 0 | exact normalized-name基準のみ |
| duplicate nonblank Company domain groups | 0 | NULL多数 |
| active Contact email NULL | 1,358 / 1,378 | email identityには使えない |
| duplicate nonblank Contact email groups | 0 | nonblank範囲 |
| active Deal businessUnit NULL | 0 / 2,129 | assignmentは完全 |
| active Deal owner NULL | 2,079 / 2,129 | 97.7%。ownerを必須と仮定不可 |
| active Deal nextAction NULL | 1,077 / 2,129 | operational completeness gap |
| active Deal without line items | 873 / 2,129 | 金額/粗利集計のcoverage gap |
| active Deal without Company association | 1 | review対象 |
| duplicate nonblank Deal external ID groups | 0 | observed |

## Classification counts

Crestix organization active Company 1,405件に対し、strong keyword ruleで医療246、飲食235、mixed 0、その他/不明924。active Dealは第一事業部504件中、医療246・飲食0・不明258。HD事業部1,595件中、医療33・飲食375・不明1,187。

これは確定業種ではなく候補。Companyの97.9%でindustryがNULLのため、名称/custom fields/Deal linkに依存し、false positive/negativeを含む。

## Executed safe SQL pattern

```sql
BEGIN READ ONLY;
SELECT count(*) FROM public.companies;
-- NULL/duplicate checks use aggregate only; no row values exported.
ROLLBACK;
```

全テーブルcountはcatalogでtable名を取得し、quoted identifierごとに`count(*)`を実行。候補分類は正規表現booleanをaggregateし、名前/連絡先は出力していない。

## UNVERIFIED

- official文書が定めるデータ品質閾値。
- Company/Contactの「医院/法人/担当者」正規化ルール。
- 不明924社/1,460件超Dealの人手分類。
- app runtimeを通した同時実行・large-scale latency。

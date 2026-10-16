# Supabase RLS / GRANT / Data API Preview検証設計

## Status and boundaries

**DESIGN ONLY**。本番DB、Production Preview、Supabase project、権限、Migration、Seedへの操作は行わない。この設計はStage1所見を安全に再現・検証する計画であり、現行本番への接続テストも未実施。

監査baseline（2026-10-15前後のREAD ONLY観測）: 80/80 public base tables RLS無効、policy 0、`anon` / `authenticated`に全80表のSELECTおよび広範な書込権限。User/session/calendar token等を含む。実際の外部到達可否はData API exposed schema/configとの組合せに依存し、ここでは全表が外部から取得されたとは主張しない。GRANTはobject到達権、RLSは許可roleのrow filterであり、両方を検査する。

Supabase公式説明では、exposed schema内のobjectにrole grantがあるとData APIから到達可能になり得て、RLSが無い場合にrowを制限できない。既存projectの既存grantは新規tableの自動exposure default変更で消えないため、設定値だけの変更は既存80表の是正ではない。参照: [Securing your API](https://supabase.com/docs/guides/api/securing-your-api), [Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security), [2026-04-28 Data API exposure changelog](https://supabase.com/changelog/45329-breaking-change-tables-not-exposed-to-data-and-graphql-api-automatically), [Supabase database testing overview](https://supabase.com/docs/guides/local-development/testing/overview)。

## Objectives

1. `anon`はCRM business dataを読めず書けない。必要なpublic intakeは個別endpoint/token・狭い契約に限る。
2. authenticated user Aは自Organizationのみ。別Organization/non-memberの行は読めず変更できない。
3. 同一Organizationのactive memberは正式要件どおりactive BusinessUnit横断で閲覧できる。`BusinessUnitMembership`をread ACLにしない。
4. role別write、soft-delete/history/audit、Webhook/OAuth/Cron/public intake、Calendar同期、service backendの動作を壊さない。
5. `service_role` / DB owner / Prisma runtime roleのbypassを把握し、秘密鍵をclient/test outputに含めない。

## Preconditions — この設計ではbranch/projectを作成しない

前川が非本番のisolated環境を用意し、縞谷/セキュリティ責任者がデータ持ち込みを承認する。CRMはSupabase Auth JWTではなく独自opaque-cookie sessionを使うため、Supabase Branch/local Supabaseで作る`authenticated` JWTはCRM sessionと別物である。Supabase Branchがproduction migrationsを反映する場合、この依頼の制約下ではbranch作成も行わない。isolated projectまたはlocal Postgres/Supabaseに、空DBから同じschemaを再構築する。

- Production snapshot/raw data/token/session/user情報をPreviewへ複製しない。
- Schema-onlyまたはsynthetic fixtureを使う。匿名化データ持込は別計画・別承認とし、識別子・自由記述・token・PIIを排除する。
- Preview credentialsとsynthetic usersを分離する。Production URL/key/JWT/passwordを環境変数、ログ、Markdownへ複写しない。
- この設計の範囲でMigration/Seedは行わない。将来実行は承認commit・isolated targetを二者確認し、実行記録へ記載する。
- Data APIの利用有無・exposed schemasを確認する。未使用なら停止も選択肢だが、アプリ依存を確認せず停止しない。

## Read-only discovery inventory

| Area | 確認するもの |
|---|---|
| Data API surface | API設定上のexposed schemas、Data API/GraphQL enabled state。Production値は許可された担当者が別に確認し、secretは複写しない |
| PostgreSQL objects | schema/table/view/materialized view/function/sequence、owner、RLS enable/force、policies、view security invoker/definer、function `SECURITY DEFINER`/search_path |
| Privileges | `anon`, `authenticated`, `service_role`, `PUBLIC`, `authenticator`, Prisma runtime role, owner/migration roleのschema USAGE、table/view CRUD/TRUNCATE/REFERENCES/TRIGGER、sequence ACL、function EXECUTE、default privileges |
| Runtime path | Vercel Preview server-side direct DB role/pooler、browser Data API/SDK、webhook/public intake/cron/provider callbackの経路・role・owner。credential値は記録しない |
| RLS assumptions | `getAuthContext()`からDBへのtenant context伝播、pool再利用時のtransaction境界/cleanup、role `BYPASSRLS`/table owner、policy内membership lookup |
| Sensitive surface | auth/session hash、calendar token/OAuth state、audit/security log、integration secret、finance/person data。Data APIは非公開を既定 |

出力はaggregate/権限名/object名に限り、顧客行・JWT/token値を記録しない。

## Candidate target boundary (not approved policy)

1. Browserから必要なSupabase objectを特定。不要ならData API停止を優先候補としてPreviewで評価。
2. Data APIが必要なら公開schema/objectをallowlist化し、内部tableは非exposed schemaに置く案を比較する。schema exposureはgrant/RLSの代替ではない。
3. `anon`は原則CRM base table/view/function grantなし。Public intakeは汎用table writeでなく、狭いserver endpoint/API契約に限定。
4. `authenticated`も明示allowlist＋最小権限grant。全exposed tableでRLSをenableし、tenant predicateとaction別policyを作る。`USING`と`WITH CHECK`双方を試験。
5. Supabase Auth利用箇所がコードにないため、`auth.uid()`をCRM sessionの認証根拠にしない。RLS tenant条件はPrisma requestが検証したserver-side identity contextから導出する案を別途実証する。user-editable `user_metadata`やclient指定organizationIdを認可根拠にしない。
6. Prisma direct DB runtimeにCRM cookieまたはSupabase Auth JWT/RLS contextが自動伝達されると仮定しない。非BYPASSRLS専用role、owner回避、requestごとのtransaction-local tenant context、pool cleanupをPreviewで実証する。各Prisma queryが共通tenant-scoped transaction wrapperを通るかは未確認。wrapper未実装ならRLS enforcement前にapp refactorが必要。実現できないpolicyは適用しない。
7. PostgreSQL対応範囲でviewに`security_invoker`を検討。exposed schemaの`SECURITY DEFINER` functionを避ける。sequence/function ACL、PUBLIC EXECUTEも検査。
8. 最初の境界はOrganization。BusinessUnit membershipはread filterに使わない。write/action permissionsは正式role/business policyとして別途検証。

## Synthetic identities

| Principal | Fixture |
|---|---|
| anon | 有効なuser JWTなし |
| member-A | Organization-A active membership。複数active BUと所属外BUの行を用意 |
| member-B | Organization-B active membership。越境negative test用 |
| suspended-A | inactive/suspended membership |
| admin-A / rep-A | 同一tenantの異なるapplication permission role |
| service/runtime | server-only synthetic credential/DB role。client到達不能を検査 |

fixtureに実在顧客・担当者・Calendar・契約・token情報を入れない。ID/email domainはtest専用。

## Test matrix / expected result

| ID | Surface / role | Action | Expected |
|---|---|---|---|
| API-01 | REST/OpenAPI root, anon | schema/table metadata | 承認済みpublic contract以外のsensitive schema/table/columnを開示しない |
| API-02 | REST GET protected table/view, anon | list/single/count/filter | permission deniedまたは非開示。business row/count leakなし |
| API-03 | REST POST/PATCH/DELETE protected table, anon | synthetic canary write | 401/403。row/sequence/audit副作用なし |
| API-04 | GraphQL (enabled only), anon | introspection/query/mutation | protected object非公開、副作用なし |
| API-05 | exposed function/sequence | anon/auth EXECUTE/nextval | 明示allowlistのみ。不要EXECUTE/sequenceアクセスなし |
| RLS-01 | SQL `SET LOCAL ROLE anon` | direct row access | SQL role ACL/RLSを分離して検査。PostgREST/Data API HTTP試験の代替ではない |
| RLS-02 | member-A | Organization-Aをselect | 必要な同一tenant行を閲覧可能 |
| RLS-03 | member-A、Organization-B既知UUID | single/list/aggregate/view | 0 rowsまたは非開示404/403。不要な存在oracleなし |
| RLS-04 | member-A | org-B row update/delete | 0変更または403。canary不変 |
| RLS-05 | member-A | organizationId偽装/row A→B移動 | `WITH CHECK`で拒否。元row不変 |
| RLS-06 | suspended-A / invalid/expired CRM cookie | Next.js session flow | default deny (401)。Supabase Auth JWTとは別に検証 |
| RLS-07 | active A member | 自身membershipのないactive BUのrowをread | Organization内なら許可。BU membership read ACL禁止を証明 |
| RLS-08 | active A member | inactive BU/deleted row | 承認済みactive/deleted policyどおり。例外記録 |
| APP-01 | Next.js Preview API/Prisma | tenantは`getAuthContext()`由来 | URL/body/query organizationId偽装でcontextを上書き不可 |
| APP-02 | server role/connection pool | 再利用connectionでorg-A→org-B連続request | 古いtenant context漏れなし。success/error/cancelでreset |
| APP-03 | application role | company/contact/deal/line item/calendar/task操作 | 既存機能保持。同一orgのactive BU可視性保持 |
| INT-01 | intake/webhook/OAuth callback/cron | valid/invalid/replay/wrong-tenant credential | endpoint個別契約を維持。汎用anon DB write不要 |
| SENS-01 | user/session/calendar token/OAuth state/audit | anon/auth Data API access | table直接access不可。server integrationのみ許可 |
| SEC-01 | view/function/default ACL | bypass/RLS/default grant | unintended PUBLIC EXECUTE、owner bypass、新規object exposureなし |
| REG-01 | CRM preview | auth/CRUD/report/KPI/Calendar v1/audit | 重要flow維持、legacy Calendar guard無変更 |

拒否writeごとにcanary row、audit/event countが不変と確認する。production record IDを使わず、PIIをCI logへechoしない。

## Separate approval後の実施順

1. **Gate 0 — isolated target承認**: productionではない環境、synthetic-only data、restore方法、owner/approverを記録。ここではproject/branchを作成しない。
2. **Gate 1 — 変更なしbaseline**: preview catalog/grant/RLS/API role結果/app smoke取得。実runtime DB roleと全consumerを確定。
3. **Gate 2 — design review**: Data API停止/個別API schema、role/grant allowlist、RLS tenant source、view/function/sequence/public intakeを決めsecurity owner承認。
4. **Gate 3 — disposable Previewで変更試験**: 承認済みSQL/migrationだけをisolated targetへ。productionには接続しない。transaction rollbackまたは破棄可能な環境を使う。
5. **Gate 4 — negative/positive matrix**: pgTAPでschema/policy/role、REST integrationで実Data API、app testsで`getAuthContext()`/connection poolingを確認。
6. **Gate 5 — regression / rollback**: protected route、public intake、OAuth/Webhook/Cron、Calendar v1、KPI、tenant visibility、性能/error rateを確認し、Previewでbackup restore/rollbackを実証。
7. **Gate 6 — owner decision**: object別結果・例外・残リスクを公開。production applyには別途明示承認、change window、backup proof、canary/rollback担当、正式release gateが必要。

## Pass / fail

**Pass条件**: Data API allowlist明確、anonに不要なdata read/writeなし、必要exposed relationのRLS/policy検証済み、cross-tenant read/write拒否、同一tenant active-BU可視、runtime role/pool動作実証、regression成功、rollback成功、artifact/logにsecret/PIIなし、security/business ownerが残リスクを承認。

**Fail / stop条件**: runtime role不明、未承認BYPASSRLS/owner経路、client制御またはpool staleのtenant context、広範anon grantに依存するpublic surface、業務regression/data diff/leak、backup不明、rollback失敗。productionで再試行せず停止・再設計。

後続証跡にはcommit SHA、synthetic dataset version、isolated project ref（要restricted管理なら文書本文外）、tool version、test件数/結果、sanitized ACL/RLS集計、status code、side-effect確認、performance、rollback結果、reviewerと承認日時のみを保持。DB URL/password/JWT/anon secret/token/顧客行は保存しない。

## Owner split

- **縞谷 / security or business owner**: risk分類/通知、Data API公開範囲、public intake例外、残余risk、release承認/change window。
- **前川**: runtime role discovery、技術target boundary、grant/policy設計、synthetic fixture/test harness、Preview結果、app regression/rollback証跡。
- **Stage2 entry**: 両者がtarget modelとtest evidenceを承認すること。設計書完成をP0是正完了とは扱わない。

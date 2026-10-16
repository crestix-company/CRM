# P0 Security: Production Read-only Findings and Preview Proof Plan

- **確認日:** 2026-10-16 (JST)
- **対象:** crestix-company/CRM / audit/aios-stage1-db-inventory
- **基準資料:** [19_p0_security_local_execution_report.md](./19_p0_security_local_execution_report.md)
- **PR:** #19（OPEN / Draftを維持）
- **範囲:** Supabase管理経路からのカタログSELECT、ローカルソース読取、Vercel接続情報の取得可否確認。顧客レコードは取得していない。
- **非実施:** Preview作成、DDL/GRANT/RLS実行、Migration/Seed、本番APIのrecord GET、本番設定変更、デプロイ。

## Production Read-only Findings

接続済みSupabase管理経路のproject一覧からCRMを特定し、対象projectに限定してread-only SQLを実行した。SQLはpg_catalog / information_schemaと権限判定関数を使い、行データは読んでいない。以下は2026-10-16時点の観測値である。

| 項目 | 確認済み | 未確認・留保 |
|---|---|---|
| DB | CRM projectはACTIVE_HEALTHY、PostgreSQL 17系 | 接続経路の認証情報・Vercelとの対応は別途確認が必要 |
| public tables | base/partitioned table 80件。全80件のownerはpostgres | public schema自体のownerはpg_database_owner |
| RLS | enabled 0/80、FORCE 0/80 | DB層のtenant row filterは現状確認できない |
| roles | anon/authenticatedはLOGINなし、BYPASSRLSなし。service_roleはBYPASSRLSあり。postgresはsuperuser属性falseだがBYPASSRLSあり | Prisma runtime roleがどれかは未確認 |
| membership/inheritance | authenticatorはanon/authenticated/service_role membershipを持つ。postgresはこれらを含む管理membershipを持ち、rolinherit=true | app roleへの実接続・SET ROLE経路はVercel側で未確認 |
| API service | pg_stat_activityにPostgREST 14.5接続を観測 | Dashboard上のData API toggle、公開schema、HTTPでの実露出は未確認 |
| pooler | PgBouncer接続を観測 | アプリ用pooler hostname/port、session/transaction mode、Prisma接続文字列は未確認 |
| その他 | pg_cron、pg_netの接続を観測 | 接続数は一時点の観測で、全利用者/consumer台帳ではない |

has_table_privilegeによる実効権限集計では、anonとauthenticatedの双方がpublic全80表にSELECT、INSERT、UPDATE、DELETE、TRUNCATE、REFERENCES、TRIGGER、MAINTAIN権限を持ち、public schemaのUSAGEもtrue。さらにcatalog上、postgresが作成する将来のpublic tableにはanon/authenticatedへの広いdefault privileges、sequenceにはUSAGE/SELECT/UPDATE、functionにはEXECUTEのdefault privilegesがある。RLSは0/80である。よってData APIがこれらのtableを公開schemaとしてルーティングする場合、DB権限・RLSによるtenant行制限がない。公開schemaとHTTPアクセスを未確認のため「外部から80表すべてが実際に読める」とは断定しないが、重大なP0露出リスクとして扱う。

### Prisma / Vercel / 外部利用

- [src/lib/prisma.ts](../../../src/lib/prisma.ts)はDATABASE_URLでPrisma Clientを初期化する。値がpooler.supabase.comを含む場合はpgbouncer=trueを追加。Prisma schemaにdirectUrlは定義されていない。
- [src/lib/auth.ts](../../../src/lib/auth.ts)はSupabase Auth JWTではなく、CRM独自opaque session cookieとactive organization membershipを検証する。通常APIはgetAuthContext()を通じアプリ層でtenantを検査する。
- Repository検索ではSupabase JS SDKやData APIの直接呼出し、GraphQL client利用は見つからなかった。public booking/form/chat、Calendar webhook、cronはNext.js APIからPrismaを使う経路がある。検索で未発見でも、他repo・BI・運用script・外部利用者がない証明にはならない。
- Vercel connectorで確認可能なアカウントにcrestix-company/CRMのlinked projectがなく、対象Production project/Deployment protection、env key、接続先、SHAを確認できなかった。秘密値は取得・出力していない。Production Vercel認証、DB接続先/role/pool mode、外部REST/GraphQL利用者はUNVERIFIED。
- Vercelの追加確認は対象projectへのread-only権限を持つownerに依頼し、project/deployment SHA、保護・認証設定、environment key名とtarget、DATABASE_URLのdirect/pooler別だけをsanitized共有してもらう。URL全体、password、JWT、API keyは共有・保存しない。

## Data API Exposure

| 層 | 状態 | 根拠 |
|---|---|---|
| HTTP service | 稼働確認 | PostgREST 14.5のDB接続あり |
| exposed schema | UNVERIFIED | 管理設定取得不可。DBのcurrent_setting('pgrst.db_schemas')も値なし |
| DB grants | FAIL / 過剰許可 | anon/authenticatedにpublic 80/80 tableの広いDML・追加権限 |
| RLS | FAIL / 保護なし | enabled 0/80、policy 0 |
| 匿名/認証HTTPアクセス | 未実施 | 本番recordの誤取得を避けるため、実データGETを行わなかった |
| GraphQL endpoint | UNVERIFIED | extension/API設定、exposureとconsumerを未確認 |

## Prisma Runtime Role

- **確認済み:** publicの全table ownerはpostgres。postgresはsuperuserではないがBYPASSRLS=true。service_roleもBYPASSRLS=true。これらをruntime roleとして使えばRLSをtenant境界にできない。
- **未確認:** Production Vercelの実Prisma role、owner属性、直接/間接BYPASSRLS、membership/INHERIT、pooler mode、接続認証方式。catalogの管理接続主体やDDL ownerをPrisma runtimeの証拠にしない。
- CRM cookieはNext.js側で検証され、DBはその認証を直接行わない。RLS導入には、検証済みmembershipから得たorganization IDを同一DB transactionに渡す機構が必要。

## Security Options Comparison

工数は暫定相対値。外部consumerと全table/route棚卸し後に再見積もりする。

| 案 | 既存機能への影響 | リスク | Migration / 工数 | Rollback |
|---|---|---|---|---|
| **A. Data API無効化、Prisma維持** | 現行source検索ではCRMはNext.js→Prisma経路。直接Data API依存は未発見のためアプリ影響は限定的と推定。未発見consumerは停止し得る | toggleだけではGRANTが残る。Prisma roleがowner/BYPASSRLSならDB credential侵害時の影響大 | toggleだけならMigration不要。anon/authenticated grantとdefault ACL撤回を永続化するならSQL migration/DB手順が必要。低〜中 | consumer影響と旧ACLを記録し、API設定・ACLを個別に復元。過剰GRANTの無条件復元はしない |
| **B. 必要APIのみ公開しGRANT最小化** | 現行コードに必要なData API consumerが特定されていない。公開対象が決まるまで互換性判断不可 | GRANTだけでは安全でない。authenticatedはSupabase AuthでありCRM cookieと別ID。公開tableはRLS必須。view/function/sequence/default ACLにも注意 | 公開対象別のGRANT/RLS migrationと設定変更。中〜高 | 変更前ACL/schema exposureをPreviewで記録し、API単位で復元。RLSは削除せずfail-closed維持 |
| **C. RLS + CRM独自認証接続** | 全Prisma route、transaction、cron、webhook、public booking/capabilityを改修し回帰が必要 | owner/BYPASSRLSでは機能しない。Supabase Auth JWTをCRM cookieと誤認できない。RLSは80表のtenant lineageに沿って個別化が必要 | 多数のpolicy/GRANT migrationとapplication実装。高〜非常に高 | Preview再作成/down手順、旧app roleへの切戻し、ACL/RLS復元と回帰を事前検証。本番は別承認 |

## Recommended Architecture

短期はAを第一候補としてPreviewで無効化とGRANT縮小を検証し、B/Cを後続判断にする。ただしconsumer inventoryが未完了なので、本書だけを根拠に本番Data APIを止めない。外部consumerを業務ownerが確認し、停止影響を承認してから、本番設定変更を別途申請する。

RLSを中期導入するなら、migration ownerとruntime roleを分離し、runtimeは非owner/NOBYPASSRLSにする。Next.jsでCRM sessionとmembershipを検証し、同じPrisma transaction内でtransaction-local tenant contextを設定する。全80表をtenant-owned、親FK経由、global、public capability、system eventに分類し、子表は親tenantを辿るpolicyを設計する。context未設定時はdeny。Supabase anon/authenticatedにCRM cookieは届かないため、直接Data APIをCRM authへ接続しない。必要なら別途secure auth bridge設計を行う。

## Preview Execution Plan

**以下は設計案のみ。Preview project/DB作成、Migration、GRANT/RLS/role変更、fixture投入は未実行で、別途承認が必要。**

### 分離・事前確認

1. 独立した新規Preview projectまたは一時DBを作り、既存Supabase stack、CRM本番、共有dev DBを再利用しない。
2. Production data/credentials/Vercel env/Google OAuth tokenを持ち込まない。DB名、role、port、hostを独立させ、外向き通信は原則deny。
3. 接続前後にDB自身からinet_server_addr(), inet_server_port(), current_database(), current_user, session_user, version()を取得。loopbackまたは承認済みPreview専用host、DB、roleの一致を二者確認。
4. fresh synthetic databaseへ21 Migrationを適用する場合、target空性・接続先・migration owner・破壊DDLを確認してから行う。seed scriptは使わず明示fixtureのみ。
5. project名、費用上限、TTL、port、migration list、fixture、破棄・復旧条件を先に提示して別承認を得る。

### Preview roleとpilot SQL案（未実行）

| Role | 用途 | 制約 |
|---|---|---|
| preview_owner | migration/schema管理 | LOGINなし、application接続禁止 |
| crm_runtime_test | Prisma用のtest role | NOLOGIN、NOINHERIT、NOBYPASSRLS、non-owner、pilot tableだけ必要DML |
| anon / authenticated | Data API denial/allow tests | Previewだけで使用。CRM cookie identityとして扱わない |
| service_role | bypass境界テスト | Previewだけで特権を確認し、application runtimeに使わない |

次のSQLはcompanies一表の概念実証に限る。適用前にPreview catalogで型、sequence名、所有関係を検証する。全表適用・本番適用は禁止。

~~~sql
-- PREVIEW ONLY / NOT APPROVED FOR EXECUTION
CREATE ROLE crm_runtime_test NOLOGIN NOINHERIT NOBYPASSRLS;
GRANT USAGE ON SCHEMA public TO crm_runtime_test;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.companies TO crm_runtime_test;
-- Add sequence privileges only if a pilot table actually uses a sequence.

ALTER TABLE public.companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.companies FORCE ROW LEVEL SECURITY;
CREATE POLICY companies_org_isolation_test ON public.companies
FOR ALL TO crm_runtime_test
USING (organization_id = NULLIF(current_setting('app.organization_id', true), '')::uuid)
WITH CHECK (organization_id = NULLIF(current_setting('app.organization_id', true), '')::uuid);
~~~

このpolicyはruntime roleが非ownerかつNOBYPASSRLSであることが前提。contextはserver側でmembershipを検証後、同一transaction内でtransaction-localに設定する。organization_idのない子表はこの例を流用せず、parent FK経由のtenant policyを個別設計する。Data API roleへの広範なGRANTを追加しない。

### Synthetic fixture / テスト

- Organization A/B: 架空UUID各1、無関係のSynthetic名。
- A1 active、B1 active、A2 suspendedのmember/session。opaque cookieはPreview専用値。
- CompanyはA/B各1件、架空Clinic名、連絡先はinvalid.example。Deal/Contact/Activityは必要最小数のみ。
- public booking/form/captureとwebhook fixtureは使い捨ての合成token。Google Calendar、メール、実OAuthを呼ばない。

| ケース | 期待値 |
|---|---|
| A1正常SELECT/INSERT | Aだけ閲覧。偽装organizationId=Bを送ってもA contextへ保存、WITH CHECKでも拒否 |
| AからB rowをSELECT/UPDATE/DELETE | 0件または拒否。Bの値・変更を返さない |
| context未設定でSELECT/INSERT | SELECT 0件、write拒否 |
| 未認証/停止member | CRM API 401/403、tenant context未設定 |
| anon/authenticated Data API | Previewでのみobject/verb別に許可範囲を検査。未許可tableはdeny |
| role escalation | runtimeからowner/service_roleへのSET ROLE、DDLを拒否。runtime BYPASSRLS=false、non-owner確認 |
| connection pooling | transaction終了後にcontext残存なし。並行A/B反復でtenant leak 0 |

### Regression / rollback

- Unit・typecheck・lint・buildに加え、CRM login/logout/org switch/session expiry、companies/contacts/deals/activities/tasks/reports/import dry-runのA/B正常・越境テスト。
- Public booking、forms/submissions、Google Forms appointment、capture link、chatはsynthetic tokenでscopeを検証。
- Calendar webhookのbad token/resource/duplicate/expiredは完全mock。OAuth/connect/sync/watchの外部通信はnetwork-denied。Cron/reminderはPreview専用secretとsynthetic対象のみ。予約hold/idempotency/overlapは合成日時で競合試験。
- Data APIはPreviewのみでOpenAPI/object visibilityとanon/authenticated各verbを合成tableに実行。Production HTTP検証でrecordを取得しない。
- 失敗時は外部通信遮断、Preview app停止、fixture marker照合。migrationを含む失敗はdown SQLを安易に実行せず、証跡保全後に独立Preview DBを再作成。復旧後CRM smoke testsを再実行。本番環境には触れない。
- policy単体のPreview rollback例（変更前にRLSがoffで、実験で作成したpolicyだけを戻す場合に限る）。ACL復旧は事前保存したPreview snapshotに合わせる。

~~~sql
-- PREVIEW ONLY / verify the experiment-created policy and baseline first.
DROP POLICY IF EXISTS companies_org_isolation_test ON public.companies;
ALTER TABLE public.companies NO FORCE ROW LEVEL SECURITY;
ALTER TABLE public.companies DISABLE ROW LEVEL SECURITY;
REVOKE SELECT, INSERT, UPDATE, DELETE ON TABLE public.companies FROM crm_runtime_test;
REVOKE USAGE ON SCHEMA public FROM crm_runtime_test;
DROP ROLE crm_runtime_test;
~~~

## Remaining Blockers

1. P0: Data API enabled toggle、公開schema、GraphQL公開設定が未確認。
2. P0: Production VercelのPrisma runtime role、owner/BYPASSRLS、membership、接続modeが未確認。
3. P0: Production appのdirect/PgBouncer接続方式、pool mode/portが未確認。
4. P0: 他repo、BI、automation、外部REST/GraphQL利用者の完全なinventoryがない。
5. P0: Vercel対象team/projectへのread-only accessまたはownerのsanitized reportが必要。
6. Stage2: 80表のtenant lineage、global data、public capability/service-role境界の業務・技術判断が未完了。
7. Preview作成、Migration、role/GRANT/RLS適用は今回未承認。

## Next Approval Required

1. **P0 / Supabase read-only:** ownerまたはread-only権限者がData API設定、exposed schemas、GraphQL、pooler modeを値/recordなしで確認し共有する。
2. **P0 / Vercel read-only:** ownerがProduction project/deployment SHA、protection/auth mode、env key名とtarget、DATABASE_URLのdirect/pooler別、接続role名をsanitizedで報告する。接続文字列やsecretは禁止。
3. **P0 / Consumer inventory:** 外部consumer、担当者、HTTP verb、停止可否を業務ownerが確認し、A無効化リスクを判断する。
4. **P0 / Preview作成:** 新規DB/project、費用上限、TTL、port、21 Migration、fixture、分離確認・破棄条件を固定した実行申請を別承認する。
5. **P0 / Preview SQL:** pilot table、role、正確なDDL/GRANT/RLS SQLとrollbackをreview後、別承認を得る。承認前に適用しない。
6. **P1 / 選択:** consumer棚卸し後にA（Data API遮断）を先行するか、B（限定公開）/C（tenant RLS）を別計画にするか決める。本番変更はどの案も別承認。

## Safety Record

- 本番DB write/DDL/Migration/Seed: **0**
- Preview作成、SQL、role・権限変更: **0**
- 本番Data APIのrecord GET/HTTP mutation: **0**
- Vercel deploy/env変更: **0**
- Google Calendar接続/API変更: **0**
- PR #1〜#18 merge/close: **0**
- PR #19: **OPEN / Draft**（GitHub read-only metadataで確認）

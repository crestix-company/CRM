# P0 Security Verification — Local Execution Report

- **実施日:** 2026-10-16
- **リポジトリ/ブランチ:** `crestix-company/CRM` / `audit/aios-stage1-db-inventory`
- **対象コミット:** `c657b92`（実行開始時点）
- **PR #19:** OPEN / Draft / base `main`。この報告を含むdocs-only更新後もDraft維持とする。
**判定:** CRMアプリ層の限定tenantシナリオはPASS。DB RLSとSupabase Data APIによる防御はFAILまたはBLOCKEDのままで、P0完了とは判定しない。

## Environment Isolation

- 実行開始時のシェル環境で `DATABASE_URL`、`DIRECT_URL`、`SUPABASE_URL`、`SUPABASE_DB_URL`、`SUPABASE_ACCESS_TOKEN`、`VERCEL`、`VERCEL_ENV` はすべて未設定。リポジトリ直下に `.env`、`.env.local`、development/test/production用の `.env*` はなかった。値は取得・出力していない。
- 既存Dockerには約41時間稼働している `platform` Supabaseコンテナ群があり、既定の54321〜54327ポートを使用中だった。これらは調査の読み取り以外に一切操作せず、stop/restart/変更していない。Supabase CLIのstack起動・停止も行っていない。
- 独立したHomebrew PostgreSQL 17.11を一時ディレクトリに初期化し、`listen_addresses=127.0.0.1`、port `45422` で起動。接続時にDB自身から `inet_server_addr=127.0.0.1`、`inet_server_port=45422`、`current_database=postgres` を確認した。ポートは起動直前に未使用であることも確認した。
- CRMは一時Git worktree（開始時HEAD `c657b92`）で `127.0.0.1:45430` に限定して起動。Node子プロセスには一時DB URL、必要な実行パス、開発用設定だけを渡し、親プロセスのその他の環境変数を継承させていない。Google OAuth、Calendar、Vercel、本番Supabaseの資格情報・URLは渡していない。
- DBパスワード、テストcookie、SQL fixture、ログ、worktree、Next build成果物は一時領域のみ。Prisma Clientはworktreeから共有node_modules symlinkを通じて生成された（ignoredの生成物のみで、tracked source変更なし）。秘密値・cookie値・ローカル接続文字列は本成果物に含めていない。実行後、CRMプロセスと一時PostgreSQLを停止し、一時領域を破棄済み。

## Migration Audit

21個すべての `prisma/migrations/*/migration.sql` を順序・DDL/DML・DROP・extension・制約の観点で確認した。空DBへ `prisma migrate deploy` を一度実行し、21/21成功。ターゲットDBの空性・loopback接続・migration ownerを確認するまで実行していない。

| # | Migration | 目的・変更の要点 | 空DB実行上の注意/結果 |
|---:|---|---|---|
| 1 | `20260612000000_init` | 組織・ユーザー・独自session、会社/Contact/Deal、活動、タスク、フォーム、予約などCRM基盤 | 初期DDL。空DBに適用成功 |
| 2 | `20260613000000_phase4` | `saved_views` | 空DBに適用成功 |
| 3 | `20260618000000_remove_external_email_accounts` | `email_accounts` をDROP | **唯一のDROP TABLE**。Migration 1が作成した空表を削除。既存DBに実データがあれば不可逆な損失候補 |
| 4 | `20260619043656_business_units` | BusinessUnit/BusinessUnitMembership、Deal/Form/Pipelineとの紐付け、索引 | 旧索引3件をDROPして再構成。空DBに適用成功 |
| 5 | `20260619065918_phase2_kpi_foundation` | Product/PriceBook、DealLineItem/Participant、KPI/metric、performance、calendar、action plan等 | 多数の新テーブル、enum、FK。FKのCASCADEは将来の親行削除時に作用。Migration自体は適用成功 |
| 6 | `20260622024137_phase3b_sales_foundation` | Sales金額基準、商品添付、失注理由、Deal要件/アラート | 旧索引2件をDROP。空DBに適用成功 |
| 7 | `20260622025927_phase3b_price_fees` | PriceBookの初期費用列 | 空DBに適用成功 |
| 8 | `20260622042427_phase3c_delivery_projects` | Delivery Pipeline/Project/Template/Items/Handoff/History、Deal等の列 | 新enum・テーブル・FK/索引。空DBに適用成功 |
| 9 | `20260622055100_phase3d_forms_scheduling_google` | Form version/routing、availability、booking hold、Google Calendar connection/OAuth/watch等 | 旧索引2件をDROP。Google接続やAPI呼出しは発生しない。空DBに適用成功 |
| 10 | `20260622060000_phase3d_booking_overlap_constraint` | `btree_gist` extensionとMeetingBookingのhost/time重複排除constraint | 空DBでextension利用可能を事前確認。既存予約があるDBでは制約追加時に失敗し得る |
| 11 | `20260622062548_phase3e_google_calendar_hardening` | Calendar同期job/operational event、接続・watch状態列 | 外部Google接続なし。空DBに適用成功 |
| 12 | `20260622062600_phase3e_unique_idempotency_indexes` | MeetingBookingの部分unique index 3件 | 既存重複値があると適用不能。空DBに適用成功 |
| 13 | `20260623010000_phase3f_appointments_activity_analysis` | Form purpose、sales territory/industry/campaign/call-list、booking分析列 | enum・テーブル・索引・FK。空DBに適用成功 |
| 14 | `20260623020000_meeting_booking_idempotency_unique` | MeetingBookingの組織別idempotency unique index | 既存重複があれば適用不能。空DBに適用成功 |
| 15 | `20260623030000_daily_metric_field_configs` | 日次metric field config、FK/indexと初期設定INSERT | INSERTは既存metric定義×active BU×IS/FS/CSから生成。fixture前の空状態で対象0件、生成0行 |
| 16 | `20260623040000_appointment_capture_links` | Appointment capture capability link | 空DBに適用成功 |
| 17 | `20260623050000_task_reminders_notifications` | Reminder/Notification enum、テーブル、FK | 空DBに適用成功 |
| 18 | `20260623060000_delivery_project_company_backfill` | ObjectAssociation経由でProjectのCompany/snapshotを補完 | UPDATE対象Delivery Project 0件。空DBで変更0行 |
| 19 | `20260625043000_backfill_deal_stage_required_fields` | 営業stage名に応じてrequired fieldsを補完 | UPDATE対象PipelineStage 0件。空DBで変更0行 |
| 20 | `20260729010000_deal_line_item_workflow` | DealLineItem status enumにplanned/considering/billedを追加 | 空DBに適用成功 |
| 21 | `20260729010100_deal_line_item_workflow_fields` | DealLineItem meeting_atとstatus default=planned | 空DBに適用成功 |

静的検査で、行データを変えるmigrationは #15 INSERT、#18 UPDATE、#19 UPDATEの3件。適用後・fixture投入前の件数はそれぞれ `daily_metric_field_configs=0`、`delivery_projects=0`、`pipeline_stages=0`。さらに #3 の `email_accounts` DROPは空表だけに作用した。明示的なTRUNCATE/DELETE FROMは検出されなかった。DROP INDEXは7件で、データ行削除ではないが、前提となる既存オブジェクトとの差分確認なしに別DBへ適用すべきではない。

## Local Setup

- DB初期化前: public schemaのrelation 0件、`btree_gist` available、migration roleは一時DBのsuperuserであることを照合。
- Migration後: `_prisma_migrations` 21/21成功、public base table 80件、`email_accounts`不存在、対象バックフィル0行。
- Synthetic fixture: 組織2、ユーザー3（うちOrg Aのsuspended member 1）、BusinessUnit 3、clinic会社2、session 2。すべて本番由来でない固定テスト値と `invalid.example` のみ。Google Calendar接続、OAuth token、外部API呼出しは作成していない。
- CRMテスト用POSTでOrg Aに合成会社1件（および通常の関連activity）が作られた。未認証POST用マーカーは0件。最終会社件数はOrg A=2、Org B=1。
- Supabase/PostgRESTを含む新規Docker stackではなくnative PostgreSQLを採用したのは、既存stackのコンテナと既定ポートに干渉しないため。したがって本環境はCRM Prisma/APIのtenant経路を確認できるが、Supabase Data APIの完全な再現環境ではない。

## Security Tests（PASS / FAIL / BLOCKED）

| テスト | 結果 | 根拠 |
|---|---|---|
| DB接続先のloopback確認、空DB・extension・migration完了 | PASS | DB内の `inet_server_addr()` と `inet_server_port()`、catalog照合、21/21 migration |
| 未認証 `GET /api/companies` | PASS | HTTP 401 |
| Org Aの有効cookieで会社一覧 | PASS | HTTP 200、Synthetic Clinic Alphaのみ。Org BのBetaは応答に含まれない |
| Org AユーザーのsessionがOrg Bを選択（Org B membershipなし） | PASS | HTTP 401 |
| 未認証 `POST /api/companies` | PASS | HTTP 401、DB上の未認証マーカー0件 |
| Org AからOrg BのorganizationIdをpayloadに指定して会社作成 | PASS | HTTP 201だが作成先はOrg A。Org B行は読めず、Org Bの件数不変 |
| BusinessUnitMembershipを持たない有効Org A memberが同じOrgのactive BUを選択 | PASS | `/api/business-units/select` HTTP 200 |
| Org A memberによるOrg B BU選択 | PASS | HTTP 403 |
| Supabase Data API匿名・認証済みHTTPアクセス、実際に露出するrelationとwrite範囲 | BLOCKED | 独立DBにPostgRESTがなく、`anon`/`authenticated` roleも未作成。既存Supabase stackは共有対象として触れず、Hosted接続情報も使っていない |
| DB RLSによるtenant境界（policy評価） | FAIL / 未実施 | Prisma schema migration後の80表すべてRLS off、policy 0。test-only RLS/GRANT適用はこの承認に含まれず未実施。従ってDB層がtenant越境を遮断するとは言えない |
| 本番Prisma runtime roleのBYPASSRLS/owner/GRANT | BLOCKED | Production資格情報を受け取らず、Productionへ接続していない。ローカル検証接続はpostgres superuser/BYPASSRLS=trueで、本番の役割を示さない |
| Data API/Calendar/Webhook/Cronの実ネットワーク経路 | BLOCKED | 外部接続資格情報なし・経路未実行。Migration/アプリBuildによるCalendar接続変更はなし |

DBカタログ上、ローカルの `anon`/`authenticated` roleは0、RLS有効表0/80、policy 0。これはPrisma migrationだけで作ったbaselineの事実であり、Hosted Supabaseの現行GRANT・Data API設定が同一であるという主張ではない。Stage1のProduction READ ONLY snapshotに記録された「80/80 RLS off、policy 0、anon/authenticated broad grants」は過去の調査時点の根拠として維持し、今回のローカル結果と混同しない。

## Existing CRM Regression

- `npm test`: 30 test files / 187 tests PASS（認証、権限、Google Calendar task sync等の既存unit testsを含む）。
- `npm run typecheck`: PASS。
- `npm run lint`: PASS。
- 一時worktreeで `npm run build`: Prisma Client generationとNext.js 15.5.19 production build PASS。`BOOTSTRAP_DATABASE_ON_BUILD`を設定せず、Vercel deployやProduction migrationは行っていない。build時DATABASE_URLも一時loopback DBのみ。
- API smoke testsではGoogle、Calendar、Webhook、Cron、メール送信を呼び出していない。build/testsでも外部Google/Vercel資格情報を渡していない。
- `GET /api/business-units` はsynthetic ADMIN roleで403となった。このrouteは `MANAGE_ORGANIZATION` を要求し、現permission mapではSUPER_ADMIN限定。一般画面の `getAccessibleBusinessUnits()` はACTIVEかつorganizationId一致で取得する実装で、BusinessUnitMembershipをread ACLにしていない。今回は画面E2Eを行っていないため、403は管理API権限の観測値として記録し、業務上の期待動作は要確認とする。
- 検証したAPIはcompaniesとBusinessUnit selectionの限定シナリオであり、全API routeやpublic capability、Google webhook、Cronの回帰を保証しない。

## Remaining P0 Risks

1. Stage1のProduction snapshotではpublic 80/80 RLS off・0 policy・anon/authenticated broad grantsが観測済み。今回のProduction再検証はなし。Hosted Data APIが有効であれば、実際にどの表がREST/GraphQLで到達可能か、SELECT/INSERT/UPDATE/DELETEの範囲は未確認。
2. Production Prisma接続roleがowner/superuser/`BYPASSRLS`か、pooler/session mode、role inheritance、default privileges、schema exposureは未確認。アプリ層の `getAuthContext()` はcookie sessionを使うが、DBにtenant contextを渡す仕組みはソース上確認できない。
3. Supabase Auth JWTとCRM独自sessionは別の認証体系。RLSで `auth.uid()` をCRM user IDと同一視できない。runtime roleやsession context設計なしの一括RLS有効化は、過剰許可または全件不可視化の危険がある。
4. Calendar webhook、public booking/form/capture、Google Forms、Cron等はcookie認証を使わずPrismaへ接続する経路がある。RLS導入時には個別tenant/capability contextと回帰試験が必要。
5. 外部REST/GraphQLクライアント、BI、運用スクリプト、他の稼働中デプロイの棚卸しは未完了。Repository検索で未発見でも外部利用がない証明にはならない。

## Production Change Recommendation（提案のみ）

現時点で本番DBのGRANT変更、RLS/Policy追加、Migration、Data API設定変更、本番デプロイは提案しない。先に本番へ書き込まない以下の確認を承認済みの読み取り専用経路で実施する。

1. Hosted project/schema exposure、全80表のACL/default ACL、view/function/sequence権限、owner、role membership、runtime role属性（特にsuperuser/BYPASSRLS）をrow dataなしで再取得。
2. Data API匿名/認証済みの実アクセス検証は、本番でなく新規の独立Preview DBへsynthetic fixtureと同一schemaを用意して実施。既存稼働Supabase stackの再利用はしない。
3. 次の承認ゲートとして、test-only RLS/GRANT SQL、限定runtime role、CRM sessionからtransaction-local tenant contextを渡す実装案、全consumer試験、完全再作成によるrollbackを別文書で提示する。承認前には適用しない。
4. Previewでpositive/negative/API/capability/webhook/cron/booking testsが通り、Data API access matrixとrole isolationが説明可能になった後にのみ、本番変更の設計・段階的適用・rollback案を別途審査する。

## Next Approval Required

優先順の次の人間判断:

1. **P0 / read-only:** Production Supabaseのcatalog/API設定を読む専用アクセスまたは、人間実行によるsanitized catalog出力を許可するか。必要理由は現行runtime role・GRANT・Data API露出を古いsnapshotでなく現在値として確定するため。
2. **P0 / non-production write:** 新しい独立Preview DB（既存stack/projectから分離）に限定したtest-only role/GRANT/RLS適用を別申請で許可するか。許可時は対象名、正確なDDL、fixture、全API試験、rollback/recreateを先に提示し、承認後に実行する。
3. **P1 / business owner:** `GET /api/business-units` がADMINで403、SUPER_ADMINのみ可能な現行仕様が期待どおりか。一般のactive memberに必要なのは一覧APIか、管理画面以外のread pathかを判断する。
4. Previewで全項目がPASSになるまで、Production修正・Migration・Vercel deployは追加承認しない。PR #19はDraft維持、PRのMerge/Closeなし。

**Production Writes:** 0

**Production/Vercel/Google Calendar mutations:** 0

**Migration実行先:** 一時native PostgreSQL `127.0.0.1:45422` のみ

**RLS/GRANT変更:** 0

**PR #1〜#18 merge/close:** 0

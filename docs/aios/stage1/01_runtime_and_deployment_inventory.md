# Runtime and Deployment Inventory

## GitHub

- `origin/main`: `0c3045a`、監査branch baseと一致。
- Open PR: #1〜#18。#18は`fix/google-calendar-legacy-token-guard`→`main`のDraftで未マージ。
- #18 head: `b5ff99a`。Vercel Preview statusは旧`crm`と新`crestix-aios-crm`の両方SUCCESSだが、機能試験完了を意味しない。
- 本監査はPR #18のbranch、内容、Draft状態を変更していない。

## Application runtime

| Item | Verified value |
|---|---|
| Framework | Next.js 15.5.19 / React 19 |
| ORM | Prisma 6.5.0 |
| Database | PostgreSQL via `DATABASE_URL` |
| Auth | application-managed opaque cookie + `auth_sessions` |
| Build | `node scripts/vercel-build.mjs` |
| Feature flags | legacy import、Google integration/webhook、public scheduling、form builder v2 |

`.env.example`にはkey名のみ存在し、secret値は調査対象外。build bootstrap flagsはrepo exampleに存在せず、統合Markdownで言及されたVercel値は対象teamを閲覧できずUNVERIFIED。

## Supabase

- Project `xtspgevvntpidkmyfwes` / name `CRM` / ap-northeast-1 / ACTIVE_HEALTHY。
- PostgreSQL 17.6、public base table 80。
- Management APIのlogin roleはquery時`postgres`だったが、通常Next.js runtimeの接続role/URLはsecret未取得のため**UNVERIFIED**。
- AppはSupabase client/Auth SDKではなくPrisma DB接続と自前sessionを使用する。Data APIはアプリの通常経路ではないが、public grantsにより別攻撃面として公開されている。

## Vercel

GitHub statusから次のdeployment integrationは存在する。

| Project/context | Evidence | Commit/config |
|---|---|---|
| `crm` (legacy) | GitHub deployment checks | Production commit、env key presenceはUNVERIFIED |
| `crestix-aios-crm` (new) | GitHub deployment checks | Production commit、env key presenceはUNVERIFIED |

ローカルVercel CLIのログインidentityは対象team `hiroyukimaekawa-langs-projects` / `shonishita-6132s-projects`へアクセスできず、project inspect/env listは不可。したがって旧/新ProductionのGit接続先、production SHA、環境変数key presence比較はBLOCKED。secret値を取得する操作は行っていない。

## Deployment risk

1. 同一DBを旧/新Vercelが参照する前提は統合Markdown由来で、env実査はUNVERIFIED。
2. 通常API書込みはbootstrap flagでは止まらない。
3. Google接続2件はv1。新環境がv2 keyで接続処理を行うと競合し得る。#18はfail-closed guard案だがDraft維持。
4. Vercel checksだけではDB、OAuth、tenant isolationのE2Eを証明しない。

## Required follow-up access

対象Vercel teamのread-only viewer権限で、project name/domain、production/preview SHA、Git repo/branch、env key名とenvironment scope、deployment protection、cron設定を再監査する。値は引き続き出力しない。

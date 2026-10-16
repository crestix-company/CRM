# Security / Grants / RLS

## Release blocker

Production `public`の80/80 base tablesでRLSが無効、RLS policyは0件。`anon`と`authenticated`は80/80テーブルに`SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER`を持つ。各role 560 privilege rows、書込系320 privilege rows。これはData API経由の認可不備につながり得る重大リスクであり、Stage2 release blocker。

特に`User.password_hash`、`auth_sessions.token_hash`、Google token暗号文、OAuth state、audit logを含むテーブルも同じgrant patternである。暗号文/ハッシュ自体を本レポートへ取得していない。

## Boundary model

- Next.js normal path: Prisma + application session。`getAuthContext()`がactive sessionとactive OrganizationMembershipを確認。
- Tenant predicate: route/serviceが`context.organization.id`をPrisma `where/data`へ入れる。
- BusinessUnit: read ACLではない。active organization memberは全active unitを取得できる。
- Database: runtime roleはUNVERIFIED。Management API audit roleは`postgres`。
- Data API: `public` schema + anon/auth grantsからexposure riskあり。全80テーブルでanon SELECTを確認。

## Code observations

1. 多くのrouteは`getAuthContext()`とpermissionを使用する。
2. public intake、OAuth callback、webhook、cronは別boundaryであり、token/state/secret検証に依存。
3. fixed role permissionのみで、個別例外/部署階層/Human Gateはmainにない。
4. `src/lib/security.ts`はproduction env keyを想定するが、default fallbackも存在する。production env presenceはVercel権限不足でUNVERIFIED。
5. SECURITY DEFINER functionはpublicで0件。

## Do not hot-fix production

即時の一括RLS enable/revokeは、Prisma接続roleとData API/public endpointsを停止させる恐れがある。次のpreview/scratch順序が必要。

1. 実runtime DB role、pooler mode、Data API利用者を特定。
2. public endpointを含むquery matrixを作る。
3. 新しいleast-privilege runtime roleを設計。
4. GRANT revokeとRLS policyをpreview cloneで適用。
5. tenant-crossing negative tests、anon REST tests、migration rollbackを実施。
6. limited canary後にproduction gateを承認。

## Acceptance gate

- anon/authenticated/PUBLICの不要write grant 0。
- exposed tableは明示allowlistのみ。
- 全exposed table RLS ON、policyがorganization isolationを保証。
- Prisma roleがBYPASSRLSか否か、責任境界を文書化。
- cross-tenant IDを送っても0/404/403で他tenantデータ非開示。
- auth/session/Google token tablesはData APIから非公開。

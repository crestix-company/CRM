# CRM UI / API / Auth / Role Inventory

## 結論

現行mainは45画面、153 API route、79 Prisma modelsを持つ広いCRMで、Company/Contact/Deal/Task/MeetingBooking/Delivery/KPI/Product/Import/Google CalendarをKEEP/EXTENDできる。一方、医院カルテ、法人→医院階層、契約/請求/入金、AI Artifact、Human Gate、MeetingRecord/Minutes/Decisionはmainに存在しない。

認証はopaque session cookie→AuthSession→active OrganizationMembership。tenant keyは `getAuthContext().organization.id` から得る。Roleは SUPER_ADMIN/ADMIN/MANAGER/USER/READ_ONLY。BusinessUnitはread ACLではなく、active organization memberは全active unitを閲覧可能（`src/lib/business-units.ts`）。

## Role / permission

| Role | Main rights |
|---|---|
| SUPER_ADMIN | 全16 permission |
| ADMIN | CRM delete、設定、監査、import/exportを含む（organization管理のみ除外） |
| MANAGER | CRM read/write、pipeline/target/delivery管理、import/export |
| USER | CRM read/write、import/export |
| READ_ONLY | CRM read、export |

Permission catalog: CRM_READ/WRITE/DELETE, pipeline/member/organization/custom-property/KPI/target/calendar/product/sales/delivery management, audit read, import/export。個別例外・部署階層scope・approval権限はmainにはない。

## 画面一覧 (53)

| Route source | Area |
|---|---|
| `(app)/appointments/new` | Other/Public/Auth |
| `(app)/companies/[id]/edit` | Company |
| `(app)/companies/[id]` | Company |
| `(app)/companies/new` | Company |
| `(app)/companies` | Company |
| `(app)/contacts/[id]/edit` | 担当者(Contact) |
| `(app)/contacts/[id]` | 担当者(Contact) |
| `(app)/contacts/new` | 担当者(Contact) |
| `(app)/contacts` | 担当者(Contact) |
| `(app)/conversations` | Other/Public/Auth |
| `(app)/daily-metrics` | KPI/Report |
| `(app)/dashboard` | KPI/Report |
| `(app)/deals/[id]/edit` | Deal |
| `(app)/deals/[id]` | Deal |
| `(app)/deals/board` | Deal |
| `(app)/deals/new` | Deal |
| `(app)/deals` | Deal |
| `(app)/delivery-projects/[id]` | CS/Delivery |
| `(app)/delivery-projects/board` | CS/Delivery |
| `(app)/delivery-projects` | CS/Delivery |
| `(app)/forms/[id]` | Other/Public/Auth |
| `(app)/forms` | Other/Public/Auth |
| `(app)/imports/[id]` | Import |
| `(app)/imports/legacy-excel` | Import |
| `(app)/imports/legacy-progress` | Import |
| `(app)/imports` | Import |
| `(app)/meetings` | Task/Meeting |
| `(app)/notifications` | Other/Public/Auth |
| `(app)/operations` | Other/Public/Auth |
| `(app)/organizations/new` | Other/Public/Auth |
| `(app)/reports` | KPI/Report |
| `(app)/settings/appointment-capture-links` | Settings |
| `(app)/settings/appointment-form` | Settings |
| `(app)/settings/business-units` | Settings |
| `(app)/settings/custom-properties` | Settings |
| `(app)/settings/daily-metric-fields` | Settings |
| `(app)/settings/delivery-pipelines` | CS/Delivery |
| `(app)/settings/email-templates` | Settings |
| `(app)/settings/kpis` | Settings |
| `(app)/settings/members` | Settings |
| `(app)/settings` | Settings |
| `(app)/settings/pipelines` | Settings |
| `(app)/settings/products` | Settings |
| `(app)/settings/targets` | Settings |
| `(app)/tasks` | Task/Meeting |
| `(auth)/invite/[token]` | Other/Public/Auth |
| `(auth)/login` | Other/Public/Auth |
| `(auth)/register` | Other/Public/Auth |
| `a/[token]` | Other/Public/Auth |
| `chat/[organizationSlug]` | Other/Public/Auth |
| `f/[slug]` | Other/Public/Auth |
| `meet/[slug]` | Other/Public/Auth |
| `page.tsx` | Other/Public/Auth |

## API一覧 (153)

判定はsourceに `getAuthContext()` があるものを AUTH、cron secretをCRON、その他をPUBLIC/STATE/WEBHOOKとして機械分類した。callback/webhookはcookie認証でないことが正常なため、個別のstate/token検証が必須。

| Route | Methods | Boundary |
|---|---|---|
| `/api/action-plans/[id]/complete` | POST | AUTH |
| `/api/action-plans/[id]` | PATCH | AUTH |
| `/api/action-plans` | GET,POST | AUTH |
| `/api/activities` | GET,POST | AUTH |
| `/api/appointment-capture-links/[id]/revoke` | POST | AUTH |
| `/api/appointment-capture-links/[id]/rotate` | POST | AUTH |
| `/api/appointment-capture-links` | GET,POST | AUTH |
| `/api/appointment-form-config/duplicate-published` | POST | AUTH |
| `/api/appointment-form-config/publish` | POST | AUTH |
| `/api/appointment-form-config/restore` | POST | AUTH |
| `/api/appointment-form-config` | GET,PUT | AUTH |
| `/api/appointments` | POST | AUTH |
| `/api/associations/[id]` | DELETE | AUTH |
| `/api/associations` | GET,POST | AUTH |
| `/api/attachment-rules/[id]` | PATCH,DELETE | AUTH |
| `/api/attachment-rules` | GET,POST | AUTH |
| `/api/auth/login` | POST | PUBLIC/STATE/WEBHOOK |
| `/api/auth/logout` | POST | PUBLIC/STATE/WEBHOOK |
| `/api/auth/register` | POST | PUBLIC/STATE/WEBHOOK |
| `/api/availability` | POST | AUTH |
| `/api/bookings/[id]/cancel` | POST | AUTH |
| `/api/bookings/[id]/external-change` | POST | AUTH |
| `/api/bookings/[id]/reschedule` | POST | AUTH |
| `/api/bookings/[id]/result` | POST | AUTH |
| `/api/bookings/[id]/sync` | POST | AUTH |
| `/api/business-calendars` | GET,POST | AUTH |
| `/api/business-unit-memberships` | POST | AUTH |
| `/api/business-units/[id]` | PATCH | AUTH |
| `/api/business-units` | GET,POST | AUTH |
| `/api/business-units/select` | POST | AUTH |
| `/api/companies/[id]` | GET,PATCH,DELETE | AUTH |
| `/api/companies` | GET,POST | AUTH |
| `/api/contacts/[id]` | GET,PATCH,DELETE | AUTH |
| `/api/contacts` | GET,POST | AUTH |
| `/api/cron/task-reminders` | POST | CRON_SECRET |
| `/api/custom-properties/[id]` | PATCH,DELETE | AUTH |
| `/api/custom-properties` | GET,POST | AUTH |
| `/api/daily-metric-field-configs/[id]` | PATCH | AUTH |
| `/api/daily-metric-field-configs/reorder` | PUT | AUTH |
| `/api/daily-metric-field-configs` | POST | AUTH |
| `/api/daily-metrics/[id]/approve` | POST | AUTH |
| `/api/daily-metrics/[id]/lock` | POST | AUTH |
| `/api/daily-metrics/[id]/unlock` | POST | AUTH |
| `/api/daily-metrics` | GET,PUT | AUTH |
| `/api/daily-metrics/submit` | POST | AUTH |
| `/api/deal-line-items/[id]` | PATCH,DELETE | AUTH |
| `/api/deal-line-items/[id]/workflow` | PATCH | AUTH |
| `/api/deals/[id]/line-items` | GET,POST | AUTH |
| `/api/deals/[id]` | GET,PATCH,DELETE | AUTH |
| `/api/deals/[id]/sales-assignments` | PATCH | AUTH |
| `/api/deals/[id]/stage/preflight` | POST | AUTH |
| `/api/deals/[id]/stage` | PATCH | AUTH |
| `/api/deals` | GET,POST | AUTH |
| `/api/delivery-pipeline-stages/[id]` | PATCH,DELETE | AUTH |
| `/api/delivery-pipeline-stages` | POST | AUTH |
| `/api/delivery-pipelines/[id]` | PATCH | AUTH |
| `/api/delivery-pipelines` | GET,POST | AUTH |
| `/api/delivery-project-templates/[id]` | PATCH | AUTH |
| `/api/delivery-project-templates` | GET,POST | AUTH |
| `/api/delivery-projects/[id]/cross-sell` | POST | AUTH |
| `/api/delivery-projects/[id]/handoff/accept` | POST | AUTH |
| `/api/delivery-projects/[id]/handoff/reject` | POST | AUTH |
| `/api/delivery-projects/[id]/handoff/submit` | POST | AUTH |
| `/api/delivery-projects/[id]` | GET,PATCH | AUTH |
| `/api/delivery-projects/[id]/sync-scope` | POST | AUTH |
| `/api/delivery-projects/[id]/transition` | POST | AUTH |
| `/api/delivery-projects/bulk-create` | POST | AUTH |
| `/api/delivery-projects/eligible-deals` | GET | AUTH |
| `/api/delivery-projects` | GET,POST | AUTH |
| `/api/email-logs` | POST | AUTH |
| `/api/email-templates/[id]` | PATCH,DELETE | AUTH |
| `/api/email-templates` | GET,POST | AUTH |
| `/api/exports/[objectType]` | GET | AUTH |
| `/api/field-visits` | POST | AUTH |
| `/api/forecast` | GET | AUTH |
| `/api/forms/[id]/duplicate` | POST | AUTH |
| `/api/forms/[id]/publish` | POST | AUTH |
| `/api/forms/[id]` | PATCH,DELETE | AUTH |
| `/api/forms/[id]/submissions` | GET | AUTH |
| `/api/forms` | GET,POST | AUTH |
| `/api/google-calendar/webhook` | POST | PUBLIC/STATE/WEBHOOK |
| `/api/imports/[id]` | GET | AUTH |
| `/api/imports/execute` | POST | AUTH |
| `/api/imports/legacy-excel/apply` | POST | AUTH |
| `/api/imports/legacy-excel/cleanup-duplicates` | POST | AUTH |
| `/api/imports/legacy-excel/dry-run` | POST | AUTH |
| `/api/imports/legacy-excel/refresh-dates` | POST | AUTH |
| `/api/imports/legacy-excel/repair-associations` | POST | AUTH |
| `/api/imports/legacy-progress/apply` | POST | AUTH |
| `/api/imports/legacy-progress/dry-run` | POST | AUTH |
| `/api/imports/preview` | POST | AUTH |
| `/api/industries/bootstrap` | POST | AUTH |
| `/api/integrations/google-calendar/calendars` | GET,PUT | AUTH |
| `/api/integrations/google-calendar/callback` | GET | PUBLIC/STATE/WEBHOOK |
| `/api/integrations/google-calendar/connect` | GET | AUTH |
| `/api/integrations/google-calendar/disconnect` | POST | AUTH |
| `/api/integrations/google-calendar/status` | GET | AUTH |
| `/api/integrations/google-calendar/sync` | POST | AUTH |
| `/api/integrations/google-calendar/test` | POST | AUTH |
| `/api/integrations/google-calendar/watch` | POST | AUTH |
| `/api/invitations/[token]` | GET,POST | PUBLIC/STATE/WEBHOOK |
| `/api/kpi-targets/[id]` | PATCH | AUTH |
| `/api/kpi-targets` | GET,POST | AUTH |
| `/api/loss-reasons/[id]` | PATCH,DELETE | AUTH |
| `/api/loss-reasons` | GET,POST | AUTH |
| `/api/meeting-links/[id]` | PATCH,DELETE | AUTH |
| `/api/meeting-links` | GET,POST | AUTH |
| `/api/metrics/[id]/drilldown` | GET | AUTH |
| `/api/metrics/[id]/preview` | POST | AUTH |
| `/api/metrics/[id]` | GET,PATCH | AUTH |
| `/api/metrics` | GET,POST | AUTH |
| `/api/organizations/invitations` | POST | AUTH |
| `/api/organizations/members/[memberId]` | PATCH | AUTH |
| `/api/organizations` | GET,POST | AUTH |
| `/api/organizations/switch` | POST | AUTH |
| `/api/pipeline-stages/[id]` | PATCH,DELETE | AUTH |
| `/api/pipeline-stages` | POST | AUTH |
| `/api/pipelines/[id]` | PATCH,DELETE | AUTH |
| `/api/pipelines/normalize-imported-stages` | POST | AUTH |
| `/api/pipelines` | GET,POST | AUTH |
| `/api/product-properties/[id]` | PATCH,DELETE | AUTH |
| `/api/products/[id]/prices` | POST | AUTH |
| `/api/products/[id]/properties` | GET,POST | AUTH |
| `/api/products/[id]` | PATCH | AUTH |
| `/api/products` | GET,POST | AUTH |
| `/api/public/appointments/[token]` | POST | PUBLIC/STATE/WEBHOOK |
| `/api/public/chat/[organizationSlug]` | POST | PUBLIC/STATE/WEBHOOK |
| `/api/public/forms/[slug]` | POST | PUBLIC/STATE/WEBHOOK |
| `/api/public/google-forms/appointments/[token]` | POST | PUBLIC/STATE/WEBHOOK |
| `/api/public/meeting-links/[slug]/availability` | GET | PUBLIC/STATE/WEBHOOK |
| `/api/public/meeting-links/[slug]/book` | POST | PUBLIC/STATE/WEBHOOK |
| `/api/public/meeting-links/[slug]/hold` | POST | PUBLIC/STATE/WEBHOOK |
| `/api/public/meetings/[slug]` | POST | PUBLIC/STATE/WEBHOOK |
| `/api/records/[objectType]/[id]/properties` | PATCH | AUTH |
| `/api/referrals` | POST | AUTH |
| `/api/reports/[reportType]/drilldown` | GET | AUTH |
| `/api/reports/attachment-rates` | GET | AUTH |
| `/api/reports/cs/drilldown` | GET | AUTH |
| `/api/reports/cs` | GET | AUTH |
| `/api/reports/loss-analysis` | GET | AUTH |
| `/api/reports/product-performance` | GET | AUTH |
| `/api/reports/sales-progress` | GET | AUTH |
| `/api/reports/salesperson-comparison` | GET | AUTH |
| `/api/required-activities` | GET | AUTH |
| `/api/routing-rules/[id]` | PATCH,DELETE | AUTH |
| `/api/routing-rules` | GET,POST | AUTH |
| `/api/routing-rules/test` | POST | AUTH |
| `/api/saved-views/[id]` | PATCH,DELETE | AUTH |
| `/api/saved-views` | GET,POST | AUTH |
| `/api/tasks/[id]` | PATCH,DELETE | AUTH |
| `/api/tasks/[id]/status` | PATCH | AUTH |
| `/api/tasks/[id]/sync` | POST | AUTH |
| `/api/tasks` | GET,POST | AUTH |

## Background / integration

- Background job: Vercel Cron想定の `/api/cron/task-reminders`。`CRON_SECRET` で保護。設定ファイル上のscheduleはこのrepoでUNVERIFIED。
- Google: OAuth connect/callback/status/calendars/sync/watch/test/disconnect、push webhook、Booking/Task同期。2接続はDBでconnected/v1、refresh token欠損0。
- Public intake: appointment token、form slug、meeting-link booking/hold、Google Forms appointment token、organization-slug chat。公開識別子・tokenごとのrate limitはコード内で一貫した共通層が確認できず、Stage2 security review対象。
- Feature flags: legacy Excel、Google integration/webhook、public scheduling、form builder v2。値はVercel権限不足によりUNVERIFIED。

## 主要Gap

| Requirement area | Current | Classification |
|---|---|---|
| Company/Contact/Deal/Task | 実装済み。Contact表示は一部「コンタクト」表記 | KEEP + EXTEND（表示を担当者へ統一） |
| 医院カルテ360° | 専用Hospital/Clinic profileなし | NEW/LINK |
| 法人→医院→担当者→複数Deal | polymorphic associationのみ | EXTEND/LINK |
| DealLineItem収益/粗利 | 実装済み | KEEP |
| DealParticipant/SalesPerformanceEvent | 実装済み | KEEP |
| Contract/Invoice/Payment/CloudSign | model/APIなし | NEW |
| MeetingRecord/Minutes/Decision | MeetingBookingのみ | NEW |
| AI Artifact/Human Gate | mainなし（PR #14〜#17にdraft stack） | NEW/HOLD |
| CS | DeliveryProjectあり | EXTEND |
| Drive/Comdesk | CRM mainに専用integrationなし | NEW/LINK |
| Google Calendar | 既存、v1/v2安全性未解決 | KEEP + BLOCKER |

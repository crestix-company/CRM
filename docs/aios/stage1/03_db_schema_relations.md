# DB Schema / Relations — Production READ ONLY

- 観測日時: 2026-10-15 21:42 JST前後
- Supabase project ref: `xtspgevvntpidkmyfwes`
- Git SHA: `0c3045acde47bf8a0c2ba4e983d3d0a6e147df36`
- DB: PostgreSQL 17.6 / public base tables: 80
- 方法: Supabase Management API経由、各SQLを `BEGIN READ ONLY ... ROLLBACK` で実行。行データ・秘密値は保存していない。
- 重要所見: 0/80テーブルでRLS有効。すなわち全publicテーブルでRLS無効。

## Drift判定

Prisma modelは79件、実DB public base tableは80件。79業務テーブルはPrisma modelに対応し、残る1件はPrisma管理用`_prisma_migrations`。Prisma migration directoryは21件、DBの完了migrationもdistinct 21件だった。DB履歴には失敗後rollbackされた2行が追加で残るため `_prisma_migrations` は23行。テーブル単位のdriftは検出されなかった。列単位は下表の実DBcatalogを全件記録したが、Prisma型・DB型の意味変換を含む完全自動diffは未実施のため、厳密な型/default driftは **UNVERIFIED**。

## 全テーブル・全列

Soft deleteは実列 `deleted_at` の有無で判定。各列の `DEFAULT` は値そのものを秘密化するため有無だけを示す。

| Table | Prisma model | Rows | RLS | Soft delete | Columns (name:type/nullability/default) |
|---|---|---:|---|---|---|
| `Organization` | `Organization` (schema:798) | 2 | OFF | no | id:uuid NOT_NULL; name:character varying NOT_NULL; slug:character varying NOT_NULL; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `User` | `User` (schema:770) | 9 | OFF | no | id:uuid NOT_NULL; email:character varying NOT_NULL; name:character varying NOT_NULL; password_hash:text NOT_NULL; email_verified_at:timestamp with time zone; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `_prisma_migrations` | UNVERIFIED | 23 | OFF | no | id:character varying NOT_NULL; checksum:character varying NOT_NULL; finished_at:timestamp with time zone; migration_name:character varying NOT_NULL; logs:text; rolled_back_at:timestamp with time zone; started_at:timestamp with time zone NOT_NULL DEFAULT; applied_steps_count:integer NOT_NULL DEFAULT |
| `action_plans` | `ActionPlan` (schema:2477) | 1 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; business_unit_id:uuid; work_function:USER-DEFINED; owner_user_id:uuid; target_id:uuid; metric_definition_id:uuid; title:character varying NOT_NULL; description:text; due_date:date; status:USER-DEFINED NOT_NULL DEFAULT; priority:USER-DEFINED NOT_NULL DEFAULT; completed_at:timestamp with time zone; created_by_user_id:uuid; metadata:jsonb NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `activities` | `Activity` (schema:1158) | 4231 | OFF | yes | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; actor_user_id:uuid; type:USER-DEFINED NOT_NULL; title:character varying NOT_NULL; body:text; metadata:jsonb NOT_NULL DEFAULT; occurred_at:timestamp with time zone NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; deleted_at:timestamp with time zone; delivery_project_id:uuid |
| `appointment_capture_links` | `AppointmentCaptureLink` (schema:1636) | 2 | OFF | no | id:uuid NOT_NULL DEFAULT; organization_id:uuid NOT_NULL; business_unit_id:uuid NOT_NULL; form_id:uuid; form_version_id:uuid; credited_appointment_setter_id:uuid NOT_NULL; name:character varying NOT_NULL; token_hash:character varying NOT_NULL; status:character varying NOT_NULL DEFAULT; expires_at:timestamp with time zone; passcode_hash:text; max_submissions:integer; submission_count:integer NOT_NULL DEFAULT; created_by_user_id:uuid NOT_NULL; last_used_at:timestamp with time zone; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL DEFAULT |
| `assignment_cursors` | `AssignmentCursor` (schema:1706) | 0 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; scope_key:character varying NOT_NULL; last_assigned_user_id:uuid; "position":integer NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `audit_logs` | `AuditLog` (schema:1886) | 79 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; actor_user_id:uuid; action:character varying NOT_NULL; target_type:character varying NOT_NULL; target_id:uuid; before:jsonb; after:jsonb; ip_address:character varying; user_agent:text; created_at:timestamp with time zone NOT_NULL DEFAULT |
| `auth_sessions` | `AuthSession` (schema:964) | 71 | OFF | no | id:uuid NOT_NULL; token_hash:character varying NOT_NULL; user_id:uuid NOT_NULL; active_organization_id:uuid NOT_NULL; expires_at:timestamp with time zone NOT_NULL; last_seen_at:timestamp with time zone NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT |
| `availability_exceptions` | `AvailabilityException` (schema:1389) | 0 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; schedule_id:uuid NOT_NULL; user_id:uuid NOT_NULL; date:date NOT_NULL; is_available:boolean NOT_NULL DEFAULT; start_minutes:integer; end_minutes:integer; reason:character varying; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `availability_rules` | `AvailabilityRule` (schema:1353) | 5 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; user_id:uuid NOT_NULL; weekday:integer NOT_NULL; start_minutes:integer NOT_NULL; end_minutes:integer NOT_NULL; timezone:character varying NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL; is_enabled:boolean NOT_NULL DEFAULT; schedule_id:uuid |
| `availability_schedules` | `AvailabilitySchedule` (schema:1374) | 0 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; user_id:uuid NOT_NULL; timezone:character varying NOT_NULL DEFAULT; name:character varying NOT_NULL DEFAULT; is_default:boolean NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `booking_holds` | `BookingHold` (schema:1718) | 0 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; meeting_link_id:uuid NOT_NULL; host_user_id:uuid; scheduled_start_at:timestamp with time zone NOT_NULL; scheduled_end_at:timestamp with time zone NOT_NULL; token_hash:character varying NOT_NULL; status:USER-DEFINED NOT_NULL DEFAULT; expires_at:timestamp with time zone NOT_NULL; created_at:timestamp with time zone NOT_NULL DEFAULT |
| `business_calendar_exceptions` | `BusinessCalendarException` (schema:2458) | 1 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; calendar_id:uuid NOT_NULL; target_date:date NOT_NULL; is_working_day:boolean NOT_NULL; name:character varying; metadata:jsonb NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `business_calendars` | `BusinessCalendar` (schema:2437) | 3 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; business_unit_id:uuid; name:character varying NOT_NULL; timezone:character varying NOT_NULL DEFAULT; work_week_definition:jsonb NOT_NULL DEFAULT; default_holidays:jsonb NOT_NULL DEFAULT; is_default:boolean NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `business_unit_memberships` | `BusinessUnitMembership` (schema:911) | 9 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; business_unit_id:uuid NOT_NULL; user_id:uuid NOT_NULL; work_function:USER-DEFINED NOT_NULL; is_manager:boolean NOT_NULL DEFAULT; status:USER-DEFINED NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `business_unit_products` | `BusinessUnitProduct` (schema:1931) | 52 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; business_unit_id:uuid NOT_NULL; product_id:uuid NOT_NULL; status:USER-DEFINED NOT_NULL DEFAULT; display_order:integer NOT_NULL DEFAULT; metadata:jsonb NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL; product_kind:USER-DEFINED; auto_create_delivery_project:boolean NOT_NULL DEFAULT; default_delivery_project_template_id:uuid; fulfillment_type:USER-DEFINED; project_grouping_mode:USER-DEFINED NOT_NULL DEFAULT |
| `business_units` | `BusinessUnit` (schema:881) | 6 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; name:character varying NOT_NULL; slug:character varying NOT_NULL; description:text; status:USER-DEFINED NOT_NULL DEFAULT; display_order:integer NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL; amount_metric_basis:USER-DEFINED; confirmed_amount_date_basis:USER-DEFINED |
| `calendar_sync_jobs` | `CalendarSyncJob` (schema:1825) | 0 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; connection_id:uuid; selection_id:uuid; channel_id:character varying; job_type:USER-DEFINED NOT_NULL; status:USER-DEFINED NOT_NULL DEFAULT; correlation_id:character varying NOT_NULL; started_at:timestamp with time zone; finished_at:timestamp with time zone; processed_count:integer NOT_NULL DEFAULT; error_code:character varying; error_message:text; metadata:jsonb NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `call_lists` | `CallList` (schema:2189) | 0 | OFF | no | id:uuid NOT_NULL DEFAULT; organization_id:uuid NOT_NULL; business_unit_id:uuid; campaign_id:uuid; name:character varying NOT_NULL; territory_id:uuid; prefecture_code:character varying; industry_id:uuid; product_id:uuid; record_count:integer NOT_NULL DEFAULT; status:character varying NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `companies` | `Company` (schema:1012) | 1419 | OFF | yes | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; owner_user_id:uuid; name:character varying NOT_NULL; domain:character varying; phone:character varying; industry:character varying; address:text; city:character varying; prefecture:character varying; postal_code:character varying; website_url:text; employee_count:integer; annual_revenue:numeric; custom_fields:jsonb NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL; deleted_at:timestamp with time zone |
| `contacts` | `Contact` (schema:981) | 1378 | OFF | yes | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; owner_user_id:uuid; first_name:character varying; last_name:character varying; email:character varying; phone:character varying; mobile_phone:character varying; job_title:character varying; lifecycle_stage:character varying; lead_status:character varying; source:character varying; memo:text; custom_fields:jsonb NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL; deleted_at:timestamp with time zone |
| `conversations` | `Conversation` (schema:1869) | 1 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; contact_id:uuid; visitor_name:character varying; visitor_email:character varying; message:text NOT_NULL; metadata:jsonb NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT |
| `custom_properties` | `CustomProperty` (schema:1268) | 9 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; object_type:USER-DEFINED NOT_NULL; name:character varying NOT_NULL; label:character varying NOT_NULL; field_type:USER-DEFINED NOT_NULL; options:jsonb NOT_NULL DEFAULT; is_required:boolean NOT_NULL DEFAULT; is_unique:boolean NOT_NULL DEFAULT; "order":integer NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL; business_unit_id:uuid; is_filterable:boolean NOT_NULL DEFAULT; is_reportable:boolean NOT_NULL DEFAULT; is_searchable:boolean NOT_NULL DEFAULT |
| `custom_property_product_scopes` | `CustomPropertyProductScope` (schema:2528) | 6 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; custom_property_id:uuid NOT_NULL; product_id:uuid NOT_NULL; created_at:timestamp with time zone NOT_NULL DEFAULT |
| `daily_metric_entries` | `DailyMetricEntry` (schema:2337) | 187 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; business_unit_id:uuid; metric_definition_id:uuid NOT_NULL; user_id:uuid NOT_NULL; work_function:USER-DEFINED; target_date:date NOT_NULL; value:numeric NOT_NULL; source:USER-DEFINED NOT_NULL DEFAULT; status:USER-DEFINED NOT_NULL DEFAULT; submitted_at:timestamp with time zone; approved_at:timestamp with time zone; approved_by_user_id:uuid; locked_at:timestamp with time zone; comment:text; metadata:jsonb NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL; dimensions:jsonb NOT_NULL DEFAULT; dimension_hash:character varying NOT_NULL DEFAULT |
| `daily_metric_field_configs` | `DailyMetricFieldConfig` (schema:2369) | 42 | OFF | no | id:uuid NOT_NULL DEFAULT; organization_id:uuid NOT_NULL; business_unit_id:uuid NOT_NULL; work_function:USER-DEFINED NOT_NULL; metric_definition_id:uuid NOT_NULL; is_enabled:boolean NOT_NULL DEFAULT; display_order:integer NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL DEFAULT |
| `deal_alert_rules` | `DealAlertRule` (schema:2593) | 3 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; business_unit_id:uuid; pipeline_id:uuid; stage_id:uuid; type:USER-DEFINED NOT_NULL; name:character varying NOT_NULL; threshold_days:integer; config:jsonb NOT_NULL DEFAULT; is_active:boolean NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `deal_line_items` | `DealLineItem` (schema:2009) | 1618 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; deal_id:uuid NOT_NULL; product_id:uuid; price_book_entry_id:uuid; business_unit_id:uuid; name:character varying NOT_NULL; quantity:numeric NOT_NULL DEFAULT; unit_price_amount:numeric; revenue_amount:numeric; gross_profit_amount:numeric; expected_gross_profit_amount:numeric; billing_started_at:date; status:USER-DEFINED NOT_NULL DEFAULT; source:character varying; metadata:jsonb NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL; cancelled_at:date; collected_amount:numeric; collected_at:date; contracted_at:date; custom_fields:jsonb NOT_NULL DEFAULT; expected_revenue_amount:numeric; initial_fee:numeric; loss_reason_id:uuid; loss_reason_note:text; lost_at:timestamp with time zone; recurring_fee:numeric; meeting_at:date |
| `deal_participants` | `DealParticipant` (schema:2056) | 10676 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; deal_id:uuid NOT_NULL; user_id:uuid; work_function:USER-DEFINED; role:USER-DEFINED NOT_NULL; status:USER-DEFINED NOT_NULL DEFAULT; contribution_weight:numeric NOT_NULL DEFAULT; credited_at:timestamp with time zone; snapshot_user_name:character varying; metadata:jsonb NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL; credit_share:numeric |
| `deals` | `Deal` (schema:1083) | 4898 | OFF | yes | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; owner_user_id:uuid; pipeline_id:uuid NOT_NULL; stage_id:uuid NOT_NULL; name:character varying NOT_NULL; amount:numeric; expected_close_date:date; close_date:date; probability:integer NOT_NULL DEFAULT; status:USER-DEFINED NOT_NULL DEFAULT; lost_reason:text; source:character varying; external_id:character varying; custom_fields:jsonb NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL; deleted_at:timestamp with time zone; business_unit_id:uuid; cancelled_at:timestamp with time zone; decision_maker_status:USER-DEFINED NOT_NULL DEFAULT; forecast_category_id:uuid; invalidated_at:timestamp with time zone; legacy_progress:character varying; lost_at:timestamp with time zone; qualification_result:USER-DEFINED NOT_NULL DEFAULT; won_at:timestamp with time zone; loss_reason_note:text; lost_by_user_id:uuid; next_action:character varying; next_action_date:date; next_action_owner_id:uuid; primary_loss_reason_id:uuid; deal_type:USER-DEFINED NOT_NULL DEFAULT; origin_deal_id:uuid; origin_project_id:uuid |
| `delivery_handoffs` | `DeliveryHandoff` (schema:2766) | 1 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; business_unit_id:uuid; delivery_project_id:uuid NOT_NULL; submitted_by_user_id:uuid; assigned_cs_user_id:uuid; status:USER-DEFINED NOT_NULL DEFAULT; handoff_snapshot:jsonb NOT_NULL DEFAULT; checklist_snapshot:jsonb NOT_NULL DEFAULT; submitted_at:timestamp with time zone; accepted_at:timestamp with time zone; accepted_by_user_id:uuid; rejected_at:timestamp with time zone; rejected_by_user_id:uuid; rejection_reason:text; version:integer NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `delivery_pipeline_stages` | `DeliveryPipelineStage` (schema:2628) | 16 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; business_unit_id:uuid; pipeline_id:uuid NOT_NULL; name:character varying NOT_NULL; "order":integer NOT_NULL; color:character varying; stage_type:USER-DEFINED NOT_NULL DEFAULT; stale_days:integer; required_fields:jsonb NOT_NULL DEFAULT; task_templates:jsonb NOT_NULL DEFAULT; is_completed:boolean NOT_NULL DEFAULT; is_paused:boolean NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `delivery_pipelines` | `DeliveryPipeline` (schema:2611) | 2 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; business_unit_id:uuid; name:character varying NOT_NULL; is_default:boolean NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL; is_active:boolean NOT_NULL DEFAULT |
| `delivery_project_items` | `DeliveryProjectItem` (schema:2740) | 3 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; business_unit_id:uuid; delivery_project_id:uuid NOT_NULL; source_deal_line_item_id:uuid; split_key:character varying NOT_NULL DEFAULT; product_id:uuid; product_code_snapshot:character varying; product_name_snapshot:character varying NOT_NULL; quantity_snapshot:numeric NOT_NULL; revenue_amount_snapshot:numeric; gross_profit_amount_snapshot:numeric; custom_fields_snapshot:jsonb NOT_NULL DEFAULT; delivery_status:USER-DEFINED NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `delivery_project_stage_histories` | `DeliveryProjectStageHistory` (schema:2793) | 2 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; business_unit_id:uuid; delivery_project_id:uuid NOT_NULL; from_stage_id:uuid; to_stage_id:uuid; changed_by_user_id:uuid; entered_at:timestamp with time zone NOT_NULL DEFAULT; exited_at:timestamp with time zone; duration_minutes:integer; note:text; created_at:timestamp with time zone NOT_NULL DEFAULT |
| `delivery_project_template_products` | `DeliveryProjectTemplateProduct` (schema:2677) | 4 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; template_id:uuid NOT_NULL; product_id:uuid NOT_NULL; created_at:timestamp with time zone NOT_NULL DEFAULT |
| `delivery_project_templates` | `DeliveryProjectTemplate` (schema:2653) | 3 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; business_unit_id:uuid; name:character varying NOT_NULL; description:text; pipeline_id:uuid; default_cs_team_id:uuid; default_cs_user_id:uuid; default_due_business_days:integer; auto_create:boolean NOT_NULL DEFAULT; handoff_required_fields:jsonb NOT_NULL DEFAULT; default_scope:jsonb NOT_NULL DEFAULT; initial_task_templates:jsonb NOT_NULL DEFAULT; stage_task_templates:jsonb NOT_NULL DEFAULT; is_active:boolean NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `delivery_projects` | `DeliveryProject` (schema:2689) | 491 | OFF | yes | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; business_unit_id:uuid; company_id:uuid; primary_contact_id:uuid; source_deal_id:uuid; template_id:uuid; pipeline_id:uuid; stage_id:uuid; idempotency_key:character varying NOT_NULL; name:character varying NOT_NULL; status:USER-DEFINED NOT_NULL DEFAULT; health_status:USER-DEFINED NOT_NULL DEFAULT; priority:USER-DEFINED NOT_NULL DEFAULT; owner_user_id:uuid; created_by_user_id:uuid; expected_start_date:date; kickoff_date:date; expected_publish_date:date; actual_publish_date:date; completed_at:timestamp with time zone; paused_at:timestamp with time zone; pause_reason:text; next_action:character varying; next_action_date:date; next_action_owner_id:uuid; blocker:text; last_activity_at:timestamp with time zone; handoff_status:USER-DEFINED NOT_NULL DEFAULT; scope_version:integer NOT_NULL DEFAULT; scope_sync_status:USER-DEFINED NOT_NULL DEFAULT; scope_snapshot:jsonb NOT_NULL DEFAULT; handoff_checklist:jsonb NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL; deleted_at:timestamp with time zone |
| `email_templates` | `EmailTemplate` (schema:1336) | 2 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; name:character varying NOT_NULL; subject:character varying NOT_NULL; body:text NOT_NULL; created_by_user_id:uuid NOT_NULL; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `field_visits` | `FieldVisit` (schema:2242) | 8 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; business_unit_id:uuid; owner_user_id:uuid; deal_id:uuid; company_name:character varying NOT_NULL; contact_name:character varying; address:text; status:USER-DEFINED NOT_NULL DEFAULT; visited_at:timestamp with time zone NOT_NULL; connected_at:timestamp with time zone; owner_connected_at:timestamp with time zone; meeting_set_at:timestamp with time zone; appointment_set_at:timestamp with time zone; won_at:timestamp with time zone; same_day_won:boolean NOT_NULL DEFAULT; metadata:jsonb NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `forecast_categories` | `ForecastCategory` (schema:1985) | 12 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; business_unit_id:uuid; key:character varying NOT_NULL; name:character varying NOT_NULL; probability:integer NOT_NULL DEFAULT; status:USER-DEFINED NOT_NULL DEFAULT; display_order:integer NOT_NULL DEFAULT; is_closed:boolean NOT_NULL DEFAULT; is_omitted:boolean NOT_NULL DEFAULT; legacy_aliases:jsonb NOT_NULL DEFAULT; metadata:jsonb NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `form_submissions` | `FormSubmission` (schema:1603) | 25 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; form_id:uuid NOT_NULL; contact_id:uuid; raw_payload:jsonb NOT_NULL; created_at:timestamp with time zone NOT_NULL DEFAULT; assigned_user_id:uuid; company_id:uuid; consent_snapshot:jsonb NOT_NULL DEFAULT; deal_id:uuid; duplicate_candidates:jsonb NOT_NULL DEFAULT; form_version_id:uuid; honeypot_value:character varying; idempotency_key:character varying; ip_address:character varying; meeting_booking_id:uuid; normalized_payload:jsonb NOT_NULL DEFAULT; routing_result:jsonb NOT_NULL DEFAULT; routing_rule_id:uuid; user_agent:character varying |
| `form_versions` | `FormVersion` (schema:1578) | 6 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; business_unit_id:uuid; form_id:uuid NOT_NULL; version:integer NOT_NULL; status:USER-DEFINED NOT_NULL DEFAULT; name_snapshot:character varying NOT_NULL; description_snapshot:text; field_schema:jsonb NOT_NULL; mapping_schema:jsonb NOT_NULL; routing_config_snapshot:jsonb NOT_NULL; scheduling_config_snapshot:jsonb NOT_NULL; submit_button_text_snapshot:character varying NOT_NULL DEFAULT; completion_message_snapshot:text; published_by_user_id:uuid; published_at:timestamp with time zone; created_at:timestamp with time zone NOT_NULL DEFAULT |
| `forms` | `Form` (schema:1535) | 7 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; name:character varying NOT_NULL; slug:character varying NOT_NULL; fields:jsonb NOT_NULL DEFAULT; submit_button_text:character varying NOT_NULL DEFAULT; redirect_url:text; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL; business_unit_id:uuid; appointment_credit_fixed_user_id:uuid; appointment_credit_policy:USER-DEFINED NOT_NULL DEFAULT; assignment_mode:USER-DEFINED NOT_NULL DEFAULT; completion_message:text; description:text; fixed_assignee_user_id:uuid; google_fallback_mode:character varying NOT_NULL DEFAULT; mapping_schema:jsonb NOT_NULL DEFAULT; meeting_link_id:uuid; pipeline_id:uuid; privacy_consent_version:character varying; published_version_id:uuid; routing_config:jsonb NOT_NULL DEFAULT; scheduling_config:jsonb NOT_NULL DEFAULT; stage_id:uuid; status:USER-DEFINED NOT_NULL DEFAULT; target_product_id:uuid; team_id:uuid; work_function:USER-DEFINED DEFAULT; form_purpose:USER-DEFINED NOT_NULL DEFAULT; is_internal:boolean NOT_NULL DEFAULT; is_default_for_business_unit:boolean NOT_NULL DEFAULT |
| `google_calendar_connections` | `GoogleCalendarConnection` (schema:1736) | 2 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; user_id:uuid NOT_NULL; provider_account_id:character varying; google_email:character varying; status:USER-DEFINED NOT_NULL DEFAULT; encrypted_access_token:text; encrypted_refresh_token:text; access_token_expires_at:timestamp with time zone; granted_scopes:ARRAY DEFAULT; selected_write_calendar_id:character varying; selected_write_calendar_name:character varying; last_connected_at:timestamp with time zone; last_refreshed_at:timestamp with time zone; last_error_code:character varying; last_error_message:text; revoked_at:timestamp with time zone; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL; encryption_key_version:character varying NOT_NULL DEFAULT |
| `google_calendar_selections` | `GoogleCalendarSelection` (schema:1763) | 1 | OFF | no | id:uuid NOT_NULL; connection_id:uuid NOT_NULL; google_calendar_id:character varying NOT_NULL; calendar_name:character varying NOT_NULL; access_role:character varying; is_write_calendar:boolean NOT_NULL DEFAULT; use_for_busy_check:boolean NOT_NULL DEFAULT; timezone:character varying; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL; last_full_sync_at:timestamp with time zone; last_incremental_sync_at:timestamp with time zone; last_sync_error_code:character varying; last_sync_error_message:text; last_sync_status:USER-DEFINED; sync_token:text; sync_token_invalidated_at:timestamp with time zone |
| `google_calendar_watch_channels` | `GoogleCalendarWatchChannel` (schema:1802) | 3 | OFF | no | id:uuid NOT_NULL; connection_id:uuid NOT_NULL; google_calendar_id:character varying NOT_NULL; channel_id:character varying NOT_NULL; resource_id:character varying; encrypted_channel_token:text; sync_token:text; status:USER-DEFINED NOT_NULL DEFAULT; expires_at:timestamp with time zone; last_notification_at:timestamp with time zone; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL; last_message_number:bigint; last_renewal_attempt_at:timestamp with time zone; last_renewal_error:text; notification_count:integer NOT_NULL DEFAULT |
| `google_oauth_states` | `GoogleOAuthState` (schema:1787) | 3 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; user_id:uuid NOT_NULL; state_hash:character varying NOT_NULL; code_verifier:character varying; redirect_path:character varying; expires_at:timestamp with time zone NOT_NULL; consumed_at:timestamp with time zone; created_at:timestamp with time zone NOT_NULL DEFAULT |
| `import_jobs` | `ImportJob` (schema:1293) | 8 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; uploaded_by_user_id:uuid NOT_NULL; object_type:character varying NOT_NULL; status:USER-DEFINED NOT_NULL DEFAULT; total_rows:integer NOT_NULL DEFAULT; success_count:integer NOT_NULL DEFAULT; error_count:integer NOT_NULL DEFAULT; skipped_count:integer NOT_NULL DEFAULT; mapping:jsonb NOT_NULL DEFAULT; error_report:jsonb NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `industries` | `Industry` (schema:2145) | 35 | OFF | no | id:uuid NOT_NULL DEFAULT; organization_id:uuid NOT_NULL; parent_id:uuid; code:character varying NOT_NULL; name:character varying NOT_NULL; is_active:boolean NOT_NULL DEFAULT; display_order:integer NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `invitations` | `Invitation` (schema:947) | 9 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; email:character varying NOT_NULL; role:USER-DEFINED NOT_NULL DEFAULT; token_hash:character varying NOT_NULL; expires_at:timestamp with time zone NOT_NULL; accepted_at:timestamp with time zone; created_at:timestamp with time zone NOT_NULL DEFAULT |
| `kpi_targets` | `KpiTarget` (schema:2410) | 9 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; metric_definition_id:uuid NOT_NULL; business_unit_id:uuid; user_id:uuid; team_id:uuid; work_function:USER-DEFINED; scope_key:character varying NOT_NULL; period_type:USER-DEFINED NOT_NULL DEFAULT; period_start:date NOT_NULL; period_end:date NOT_NULL; target_value:numeric NOT_NULL; metadata:jsonb NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `legacy_source_links` | `LegacySourceLink` (schema:2506) | 26912 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; import_job_id:uuid; provider:character varying NOT_NULL; workbook_fingerprint:character varying NOT_NULL; sheet_name:character varying NOT_NULL; row_number:integer NOT_NULL; row_fingerprint:character varying NOT_NULL; target_object_type:character varying NOT_NULL; target_object_id:character varying NOT_NULL; imported_at:timestamp with time zone NOT_NULL DEFAULT; metadata:jsonb NOT_NULL DEFAULT |
| `loss_reason_definitions` | `LossReasonDefinition` (schema:2572) | 18 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; business_unit_id:uuid; product_id:uuid; code:character varying NOT_NULL; name:character varying NOT_NULL; category:character varying; applicable_scope:USER-DEFINED NOT_NULL DEFAULT; applicable_status:ARRAY DEFAULT; requires_note:boolean NOT_NULL DEFAULT; is_active:boolean NOT_NULL DEFAULT; display_order:integer NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `meeting_bookings` | `MeetingBooking` (schema:1453) | 25 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; meeting_link_id:uuid NOT_NULL; contact_id:uuid; guest_name:character varying NOT_NULL; guest_email:character varying NOT_NULL; starts_at:timestamp with time zone NOT_NULL; ends_at:timestamp with time zone NOT_NULL; created_at:timestamp with time zone NOT_NULL DEFAULT; appointment_set_at:timestamp with time zone; attended_at:timestamp with time zone; business_unit_id:uuid; cancelled_at:timestamp with time zone; deal_id:uuid; host_user_id:uuid; legacy_metadata:jsonb NOT_NULL DEFAULT; meeting_type:character varying; no_show_at:timestamp with time zone; qualification_result:USER-DEFINED NOT_NULL DEFAULT; set_by_user_id:uuid; source_channel:character varying; status:USER-DEFINED NOT_NULL DEFAULT; assigned_user_id:uuid; booking_hold_id:uuid; booking_origin:USER-DEFINED NOT_NULL DEFAULT; booking_status:USER-DEFINED NOT_NULL DEFAULT; cancel_reason:character varying; company_id:uuid; credited_appointment_setter_id:uuid; form_submission_id:uuid; google_calendar_id:character varying; google_event_etag:character varying; google_event_html_link:text; google_event_id:character varying; guest_phone:character varying; idempotency_key:character varying; last_synced_at:timestamp with time zone; next_retry_at:timestamp with time zone; submitted_by_contact_id:uuid; sync_attempt_count:integer NOT_NULL DEFAULT; sync_error_code:character varying; sync_error_message:text; sync_status:USER-DEFINED NOT_NULL DEFAULT; timezone:character varying NOT_NULL DEFAULT; external_change_detected_at:timestamp with time zone; external_change_snapshot:jsonb NOT_NULL DEFAULT; external_change_type:USER-DEFINED; external_submission_id:character varying; external_sync_status:USER-DEFINED; google_event_ical_uid:character varying; territory_id:uuid; prefecture_code:character varying; city:character varying; industry_id:uuid; product_id:uuid; campaign_id:uuid; call_list_id:uuid |
| `meeting_links` | `MeetingLink` (schema:1407) | 4 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; user_id:uuid NOT_NULL; name:character varying NOT_NULL; slug:character varying NOT_NULL; duration_minutes:integer NOT_NULL DEFAULT; is_active:boolean NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL; appointment_credit_fixed_user_id:uuid; appointment_credit_policy:USER-DEFINED NOT_NULL DEFAULT; assignment_mode:USER-DEFINED NOT_NULL DEFAULT; available_end_minutes:integer NOT_NULL DEFAULT; available_start_minutes:integer NOT_NULL DEFAULT; available_weekdays:jsonb NOT_NULL DEFAULT; booking_horizon_days:integer NOT_NULL DEFAULT; buffer_after_minutes:integer NOT_NULL DEFAULT; buffer_before_minutes:integer NOT_NULL DEFAULT; business_unit_id:uuid; cancellation_deadline_minutes:integer; google_calendar_enabled:boolean NOT_NULL DEFAULT; google_fallback_mode:character varying NOT_NULL DEFAULT; hold_minutes:integer NOT_NULL DEFAULT; location_type:USER-DEFINED NOT_NULL DEFAULT; location_value:character varying; max_bookings_per_day:integer; minimum_notice_minutes:integer NOT_NULL DEFAULT; owner_user_id:uuid; reschedule_deadline_minutes:integer; slot_interval_minutes:integer NOT_NULL DEFAULT; status:USER-DEFINED NOT_NULL DEFAULT; team_id:uuid; timezone:character varying NOT_NULL DEFAULT; title_template:character varying; work_function:USER-DEFINED |
| `metric_definition_versions` | `MetricDefinitionVersion` (schema:2313) | 76 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; metric_definition_id:uuid NOT_NULL; version:integer NOT_NULL; display_name:character varying NOT_NULL; description:text; source_type:USER-DEFINED NOT_NULL; aggregation:USER-DEFINED NOT_NULL; unit:USER-DEFINED NOT_NULL; query_definition:jsonb NOT_NULL DEFAULT; filter_definition:jsonb NOT_NULL DEFAULT; created_by_user_id:uuid; is_current:boolean NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT |
| `metric_definitions` | `MetricDefinition` (schema:2271) | 76 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; business_unit_id:uuid; key:character varying NOT_NULL; display_name:character varying NOT_NULL; description:text; category:USER-DEFINED NOT_NULL DEFAULT; unit:USER-DEFINED NOT_NULL DEFAULT; source_type:USER-DEFINED NOT_NULL; aggregation:USER-DEFINED NOT_NULL DEFAULT; work_function:USER-DEFINED; object_type:character varying; date_field:character varying; attribution_role:USER-DEFINED; numerator_metric_id:uuid; denominator_metric_id:uuid; is_active:boolean NOT_NULL DEFAULT; is_primary:boolean NOT_NULL DEFAULT; is_visible_by_default:boolean NOT_NULL DEFAULT; display_order:integer NOT_NULL DEFAULT; min_sample_size:integer NOT_NULL DEFAULT; query_definition:jsonb NOT_NULL DEFAULT; filter_definition:jsonb NOT_NULL DEFAULT; metadata:jsonb NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `metric_validation_rules` | `MetricValidationRule` (schema:2389) | 3 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; metric_definition_id:uuid NOT_NULL; key:character varying NOT_NULL; name:character varying NOT_NULL; severity:USER-DEFINED NOT_NULL DEFAULT; condition:jsonb NOT_NULL DEFAULT; message:text NOT_NULL; is_active:boolean NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `notifications` | `Notification` (schema:1248) | 0 | OFF | no | id:uuid NOT_NULL DEFAULT; organization_id:uuid NOT_NULL; recipient_user_id:uuid NOT_NULL; type:character varying NOT_NULL; title:character varying NOT_NULL; body:text; target_type:character varying; target_id:uuid; read_at:timestamp with time zone; created_at:timestamp with time zone NOT_NULL DEFAULT |
| `object_associations` | `ObjectAssociation` (schema:1138) | 5838 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; source_object_type:USER-DEFINED NOT_NULL; source_object_id:uuid NOT_NULL; target_object_type:USER-DEFINED NOT_NULL; target_object_id:uuid NOT_NULL; label:character varying; is_primary:boolean NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `operational_events` | `OperationalEvent` (schema:1849) | 5 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; event_type:USER-DEFINED NOT_NULL; correlation_id:character varying; booking_id:uuid; form_submission_id:uuid; sync_job_id:uuid; channel_id:character varying; status:character varying; metadata:jsonb NOT_NULL DEFAULT; occurred_at:timestamp with time zone NOT_NULL DEFAULT |
| `organization_members` | `OrganizationMember` (schema:858) | 9 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; user_id:uuid NOT_NULL; role:USER-DEFINED NOT_NULL DEFAULT; team_id:uuid; status:USER-DEFINED NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL; selected_business_unit_id:uuid |
| `outbound_campaigns` | `OutboundCampaign` (schema:2165) | 0 | OFF | no | id:uuid NOT_NULL DEFAULT; organization_id:uuid NOT_NULL; business_unit_id:uuid; name:character varying NOT_NULL; product_id:uuid; territory_id:uuid; prefecture_code:character varying; industry_id:uuid; status:character varying NOT_NULL DEFAULT; start_date:date; end_date:date; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `pipeline_stages` | `PipelineStage` (schema:1060) | 106 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; pipeline_id:uuid NOT_NULL; name:character varying NOT_NULL; "order":integer NOT_NULL; probability:integer NOT_NULL DEFAULT; stage_type:USER-DEFINED NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL; required_fields:jsonb NOT_NULL DEFAULT; stale_days:integer |
| `pipelines` | `Pipeline` (schema:1041) | 7 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; name:character varying NOT_NULL; is_default:boolean NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL; business_unit_id:uuid |
| `price_book_entries` | `PriceBookEntry` (schema:1957) | 8 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; product_id:uuid NOT_NULL; business_unit_id:uuid; name:character varying NOT_NULL; currency:character varying NOT_NULL DEFAULT; unit_price_amount:numeric; revenue_amount:numeric; gross_profit_amount:numeric; effective_from:date; effective_until:date; status:USER-DEFINED NOT_NULL DEFAULT; metadata:jsonb NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL; initial_fee:numeric; recurring_fee:numeric |
| `product_attachment_rule_base_products` | `ProductAttachmentRuleBaseProduct` (schema:2560) | 3 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; rule_id:uuid NOT_NULL; product_id:uuid NOT_NULL; created_at:timestamp with time zone NOT_NULL DEFAULT |
| `product_attachment_rules` | `ProductAttachmentRule` (schema:2540) | 1 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; business_unit_id:uuid; name:character varying NOT_NULL; attached_product_id:uuid NOT_NULL; denominator_mode:USER-DEFINED NOT_NULL; date_basis:USER-DEFINED; target_rate:numeric; eligibility_filter:jsonb NOT_NULL DEFAULT; is_active:boolean NOT_NULL DEFAULT; display_order:integer NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `products` | `Product` (schema:1907) | 41 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; name:character varying NOT_NULL; normalized_name:character varying NOT_NULL; sku:character varying; description:text; category:character varying; status:USER-DEFINED NOT_NULL DEFAULT; metadata:jsonb NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL; fulfillment_type:USER-DEFINED |
| `referrals` | `Referral` (schema:2214) | 6 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; business_unit_id:uuid; deal_id:uuid; referrer_user_id:uuid; owner_user_id:uuid; referred_company_name:character varying NOT_NULL; referred_contact_name:character varying; referred_email:character varying; referred_phone:character varying; status:USER-DEFINED NOT_NULL DEFAULT; referred_at:timestamp with time zone NOT_NULL DEFAULT; appointment_set_at:timestamp with time zone; meeting_attended_at:timestamp with time zone; won_at:timestamp with time zone; metadata:jsonb NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `routing_execution_logs` | `RoutingExecutionLog` (schema:1687) | 0 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; routing_rule_id:uuid; form_submission_id:uuid; candidate_user_ids:jsonb NOT_NULL DEFAULT; selected_user_id:uuid; matched:boolean NOT_NULL DEFAULT; reason:character varying; fallback_reason:character varying; input_snapshot:jsonb NOT_NULL DEFAULT; result_snapshot:jsonb NOT_NULL DEFAULT; executed_at:timestamp with time zone NOT_NULL DEFAULT |
| `routing_rules` | `RoutingRule` (schema:1662) | 0 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; business_unit_id:uuid; form_id:uuid; name:character varying NOT_NULL; priority:integer NOT_NULL DEFAULT; status:USER-DEFINED NOT_NULL DEFAULT; condition_join:USER-DEFINED NOT_NULL DEFAULT; conditions:jsonb NOT_NULL DEFAULT; actions:jsonb NOT_NULL DEFAULT; stop_processing:boolean NOT_NULL DEFAULT; assignment_mode:USER-DEFINED; fixed_user_id:uuid; team_id:uuid; work_function:USER-DEFINED; fallback_config:jsonb NOT_NULL DEFAULT; version:integer NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `sales_performance_events` | `SalesPerformanceEvent` (schema:2080) | 94 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; business_unit_id:uuid; deal_id:uuid; deal_line_item_id:uuid; meeting_booking_id:uuid; referral_id:uuid; field_visit_id:uuid; metric_definition_id:uuid; credited_user_id:uuid; credited_role:USER-DEFINED; work_function:USER-DEFINED; event_type:USER-DEFINED NOT_NULL; source:USER-DEFINED NOT_NULL DEFAULT; occurred_at:timestamp with time zone NOT_NULL; quantity:numeric NOT_NULL DEFAULT; amount:numeric; idempotency_key:character varying NOT_NULL; metadata:jsonb NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; cancelled_at:timestamp with time zone; territory_id:uuid; prefecture_code:character varying; city:character varying; industry_id:uuid; product_id:uuid; campaign_id:uuid; call_list_id:uuid |
| `sales_territories` | `SalesTerritory` (schema:2126) | 0 | OFF | no | id:uuid NOT_NULL DEFAULT; organization_id:uuid NOT_NULL; business_unit_id:uuid; name:character varying NOT_NULL; description:text; mapping_rules:jsonb NOT_NULL DEFAULT; is_active:boolean NOT_NULL DEFAULT; display_order:integer NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `saved_views` | `SavedView` (schema:1315) | 1 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; user_id:uuid NOT_NULL; object_type:USER-DEFINED NOT_NULL; name:character varying NOT_NULL; filters:jsonb NOT_NULL DEFAULT; columns:jsonb NOT_NULL DEFAULT; sort:jsonb NOT_NULL DEFAULT; is_shared:boolean NOT_NULL DEFAULT; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |
| `task_reminders` | `TaskReminder` (schema:1222) | 16 | OFF | no | id:uuid NOT_NULL DEFAULT; organization_id:uuid NOT_NULL; task_id:uuid NOT_NULL; recipient_user_id:uuid NOT_NULL; channel:USER-DEFINED NOT_NULL; scheduled_at:timestamp with time zone NOT_NULL; status:USER-DEFINED NOT_NULL DEFAULT; sent_at:timestamp with time zone; attempt_count:integer NOT_NULL DEFAULT; last_error:text; idempotency_key:character varying NOT_NULL; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL DEFAULT |
| `tasks` | `Task` (schema:1179) | 323 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; owner_user_id:uuid NOT_NULL; created_by_user_id:uuid NOT_NULL; title:character varying NOT_NULL; description:text; due_date:timestamp with time zone; status:USER-DEFINED NOT_NULL DEFAULT; priority:USER-DEFINED NOT_NULL DEFAULT; task_type:USER-DEFINED NOT_NULL DEFAULT; completed_at:timestamp with time zone; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL; auto_task_key:character varying; delivery_project_id:uuid; source_delivery_stage_id:uuid; duration_minutes:integer; timezone:character varying NOT_NULL DEFAULT; calendar_sync_enabled:boolean NOT_NULL DEFAULT; calendar_sync_status:USER-DEFINED NOT_NULL DEFAULT; google_calendar_id:character varying; google_event_id:character varying; google_event_html_link:text; calendar_sync_attempt_count:integer NOT_NULL DEFAULT; calendar_sync_error_code:character varying; calendar_sync_error_message:text; calendar_last_synced_at:timestamp with time zone; calendar_next_retry_at:timestamp with time zone |
| `teams` | `Team` (schema:932) | 1 | OFF | no | id:uuid NOT_NULL; organization_id:uuid NOT_NULL; name:character varying NOT_NULL; created_at:timestamp with time zone NOT_NULL DEFAULT; updated_at:timestamp with time zone NOT_NULL |

## PK / Unique / FK

### `Organization`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `User`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `_prisma_migrations`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `action_plans`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `action_plans_metric_definition_id_fkey: FOREIGN KEY (metric_definition_id) REFERENCES metric_definitions(id) ON UPDATE CASCADE ON DELETE SET NULL; action_plans_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE; action_plans_target_id_fkey: FOREIGN KEY (target_id) REFERENCES kpi_targets(id) ON UPDATE CASCADE ON DELETE SET NULL`

### `activities`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `activities_actor_user_id_fkey: FOREIGN KEY (actor_user_id) REFERENCES "User"(id) ON UPDATE CASCADE ON DELETE SET NULL; activities_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `appointment_capture_links`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `appointment_capture_links_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `assignment_cursors`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `audit_logs`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `audit_logs_actor_user_id_fkey: FOREIGN KEY (actor_user_id) REFERENCES "User"(id) ON UPDATE CASCADE ON DELETE SET NULL; audit_logs_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `auth_sessions`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `auth_sessions_active_organization_id_fkey: FOREIGN KEY (active_organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE; auth_sessions_user_id_fkey: FOREIGN KEY (user_id) REFERENCES "User"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `availability_exceptions`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `availability_rules`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `availability_rules_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE; availability_rules_user_id_fkey: FOREIGN KEY (user_id) REFERENCES "User"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `availability_schedules`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `booking_holds`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `business_calendar_exceptions`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `business_calendar_exceptions_calendar_id_fkey: FOREIGN KEY (calendar_id) REFERENCES business_calendars(id) ON UPDATE CASCADE ON DELETE CASCADE; business_calendar_exceptions_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `business_calendars`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `business_calendars_business_unit_id_fkey: FOREIGN KEY (business_unit_id) REFERENCES business_units(id) ON UPDATE CASCADE ON DELETE CASCADE; business_calendars_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `business_unit_memberships`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `business_unit_memberships_business_unit_id_fkey: FOREIGN KEY (business_unit_id) REFERENCES business_units(id) ON UPDATE CASCADE ON DELETE CASCADE; business_unit_memberships_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE; business_unit_memberships_user_id_fkey: FOREIGN KEY (user_id) REFERENCES "User"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `business_unit_products`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `business_unit_products_business_unit_id_fkey: FOREIGN KEY (business_unit_id) REFERENCES business_units(id) ON UPDATE CASCADE ON DELETE CASCADE; business_unit_products_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE; business_unit_products_product_id_fkey: FOREIGN KEY (product_id) REFERENCES products(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `business_units`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `business_units_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `calendar_sync_jobs`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `call_lists`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `call_lists_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `companies`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `companies_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE; companies_owner_user_id_fkey: FOREIGN KEY (owner_user_id) REFERENCES "User"(id) ON UPDATE CASCADE ON DELETE SET NULL`

### `contacts`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `contacts_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE; contacts_owner_user_id_fkey: FOREIGN KEY (owner_user_id) REFERENCES "User"(id) ON UPDATE CASCADE ON DELETE SET NULL`

### `conversations`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `conversations_contact_id_fkey: FOREIGN KEY (contact_id) REFERENCES contacts(id) ON UPDATE CASCADE ON DELETE SET NULL; conversations_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `custom_properties`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `custom_properties_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `custom_property_product_scopes`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `daily_metric_entries`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `daily_metric_entries_metric_definition_id_fkey: FOREIGN KEY (metric_definition_id) REFERENCES metric_definitions(id) ON UPDATE CASCADE ON DELETE CASCADE; daily_metric_entries_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `daily_metric_field_configs`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `daily_metric_field_configs_business_unit_id_fkey: FOREIGN KEY (business_unit_id) REFERENCES business_units(id) ON UPDATE CASCADE ON DELETE CASCADE; daily_metric_field_configs_metric_definition_id_fkey: FOREIGN KEY (metric_definition_id) REFERENCES metric_definitions(id) ON UPDATE CASCADE ON DELETE CASCADE; daily_metric_field_configs_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `deal_alert_rules`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `deal_line_items`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `deal_line_items_deal_id_fkey: FOREIGN KEY (deal_id) REFERENCES deals(id) ON UPDATE CASCADE ON DELETE CASCADE; deal_line_items_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE; deal_line_items_price_book_entry_id_fkey: FOREIGN KEY (price_book_entry_id) REFERENCES price_book_entries(id) ON UPDATE CASCADE ON DELETE SET NULL; deal_line_items_product_id_fkey: FOREIGN KEY (product_id) REFERENCES products(id) ON UPDATE CASCADE ON DELETE SET NULL`

### `deal_participants`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `deal_participants_deal_id_fkey: FOREIGN KEY (deal_id) REFERENCES deals(id) ON UPDATE CASCADE ON DELETE CASCADE; deal_participants_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `deals`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `deals_business_unit_id_fkey: FOREIGN KEY (business_unit_id) REFERENCES business_units(id) ON UPDATE CASCADE ON DELETE SET NULL; deals_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE; deals_owner_user_id_fkey: FOREIGN KEY (owner_user_id) REFERENCES "User"(id) ON UPDATE CASCADE ON DELETE SET NULL; deals_pipeline_id_fkey: FOREIGN KEY (pipeline_id) REFERENCES pipelines(id) ON UPDATE CASCADE ON DELETE RESTRICT; deals_stage_id_fkey: FOREIGN KEY (stage_id) REFERENCES pipeline_stages(id) ON UPDATE CASCADE ON DELETE RESTRICT`

### `delivery_handoffs`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `delivery_handoffs_delivery_project_id_fkey: FOREIGN KEY (delivery_project_id) REFERENCES delivery_projects(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `delivery_pipeline_stages`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `delivery_pipeline_stages_pipeline_id_fkey: FOREIGN KEY (pipeline_id) REFERENCES delivery_pipelines(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `delivery_pipelines`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `delivery_project_items`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `delivery_project_items_delivery_project_id_fkey: FOREIGN KEY (delivery_project_id) REFERENCES delivery_projects(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `delivery_project_stage_histories`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `delivery_project_stage_histories_delivery_project_id_fkey: FOREIGN KEY (delivery_project_id) REFERENCES delivery_projects(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `delivery_project_template_products`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `delivery_project_templates`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `delivery_projects`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `email_templates`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `email_templates_created_by_user_id_fkey: FOREIGN KEY (created_by_user_id) REFERENCES "User"(id) ON UPDATE CASCADE ON DELETE RESTRICT; email_templates_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `field_visits`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `field_visits_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `forecast_categories`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `forecast_categories_business_unit_id_fkey: FOREIGN KEY (business_unit_id) REFERENCES business_units(id) ON UPDATE CASCADE ON DELETE CASCADE; forecast_categories_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `form_submissions`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `form_submissions_contact_id_fkey: FOREIGN KEY (contact_id) REFERENCES contacts(id) ON UPDATE CASCADE ON DELETE SET NULL; form_submissions_form_id_fkey: FOREIGN KEY (form_id) REFERENCES forms(id) ON UPDATE CASCADE ON DELETE CASCADE; form_submissions_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `form_versions`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `forms`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `forms_business_unit_id_fkey: FOREIGN KEY (business_unit_id) REFERENCES business_units(id) ON UPDATE CASCADE ON DELETE SET NULL; forms_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `google_calendar_connections`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `google_calendar_selections`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `google_calendar_watch_channels`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `google_oauth_states`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `import_jobs`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `import_jobs_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE; import_jobs_uploaded_by_user_id_fkey: FOREIGN KEY (uploaded_by_user_id) REFERENCES "User"(id) ON UPDATE CASCADE ON DELETE RESTRICT`

### `industries`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `industries_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE; industries_parent_id_fkey: FOREIGN KEY (parent_id) REFERENCES industries(id) ON UPDATE CASCADE ON DELETE SET NULL`

### `invitations`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `invitations_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `kpi_targets`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `kpi_targets_metric_definition_id_fkey: FOREIGN KEY (metric_definition_id) REFERENCES metric_definitions(id) ON UPDATE CASCADE ON DELETE CASCADE; kpi_targets_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `legacy_source_links`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `legacy_source_links_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `loss_reason_definitions`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `meeting_bookings`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `meeting_bookings_contact_id_fkey: FOREIGN KEY (contact_id) REFERENCES contacts(id) ON UPDATE CASCADE ON DELETE SET NULL; meeting_bookings_meeting_link_id_fkey: FOREIGN KEY (meeting_link_id) REFERENCES meeting_links(id) ON UPDATE CASCADE ON DELETE CASCADE; meeting_bookings_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `meeting_links`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `meeting_links_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE; meeting_links_user_id_fkey: FOREIGN KEY (user_id) REFERENCES "User"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `metric_definition_versions`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `metric_definition_versions_metric_definition_id_fkey: FOREIGN KEY (metric_definition_id) REFERENCES metric_definitions(id) ON UPDATE CASCADE ON DELETE CASCADE; metric_definition_versions_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `metric_definitions`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `metric_definitions_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `metric_validation_rules`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `metric_validation_rules_metric_definition_id_fkey: FOREIGN KEY (metric_definition_id) REFERENCES metric_definitions(id) ON UPDATE CASCADE ON DELETE CASCADE; metric_validation_rules_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `notifications`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `notifications_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE; notifications_recipient_user_id_fkey: FOREIGN KEY (recipient_user_id) REFERENCES "User"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `object_associations`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `object_associations_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `operational_events`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `organization_members`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `organization_members_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE; organization_members_selected_business_unit_id_fkey: FOREIGN KEY (selected_business_unit_id) REFERENCES business_units(id) ON UPDATE CASCADE ON DELETE SET NULL; organization_members_team_id_fkey: FOREIGN KEY (team_id) REFERENCES teams(id) ON UPDATE CASCADE ON DELETE SET NULL; organization_members_user_id_fkey: FOREIGN KEY (user_id) REFERENCES "User"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `outbound_campaigns`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `outbound_campaigns_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `pipeline_stages`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `pipeline_stages_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE; pipeline_stages_pipeline_id_fkey: FOREIGN KEY (pipeline_id) REFERENCES pipelines(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `pipelines`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `pipelines_business_unit_id_fkey: FOREIGN KEY (business_unit_id) REFERENCES business_units(id) ON UPDATE CASCADE ON DELETE SET NULL; pipelines_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `price_book_entries`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `price_book_entries_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE; price_book_entries_product_id_fkey: FOREIGN KEY (product_id) REFERENCES products(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `product_attachment_rule_base_products`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `product_attachment_rules`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `products`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `products_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `referrals`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `referrals_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `routing_execution_logs`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `routing_rules`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: none

### `sales_performance_events`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `sales_performance_events_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `sales_territories`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `sales_territories_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `saved_views`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `saved_views_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE; saved_views_user_id_fkey: FOREIGN KEY (user_id) REFERENCES "User"(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `task_reminders`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `task_reminders_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE; task_reminders_recipient_user_id_fkey: FOREIGN KEY (recipient_user_id) REFERENCES "User"(id) ON UPDATE CASCADE ON DELETE CASCADE; task_reminders_task_id_fkey: FOREIGN KEY (task_id) REFERENCES tasks(id) ON UPDATE CASCADE ON DELETE CASCADE`

### `tasks`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `tasks_created_by_user_id_fkey: FOREIGN KEY (created_by_user_id) REFERENCES "User"(id) ON UPDATE CASCADE ON DELETE RESTRICT; tasks_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE; tasks_owner_user_id_fkey: FOREIGN KEY (owner_user_id) REFERENCES "User"(id) ON UPDATE CASCADE ON DELETE RESTRICT`

### `teams`

- PK: `PRIMARY KEY (id)`
- Unique: none
- FK: `teams_organization_id_fkey: FOREIGN KEY (organization_id) REFERENCES "Organization"(id) ON UPDATE CASCADE ON DELETE CASCADE`

## Index catalog

| Table | Index names |
|---|---|
| `Organization` | Organization_pkey, Organization_slug_key |
| `User` | User_email_key, User_pkey |
| `_prisma_migrations` | _prisma_migrations_pkey |
| `action_plans` | action_plans_organization_id_business_unit_id_status_due_da_idx, action_plans_organization_id_metric_definition_id_idx, action_plans_organization_id_owner_user_id_status_due_date_idx, action_plans_pkey |
| `activities` | activities_organization_id_delivery_project_id_occurred_at_idx, activities_organization_id_occurred_at_idx, activities_pkey |
| `appointment_capture_links` | appointment_capture_links_organization_id_business_unit_id_stat, appointment_capture_links_organization_id_credited_appointment_, appointment_capture_links_pkey, appointment_capture_links_token_hash_key |
| `assignment_cursors` | assignment_cursors_organization_id_scope_key_key, assignment_cursors_pkey |
| `audit_logs` | audit_logs_organization_id_created_at_idx, audit_logs_organization_id_target_type_target_id_idx, audit_logs_pkey |
| `auth_sessions` | auth_sessions_active_organization_id_idx, auth_sessions_pkey, auth_sessions_token_hash_key, auth_sessions_user_id_expires_at_idx |
| `availability_exceptions` | availability_exceptions_organization_id_user_id_date_idx, availability_exceptions_pkey, availability_exceptions_schedule_id_date_key |
| `availability_rules` | availability_rules_organization_id_user_id_weekday_key, availability_rules_pkey, availability_rules_schedule_id_weekday_idx |
| `availability_schedules` | availability_schedules_organization_id_user_id_is_default_idx, availability_schedules_organization_id_user_id_name_key, availability_schedules_pkey |
| `booking_holds` | booking_holds_organization_id_host_user_id_scheduled_start__idx, booking_holds_organization_id_meeting_link_id_scheduled_sta_idx, booking_holds_pkey, booking_holds_token_hash_key |
| `business_calendar_exceptions` | business_calendar_exceptions_calendar_id_target_date_key, business_calendar_exceptions_organization_id_target_date_idx, business_calendar_exceptions_pkey |
| `business_calendars` | business_calendars_organization_id_business_unit_id_is_defa_idx, business_calendars_organization_id_business_unit_id_name_key, business_calendars_pkey |
| `business_unit_memberships` | business_unit_memberships_business_unit_id_user_id_work_fun_key, business_unit_memberships_organization_id_business_unit_id__idx, business_unit_memberships_organization_id_user_id_status_idx, business_unit_memberships_pkey |
| `business_unit_products` | business_unit_products_organization_id_business_unit_id_ful_idx, business_unit_products_organization_id_business_unit_id_pro_idx, business_unit_products_organization_id_business_unit_id_pro_key, business_unit_products_pkey |
| `business_units` | business_units_organization_id_name_key, business_units_organization_id_slug_key, business_units_organization_id_status_display_order_idx, business_units_pkey |
| `calendar_sync_jobs` | calendar_sync_jobs_connection_id_status_idx, calendar_sync_jobs_organization_id_status_created_at_idx, calendar_sync_jobs_pkey, calendar_sync_jobs_selection_id_status_idx |
| `call_lists` | call_lists_organization_id_business_unit_id_name_key, call_lists_organization_id_business_unit_id_status_idx, call_lists_organization_id_campaign_id_idx, call_lists_organization_id_industry_id_idx, call_lists_organization_id_territory_id_idx, call_lists_pkey |
| `companies` | companies_organization_id_deleted_at_updated_at_idx, companies_organization_id_domain_key, companies_organization_id_owner_user_id_idx, companies_pkey |
| `contacts` | contacts_organization_id_deleted_at_updated_at_idx, contacts_organization_id_email_key, contacts_organization_id_owner_user_id_idx, contacts_pkey |
| `conversations` | conversations_organization_id_created_at_idx, conversations_pkey |
| `custom_properties` | custom_properties_organization_id_business_unit_id_object_t_idx, custom_properties_organization_id_object_type_name_key, custom_properties_pkey |
| `custom_property_product_scopes` | custom_property_product_scopes_custom_property_id_product_i_key, custom_property_product_scopes_organization_id_product_id_idx, custom_property_product_scopes_pkey |
| `daily_metric_entries` | daily_metric_entries_dimension_unique, daily_metric_entries_organization_id_business_unit_id_targe_idx, daily_metric_entries_organization_id_metric_definition_id_t_idx, daily_metric_entries_organization_id_user_id_target_date_idx, daily_metric_entries_pkey |
| `daily_metric_field_configs` | daily_metric_field_configs_pkey, daily_metric_field_configs_scope_enabled_order_idx, daily_metric_field_configs_scope_metric_key |
| `deal_alert_rules` | deal_alert_rules_organization_id_business_unit_id_pipeline__idx, deal_alert_rules_pkey |
| `deal_line_items` | deal_line_items_organization_id_billing_started_at_idx, deal_line_items_organization_id_business_unit_id_status_idx, deal_line_items_organization_id_collected_at_idx, deal_line_items_organization_id_contracted_at_idx, deal_line_items_organization_id_deal_id_idx, deal_line_items_organization_id_loss_reason_id_idx, deal_line_items_organization_id_product_id_idx, deal_line_items_pkey |
| `deal_participants` | deal_participants_organization_id_deal_id_role_idx, deal_participants_organization_id_user_id_role_credited_at_idx, deal_participants_pkey |
| `deals` | deals_organization_id_business_unit_id_pipeline_id_stage_id_idx, deals_organization_id_business_unit_id_status_close_date_idx, deals_organization_id_deal_type_origin_project_id_idx, deals_organization_id_external_id_key, deals_organization_id_forecast_category_id_idx, deals_organization_id_owner_user_id_idx, deals_pkey |
| `delivery_handoffs` | delivery_handoffs_delivery_project_id_version_key, delivery_handoffs_organization_id_business_unit_id_status_idx, delivery_handoffs_pkey |
| `delivery_pipeline_stages` | delivery_pipeline_stages_organization_id_business_unit_id_p_idx, delivery_pipeline_stages_pipeline_id_name_key, delivery_pipeline_stages_pipeline_id_order_key, delivery_pipeline_stages_pkey |
| `delivery_pipelines` | delivery_pipelines_organization_id_business_unit_id_is_defa_idx, delivery_pipelines_organization_id_business_unit_id_name_key, delivery_pipelines_pkey |
| `delivery_project_items` | delivery_project_items_organization_id_delivery_project_id_idx, delivery_project_items_organization_id_product_id_idx, delivery_project_items_organization_id_source_deal_line_ite_key, delivery_project_items_pkey |
| `delivery_project_stage_histories` | delivery_project_stage_histories_organization_id_delivery_p_idx, delivery_project_stage_histories_organization_id_to_stage_i_idx, delivery_project_stage_histories_pkey |
| `delivery_project_template_products` | delivery_project_template_products_organization_id_product__idx, delivery_project_template_products_pkey, delivery_project_template_products_template_id_product_id_key |
| `delivery_project_templates` | delivery_project_templates_organization_id_business_unit_id_idx, delivery_project_templates_organization_id_business_unit_id_key, delivery_project_templates_pkey |
| `delivery_projects` | delivery_projects_organization_id_business_unit_id_status_d_idx, delivery_projects_organization_id_expected_publish_date_idx, delivery_projects_organization_id_idempotency_key_key, delivery_projects_organization_id_owner_user_id_status_idx, delivery_projects_organization_id_source_deal_id_idx, delivery_projects_pkey |
| `email_templates` | email_templates_organization_id_name_key, email_templates_pkey |
| `field_visits` | field_visits_organization_id_business_unit_id_visited_at_idx, field_visits_organization_id_owner_user_id_visited_at_idx, field_visits_organization_id_status_idx, field_visits_pkey |
| `forecast_categories` | forecast_categories_organization_id_business_unit_id_key_key, forecast_categories_organization_id_business_unit_id_status_idx, forecast_categories_pkey |
| `form_submissions` | form_submissions_organization_id_assigned_user_id_created_a_idx, form_submissions_organization_id_deal_id_idx, form_submissions_organization_id_form_id_created_at_idx, form_submissions_organization_id_idempotency_key_key, form_submissions_pkey |
| `form_versions` | form_versions_form_id_version_key, form_versions_organization_id_business_unit_id_status_idx, form_versions_organization_id_form_id_status_idx, form_versions_pkey |
| `forms` | forms_organization_id_business_unit_id_form_purpose_is_default_, forms_organization_id_business_unit_id_status_idx, forms_pkey, forms_slug_key |
| `google_calendar_connections` | google_calendar_connections_organization_id_status_idx, google_calendar_connections_organization_id_user_id_key, google_calendar_connections_pkey |
| `google_calendar_selections` | google_calendar_selections_connection_id_google_calendar_id_key, google_calendar_selections_connection_id_is_write_calendar_idx, google_calendar_selections_pkey |
| `google_calendar_watch_channels` | google_calendar_watch_channels_channel_id_key, google_calendar_watch_channels_connection_id_google_calenda_idx, google_calendar_watch_channels_pkey |
| `google_oauth_states` | google_oauth_states_organization_id_user_id_expires_at_idx, google_oauth_states_pkey, google_oauth_states_state_hash_key |
| `import_jobs` | import_jobs_organization_id_created_at_idx, import_jobs_pkey |
| `industries` | industries_organization_id_code_key, industries_organization_id_parent_id_is_active_display_order_id, industries_pkey |
| `invitations` | invitations_expires_at_idx, invitations_organization_id_email_idx, invitations_pkey, invitations_token_hash_key |
| `kpi_targets` | kpi_targets_organization_id_business_unit_id_period_start_p_idx, kpi_targets_organization_id_metric_definition_id_scope_key__key, kpi_targets_organization_id_user_id_period_start_period_end_idx, kpi_targets_pkey |
| `legacy_source_links` | legacy_source_links_organization_id_provider_workbook_finge_key, legacy_source_links_organization_id_target_object_type_targ_idx, legacy_source_links_organization_id_workbook_fingerprint_sh_idx, legacy_source_links_pkey |
| `loss_reason_definitions` | loss_reason_definitions_organization_id_business_unit_id_pr_idx, loss_reason_definitions_organization_id_business_unit_id_pr_key, loss_reason_definitions_pkey |
| `meeting_bookings` | meeting_bookings_meeting_link_id_starts_at_key, meeting_bookings_no_host_overlap, meeting_bookings_org_google_event_uidx, meeting_bookings_org_idempotency_key_uidx, meeting_bookings_org_link_external_submission_uidx, meeting_bookings_organization_id_booking_status_sync_status_idx, meeting_bookings_organization_id_business_unit_id_starts_at_idx, meeting_bookings_organization_id_call_list_id_starts_at_idx, meeting_bookings_organization_id_campaign_id_starts_at_idx, meeting_bookings_organization_id_deal_id_idx, meeting_bookings_organization_id_google_calendar_id_google__idx, meeting_bookings_organization_id_host_user_id_starts_at_idx, meeting_bookings_organization_id_idempotency_key_key, meeting_bookings_organization_id_industry_id_starts_at_idx, meeting_bookings_organization_id_meeting_link_id_external_s_idx, meeting_bookings_organization_id_prefecture_code_starts_at_idx, meeting_bookings_organization_id_product_id_starts_at_idx, meeting_bookings_organization_id_set_by_user_id_appointment_idx, meeting_bookings_organization_id_starts_at_idx, meeting_bookings_organization_id_territory_id_starts_at_idx, meeting_bookings_pkey |
| `meeting_links` | meeting_links_organization_id_business_unit_id_status_idx, meeting_links_organization_id_user_id_idx, meeting_links_pkey, meeting_links_slug_key |
| `metric_definition_versions` | metric_definition_versions_metric_definition_id_version_key, metric_definition_versions_organization_id_metric_definitio_idx, metric_definition_versions_pkey |
| `metric_definitions` | metric_definitions_organization_id_business_unit_id_work_fu_idx, metric_definitions_organization_id_key_key, metric_definitions_organization_id_source_type_aggregation_idx, metric_definitions_pkey |
| `metric_validation_rules` | metric_validation_rules_metric_definition_id_key_key, metric_validation_rules_organization_id_is_active_idx, metric_validation_rules_pkey |
| `notifications` | notifications_organization_id_recipient_user_id_read_at_created, notifications_organization_id_target_type_target_id_idx, notifications_pkey |
| `object_associations` | object_associations_organization_id_source_object_type_sour_idx, object_associations_organization_id_source_object_type_sour_key, object_associations_organization_id_target_object_type_targ_idx, object_associations_pkey |
| `operational_events` | operational_events_organization_id_booking_id_idx, operational_events_organization_id_event_type_occurred_at_idx, operational_events_organization_id_form_submission_id_idx, operational_events_organization_id_sync_job_id_idx, operational_events_pkey |
| `organization_members` | organization_members_organization_id_role_status_idx, organization_members_organization_id_selected_business_unit_idx, organization_members_organization_id_user_id_key, organization_members_pkey, organization_members_user_id_status_idx |
| `outbound_campaigns` | outbound_campaigns_organization_id_business_unit_id_name_key, outbound_campaigns_organization_id_business_unit_id_status_idx, outbound_campaigns_organization_id_industry_id_idx, outbound_campaigns_organization_id_territory_id_idx, outbound_campaigns_pkey |
| `pipeline_stages` | pipeline_stages_organization_id_idx, pipeline_stages_pipeline_id_name_key, pipeline_stages_pipeline_id_order_key, pipeline_stages_pkey |
| `pipelines` | pipelines_organization_id_business_unit_id_is_default_idx, pipelines_organization_id_name_key, pipelines_pkey |
| `price_book_entries` | price_book_entries_organization_id_business_unit_id_status_idx, price_book_entries_organization_id_product_id_status_idx, price_book_entries_pkey |
| `product_attachment_rule_base_products` | product_attachment_rule_base_products_organization_id_produ_idx, product_attachment_rule_base_products_pkey, product_attachment_rule_base_products_rule_id_product_id_key |
| `product_attachment_rules` | product_attachment_rules_organization_id_attached_product_i_idx, product_attachment_rules_organization_id_business_unit_id_i_idx, product_attachment_rules_pkey |
| `products` | products_organization_id_normalized_name_key, products_organization_id_status_name_idx, products_pkey |
| `referrals` | referrals_organization_id_business_unit_id_referred_at_idx, referrals_organization_id_referrer_user_id_referred_at_idx, referrals_organization_id_status_idx, referrals_pkey |
| `routing_execution_logs` | routing_execution_logs_organization_id_form_submission_id_e_idx, routing_execution_logs_organization_id_routing_rule_id_exec_idx, routing_execution_logs_pkey |
| `routing_rules` | routing_rules_organization_id_business_unit_id_form_id_stat_idx, routing_rules_pkey |
| `sales_performance_events` | sales_performance_events_organization_id_business_unit_id_o_idx, sales_performance_events_organization_id_call_list_id_occurred_, sales_performance_events_organization_id_campaign_id_occurred_a, sales_performance_events_organization_id_credited_user_id_o_idx, sales_performance_events_organization_id_deal_id_idx, sales_performance_events_organization_id_event_type_occurre_idx, sales_performance_events_organization_id_idempotency_key_key, sales_performance_events_organization_id_industry_id_occurred_a, sales_performance_events_organization_id_prefecture_code_occurr, sales_performance_events_organization_id_product_id_occurred_at, sales_performance_events_organization_id_territory_id_occurred_, sales_performance_events_pkey |
| `sales_territories` | sales_territories_organization_id_business_unit_id_is_active_di, sales_territories_organization_id_business_unit_id_name_key, sales_territories_pkey |
| `saved_views` | saved_views_organization_id_object_type_is_shared_idx, saved_views_organization_id_user_id_object_type_name_key, saved_views_pkey |
| `task_reminders` | task_reminders_organization_id_idempotency_key_key, task_reminders_organization_id_recipient_user_id_status_schedul, task_reminders_organization_id_status_scheduled_at_idx, task_reminders_pkey, task_reminders_task_id_channel_scheduled_at_key |
| `tasks` | tasks_organization_id_calendar_sync_status_calendar_next_retry_, tasks_organization_id_delivery_project_id_auto_task_key_idx, tasks_organization_id_delivery_project_id_status_due_date_idx, tasks_organization_id_owner_user_id_status_due_date_idx, tasks_pkey |
| `teams` | teams_organization_id_idx, teams_organization_id_name_key, teams_pkey |

## Relation risk from PR #13, production-verified context

PR #13 identified the absence of direct Company↔Contact and Deal↔Company/Contact FKs, polymorphic `object_associations`, and many loose UUID links in MeetingBooking, DeliveryProject and SalesPerformanceEvent. Production confirms 5,838 object associations. These links must be traversed before any cleanup. Physical FK absence does not mean deletion safety. See `13_open_pr_inventory_and_merge_plan.md`.

## Reproduction SQL (safe form)

Use catalog queries only inside `BEGIN READ ONLY`; exact row counts were obtained from one `count(*)` per quoted catalog table. Do not reuse the dynamic query mechanism for DML. The executed query selected `pg_class`, `information_schema.columns`, `pg_constraint`, and `pg_indexes`, then rolled back.

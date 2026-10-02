-- Stage3 Core Foundation
-- Additive migration draft. Do not apply to production before preview validation.
-- New entity IDs are application-supplied UUIDv7.

CREATE TYPE "org_node_type" AS ENUM ('business', 'department', 'team');
CREATE TYPE "org_node_status" AS ENUM ('active', 'inactive');
CREATE TYPE "permission_override_effect" AS ENUM ('allow', 'deny');
CREATE TYPE "approval_priority" AS ENUM ('urgent', 'important', 'normal');
CREATE TYPE "approval_status" AS ENUM ('draft', 'pending', 'approved', 'rejected', 'returned', 'canceled', 'expired', 'execution_failed');
CREATE TYPE "approval_step_kind" AS ENUM ('review', 'approve');
CREATE TYPE "approval_step_status" AS ENUM ('pending', 'approved', 'rejected', 'returned', 'skipped');
CREATE TYPE "approval_action_type" AS ENUM ('submit', 'comment', 'approve', 'reject', 'return', 'delegate', 'escalate', 'expire', 'execute', 'execution_fail');

CREATE TABLE "org_nodes" (
  "id" UUID NOT NULL,
  "organization_id" UUID NOT NULL,
  "parent_id" UUID,
  "type" "org_node_type" NOT NULL,
  "name" VARCHAR(160) NOT NULL,
  "status" "org_node_status" NOT NULL DEFAULT 'active',
  "display_order" INTEGER NOT NULL DEFAULT 0,
  "metadata" JSONB NOT NULL DEFAULT '{}',
  "created_at" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "org_nodes_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "role_definitions" (
  "id" UUID NOT NULL,
  "organization_id" UUID NOT NULL,
  "key" VARCHAR(80) NOT NULL,
  "name" VARCHAR(120) NOT NULL,
  "level" INTEGER NOT NULL DEFAULT 0,
  "permissions" JSONB NOT NULL DEFAULT '[]',
  "aggregation_rule" JSONB,
  "is_system" BOOLEAN NOT NULL DEFAULT false,
  "created_at" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "role_definitions_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "org_node_memberships" (
  "id" UUID NOT NULL,
  "organization_id" UUID NOT NULL,
  "user_id" UUID NOT NULL,
  "org_node_id" UUID NOT NULL,
  "role_definition_id" UUID,
  "is_primary" BOOLEAN NOT NULL DEFAULT false,
  "valid_from" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "valid_to" TIMESTAMPTZ(3),
  "created_at" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "org_node_memberships_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "user_permission_overrides" (
  "id" UUID NOT NULL,
  "organization_id" UUID NOT NULL,
  "user_id" UUID NOT NULL,
  "permission" VARCHAR(120) NOT NULL,
  "effect" "permission_override_effect" NOT NULL,
  "org_node_id" UUID,
  "reason" TEXT,
  "valid_from" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "valid_to" TIMESTAMPTZ(3),
  "created_by_user_id" UUID,
  "created_at" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "user_permission_overrides_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "corporate_groups" (
  "id" UUID NOT NULL,
  "organization_id" UUID NOT NULL,
  "name" VARCHAR(200) NOT NULL,
  "normalized_name" VARCHAR(200),
  "metadata" JSONB NOT NULL DEFAULT '{}',
  "created_at" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "corporate_groups_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "hospital_profiles" (
  "id" UUID NOT NULL,
  "organization_id" UUID NOT NULL,
  "company_id" UUID NOT NULL,
  "corporate_group_id" UUID,
  "specialty" VARCHAR(200),
  "director_name" VARCHAR(160),
  "trade_area" JSONB,
  "urls" JSONB NOT NULL DEFAULT '{}',
  "current_state" JSONB NOT NULL DEFAULT '{}',
  "metadata" JSONB NOT NULL DEFAULT '{}',
  "created_at" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "hospital_profiles_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "approval_sla_policies" (
  "id" UUID NOT NULL,
  "organization_id" UUID NOT NULL,
  "priority" "approval_priority" NOT NULL,
  "reminder_minutes" INTEGER,
  "escalation_mode" VARCHAR(40) NOT NULL,
  "escalation_minutes" INTEGER,
  "cutoff_hour" INTEGER,
  "cutoff_minute" INTEGER DEFAULT 0,
  "timezone" VARCHAR(80) NOT NULL DEFAULT 'Asia/Tokyo',
  "enabled" BOOLEAN NOT NULL DEFAULT true,
  "created_at" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "approval_sla_policies_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "approval_requests" (
  "id" UUID NOT NULL,
  "organization_id" UUID NOT NULL,
  "type" VARCHAR(80) NOT NULL,
  "target_type" VARCHAR(80) NOT NULL,
  "target_id" UUID,
  "requested_by_user_id" UUID,
  "requested_by_agent_type" VARCHAR(120),
  "priority" "approval_priority" NOT NULL,
  "risk_level" VARCHAR(40),
  "amount" DECIMAL(18,2),
  "amount_delta" DECIMAL(18,2),
  "reason" TEXT,
  "before_snapshot" JSONB,
  "proposed_snapshot" JSONB,
  "expected_target_updated_at" TIMESTAMPTZ(3),
  "status" "approval_status" NOT NULL DEFAULT 'pending',
  "reminded_at" TIMESTAMPTZ(3),
  "escalated_at" TIMESTAMPTZ(3),
  "correlation_id" VARCHAR(120),
  "idempotency_key" VARCHAR(200),
  "executed_at" TIMESTAMPTZ(3),
  "execution_status" VARCHAR(80),
  "execution_error" TEXT,
  "created_at" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "approval_requests_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "approval_steps" (
  "id" UUID NOT NULL,
  "organization_id" UUID NOT NULL,
  "approval_request_id" UUID NOT NULL,
  "step_order" INTEGER NOT NULL,
  "kind" "approval_step_kind" NOT NULL,
  "status" "approval_step_status" NOT NULL DEFAULT 'pending',
  "assigned_user_id" UUID,
  "assigned_role_key" VARCHAR(80),
  "assigned_org_node_id" UUID,
  "any_one_group_key" VARCHAR(80),
  "acted_by_user_id" UUID,
  "acted_at" TIMESTAMPTZ(3),
  "due_at" TIMESTAMPTZ(3),
  "metadata" JSONB NOT NULL DEFAULT '{}',
  "created_at" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updated_at" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "approval_steps_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "approval_actions" (
  "id" UUID NOT NULL,
  "organization_id" UUID NOT NULL,
  "approval_request_id" UUID NOT NULL,
  "approval_step_id" UUID,
  "actor_user_id" UUID,
  "action" "approval_action_type" NOT NULL,
  "comment" TEXT,
  "metadata" JSONB NOT NULL DEFAULT '{}',
  "created_at" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "approval_actions_pkey" PRIMARY KEY ("id")
);

CREATE TABLE "approval_delegations" (
  "id" UUID NOT NULL,
  "organization_id" UUID NOT NULL,
  "from_user_id" UUID NOT NULL,
  "to_user_id" UUID NOT NULL,
  "approval_types" JSONB NOT NULL DEFAULT '[]',
  "valid_from" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "valid_to" TIMESTAMPTZ(3),
  "enabled" BOOLEAN NOT NULL DEFAULT true,
  "created_by_user_id" UUID,
  "created_at" TIMESTAMPTZ(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "approval_delegations_pkey" PRIMARY KEY ("id")
);

ALTER TABLE "audit_logs"
  ADD COLUMN "correlation_id" VARCHAR(120),
  ADD COLUMN "approval_request_id" UUID,
  ADD COLUMN "source_type" VARCHAR(40),
  ADD COLUMN "source_id" VARCHAR(160),
  ADD COLUMN "reason" TEXT;

CREATE UNIQUE INDEX "role_definitions_organization_id_key_key" ON "role_definitions"("organization_id","key");
CREATE INDEX "org_nodes_organization_id_parent_id_status_display_order_idx" ON "org_nodes"("organization_id","parent_id","status","display_order");
CREATE INDEX "org_node_memberships_organization_id_user_id_valid_to_idx" ON "org_node_memberships"("organization_id","user_id","valid_to");
CREATE INDEX "org_node_memberships_organization_id_org_node_id_valid_to_idx" ON "org_node_memberships"("organization_id","org_node_id","valid_to");
CREATE UNIQUE INDEX "org_node_memberships_one_active_primary_uq" ON "org_node_memberships"("organization_id","user_id")
  WHERE "is_primary" = true AND "valid_to" IS NULL;
CREATE INDEX "user_permission_overrides_organization_id_user_id_permission_valid_to_idx" ON "user_permission_overrides"("organization_id","user_id","permission","valid_to");
CREATE INDEX "corporate_groups_organization_id_name_idx" ON "corporate_groups"("organization_id","name");
CREATE UNIQUE INDEX "hospital_profiles_company_id_key" ON "hospital_profiles"("company_id");
CREATE INDEX "hospital_profiles_organization_id_corporate_group_id_idx" ON "hospital_profiles"("organization_id","corporate_group_id");
CREATE UNIQUE INDEX "approval_sla_policies_organization_id_priority_key" ON "approval_sla_policies"("organization_id","priority");
CREATE INDEX "approval_requests_organization_id_status_priority_created_at_idx" ON "approval_requests"("organization_id","status","priority","created_at");
CREATE INDEX "approval_requests_organization_id_target_type_target_id_idx" ON "approval_requests"("organization_id","target_type","target_id");
CREATE INDEX "approval_requests_organization_id_correlation_id_idx" ON "approval_requests"("organization_id","correlation_id");
CREATE UNIQUE INDEX "approval_requests_org_idempotency_uq" ON "approval_requests"("organization_id","idempotency_key")
  WHERE "idempotency_key" IS NOT NULL;
CREATE UNIQUE INDEX "approval_steps_approval_request_id_step_order_key" ON "approval_steps"("approval_request_id","step_order");
CREATE INDEX "approval_steps_organization_id_status_assigned_user_id_due_at_idx" ON "approval_steps"("organization_id","status","assigned_user_id","due_at");
CREATE INDEX "approval_steps_organization_id_approval_request_id_step_order_idx" ON "approval_steps"("organization_id","approval_request_id","step_order");
CREATE INDEX "approval_actions_organization_id_approval_request_id_created_at_idx" ON "approval_actions"("organization_id","approval_request_id","created_at");
CREATE INDEX "approval_delegations_organization_id_from_user_id_enabled_valid_to_idx" ON "approval_delegations"("organization_id","from_user_id","enabled","valid_to");
CREATE INDEX "audit_logs_organization_id_approval_request_id_created_at_idx" ON "audit_logs"("organization_id","approval_request_id","created_at");
CREATE INDEX "audit_logs_organization_id_correlation_id_idx" ON "audit_logs"("organization_id","correlation_id");

ALTER TABLE "org_nodes" ADD CONSTRAINT "org_nodes_organization_id_fkey" FOREIGN KEY ("organization_id") REFERENCES "Organization"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "org_nodes" ADD CONSTRAINT "org_nodes_parent_id_fkey" FOREIGN KEY ("parent_id") REFERENCES "org_nodes"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "role_definitions" ADD CONSTRAINT "role_definitions_organization_id_fkey" FOREIGN KEY ("organization_id") REFERENCES "Organization"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "org_node_memberships" ADD CONSTRAINT "org_node_memberships_organization_id_fkey" FOREIGN KEY ("organization_id") REFERENCES "Organization"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "org_node_memberships" ADD CONSTRAINT "org_node_memberships_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "org_node_memberships" ADD CONSTRAINT "org_node_memberships_org_node_id_fkey" FOREIGN KEY ("org_node_id") REFERENCES "org_nodes"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "org_node_memberships" ADD CONSTRAINT "org_node_memberships_role_definition_id_fkey" FOREIGN KEY ("role_definition_id") REFERENCES "role_definitions"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "user_permission_overrides" ADD CONSTRAINT "user_permission_overrides_organization_id_fkey" FOREIGN KEY ("organization_id") REFERENCES "Organization"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "user_permission_overrides" ADD CONSTRAINT "user_permission_overrides_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "user_permission_overrides" ADD CONSTRAINT "user_permission_overrides_org_node_id_fkey" FOREIGN KEY ("org_node_id") REFERENCES "org_nodes"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "user_permission_overrides" ADD CONSTRAINT "user_permission_overrides_created_by_user_id_fkey" FOREIGN KEY ("created_by_user_id") REFERENCES "User"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "corporate_groups" ADD CONSTRAINT "corporate_groups_organization_id_fkey" FOREIGN KEY ("organization_id") REFERENCES "Organization"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "hospital_profiles" ADD CONSTRAINT "hospital_profiles_organization_id_fkey" FOREIGN KEY ("organization_id") REFERENCES "Organization"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "hospital_profiles" ADD CONSTRAINT "hospital_profiles_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "companies"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "hospital_profiles" ADD CONSTRAINT "hospital_profiles_corporate_group_id_fkey" FOREIGN KEY ("corporate_group_id") REFERENCES "corporate_groups"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "approval_sla_policies" ADD CONSTRAINT "approval_sla_policies_organization_id_fkey" FOREIGN KEY ("organization_id") REFERENCES "Organization"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "approval_requests" ADD CONSTRAINT "approval_requests_organization_id_fkey" FOREIGN KEY ("organization_id") REFERENCES "Organization"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "approval_requests" ADD CONSTRAINT "approval_requests_requested_by_user_id_fkey" FOREIGN KEY ("requested_by_user_id") REFERENCES "User"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "approval_steps" ADD CONSTRAINT "approval_steps_organization_id_fkey" FOREIGN KEY ("organization_id") REFERENCES "Organization"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "approval_steps" ADD CONSTRAINT "approval_steps_approval_request_id_fkey" FOREIGN KEY ("approval_request_id") REFERENCES "approval_requests"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "approval_steps" ADD CONSTRAINT "approval_steps_assigned_user_id_fkey" FOREIGN KEY ("assigned_user_id") REFERENCES "User"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "approval_steps" ADD CONSTRAINT "approval_steps_acted_by_user_id_fkey" FOREIGN KEY ("acted_by_user_id") REFERENCES "User"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "approval_steps" ADD CONSTRAINT "approval_steps_assigned_org_node_id_fkey" FOREIGN KEY ("assigned_org_node_id") REFERENCES "org_nodes"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "approval_actions" ADD CONSTRAINT "approval_actions_organization_id_fkey" FOREIGN KEY ("organization_id") REFERENCES "Organization"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "approval_actions" ADD CONSTRAINT "approval_actions_approval_request_id_fkey" FOREIGN KEY ("approval_request_id") REFERENCES "approval_requests"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "approval_actions" ADD CONSTRAINT "approval_actions_approval_step_id_fkey" FOREIGN KEY ("approval_step_id") REFERENCES "approval_steps"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "approval_actions" ADD CONSTRAINT "approval_actions_actor_user_id_fkey" FOREIGN KEY ("actor_user_id") REFERENCES "User"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "approval_delegations" ADD CONSTRAINT "approval_delegations_organization_id_fkey" FOREIGN KEY ("organization_id") REFERENCES "Organization"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "approval_delegations" ADD CONSTRAINT "approval_delegations_from_user_id_fkey" FOREIGN KEY ("from_user_id") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "approval_delegations" ADD CONSTRAINT "approval_delegations_to_user_id_fkey" FOREIGN KEY ("to_user_id") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "approval_delegations" ADD CONSTRAINT "approval_delegations_created_by_user_id_fkey" FOREIGN KEY ("created_by_user_id") REFERENCES "User"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "audit_logs" ADD CONSTRAINT "audit_logs_approval_request_id_fkey" FOREIGN KEY ("approval_request_id") REFERENCES "approval_requests"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- SECURITY:
-- Do not GRANT anon/authenticated on these new tables.
-- Data API / grants / RLS hardening is a separate reviewed migration.

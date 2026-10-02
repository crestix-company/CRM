import type {
  ApprovalPriority,
  ApprovalStepKind,
  Prisma,
} from "@prisma/client";

export type ApprovalType =
  | "AMOUNT_CHANGE"
  | "DISCOUNT"
  | "CONTRACT_SEND"
  | "CUSTOMER_MINUTES_SEND"
  | "CS_PLAN"
  | "CROSS_SELL"
  | "KNOWLEDGE_IS"
  | "KNOWLEDGE_FS"
  | "ADMIN_SETTING"
  | "COMPANY_PRIORITY"
  | "SYSTEM_IMPORTANT_CHANGE"
  | "HR_MAJOR";

export type ApprovalStepTemplate = {
  kind: ApprovalStepKind;
  assignedUserId?: string | null;
  assignedRoleKey?: string | null;
  eligibleRoleKeys?: string[];
  anyOneGroupKey?: string | null;
  metadata?: Prisma.InputJsonValue;
};

export type ApprovalPolicy = {
  priority: ApprovalPriority;
  steps: ApprovalStepTemplate[];
};

export type CreateApprovalInput = {
  type: ApprovalType;
  targetType: string;
  targetId?: string | null;
  requestedByUserId?: string | null;
  requestedByAgentType?: string | null;
  riskLevel?: string | null;
  amount?: number | string | null;
  amountDelta?: number | string | null;
  reason?: string | null;
  beforeSnapshot?: Prisma.InputJsonValue;
  proposedSnapshot?: Prisma.InputJsonValue;
  expectedTargetUpdatedAt?: Date | null;
  idempotencyKey?: string | null;
  correlationId?: string | null;
};

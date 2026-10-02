import { ApprovalPriority, ApprovalStepKind } from "@prisma/client";
import type { ApprovalPolicy, ApprovalType } from "./types";

export const ApprovalRoleKey = {
  EXECUTIVE_FINAL: "executive_final",
  FS_MANAGER: "fs_manager",
  IS_MANAGER: "is_manager",
  TECHNICAL_OWNER: "technical_owner",
} as const;

function requesterReview(): ApprovalPolicy["steps"][number] {
  return {
    kind: ApprovalStepKind.REVIEW,
    metadata: { assignment: "requester" },
  };
}

const policies: Record<ApprovalType, ApprovalPolicy> = {
  AMOUNT_CHANGE: {
    priority: ApprovalPriority.URGENT,
    steps: [
      {
        kind: ApprovalStepKind.REVIEW,
        assignedRoleKey: ApprovalRoleKey.FS_MANAGER,
      },
      {
        kind: ApprovalStepKind.APPROVE,
        assignedRoleKey: ApprovalRoleKey.EXECUTIVE_FINAL,
      },
    ],
  },
  DISCOUNT: {
    priority: ApprovalPriority.URGENT,
    steps: [
      {
        kind: ApprovalStepKind.REVIEW,
        assignedRoleKey: ApprovalRoleKey.FS_MANAGER,
      },
      {
        kind: ApprovalStepKind.APPROVE,
        assignedRoleKey: ApprovalRoleKey.EXECUTIVE_FINAL,
      },
    ],
  },
  CONTRACT_SEND: {
    priority: ApprovalPriority.URGENT,
    steps: [
      requesterReview(),
      {
        kind: ApprovalStepKind.APPROVE,
        eligibleRoleKeys: [
          ApprovalRoleKey.EXECUTIVE_FINAL,
          ApprovalRoleKey.FS_MANAGER,
        ],
        anyOneGroupKey: "contract_final",
      },
    ],
  },
  CUSTOMER_MINUTES_SEND: {
    priority: ApprovalPriority.IMPORTANT,
    steps: [
      {
        kind: ApprovalStepKind.APPROVE,
        metadata: { assignment: "requester" },
      },
    ],
  },
  CS_PLAN: {
    priority: ApprovalPriority.IMPORTANT,
    steps: [
      requesterReview(),
      {
        kind: ApprovalStepKind.APPROVE,
        assignedRoleKey: ApprovalRoleKey.FS_MANAGER,
      },
    ],
  },
  CROSS_SELL: {
    priority: ApprovalPriority.IMPORTANT,
    steps: [
      requesterReview(),
      {
        kind: ApprovalStepKind.APPROVE,
        assignedRoleKey: ApprovalRoleKey.FS_MANAGER,
      },
    ],
  },
  KNOWLEDGE_IS: {
    priority: ApprovalPriority.NORMAL,
    steps: [
      {
        kind: ApprovalStepKind.APPROVE,
        assignedRoleKey: ApprovalRoleKey.IS_MANAGER,
      },
    ],
  },
  KNOWLEDGE_FS: {
    priority: ApprovalPriority.NORMAL,
    steps: [
      {
        kind: ApprovalStepKind.APPROVE,
        assignedRoleKey: ApprovalRoleKey.FS_MANAGER,
      },
    ],
  },
  ADMIN_SETTING: {
    priority: ApprovalPriority.NORMAL,
    steps: [
      {
        kind: ApprovalStepKind.REVIEW,
        assignedRoleKey: ApprovalRoleKey.TECHNICAL_OWNER,
      },
      {
        kind: ApprovalStepKind.APPROVE,
        assignedRoleKey: ApprovalRoleKey.EXECUTIVE_FINAL,
      },
    ],
  },
  COMPANY_PRIORITY: {
    priority: ApprovalPriority.IMPORTANT,
    steps: [
      {
        kind: ApprovalStepKind.APPROVE,
        assignedRoleKey: ApprovalRoleKey.EXECUTIVE_FINAL,
      },
    ],
  },
  SYSTEM_IMPORTANT_CHANGE: {
    priority: ApprovalPriority.IMPORTANT,
    steps: [
      {
        kind: ApprovalStepKind.REVIEW,
        assignedRoleKey: ApprovalRoleKey.TECHNICAL_OWNER,
      },
      {
        kind: ApprovalStepKind.APPROVE,
        assignedRoleKey: ApprovalRoleKey.EXECUTIVE_FINAL,
      },
    ],
  },
  HR_MAJOR: {
    priority: ApprovalPriority.IMPORTANT,
    steps: [
      {
        kind: ApprovalStepKind.APPROVE,
        assignedRoleKey: ApprovalRoleKey.EXECUTIVE_FINAL,
      },
    ],
  },
};

export function approvalPolicyFor(type: ApprovalType): ApprovalPolicy {
  return policies[type];
}

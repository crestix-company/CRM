import {
  ApprovalActionType,
  ApprovalStatus,
  ApprovalStepKind,
  ApprovalStepStatus,
  OperationalEventType,
  type Prisma,
} from "@prisma/client";
import type { AuthContext } from "../auth";
import { BadRequestError } from "../api";
import {
  Permission,
  AuthorizationError,
} from "../permissions";
import { requireEffectivePermission } from "../effective-permissions";
import { prisma } from "../prisma";
import { uuidv7 } from "../server/uuidv7";
import { notifyApprovalUsers } from "./notifications";
import { approvalPolicyFor } from "./policies";
import { approvalSlaWindow } from "./sla";
import type {
  ApprovalStepTemplate,
  CreateApprovalInput,
} from "./types";

function stepMetadata(
  template: ApprovalStepTemplate,
  requestedByUserId: string | null,
): Prisma.InputJsonValue {
  const base =
    template.metadata &&
    typeof template.metadata === "object" &&
    !Array.isArray(template.metadata)
      ? template.metadata
      : {};
  return {
    ...base,
    ...(template.eligibleRoleKeys
      ? { eligibleRoleKeys: template.eligibleRoleKeys }
      : {}),
    ...(base && "assignment" in base && base.assignment === "requester"
      ? { requesterUserId: requestedByUserId }
      : {}),
  } as Prisma.InputJsonValue;
}

async function activeUsersForRole(
  organizationId: string,
  roleKey: string,
) {
  const now = new Date();
  const rows = await prisma.orgNodeMembership.findMany({
    where: {
      organizationId,
      validFrom: { lte: now },
      OR: [{ validTo: null }, { validTo: { gt: now } }],
      roleDefinition: { key: roleKey },
    },
    select: { userId: true },
    distinct: ["userId"],
  });
  return rows.map((row) => row.userId);
}

async function eligibleUsersForStep(step: {
  assignedUserId: string | null;
  assignedRoleKey: string | null;
  metadata: unknown;
  organizationId: string;
}) {
  if (step.assignedUserId) return [step.assignedUserId];

  const metadata =
    step.metadata && typeof step.metadata === "object" && !Array.isArray(step.metadata)
      ? (step.metadata as Record<string, unknown>)
      : {};
  const requesterUserId =
    typeof metadata.requesterUserId === "string" ? metadata.requesterUserId : null;
  if (requesterUserId) return [requesterUserId];

  const keys = [
    ...(step.assignedRoleKey ? [step.assignedRoleKey] : []),
    ...(Array.isArray(metadata.eligibleRoleKeys)
      ? metadata.eligibleRoleKeys.filter(
          (item): item is string => typeof item === "string",
        )
      : []),
  ];
  const users = await Promise.all(
    [...new Set(keys)].map((key) =>
      activeUsersForRole(step.organizationId, key),
    ),
  );
  return [...new Set(users.flat())];
}

async function currentStep(approvalRequestId: string) {
  return prisma.approvalStep.findFirst({
    where: {
      approvalRequestId,
      status: ApprovalStepStatus.PENDING,
    },
    orderBy: { stepOrder: "asc" },
  });
}

async function isDelegatedTo(
  organizationId: string,
  fromUserIds: string[],
  toUserId: string,
  approvalType: string,
) {
  if (!fromUserIds.length) return false;
  const now = new Date();
  const rows = await prisma.approvalDelegation.findMany({
    where: {
      organizationId,
      fromUserId: { in: fromUserIds },
      toUserId,
      enabled: true,
      validFrom: { lte: now },
      OR: [{ validTo: null }, { validTo: { gt: now } }],
    },
    select: { approvalTypes: true },
  });
  return rows.some((row) => {
    if (!Array.isArray(row.approvalTypes)) return true;
    const types = row.approvalTypes.filter(
      (item): item is string => typeof item === "string",
    );
    return types.length === 0 || types.includes(approvalType);
  });
}

async function assertStepActor(
  context: AuthContext,
  request: { id: string; type: string; organizationId: string },
  stepId: string,
) {
  const step = await currentStep(request.id);
  if (!step || step.id !== stepId) {
    throw new BadRequestError("現在処理できる承認ステップではありません。");
  }

  const eligibleUsers = await eligibleUsersForStep(step);
  if (eligibleUsers.includes(context.user.id)) return step;
  if (
    await isDelegatedTo(
      request.organizationId,
      eligibleUsers,
      context.user.id,
      request.type,
    )
  ) {
    return step;
  }
  throw new AuthorizationError("この承認ステップの担当者ではありません。");
}

export async function createApprovalRequest(
  context: AuthContext,
  input: CreateApprovalInput,
) {
  await requireEffectivePermission(context, Permission.READ_APPROVAL);
  const organizationId = context.organization.id;
  const requestedByUserId = input.requestedByUserId ?? context.user.id;
  const policy = approvalPolicyFor(input.type);
  const requestId = uuidv7();
  const correlationId = input.correlationId ?? uuidv7();
  const now = new Date();
  const sla = approvalSlaWindow(policy.priority, now);

  const existing = input.idempotencyKey
    ? await prisma.approvalRequest.findFirst({
        where: { organizationId, idempotencyKey: input.idempotencyKey },
        include: { steps: { orderBy: { stepOrder: "asc" } } },
      })
    : null;
  if (existing) return existing;

  const created = await prisma.$transaction(async (tx) => {
    const request = await tx.approvalRequest.create({
      data: {
        id: requestId,
        organizationId,
        type: input.type,
        targetType: input.targetType,
        targetId: input.targetId ?? null,
        requestedByUserId,
        requestedByAgentType: input.requestedByAgentType ?? null,
        priority: policy.priority,
        riskLevel: input.riskLevel ?? null,
        amount: input.amount ?? null,
        amountDelta: input.amountDelta ?? null,
        reason: input.reason ?? null,
        beforeSnapshot: input.beforeSnapshot,
        proposedSnapshot: input.proposedSnapshot,
        expectedTargetUpdatedAt: input.expectedTargetUpdatedAt ?? null,
        status: ApprovalStatus.PENDING,
        correlationId,
        idempotencyKey: input.idempotencyKey ?? null,
      },
    });

    await tx.approvalStep.createMany({
      data: policy.steps.map((template, index) => ({
        id: uuidv7(),
        organizationId,
        approvalRequestId: request.id,
        stepOrder: index + 1,
        kind: template.kind,
        assignedUserId: template.assignedUserId ?? null,
        assignedRoleKey: template.assignedRoleKey ?? null,
        anyOneGroupKey: template.anyOneGroupKey ?? null,
        dueAt: index === 0 ? sla.escalationAt : null,
        metadata: stepMetadata(template, requestedByUserId),
      })),
    });

    await tx.approvalAction.create({
      data: {
        id: uuidv7(),
        organizationId,
        approvalRequestId: request.id,
        actorUserId: context.user.id,
        action: ApprovalActionType.SUBMIT,
        metadata: {
          reminderAt: sla.reminderAt.toISOString(),
          escalationAt: sla.escalationAt.toISOString(),
        },
      },
    });

    await tx.auditLog.create({
      data: {
        organizationId,
        actorUserId: context.user.id,
        action: "APPROVAL_REQUESTED",
        targetType: input.targetType,
        targetId: input.targetId ?? null,
        before: input.beforeSnapshot,
        after: input.proposedSnapshot,
        correlationId,
        approvalRequestId: request.id,
        sourceType: input.requestedByAgentType ? "AI" : "USER",
        sourceId: input.requestedByAgentType ?? context.user.id,
        reason: input.reason ?? null,
      },
    });

    await tx.operationalEvent.create({
      data: {
        organizationId,
        eventType: OperationalEventType.APPROVAL_REQUESTED,
        correlationId,
        status: "PENDING",
        metadata: {
          approvalRequestId: request.id,
          type: request.type,
          targetType: request.targetType,
          targetId: request.targetId,
        },
      },
    });

    return request;
  });

  const first = await currentStep(created.id);
  if (first) {
    const recipients = await eligibleUsersForStep(first);
    await notifyApprovalUsers(prisma, {
      organizationId,
      recipientUserIds: recipients,
      type: "APPROVAL_REQUESTED",
      title: "承認依頼があります",
      body: input.reason ?? null,
      approvalRequestId: created.id,
    });
  }

  return prisma.approvalRequest.findUniqueOrThrow({
    where: { id: created.id },
    include: { steps: { orderBy: { stepOrder: "asc" } } },
  });
}

async function actOnStep(
  context: AuthContext,
  approvalRequestId: string,
  stepId: string,
  action: "approve" | "reject" | "return",
  comment?: string | null,
) {
  const request = await prisma.approvalRequest.findFirst({
    where: {
      id: approvalRequestId,
      organizationId: context.organization.id,
      status: ApprovalStatus.PENDING,
    },
  });
  if (!request) throw new BadRequestError("承認依頼が見つかりません。");

  const step = await assertStepActor(context, request, stepId);
  const requiredPermission =
    step.kind === ApprovalStepKind.APPROVE
      ? Permission.APPROVE_APPROVAL
      : Permission.REVIEW_APPROVAL;
  await requireEffectivePermission(context, requiredPermission);

  if (action !== "approve" && !comment?.trim()) {
    throw new BadRequestError("却下・差戻し理由を入力してください。");
  }

  const nextStatus =
    action === "reject"
      ? ApprovalStatus.REJECTED
      : action === "return"
        ? ApprovalStatus.RETURNED
        : null;
  const stepStatus =
    action === "reject"
      ? ApprovalStepStatus.REJECTED
      : action === "return"
        ? ApprovalStepStatus.RETURNED
        : ApprovalStepStatus.APPROVED;
  const actionType =
    action === "reject"
      ? ApprovalActionType.REJECT
      : action === "return"
        ? ApprovalActionType.RETURN
        : ApprovalActionType.APPROVE;
  const eventType =
    action === "reject"
      ? OperationalEventType.APPROVAL_REJECTED
      : action === "return"
        ? OperationalEventType.APPROVAL_RETURNED
        : step.kind === ApprovalStepKind.REVIEW
          ? OperationalEventType.APPROVAL_REVIEWED
          : OperationalEventType.APPROVAL_APPROVED;

  await prisma.$transaction(async (tx) => {
    await tx.approvalStep.update({
      where: { id: step.id },
      data: {
        status: stepStatus,
        actedByUserId: context.user.id,
        actedAt: new Date(),
      },
    });

    await tx.approvalAction.create({
      data: {
        id: uuidv7(),
        organizationId: context.organization.id,
        approvalRequestId,
        approvalStepId: step.id,
        actorUserId: context.user.id,
        action: actionType,
        comment: comment?.trim() || null,
      },
    });

    const remaining = await tx.approvalStep.count({
      where: {
        approvalRequestId,
        status: ApprovalStepStatus.PENDING,
      },
    });

    await tx.approvalRequest.update({
      where: { id: approvalRequestId },
      data: {
        status:
          nextStatus ??
          (remaining === 0 ? ApprovalStatus.APPROVED : ApprovalStatus.PENDING),
      },
    });

    await tx.auditLog.create({
      data: {
        organizationId: context.organization.id,
        actorUserId: context.user.id,
        action: `APPROVAL_${action.toUpperCase()}`,
        targetType: request.targetType,
        targetId: request.targetId,
        correlationId: request.correlationId,
        approvalRequestId,
        sourceType: "USER",
        sourceId: context.user.id,
        reason: comment?.trim() || null,
      },
    });

    await tx.operationalEvent.create({
      data: {
        organizationId: context.organization.id,
        eventType,
        correlationId: request.correlationId,
        status: action === "approve" ? "APPROVED" : nextStatus,
        metadata: {
          approvalRequestId,
          stepId: step.id,
          stepKind: step.kind,
          actorUserId: context.user.id,
        },
      },
    });
  });

  if (action === "approve") {
    const next = await currentStep(approvalRequestId);
    if (next) {
      const recipients = await eligibleUsersForStep(next);
      await notifyApprovalUsers(prisma, {
        organizationId: context.organization.id,
        recipientUserIds: recipients,
        type: "APPROVAL_REQUESTED",
        title: "承認依頼があります",
        approvalRequestId,
      });
    }
  }

  return prisma.approvalRequest.findUniqueOrThrow({
    where: { id: approvalRequestId },
    include: {
      steps: { orderBy: { stepOrder: "asc" } },
      actions: { orderBy: { createdAt: "asc" } },
    },
  });
}

export function approveApprovalStep(
  context: AuthContext,
  approvalRequestId: string,
  stepId: string,
  comment?: string | null,
) {
  return actOnStep(context, approvalRequestId, stepId, "approve", comment);
}

export function rejectApprovalStep(
  context: AuthContext,
  approvalRequestId: string,
  stepId: string,
  reason: string,
) {
  return actOnStep(context, approvalRequestId, stepId, "reject", reason);
}

export function returnApprovalStep(
  context: AuthContext,
  approvalRequestId: string,
  stepId: string,
  reason: string,
) {
  return actOnStep(context, approvalRequestId, stepId, "return", reason);
}

export async function addApprovalComment(
  context: AuthContext,
  approvalRequestId: string,
  comment: string,
) {
  await requireEffectivePermission(context, Permission.READ_APPROVAL);
  if (!comment.trim()) throw new BadRequestError("コメントを入力してください。");

  const request = await prisma.approvalRequest.findFirst({
    where: { id: approvalRequestId, organizationId: context.organization.id },
    select: { id: true },
  });
  if (!request) throw new BadRequestError("承認依頼が見つかりません。");

  return prisma.approvalAction.create({
    data: {
      id: uuidv7(),
      organizationId: context.organization.id,
      approvalRequestId,
      actorUserId: context.user.id,
      action: ApprovalActionType.COMMENT,
      comment: comment.trim(),
    },
  });
}

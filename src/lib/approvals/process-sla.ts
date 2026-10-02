import { ApprovalActionType, ApprovalStatus, OperationalEventType } from "@prisma/client";
import { prisma } from "../prisma";
import { uuidv7 } from "../server/uuidv7";
import { notifyApprovalUsers } from "./notifications";
import { activeUsersForApprovalRole, eligibleUsersForApprovalStep } from "./service";
import { approvalSlaWindow } from "./sla";

function obj(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};
}

export async function processApprovalSla(now = new Date()) {
  const requests = await prisma.approvalRequest.findMany({
    where: { status: ApprovalStatus.PENDING },
    include: {
      steps: {
        where: { status: "PENDING" },
        orderBy: { stepOrder: "asc" },
        take: 1,
      },
    },
    orderBy: { createdAt: "asc" },
    take: 200,
  });

  let reminded = 0;
  let escalated = 0;

  for (const request of requests) {
    const step = request.steps[0];
    if (!step) continue;
    const sla = approvalSlaWindow(request.priority, request.createdAt);

    if (!request.remindedAt && now >= sla.reminderAt) {
      const claim = await prisma.approvalRequest.updateMany({
        where: { id: request.id, remindedAt: null, status: ApprovalStatus.PENDING },
        data: { remindedAt: now },
      });
      if (claim.count === 1) {
        await notifyApprovalUsers(prisma, {
          organizationId: request.organizationId,
          recipientUserIds: await eligibleUsersForApprovalStep(step),
          type: "APPROVAL_REMINDER",
          title: "承認依頼の再通知",
          body: "未処理の承認依頼があります。",
          approvalRequestId: request.id,
        });
        reminded += 1;
      }
    }

    if (!request.escalatedAt && now >= sla.escalationAt) {
      const claim = await prisma.approvalRequest.updateMany({
        where: { id: request.id, escalatedAt: null, status: ApprovalStatus.PENDING },
        data: { escalatedAt: now },
      });
      if (claim.count !== 1) continue;

      const meta = obj(step.metadata);
      const escalationRoleKey =
        typeof meta.escalationRoleKey === "string" ? meta.escalationRoleKey : null;
      const currentRecipients = await eligibleUsersForApprovalStep(step);
      const managerRecipients = escalationRoleKey
        ? await activeUsersForApprovalRole(request.organizationId, escalationRoleKey)
        : [];
      const recipients = [...new Set([
        ...currentRecipients,
        ...managerRecipients,
        ...(request.requestedByUserId ? [request.requestedByUserId] : []),
      ])];

      await prisma.$transaction(async (tx) => {
        await tx.approvalAction.create({
          data: {
            id: uuidv7(),
            organizationId: request.organizationId,
            approvalRequestId: request.id,
            approvalStepId: step.id,
            action: ApprovalActionType.ESCALATE,
            metadata: { priority: request.priority, escalationRoleKey },
          },
        });
        await tx.auditLog.create({
          data: {
            organizationId: request.organizationId,
            action: "APPROVAL_ESCALATED",
            targetType: request.targetType,
            targetId: request.targetId,
            correlationId: request.correlationId,
            approvalRequestId: request.id,
            sourceType: "SYSTEM",
            sourceId: "approval-sla",
            reason: "Approval SLA exceeded",
          },
        });
        await tx.operationalEvent.create({
          data: {
            organizationId: request.organizationId,
            eventType: OperationalEventType.APPROVAL_ESCALATED,
            correlationId: request.correlationId,
            status: "PENDING",
            metadata: {
              approvalRequestId: request.id,
              stepId: step.id,
              priority: request.priority,
            },
          },
        });
      });

      await notifyApprovalUsers(prisma, {
        organizationId: request.organizationId,
        recipientUserIds: recipients,
        type: "APPROVAL_ESCALATED",
        title: "承認依頼がエスカレーションされました",
        body: "承認SLAを超過しています。",
        approvalRequestId: request.id,
      });
      escalated += 1;
    }
  }

  return { scanned: requests.length, reminded, escalated };
}

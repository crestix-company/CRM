import type { AuthContext } from "../auth";
import { prisma } from "../prisma";

function canViewAll(context: AuthContext) {
  return ["SUPER_ADMIN", "ADMIN", "MANAGER"].includes(context.membership.role);
}

export function approvalVisibilityWhere(context: AuthContext) {
  if (canViewAll(context)) {
    return { organizationId: context.organization.id };
  }
  return {
    organizationId: context.organization.id,
    OR: [
      { requestedByUserId: context.user.id },
      { steps: { some: { assignedUserId: context.user.id } } },
      { steps: { some: { actedByUserId: context.user.id } } },
    ],
  };
}

export async function getVisibleApproval(
  context: AuthContext,
  approvalRequestId: string,
) {
  return prisma.approvalRequest.findFirst({
    where: {
      id: approvalRequestId,
      ...approvalVisibilityWhere(context),
    },
    include: {
      requestedBy: { select: { id: true, name: true, email: true } },
      steps: {
        include: {
          assignedUser: { select: { id: true, name: true } },
          actedBy: { select: { id: true, name: true } },
        },
        orderBy: { stepOrder: "asc" },
      },
      actions: {
        include: { actor: { select: { id: true, name: true } } },
        orderBy: { createdAt: "asc" },
      },
    },
  });
}

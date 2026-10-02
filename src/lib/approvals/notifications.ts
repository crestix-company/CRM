import type { PrismaClient, Prisma } from "@prisma/client";

type Tx = Prisma.TransactionClient | PrismaClient;

export async function notifyApprovalUsers(
  db: Tx,
  input: {
    organizationId: string;
    recipientUserIds: string[];
    type: "APPROVAL_REQUESTED" | "APPROVAL_REMINDER" | "APPROVAL_ESCALATED";
    title: string;
    body?: string | null;
    approvalRequestId: string;
  },
) {
  const recipients = [...new Set(input.recipientUserIds)].filter(Boolean);
  if (!recipients.length) return;

  await db.notification.createMany({
    data: recipients.map((recipientUserId) => ({
      organizationId: input.organizationId,
      recipientUserId,
      type: input.type,
      title: input.title,
      body: input.body ?? null,
      targetType: "APPROVAL_REQUEST",
      targetId: input.approvalRequestId,
    })),
  });
}

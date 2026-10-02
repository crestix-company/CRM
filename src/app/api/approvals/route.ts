import { NextResponse } from "next/server";
import { z } from "zod";
import { apiError } from "@/lib/api";
import { getAuthContext } from "@/lib/auth";
import { createApprovalRequest } from "@/lib/approvals/service";
import { approvalVisibilityWhere } from "@/lib/approvals/queries";
import { Permission, requirePermission } from "@/lib/permissions";
import { prisma } from "@/lib/prisma";

const createSchema = z.object({
  type: z.enum([
    "AMOUNT_CHANGE",
    "DISCOUNT",
    "CONTRACT_SEND",
    "CUSTOMER_MINUTES_SEND",
    "CS_PLAN",
    "CROSS_SELL",
    "KNOWLEDGE_IS",
    "KNOWLEDGE_FS",
    "ADMIN_SETTING",
    "COMPANY_PRIORITY",
    "SYSTEM_IMPORTANT_CHANGE",
    "HR_MAJOR",
  ]),
  targetType: z.string().min(1).max(80),
  targetId: z.string().uuid().nullable().optional(),
  riskLevel: z.string().max(40).nullable().optional(),
  amount: z.union([z.number(), z.string()]).nullable().optional(),
  amountDelta: z.union([z.number(), z.string()]).nullable().optional(),
  reason: z.string().max(5000).nullable().optional(),
  beforeSnapshot: z.record(z.string(), z.unknown()).optional(),
  proposedSnapshot: z.record(z.string(), z.unknown()).optional(),
  expectedTargetUpdatedAt: z.coerce.date().nullable().optional(),
  idempotencyKey: z.string().max(200).nullable().optional(),
});

export async function GET() {
  try {
    const context = await getAuthContext();
    if (!context) return NextResponse.json({ message: "ログインが必要です。" }, { status: 401 });
    requirePermission(context.membership.role, Permission.READ_APPROVAL);

    const items = await prisma.approvalRequest.findMany({
      where: approvalVisibilityWhere(context),
      include: {
        requestedBy: { select: { name: true } },
        steps: {
          where: { status: "PENDING" },
          orderBy: { stepOrder: "asc" },
          take: 1,
        },
      },
      orderBy: [{ priority: "asc" }, { createdAt: "desc" }],
      take: 100,
    });
    return NextResponse.json({ items });
  } catch (error) {
    return apiError(error);
  }
}

export async function POST(request: Request) {
  try {
    const context = await getAuthContext();
    if (!context) return NextResponse.json({ message: "ログインが必要です。" }, { status: 401 });
    requirePermission(context.membership.role, Permission.CRM_WRITE);
    const input = createSchema.parse(await request.json());
    const item = await createApprovalRequest(context, input);
    return NextResponse.json({ item }, { status: 201 });
  } catch (error) {
    return apiError(error);
  }
}

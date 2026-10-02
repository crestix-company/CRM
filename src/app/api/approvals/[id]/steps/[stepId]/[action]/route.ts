import { NextResponse } from "next/server";
import { z } from "zod";
import { apiError, BadRequestError } from "@/lib/api";
import { getAuthContext } from "@/lib/auth";
import {
  approveApprovalStep,
  rejectApprovalStep,
  returnApprovalStep,
} from "@/lib/approvals/service";

type Params = {
  params: Promise<{ id: string; stepId: string; action: string }>;
};

const bodySchema = z.object({
  comment: z.string().max(5000).optional().default(""),
});

export async function POST(request: Request, { params }: Params) {
  try {
    const context = await getAuthContext();
    if (!context) return NextResponse.json({ message: "ログインが必要です。" }, { status: 401 });
    const { id, stepId, action } = await params;
    const body = bodySchema.parse(await request.json().catch(() => ({})));

    const item =
      action === "approve"
        ? await approveApprovalStep(context, id, stepId, body.comment)
        : action === "reject"
          ? await rejectApprovalStep(context, id, stepId, body.comment)
          : action === "return"
            ? await returnApprovalStep(context, id, stepId, body.comment)
            : null;

    if (!item) throw new BadRequestError("不正な承認操作です。");
    return NextResponse.json({ item });
  } catch (error) {
    return apiError(error);
  }
}

import Link from "next/link";
import { redirect } from "next/navigation";
import { PageHeading } from "@/components/ui/page-heading";
import { getAuthContext } from "@/lib/auth";
import { approvalVisibilityWhere } from "@/lib/approvals/queries";
import { Permission, requirePermission } from "@/lib/permissions";
import { prisma } from "@/lib/prisma";

const priorityLabel = { URGENT: "Urgent", IMPORTANT: "Important", NORMAL: "Normal" } as const;

export default async function ApprovalsPage() {
  const context = await getAuthContext();
  if (!context) redirect("/login");
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
    orderBy: [{ createdAt: "desc" }],
    take: 100,
  });

  const rank = { URGENT: 0, IMPORTANT: 1, NORMAL: 2 } as const;
  items.sort((a, b) => rank[a.priority] - rank[b.priority] || b.createdAt.getTime() - a.createdAt.getTime());

  return (
    <div className="mx-auto max-w-[1400px]">
      <PageHeading
        eyebrow="Approval"
        title="承認 Inbox"
        description="金額・契約・顧客送信・重要設定など、人間承認が必要な操作を管理します。"
      />
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] text-left text-sm">
            <thead className="bg-slate-50 text-xs text-slate-500">
              <tr>
                <th className="px-4 py-3">優先度</th>
                <th className="px-4 py-3">種別</th>
                <th className="px-4 py-3">状態</th>
                <th className="px-4 py-3">申請者</th>
                <th className="px-4 py-3">金額影響</th>
                <th className="px-4 py-3">待機時間</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {items.map((item) => (
                <tr key={item.id}>
                  <td className="px-4 py-3 font-bold">{priorityLabel[item.priority]}</td>
                  <td className="px-4 py-3">{item.type}</td>
                  <td className="px-4 py-3">{item.status}</td>
                  <td className="px-4 py-3">{item.requestedBy?.name ?? "AI / System"}</td>
                  <td className="px-4 py-3">
                    {item.amountDelta != null ? `¥${Number(item.amountDelta).toLocaleString()}` : "-"}
                  </td>
                  <td className="px-4 py-3">{waitingText(item.createdAt)}</td>
                  <td className="px-4 py-3 text-right">
                    <Link className="font-bold text-brand-700" href={`/approvals/${item.id}`}>
                      詳細
                    </Link>
                  </td>
                </tr>
              ))}
              {!items.length ? (
                <tr><td colSpan={7} className="px-4 py-12 text-center text-slate-400">承認依頼はありません。</td></tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function waitingText(createdAt: Date) {
  const minutes = Math.max(0, Math.floor((Date.now() - createdAt.getTime()) / 60000));
  if (minutes < 60) return `${minutes}分`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}時間`;
  return `${Math.floor(hours / 24)}日`;
}

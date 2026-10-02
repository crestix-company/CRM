import { notFound, redirect } from "next/navigation";
import { ApprovalActions } from "@/components/approvals/approval-actions";
import { PageHeading } from "@/components/ui/page-heading";
import { getAuthContext } from "@/lib/auth";
import { getVisibleApproval } from "@/lib/approvals/queries";
import { Permission, hasPermission } from "@/lib/permissions";

export default async function ApprovalDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const context = await getAuthContext();
  if (!context) redirect("/login");
  const { id } = await params;
  const item = await getVisibleApproval(context, id);
  if (!item) notFound();

  const currentStep = item.steps.find((step) => step.status === "PENDING") ?? null;
  const canAct = currentStep
    ? currentStep.assignedUserId === context.user.id ||
      ["SUPER_ADMIN", "ADMIN", "MANAGER"].includes(context.membership.role)
    : false;
  const canApprove = hasPermission(
    context.membership.role,
    currentStep?.kind === "APPROVE"
      ? Permission.APPROVE_APPROVAL
      : Permission.REVIEW_APPROVAL,
  );

  return (
    <div className="mx-auto max-w-[1200px]">
      <PageHeading
        eyebrow="Approval"
        title={item.type}
        description={item.reason ?? "承認依頼の内容と履歴を確認します。"}
      />

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
        <main className="space-y-6">
          <section className="card p-5">
            <h2 className="font-bold">変更内容</h2>
            <div className="mt-4 grid gap-4 md:grid-cols-2">
              <Snapshot title="変更前" value={item.beforeSnapshot} />
              <Snapshot title="変更案" value={item.proposedSnapshot} />
            </div>
          </section>

          <section className="card p-5">
            <h2 className="font-bold">承認ルート</h2>
            <div className="mt-4 space-y-3">
              {item.steps.map((step) => (
                <div key={step.id} className="rounded-lg border border-line p-3">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-bold">Step {step.stepOrder} · {step.kind}</p>
                    <span className="text-xs font-bold text-slate-500">{step.status}</span>
                  </div>
                  <p className="mt-1 text-sm text-slate-600">
                    {step.assignedUser?.name ?? step.assignedRoleKey ?? "Policy assignment"}
                  </p>
                  {step.actedBy ? (
                    <p className="mt-1 text-xs text-slate-400">処理: {step.actedBy.name}</p>
                  ) : null}
                </div>
              ))}
            </div>
          </section>

          <section className="card p-5">
            <h2 className="font-bold">履歴</h2>
            <div className="mt-4 space-y-3">
              {item.actions.map((action) => (
                <div key={action.id} className="border-l-2 border-line pl-4">
                  <p className="text-sm font-bold">{action.action}</p>
                  <p className="text-xs text-slate-400">
                    {action.actor?.name ?? "System"} · {action.createdAt.toLocaleString("ja-JP")}
                  </p>
                  {action.comment ? <p className="mt-1 text-sm">{action.comment}</p> : null}
                </div>
              ))}
            </div>
          </section>
        </main>

        <aside className="space-y-6">
          <section className="card p-5 text-sm">
            <h2 className="font-bold">概要</h2>
            <dl className="mt-4 space-y-3">
              <Row label="状態" value={item.status} />
              <Row label="優先度" value={item.priority} />
              <Row label="申請者" value={item.requestedBy?.name ?? "AI / System"} />
              <Row label="対象" value={item.targetType} />
              <Row label="金額" value={item.amount != null ? `¥${Number(item.amount).toLocaleString()}` : "-"} />
              <Row label="差額" value={item.amountDelta != null ? `¥${Number(item.amountDelta).toLocaleString()}` : "-"} />
              <Row label="申請日時" value={item.createdAt.toLocaleString("ja-JP")} />
            </dl>
          </section>

          <ApprovalActions
            approvalId={item.id}
            stepId={currentStep?.id ?? null}
            canAct={Boolean(currentStep && canAct && canApprove)}
          />
        </aside>
      </div>
    </div>
  );
}

function Snapshot({ title, value }: { title: string; value: unknown }) {
  return (
    <div>
      <p className="mb-2 text-xs font-bold text-slate-500">{title}</p>
      <pre className="max-h-96 overflow-auto rounded-lg bg-slate-950 p-4 text-xs text-slate-100">
        {JSON.stringify(value ?? {}, null, 2)}
      </pre>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs font-bold text-slate-400">{label}</dt>
      <dd className="mt-1 font-semibold text-slate-700">{value}</dd>
    </div>
  );
}

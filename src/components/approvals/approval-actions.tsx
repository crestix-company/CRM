"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export function ApprovalActions({
  approvalId,
  stepId,
  canAct,
}: {
  approvalId: string;
  stepId: string | null;
  canAct: boolean;
}) {
  const router = useRouter();
  const [comment, setComment] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");

  if (!canAct || !stepId) return null;

  async function submit(action: "approve" | "return" | "reject") {
    setPending(true);
    setError("");
    const response = await fetch(
      `/api/approvals/${approvalId}/steps/${stepId}/${action}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ comment }),
      },
    );
    const body = await response.json().catch(() => ({}));
    setPending(false);
    if (!response.ok) {
      setError(body.message ?? "処理に失敗しました。");
      return;
    }
    setComment("");
    router.refresh();
  }

  return (
    <section className="card p-5">
      <h2 className="font-bold">承認操作</h2>
      <textarea
        className="mt-3 min-h-24 w-full rounded-lg border border-line px-3 py-2 text-sm"
        placeholder="コメント / 差戻し・却下理由"
        value={comment}
        onChange={(event) => setComment(event.target.value)}
      />
      {error ? <p className="mt-2 text-sm text-red-600">{error}</p> : null}
      <div className="mt-3 flex flex-wrap gap-2">
        <button
          type="button"
          className="primary-button"
          disabled={pending}
          onClick={() => submit("approve")}
        >
          {pending ? "処理中..." : "承認 / 確認完了"}
        </button>
        <button
          type="button"
          className="secondary-button"
          disabled={pending}
          onClick={() => submit("return")}
        >
          差戻し
        </button>
        <button
          type="button"
          className="secondary-button"
          disabled={pending}
          onClick={() => submit("reject")}
        >
          却下
        </button>
      </div>
    </section>
  );
}

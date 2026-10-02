import { describe, expect, it } from "vitest";
import { ApprovalPriority } from "@prisma/client";
import {
  approvalEscalationAt,
  approvalReminderAt,
} from "./sla";

describe("approval SLA", () => {
  it("uses 1 minute / 5 minutes for urgent", () => {
    const createdAt = new Date("2026-10-02T09:00:00.000Z");
    expect(
      approvalReminderAt(ApprovalPriority.URGENT, createdAt).toISOString(),
    ).toBe("2026-10-02T09:01:00.000Z");
    expect(
      approvalEscalationAt(ApprovalPriority.URGENT, createdAt).toISOString(),
    ).toBe("2026-10-02T09:05:00.000Z");
  });

  it("uses 4 hours and 19:00 JST for important", () => {
    const createdAt = new Date("2026-10-02T08:00:00.000Z"); // 17:00 JST
    expect(
      approvalReminderAt(ApprovalPriority.IMPORTANT, createdAt).toISOString(),
    ).toBe("2026-10-02T12:00:00.000Z");
    expect(
      approvalEscalationAt(ApprovalPriority.IMPORTANT, createdAt).toISOString(),
    ).toBe("2026-10-02T10:00:00.000Z"); // 19:00 JST
  });

  it("moves important cutoff to the next calendar day when created after 19:00 JST", () => {
    const createdAt = new Date("2026-10-02T11:30:00.000Z"); // 20:30 JST
    expect(
      approvalEscalationAt(ApprovalPriority.IMPORTANT, createdAt).toISOString(),
    ).toBe("2026-10-03T10:00:00.000Z");
  });

  it("uses 24 hours / 48 hours for normal", () => {
    const createdAt = new Date("2026-10-02T00:00:00.000Z");
    expect(
      approvalReminderAt(ApprovalPriority.NORMAL, createdAt).toISOString(),
    ).toBe("2026-10-03T00:00:00.000Z");
    expect(
      approvalEscalationAt(ApprovalPriority.NORMAL, createdAt).toISOString(),
    ).toBe("2026-10-04T00:00:00.000Z");
  });
});

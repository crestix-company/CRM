import { ApprovalPriority } from "@prisma/client";

const JST_OFFSET_MS = 9 * 60 * 60 * 1000;

function toJstParts(date: Date) {
  const shifted = new Date(date.getTime() + JST_OFFSET_MS);
  return {
    year: shifted.getUTCFullYear(),
    month: shifted.getUTCMonth(),
    day: shifted.getUTCDate(),
    hour: shifted.getUTCHours(),
    minute: shifted.getUTCMinutes(),
  };
}

function jstDateAt(
  year: number,
  month: number,
  day: number,
  hour: number,
  minute = 0,
) {
  return new Date(
    Date.UTC(year, month, day, hour, minute, 0, 0) - JST_OFFSET_MS,
  );
}

export function approvalReminderAt(
  priority: ApprovalPriority,
  createdAt: Date,
) {
  const ms =
    priority === ApprovalPriority.URGENT
      ? 60_000
      : priority === ApprovalPriority.IMPORTANT
        ? 4 * 60 * 60 * 1000
        : 24 * 60 * 60 * 1000;
  return new Date(createdAt.getTime() + ms);
}

export function approvalEscalationAt(
  priority: ApprovalPriority,
  createdAt: Date,
) {
  if (priority === ApprovalPriority.URGENT) {
    return new Date(createdAt.getTime() + 5 * 60_000);
  }
  if (priority === ApprovalPriority.NORMAL) {
    return new Date(createdAt.getTime() + 48 * 60 * 60 * 1000);
  }

  const jst = toJstParts(createdAt);
  const afterCutoff = jst.hour >= 19;
  const day = jst.day + (afterCutoff ? 1 : 0);
  return jstDateAt(jst.year, jst.month, day, 19, 0);
}

export function approvalSlaWindow(
  priority: ApprovalPriority,
  createdAt: Date,
) {
  return {
    reminderAt: approvalReminderAt(priority, createdAt),
    escalationAt: approvalEscalationAt(priority, createdAt),
  };
}

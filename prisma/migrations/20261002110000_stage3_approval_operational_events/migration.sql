-- Stage3 Approval operational events
ALTER TYPE "operational_event_type" ADD VALUE IF NOT EXISTS 'approval_requested';
ALTER TYPE "operational_event_type" ADD VALUE IF NOT EXISTS 'approval_reviewed';
ALTER TYPE "operational_event_type" ADD VALUE IF NOT EXISTS 'approval_approved';
ALTER TYPE "operational_event_type" ADD VALUE IF NOT EXISTS 'approval_rejected';
ALTER TYPE "operational_event_type" ADD VALUE IF NOT EXISTS 'approval_returned';
ALTER TYPE "operational_event_type" ADD VALUE IF NOT EXISTS 'approval_escalated';
ALTER TYPE "operational_event_type" ADD VALUE IF NOT EXISTS 'approval_executed';
ALTER TYPE "operational_event_type" ADD VALUE IF NOT EXISTS 'approval_execution_failed';

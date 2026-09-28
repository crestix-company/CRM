"""Read-only cutover-gate counts for research_jobs / research_job_items.

Per docs/clinic-db-review-resolution.md section 5: legacy job rows are never
migrated, but the cutover gate needs to know whether any are still in flight.
This module only counts; it never stops or deletes anything.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass
class JobCutoverStatus:
    running_jobs: int
    paused_jobs: int
    completed_jobs: int
    reset_jobs: int
    other_job_statuses: dict
    pending_items: int
    running_items: int
    done_items: int
    cancelled_items: int
    other_item_states: dict

    @property
    def gate_clear(self) -> bool:
        return self.pending_items == 0 and self.running_items == 0 and self.running_jobs == 0


def read_job_cutover_status(conn: sqlite3.Connection) -> JobCutoverStatus:
    job_counts = dict(conn.execute("SELECT status, COUNT(*) FROM research_jobs GROUP BY status;").fetchall())
    item_counts = dict(conn.execute("SELECT state, COUNT(*) FROM research_job_items GROUP BY state;").fetchall())

    known_job = {"RUNNING", "PAUSED", "COMPLETED", "RESET", "BUDGET"}
    known_item = {"PENDING", "RUNNING", "DONE", "CANCELLED"}

    return JobCutoverStatus(
        running_jobs=job_counts.get("RUNNING", 0),
        paused_jobs=job_counts.get("PAUSED", 0),
        completed_jobs=job_counts.get("COMPLETED", 0),
        reset_jobs=job_counts.get("RESET", 0),
        other_job_statuses={k: v for k, v in job_counts.items() if k not in known_job},
        pending_items=item_counts.get("PENDING", 0),
        running_items=item_counts.get("RUNNING", 0),
        done_items=item_counts.get("DONE", 0),
        cancelled_items=item_counts.get("CANCELLED", 0),
        other_item_states={k: v for k, v in item_counts.items() if k not in known_item},
    )

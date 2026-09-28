"""Aggregation, determinism fingerprinting, and output routing.

Safety rule enforced here, not just by convention: `write_detail_rows` refuses
to write anywhere under the git-tracked repo tree. Detail rows can contain
clinic names/phones/addresses (PII-adjacent business data) and must never be
committed. Summary counts contain no such data and are safe for docs/.
"""
from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from dataclasses import dataclass, field


@dataclass
class Tally:
    total: int = 0
    decision_counts: Counter = field(default_factory=Counter)
    reason_counts: Counter = field(default_factory=Counter)

    def add(self, decision: str, reasons: list[str]) -> None:
        self.total += 1
        self.decision_counts[decision] += 1
        for r in reasons:
            self.reason_counts[r] += 1

    def as_dict(self) -> dict:
        return {
            "total": self.total,
            "decisions": dict(sorted(self.decision_counts.items())),
            "reasons": dict(sorted(self.reason_counts.items())),
        }

    def fingerprint(self) -> str:
        payload = json.dumps(self.as_dict(), sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def write_detail_rows(path: str, rows: list[dict]) -> None:
    """Writes PII-bearing detail rows. Refuses any path inside the git repo tree."""
    abs_path = os.path.abspath(path)
    if abs_path.startswith(REPO_ROOT + os.sep):
        raise ValueError(
            f"Refusing to write detail rows inside the git repo ({REPO_ROOT}): {abs_path}. "
            "Use a path under /tmp or another gitignored location."
        )
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")

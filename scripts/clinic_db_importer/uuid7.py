"""UUIDv7 generation for this rehearsal only -- NOT the Production implementation.

This is the dependency-free reference implementation documented in
docs/clinic-uuid-strategy.md section 4.3, used here unmodified so the rehearsal
exercises the exact algorithm already reviewed. Production's actual decision
(docs/clinic-db-consumer-contract.md section 1) is a `uuid6` dependency added
to Clinic Lead's own requirements.txt -- this repo does not add that
dependency, and this module must never be treated as the Production
generator. IDs produced here are Scratch-only and are never written to
Production Supabase.
"""
from __future__ import annotations

import os
import time
import uuid


def uuid7() -> uuid.UUID:
    unix_ts_ms = time.time_ns() // 1_000_000
    rand = os.urandom(10)

    b = bytearray(16)
    b[0:6] = unix_ts_ms.to_bytes(6, "big")
    b[6] = 0x70 | (rand[0] & 0x0F)
    b[7] = rand[1]
    b[8] = 0x80 | (rand[2] & 0x3F)
    b[9:16] = rand[3:10]

    return uuid.UUID(bytes=bytes(b))

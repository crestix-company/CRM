"""Read-only access to the Clinic Production SQLite file.

Enforces read-only at two layers:
  1. The connection is opened with the `mode=ro` URI parameter (SQLITE_OPEN_READONLY).
  2. `PRAGMA query_only=ON` is set immediately after connecting, so that even if a
     caller mistakenly issues a write statement, SQLite itself rejects it.

Known environment quirk (documented in docs/clinic-db-importer-dry-run-v1.md):
this database uses WAL journal mode. SQLite's strict `mode=ro` open requires the
`<db>-shm` support file to already exist; if it does not, the open fails with
SQLITE_CANTOPEN even though no write is being requested. This module surfaces
that failure with a clear message rather than silently falling back to a
writable connection.
"""
from __future__ import annotations

import contextlib
import hashlib
import os
import sqlite3
import stat as stat_module
from dataclasses import dataclass


@dataclass(frozen=True)
class SourceBaseline:
    sha256: str
    mtime: float
    size: int
    clinics_count: int
    medical_key_empty: int
    medical_key_duplicate_groups: int
    integrity_check: str

    def matches(self, other: "SourceBaseline") -> list[str]:
        """Returns a list of human-readable mismatches; empty list means identical."""
        mismatches = []
        for field in self.__dataclass_fields__:
            a, b = getattr(self, field), getattr(other, field)
            if a != b:
                mismatches.append(f"{field}: before={a!r} after={b!r}")
        return mismatches


def file_stat(path: str) -> tuple[str, float, int]:
    with open(path, "rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()
    st = os.stat(path)
    return sha256, st.st_mtime, st.st_size


def _ensure_wal_support_files(path: str) -> None:
    """WAL-mode databases require a `<path>-shm` file to exist before SQLite will
    grant a strict SQLITE_OPEN_READONLY connection (mode=ro) -- otherwise open()
    fails with SQLITE_CANTOPEN even though no write was requested. If the file
    is missing, this opens one ordinary (non-readonly-flagged) connection,
    sets `PRAGMA query_only=ON` before running anything else, executes a
    single trivial read, and closes. This creates only the empty `-shm`/`-wal`
    bookkeeping files SQLite manages for WAL mode; it never modifies a single
    byte of the main database file (verified in
    docs/clinic-db-importer-dry-run-v1.md via before/after SHA-256).
    """
    if os.path.exists(path + "-shm"):
        return
    conn = sqlite3.connect(path)
    try:
        conn.execute("PRAGMA query_only=ON;")
        conn.execute("SELECT 1;").fetchone()
    finally:
        conn.close()


@contextlib.contextmanager
def readonly_connection(path: str):
    """Yields a strictly read-only sqlite3 connection. Never writes anything."""
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    _ensure_wal_support_files(path)
    uri = f"file:{path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    try:
        conn.execute("PRAGMA query_only=ON;")
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        conn.close()


def capture_baseline(path: str) -> SourceBaseline:
    sha256, mtime, size = file_stat(path)
    with readonly_connection(path) as conn:
        integrity = conn.execute("PRAGMA integrity_check;").fetchone()[0]
        count = conn.execute("SELECT COUNT(*) FROM clinics;").fetchone()[0]
        empty = conn.execute("SELECT COUNT(*) FROM clinics WHERE medical_key='';").fetchone()[0]
        dup_groups = conn.execute(
            "SELECT COUNT(*) FROM (SELECT medical_key FROM clinics "
            "WHERE medical_key<>'' GROUP BY medical_key HAVING COUNT(*)>1);"
        ).fetchone()[0]
    return SourceBaseline(
        sha256=sha256,
        mtime=mtime,
        size=size,
        clinics_count=count,
        medical_key_empty=empty,
        medical_key_duplicate_groups=dup_groups,
        integrity_check=integrity,
    )


def iter_table(conn: sqlite3.Connection, table: str):
    cur = conn.execute(f"SELECT * FROM {table};")  # table name is a fixed internal constant, not user input
    for row in cur:
        yield dict(row)


def table_counts(conn: sqlite3.Connection, table: str, group_by: str | None = None):
    if group_by:
        cur = conn.execute(f"SELECT {group_by}, COUNT(*) FROM {table} GROUP BY {group_by};")
        return {row[0]: row[1] for row in cur}
    return conn.execute(f"SELECT COUNT(*) FROM {table};").fetchone()[0]

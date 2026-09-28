"""Pure transform helpers: date / boolean / numeric / JSON / UUID parsing.

Every function returns (value_or_none, ok: bool) rather than raising, so
classify.py can aggregate parse failures without try/except sprawl. `ok=False`
never means "silently coerced" -- it means "could not confidently transform,
do not auto-INSERT this value."
"""
from __future__ import annotations

import json
import re
import uuid as uuid_mod
from datetime import date, datetime

_UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def strip_nul(value: str) -> str:
    """PostgreSQL text/jsonb cannot store the NUL byte (U+0000) under any
    circumstances -- not even as a valid JSON \\u0000 escape, which Python's
    json.loads accepts but Postgres's jsonb input function rejects outright
    ("unsupported Unicode escape sequence"). Found via the full-scale
    migration rehearsal (docs/clinic-db-migration-rehearsal-v1.md): a scraped
    URL contained a literal NUL. Stripping (not replacing with a placeholder)
    matches the general spirit of the other transforms here -- never invent
    a value, and a mid-string NUL carries no meaningful information anyway.
    """
    return value.replace("\x00", "")


def to_optional_text(value) -> str | None:
    """SQLite empty-string-as-default -> NULL. Never invents a value."""
    if value is None:
        return None
    text = strip_nul(str(value)).strip()
    return text if text else None


def sanitize_json_value(value):
    """Recursively strips NUL bytes from every string inside a parsed JSON
    value, so it can be safely re-serialized into a PostgreSQL jsonb column.
    """
    if isinstance(value, str):
        return strip_nul(value)
    if isinstance(value, dict):
        return {k: sanitize_json_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize_json_value(v) for v in value]
    return value


def parse_bool(value) -> tuple[bool | None, bool]:
    """SQLite 0/1 INTEGER -> boolean. Returns (value, ok)."""
    if value is None:
        return None, True
    if value in (0, 1):
        return bool(value), True
    return None, False


def parse_numeric(value) -> tuple[float | None, bool]:
    if value is None or value == "":
        return None, True
    try:
        return float(value), True
    except (TypeError, ValueError):
        return None, False


def parse_date(value) -> tuple[date | None, bool]:
    text = to_optional_text(value)
    if text is None:
        return None, True
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt).date(), True
        except ValueError:
            continue
    return None, False


def parse_timestamp(value) -> tuple[datetime | None, bool]:
    text = to_optional_text(value)
    if text is None:
        return None, True
    candidates = [text, text.replace(" ", "T")]
    for cand in candidates:
        try:
            return datetime.fromisoformat(cand), True
        except ValueError:
            continue
    return None, False


def parse_json(value) -> tuple[object | None, bool]:
    text = to_optional_text(value)
    if text is None:
        return None, True
    try:
        return json.loads(text), True
    except (TypeError, ValueError):
        return None, False


def parse_uuid(value) -> tuple[str | None, bool]:
    """SQLite empty string -> NULL (ok). Non-empty must be a canonical UUID."""
    text = to_optional_text(value)
    if text is None:
        return None, True
    if not _UUID_RE.match(text):
        return None, False
    try:
        return str(uuid_mod.UUID(text)), True
    except ValueError:
        return None, False

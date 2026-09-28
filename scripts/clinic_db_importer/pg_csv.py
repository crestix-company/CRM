"""Minimal, explicit CSV serialization for PostgreSQL `COPY ... FROM STDIN WITH
(FORMAT csv)`. Written by hand rather than via csv.writer because COPY's csv
format has one subtlety that matters here: an unquoted empty field means NULL,
while a quoted empty field ("") means an empty string. csv.writer's default
quoting does not draw that line where we need it, so every non-NULL value is
quoted explicitly here and NULL is always the fully empty (unquoted) field.
"""
from __future__ import annotations

import json

from . import transform


def field(value) -> str:
    """Renders one CSV field for COPY FORMAT csv. None -> unquoted empty (NULL)."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = transform.strip_nul(str(value))
    return '"' + text.replace('"', '""') + '"'


def json_field(value) -> str:
    """Serializes a parsed JSON value for a jsonb column. Sanitizes NUL bytes
    first -- see transform.sanitize_json_value for why this is required
    (Postgres rejects \\u0000 in jsonb input even though it's valid JSON)."""
    if value is None:
        return ""
    return field(json.dumps(transform.sanitize_json_value(value), ensure_ascii=False))


def text_array_field(values) -> str:
    """Postgres text[] literal, e.g. {a,"b,c",NULL}. None -> unquoted empty (NULL column)."""
    if values is None:
        return ""
    parts = []
    for v in values:
        if v is None:
            parts.append("NULL")
        else:
            escaped = transform.strip_nul(str(v)).replace("\\", "\\\\").replace('"', '\\"')
            parts.append(f'"{escaped}"')
    literal = "{" + ",".join(parts) + "}"
    return field(literal)


def row(values: list[str]) -> str:
    return ",".join(values)


def write_copy_block(f, schema: str, table: str, columns: list[str], rows: list[list[str]]) -> None:
    """Writes one embedded COPY block (plain SQL COPY, not \\copy, so it can be
    embedded directly in a larger script fed via stdin -- the same technique
    pg_dump output uses)."""
    col_list = ", ".join(columns)
    f.write(f"COPY {schema}.{table} ({col_list}) FROM STDIN WITH (FORMAT csv);\n")
    for r in rows:
        f.write(row(r) + "\n")
    f.write("\\.\n")

"""Read-only bridge to Clinic Lead's existing normalizer functions.

Per docs/clinic-db-runtime-vocab-v1.md, name_norm/name_prefix/phone_norm/
tel_match_key/address_norm are pure functions of a single already-migrated
column. Rather than re-implementing that logic (which would drift from the
real app over time), this module imports the actual functions from the
Clinic Lead repository at read time.

This module NEVER writes to the Clinic Lead repository. It only adds the
repo's root to sys.path so `import src.normalizer.*` resolves, exactly as if
this script were running inside that repo. No files there are opened for
writing, and this script performs no `git` operations on that repo.
"""
from __future__ import annotations

import os
import sys

CLINIC_LEAD_REPO = os.environ.get(
    "CLINIC_LEAD_REPO_PATH",
    os.path.expanduser("~/Desktop/clinic-list-filter-complete"),
)


class NormalizerUnavailable(RuntimeError):
    pass


def load_normalizers():
    """Imports and returns the Clinic Lead normalizer functions.

    Raises NormalizerUnavailable with a clear message if the repo path is
    missing or the expected modules cannot be imported, so callers can decide
    how to degrade (e.g. skip normalizer validation) rather than silently
    reimplementing the algorithm.
    """
    if not os.path.isdir(CLINIC_LEAD_REPO):
        raise NormalizerUnavailable(f"Clinic Lead repo not found at {CLINIC_LEAD_REPO}")

    inserted = False
    if CLINIC_LEAD_REPO not in sys.path:
        sys.path.insert(0, CLINIC_LEAD_REPO)
        inserted = True
    try:
        from src.normalizer.clinic_name import normalize_clinic_name  # noqa: E402
        from src.normalizer.phone import normalize_phone, tel_match_key  # noqa: E402
        from src.normalizer.address import normalize_address  # noqa: E402
    except Exception as exc:  # pragma: no cover - depends on external repo state
        raise NormalizerUnavailable(f"Failed to import Clinic Lead normalizers: {exc}") from exc
    finally:
        # Leave sys.path exactly as we found it once the functions are bound.
        if inserted:
            sys.path.remove(CLINIC_LEAD_REPO)

    def name_norm(clinic_name):
        return normalize_clinic_name(clinic_name)

    def name_prefix(clinic_name):
        return normalize_clinic_name(clinic_name)[:2]

    def phone_norm(phone):
        return normalize_phone(phone)

    def tel_match_key_(phone):
        return tel_match_key(phone)

    def address_norm(address):
        return normalize_address(address)

    return {
        "name_norm": name_norm,
        "name_prefix": name_prefix,
        "phone_norm": phone_norm,
        "tel_match_key": tel_match_key_,
        "address_norm": address_norm,
    }

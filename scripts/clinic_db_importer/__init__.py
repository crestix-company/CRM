"""Read-only dry-run importer for the Clinic SQLite -> Schema v1 (Postgres) migration.

This package performs NO writes anywhere: not to Production SQLite, not to any
PostgreSQL (scratch or Supabase). It only classifies rows and reports counts.
See docs/clinic-db-importer-dry-run-v1.md for the full design and results.
"""

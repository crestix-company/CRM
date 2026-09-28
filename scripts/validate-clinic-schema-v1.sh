#!/usr/bin/env bash
# Validates docs/clinic-db-sql-drafts/{001,002,005,004,006}*.sql against a throwaway,
# localhost-only PostgreSQL 17 container. NEVER connects to Production Supabase or any
# non-local host. This script creates and destroys its own scratch container; it does not
# accept a DATABASE_URL or any external connection target.
#
# Usage: scripts/validate-clinic-schema-v1.sh
#
# Safety: hard-coded to 127.0.0.1. If DB_HOST is ever overridden to anything else, the
# script refuses to run (fail closed).
set -euo pipefail

DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-55432}"
DB_NAME="clinic_schema_scratch"
DB_USER="postgres"
DB_PASSWORD="scratch_pw_local_only"
CONTAINER_NAME="clinic-schema-scratch-validate"
SQL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../docs/clinic-db-sql-drafts" && pwd)"

PASS=0
FAIL=0
FAILURES=()

# --- Safety guard: fail closed unless target is localhost -------------------------------
if [[ "$DB_HOST" != "127.0.0.1" && "$DB_HOST" != "localhost" ]]; then
  echo "REFUSING TO RUN: DB_HOST=$DB_HOST is not localhost/127.0.0.1." >&2
  echo "This script must never target a non-local host (Supabase or otherwise)." >&2
  exit 1
fi

psql_exec() {
  # Runs SQL from stdin inside the scratch container. Returns psql's exit code.
  docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 "$@"
}

psql_query() {
  docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -tA "$@"
}

cleanup() {
  docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "== Starting scratch PostgreSQL 17 container ($CONTAINER_NAME, $DB_HOST:$DB_PORT, localhost-only) =="
docker run -d --name "$CONTAINER_NAME" \
  -e POSTGRES_PASSWORD="$DB_PASSWORD" \
  -e POSTGRES_DB="$DB_NAME" \
  -p "${DB_HOST}:${DB_PORT}:5432" \
  postgres:17 >/dev/null

for i in $(seq 1 30); do
  if docker exec "$CONTAINER_NAME" pg_isready -U "$DB_USER" >/dev/null 2>&1; then
    echo "Ready after ${i}s"
    break
  fi
  sleep 1
done

expect_pass() {
  local desc="$1"; local sql="$2"
  if echo "BEGIN; $sql ROLLBACK;" | psql_exec >/dev/null 2>/tmp/validate_err.log; then
    echo "PASS (expected pass): $desc"
    PASS=$((PASS+1))
  else
    echo "FAIL (expected pass, got error): $desc"
    cat /tmp/validate_err.log
    FAIL=$((FAIL+1)); FAILURES+=("$desc")
  fi
}

expect_fail() {
  local desc="$1"; local sql="$2"
  if echo "BEGIN; $sql ROLLBACK;" | psql_exec >/dev/null 2>/tmp/validate_err.log; then
    echo "FAIL (expected constraint violation, but succeeded): $desc"
    FAIL=$((FAIL+1)); FAILURES+=("$desc")
  else
    echo "PASS (expected fail, got error as expected): $desc"
    PASS=$((PASS+1))
  fi
}

echo ""
echo "== DDL apply (order per docs/clinic-db-sql-drafts/README.md) =="
for f in 001_create_clinic_master.sql 002_create_clinic_ops.sql 005_create_clinic_ops_extended.sql \
         004_current_hp_rank_view.sql 006_create_current_views.sql; do
  echo "-- applying $f"
  if cat "$SQL_DIR/$f" | psql_exec >/tmp/validate_ddl.log 2>&1; then
    echo "   OK"
  else
    echo "   ERROR"
    cat /tmp/validate_ddl.log
    FAIL=$((FAIL+1)); FAILURES+=("DDL apply: $f")
  fi
done

echo ""
echo "== Schema assertions =="
TABLES=$(psql_query -c "SELECT table_schema||'.'||table_name FROM information_schema.tables WHERE table_schema IN ('clinic_master','clinic_ops') AND table_type='BASE TABLE' ORDER BY 1;")
echo "$TABLES"
VIEWS=$(psql_query -c "SELECT table_schema||'.'||table_name FROM information_schema.views WHERE table_schema='clinic_ops' ORDER BY 1;")
echo "$VIEWS"

echo ""
echo "== Fixture: base clinic + machine/manual HP rank history =="
psql_exec <<'SQL'
INSERT INTO clinic_master.clinics (clinic_id, medical_key, clinic_name)
VALUES ('00000000-0000-7000-8000-000000000001', 'MK-FIXTURE-0001', 'Fixture Clinic A');
SQL

echo ""
echo "== 1. medical_key constraint tests =="
expect_pass  "non-empty unique medical_key" "INSERT INTO clinic_master.clinics (clinic_id, medical_key, clinic_name) VALUES ('00000000-0000-7000-8000-000000000002','MK-OK-0002','C');"
expect_fail  "empty medical_key" "INSERT INTO clinic_master.clinics (clinic_id, medical_key, clinic_name) VALUES ('00000000-0000-7000-8000-000000000003','','C');"
expect_fail  "whitespace-only medical_key" "INSERT INTO clinic_master.clinics (clinic_id, medical_key, clinic_name) VALUES ('00000000-0000-7000-8000-000000000004','   ','C');"
expect_fail  "duplicate medical_key" "INSERT INTO clinic_master.clinics (clinic_id, medical_key, clinic_name) VALUES ('00000000-0000-7000-8000-000000000005','MK-FIXTURE-0001','C');"

echo ""
echo "== 2. legacy_uuid constraint tests =="
expect_pass  "multiple NULL legacy_uuid" "INSERT INTO clinic_master.clinics (clinic_id, medical_key, clinic_name, legacy_uuid) VALUES ('00000000-0000-7000-8000-000000000006','MK-LU-0006','C',NULL); INSERT INTO clinic_master.clinics (clinic_id, medical_key, clinic_name, legacy_uuid) VALUES ('00000000-0000-7000-8000-000000000007','MK-LU-0007','C',NULL);"
expect_pass  "first non-null legacy_uuid" "INSERT INTO clinic_master.clinics (clinic_id, medical_key, clinic_name, legacy_uuid) VALUES ('00000000-0000-7000-8000-000000000008','MK-LU-0008','C','11111111-1111-1111-1111-111111111111');"
expect_fail  "duplicate non-null legacy_uuid" "INSERT INTO clinic_master.clinics (clinic_id, medical_key, clinic_name, legacy_uuid) VALUES ('00000000-0000-7000-8000-000000000008','MK-LU-0008','C','11111111-1111-1111-1111-111111111111'); INSERT INTO clinic_master.clinics (clinic_id, medical_key, clinic_name, legacy_uuid) VALUES ('00000000-0000-7000-8000-000000000009','MK-LU-0009','C','11111111-1111-1111-1111-111111111111');"

echo ""
echo "== 3. HP rank (hp_research.machine_rank) constraint tests =="
expect_pass "machine_rank A" "INSERT INTO clinic_ops.hp_research (clinic_id, fetch_status, machine_rank) VALUES ('00000000-0000-7000-8000-000000000001','SUCCESS','A');"
expect_pass "machine_rank D" "INSERT INTO clinic_ops.hp_research (clinic_id, fetch_status, machine_rank) VALUES ('00000000-0000-7000-8000-000000000001','SUCCESS','D');"
expect_fail "machine_rank UNKNOWN" "INSERT INTO clinic_ops.hp_research (clinic_id, fetch_status, machine_rank) VALUES ('00000000-0000-7000-8000-000000000001','SUCCESS','UNKNOWN');"
expect_fail "machine_rank NO_HP" "INSERT INTO clinic_ops.hp_research (clinic_id, fetch_status, machine_rank) VALUES ('00000000-0000-7000-8000-000000000001','NOT_FOUND','NO_HP');"

echo ""
echo "== 4. hp_research.fetch_status constraint tests =="
for v in SUCCESS REVIEW ERROR NOT_FOUND; do
  expect_pass "fetch_status $v" "INSERT INTO clinic_ops.hp_research (clinic_id, fetch_status) VALUES ('00000000-0000-7000-8000-000000000001','$v');"
done
for v in VERIFIED UNRESEARCHED; do
  expect_fail "fetch_status $v (invalid)" "INSERT INTO clinic_ops.hp_research (clinic_id, fetch_status) VALUES ('00000000-0000-7000-8000-000000000001','$v');"
done

echo ""
echo "== 5. manual_override_events constraint tests =="
expect_pass "SET with non-null value" "INSERT INTO clinic_ops.manual_override_events (clinic_id, field, operation, value, reviewer, source, reviewed_at) VALUES ('00000000-0000-7000-8000-000000000001','hp_url','SET','\"https://example.com\"','tester','manual',now());"
expect_pass "CLEAR with null value" "INSERT INTO clinic_ops.manual_override_events (clinic_id, field, operation, value, reviewer, source, reviewed_at) VALUES ('00000000-0000-7000-8000-000000000001','hp_url','CLEAR',NULL,'tester','manual',now());"
expect_fail "SET with null value" "INSERT INTO clinic_ops.manual_override_events (clinic_id, field, operation, value, reviewer, source, reviewed_at) VALUES ('00000000-0000-7000-8000-000000000001','hp_url','SET',NULL,'tester','manual',now());"
expect_fail "CLEAR with non-null value" "INSERT INTO clinic_ops.manual_override_events (clinic_id, field, operation, value, reviewer, source, reviewed_at) VALUES ('00000000-0000-7000-8000-000000000001','hp_url','CLEAR','\"x\"','tester','manual',now());"
expect_fail "unsupported field" "INSERT INTO clinic_ops.manual_override_events (clinic_id, field, operation, value, reviewer, source, reviewed_at) VALUES ('00000000-0000-7000-8000-000000000001','not_a_real_field','SET','\"x\"','tester','manual',now());"

echo ""
echo "== 6. Jobs constraint tests =="
for v in PAUSED RUNNING COMPLETED RESET BUDGET; do
  expect_pass "research_jobs.status $v" "INSERT INTO clinic_ops.research_jobs (kind, options, status, max_searches) VALUES ('hp','{}','$v',100);"
done
expect_fail "research_jobs.status invented value" "INSERT INTO clinic_ops.research_jobs (kind, options, status, max_searches) VALUES ('hp','{}','PENDING',100);"

psql_exec <<'SQL' >/tmp/validate_job.log 2>&1 || true
INSERT INTO clinic_ops.research_jobs (id, kind, options, status, max_searches)
VALUES ('00000000-0000-4000-9000-0000000000aa','hp','{}','PAUSED',100);
SQL
for v in PENDING RUNNING DONE; do
  expect_pass "research_job_items.state $v" "INSERT INTO clinic_ops.research_job_items (job_id, clinic_id, state) VALUES ('00000000-0000-4000-9000-0000000000aa','00000000-0000-7000-8000-000000000001','$v');"
done
for v in ERROR SKIPPED; do
  expect_fail "research_job_items.state $v (invalid)" "INSERT INTO clinic_ops.research_job_items (job_id, clinic_id, state) VALUES ('00000000-0000-4000-9000-0000000000aa','00000000-0000-7000-8000-000000000001','$v');"
done

echo ""
echo "== Comdesk constraint tests =="
psql_exec <<'SQL' >/tmp/validate_comdesk_setup.log 2>&1 || true
INSERT INTO clinic_ops.comdesk_templates (template_id, headers, field_mapping, created_at)
VALUES ('tmpl-1', (SELECT jsonb_agg(x) FROM generate_series(1,28) x), '{}'::jsonb, now());
SQL
cat /tmp/validate_comdesk_setup.log
HEADERS_27=$(python3 -c "import json; print(json.dumps(list(range(27))))")
HEADERS_29=$(python3 -c "import json; print(json.dumps(list(range(29))))")
HEADERS_28=$(python3 -c "import json; print(json.dumps(list(range(28))))")
expect_fail "comdesk_templates.headers 27 elements" "INSERT INTO clinic_ops.comdesk_templates (template_id, headers, field_mapping, created_at) VALUES ('tmpl-27','$HEADERS_27'::jsonb,'{}'::jsonb,now());"
expect_fail "comdesk_templates.headers 29 elements" "INSERT INTO clinic_ops.comdesk_templates (template_id, headers, field_mapping, created_at) VALUES ('tmpl-29','$HEADERS_29'::jsonb,'{}'::jsonb,now());"
expect_pass "comdesk_templates.headers 28 elements" "INSERT INTO clinic_ops.comdesk_templates (template_id, headers, field_mapping, created_at) VALUES ('tmpl-28','$HEADERS_28'::jsonb,'{}'::jsonb,now());"
expect_fail "comdesk_original_rows.original_values 27 elements" "INSERT INTO clinic_ops.comdesk_original_rows (clinic_id, template_id, original_values, source_hash, source_row_number, created_at) VALUES ('00000000-0000-7000-8000-000000000001','tmpl-1','$HEADERS_27'::jsonb,'hash-a',1,now());"
expect_fail "comdesk_original_rows.original_values 29 elements" "INSERT INTO clinic_ops.comdesk_original_rows (clinic_id, template_id, original_values, source_hash, source_row_number, created_at) VALUES ('00000000-0000-7000-8000-000000000001','tmpl-1','$HEADERS_29'::jsonb,'hash-b',2,now());"
expect_pass "comdesk_original_rows.original_values 28 elements" "INSERT INTO clinic_ops.comdesk_original_rows (clinic_id, template_id, original_values, source_hash, source_row_number, created_at) VALUES ('00000000-0000-7000-8000-000000000001','tmpl-1','$HEADERS_28'::jsonb,'hash-c',3,now());"
psql_exec <<SQL >/tmp/validate_comdesk_dup_setup.log 2>&1 || true
INSERT INTO clinic_ops.comdesk_original_rows (clinic_id, template_id, original_values, source_hash, source_row_number, created_at)
VALUES ('00000000-0000-7000-8000-000000000001','tmpl-1','$HEADERS_28'::jsonb,'hash-dup',10,now());
SQL
expect_fail "comdesk_original_rows duplicate (source_hash, source_row_number)" "INSERT INTO clinic_ops.comdesk_original_rows (clinic_id, template_id, original_values, source_hash, source_row_number, created_at) VALUES ('00000000-0000-7000-8000-000000000001','tmpl-1','$HEADERS_28'::jsonb,'hash-dup',10,now());"

echo ""
echo "== Behavior: current_hp_rank manual-wins-machine =="
psql_exec <<'SQL' >/tmp/validate_behavior_setup.log 2>&1 || true
INSERT INTO clinic_master.clinics (clinic_id, medical_key, clinic_name) VALUES ('00000000-0000-7000-8000-0000000000b1','MK-BEHAVIOR-1','Behavior Clinic');
INSERT INTO clinic_ops.hp_research (clinic_id, fetch_status, machine_rank, features) VALUES ('00000000-0000-7000-8000-0000000000b1','SUCCESS','B','{"treatment_categories":["内科"],"confirmed_signals":["LINE公式運用"]}');
SQL
R1=$(psql_query -c "SELECT final_rank FROM clinic_ops.current_hp_rank WHERE clinic_id='00000000-0000-7000-8000-0000000000b1';")
echo "after machine only: final_rank=$R1 (expect B)"
[[ "$R1" == "B" ]] && { PASS=$((PASS+1)); } || { FAIL=$((FAIL+1)); FAILURES+=("current_hp_rank machine-only expected B got $R1"); }

psql_exec <<'SQL' >/tmp/validate_behavior_manual.log 2>&1 || true
INSERT INTO clinic_ops.hp_rank_feedback (clinic_id, manual_rank, reviewer, reviewed_at, machine_rank_at_review) VALUES ('00000000-0000-7000-8000-0000000000b1','A','tester',now(),'B');
SQL
R2=$(psql_query -c "SELECT final_rank FROM clinic_ops.current_hp_rank WHERE clinic_id='00000000-0000-7000-8000-0000000000b1';")
echo "after manual review: final_rank=$R2 (expect A, manual wins)"
[[ "$R2" == "A" ]] && { PASS=$((PASS+1)); } || { FAIL=$((FAIL+1)); FAILURES+=("current_hp_rank manual-wins expected A got $R2"); }

psql_exec <<'SQL' >/tmp/validate_behavior_machine2.log 2>&1 || true
INSERT INTO clinic_ops.hp_research (clinic_id, fetch_status, machine_rank) VALUES ('00000000-0000-7000-8000-0000000000b1','SUCCESS','C');
SQL
R3=$(psql_query -c "SELECT final_rank FROM clinic_ops.current_hp_rank WHERE clinic_id='00000000-0000-7000-8000-0000000000b1';")
echo "after second machine recompute: final_rank=$R3 (expect A, manual still wins)"
[[ "$R3" == "A" ]] && { PASS=$((PASS+1)); } || { FAIL=$((FAIL+1)); FAILURES+=("current_hp_rank manual-persists expected A got $R3"); }

echo ""
echo "== Behavior: maps_current confirmed-protection =="
psql_exec <<'SQL' >/tmp/validate_maps_setup.log 2>&1 || true
INSERT INTO clinic_master.clinics (clinic_id, medical_key, clinic_name) VALUES ('00000000-0000-7000-8000-0000000000c1','MK-MAPS-1','Maps Clinic');
INSERT INTO clinic_ops.maps_results (clinic_id, maps_status, maps_website_url, created_at) VALUES ('00000000-0000-7000-8000-0000000000c1','MAPS_MATCHED_WEBSITE','https://confirmed.example.com', now());
SQL
M1=$(psql_query -c "SELECT maps_website_url, is_confirmed FROM clinic_ops.maps_current WHERE clinic_id='00000000-0000-7000-8000-0000000000c1';")
echo "after confirmed event: $M1 (expect confirmed.example.com|t)"

psql_exec <<'SQL' >/tmp/validate_maps_downgrade.log 2>&1 || true
INSERT INTO clinic_ops.maps_results (clinic_id, maps_status, maps_website_url, created_at) VALUES ('00000000-0000-7000-8000-0000000000c1','NOT_FOUND',NULL, now() + interval '1 second');
INSERT INTO clinic_ops.maps_results (clinic_id, maps_status, maps_website_url, created_at) VALUES ('00000000-0000-7000-8000-0000000000c1','AMBIGUOUS',NULL, now() + interval '2 second');
INSERT INTO clinic_ops.maps_results (clinic_id, maps_status, maps_website_url, created_at) VALUES ('00000000-0000-7000-8000-0000000000c1','ERROR',NULL, now() + interval '3 second');
INSERT INTO clinic_ops.maps_results (clinic_id, maps_status, maps_website_url, created_at) VALUES ('00000000-0000-7000-8000-0000000000c1','MAPS_MATCHED_WEBSITE','', now() + interval '4 second');
SQL
M2=$(psql_query -c "SELECT maps_website_url, is_confirmed FROM clinic_ops.maps_current WHERE clinic_id='00000000-0000-7000-8000-0000000000c1';")
echo "after NOT_FOUND/AMBIGUOUS/ERROR/empty-url events: $M2 (expect still confirmed.example.com|t, no downgrade)"
[[ "$M2" == "https://confirmed.example.com|t" ]] && { PASS=$((PASS+1)); } || { FAIL=$((FAIL+1)); FAILURES+=("maps_current downgrade-protection got $M2"); }

psql_exec <<'SQL' >/tmp/validate_maps_new_confirmed.log 2>&1 || true
INSERT INTO clinic_ops.maps_results (clinic_id, maps_status, maps_website_url, created_at) VALUES ('00000000-0000-7000-8000-0000000000c1','MAPS_MATCHED_WEBSITE','https://newconfirmed.example.com', now() + interval '5 second');
SQL
M3=$(psql_query -c "SELECT maps_website_url, is_confirmed FROM clinic_ops.maps_current WHERE clinic_id='00000000-0000-7000-8000-0000000000c1';")
echo "after new confirmed event: $M3 (expect newconfirmed.example.com|t)"
[[ "$M3" == "https://newconfirmed.example.com|t" ]] && { PASS=$((PASS+1)); } || { FAIL=$((FAIL+1)); FAILURES+=("maps_current new-confirmed-replaces got $M3"); }

echo ""
echo "== Behavior: website priority views =="
psql_exec <<'SQL' >/tmp/validate_website_setup.log 2>&1 || true
INSERT INTO clinic_master.clinics (clinic_id, medical_key, clinic_name) VALUES ('00000000-0000-7000-8000-0000000000d1','MK-WEB-1','Website Clinic');
INSERT INTO clinic_ops.hp_research (clinic_id, fetch_status, url) VALUES ('00000000-0000-7000-8000-0000000000d1','SUCCESS','https://machine-hp.example.com');
INSERT INTO clinic_ops.maps_results (clinic_id, maps_status, maps_website_url, created_at) VALUES ('00000000-0000-7000-8000-0000000000d1','MAPS_MATCHED_WEBSITE','https://maps-confirmed.example.com', now());
SQL
W1=$(psql_query -c "SELECT website, is_manual FROM clinic_ops.current_hp_website WHERE clinic_id='00000000-0000-7000-8000-0000000000d1';")
echo "no manual override: current_hp_website=$W1 (expect machine-hp.example.com|f)"
[[ "$W1" == "https://machine-hp.example.com|f" ]] && { PASS=$((PASS+1)); } || { FAIL=$((FAIL+1)); FAILURES+=("current_hp_website machine-fallback got $W1"); }
WO1=$(psql_query -c "SELECT website FROM clinic_ops.current_official_website WHERE clinic_id='00000000-0000-7000-8000-0000000000d1';")
echo "current_official_website (no manual): $WO1 (expect machine-hp, hp wins over maps per priority)"

psql_exec <<'SQL' >/tmp/validate_website_manual_set.log 2>&1 || true
INSERT INTO clinic_ops.manual_override_events (clinic_id, field, operation, value, reviewer, source, reviewed_at)
VALUES ('00000000-0000-7000-8000-0000000000d1','hp_url','SET','"https://manual-hp.example.com"','tester','manual',now());
SQL
W2=$(psql_query -c "SELECT website, is_manual FROM clinic_ops.current_hp_website WHERE clinic_id='00000000-0000-7000-8000-0000000000d1';")
echo "after manual SET: current_hp_website=$W2 (expect manual-hp.example.com|t)"
[[ "$W2" == "https://manual-hp.example.com|t" ]] && { PASS=$((PASS+1)); } || { FAIL=$((FAIL+1)); FAILURES+=("current_hp_website manual-set got $W2"); }

psql_exec <<'SQL' >/tmp/validate_website_manual_clear.log 2>&1 || true
INSERT INTO clinic_ops.manual_override_events (clinic_id, field, operation, value, reviewer, source, reviewed_at)
VALUES ('00000000-0000-7000-8000-0000000000d1','hp_url','CLEAR',NULL,'tester','manual',now() + interval '1 second');
SQL
W3=$(psql_query -c "SELECT website, is_manual FROM clinic_ops.current_hp_website WHERE clinic_id='00000000-0000-7000-8000-0000000000d1';")
echo "after manual CLEAR: current_hp_website=$W3 (expect back to machine-hp.example.com|f)"
[[ "$W3" == "https://machine-hp.example.com|f" ]] && { PASS=$((PASS+1)); } || { FAIL=$((FAIL+1)); FAILURES+=("current_hp_website manual-clear-reverts got $W3"); }

echo ""
echo "== FK delete behavior =="
expect_fail "DELETE clinic with hp_research history (RESTRICT)" "DELETE FROM clinic_master.clinics WHERE clinic_id='00000000-0000-7000-8000-0000000000b1';"

psql_exec <<'SQL' >/tmp/validate_rollback_setup.log 2>&1 || true
INSERT INTO clinic_master.clinics (clinic_id, medical_key, clinic_name, imported_batch_id)
VALUES ('00000000-0000-7000-8000-0000000000e1','MK-ROLLBACK-1','Rollback Clinic','00000000-0000-4000-9000-0000000000bb');
INSERT INTO clinic_ops.import_logs (batch_id, source_file, status) VALUES ('00000000-0000-4000-9000-0000000000bb','fixture.csv','completed');
INSERT INTO clinic_ops.import_log_items (batch_id, medical_key, clinic_id, decision) VALUES ('00000000-0000-4000-9000-0000000000bb','MK-ROLLBACK-1','00000000-0000-7000-8000-0000000000e1','insert');
SQL
BEFORE=$(psql_query -c "SELECT clinic_id FROM clinic_ops.import_log_items WHERE batch_id='00000000-0000-4000-9000-0000000000bb';")
echo "import_log_items.clinic_id before rollback: $BEFORE"
psql_exec <<'SQL' >/tmp/validate_rollback_delete.log 2>&1
DELETE FROM clinic_master.clinics WHERE imported_batch_id='00000000-0000-4000-9000-0000000000bb';
SQL
AFTER_ROW_COUNT=$(psql_query -c "SELECT count(*) FROM clinic_ops.import_log_items WHERE batch_id='00000000-0000-4000-9000-0000000000bb';")
AFTER_CLINIC_ID=$(psql_query -c "SELECT COALESCE(clinic_id::text,'NULL') FROM clinic_ops.import_log_items WHERE batch_id='00000000-0000-4000-9000-0000000000bb';")
echo "after rollback DELETE: import_log_items row_count=$AFTER_ROW_COUNT clinic_id=$AFTER_CLINIC_ID (expect 1 row retained, clinic_id=NULL)"
[[ "$AFTER_ROW_COUNT" == "1" && "$AFTER_CLINIC_ID" == "NULL" ]] && { PASS=$((PASS+1)); } || { FAIL=$((FAIL+1)); FAILURES+=("import_log_items SET NULL on rollback got count=$AFTER_ROW_COUNT clinic_id=$AFTER_CLINIC_ID"); }

echo ""
echo "== Idempotency: re-apply all DDL files =="
for f in 001_create_clinic_master.sql 002_create_clinic_ops.sql 005_create_clinic_ops_extended.sql \
         004_current_hp_rank_view.sql 006_create_current_views.sql; do
  echo "-- re-applying $f"
  if cat "$SQL_DIR/$f" | psql_exec >/tmp/validate_idempotent.log 2>&1; then
    echo "   OK (idempotent)"
  else
    echo "   ERROR (not idempotent, see /tmp/validate_idempotent.log)"
    tail -5 /tmp/validate_idempotent.log
  fi
done

echo ""
echo "=================================================="
echo "SUMMARY: PASS=$PASS FAIL=$FAIL"
if [[ $FAIL -gt 0 ]]; then
  echo "Failures:"
  for f in "${FAILURES[@]}"; do echo "  - $f"; done
fi
echo "=================================================="

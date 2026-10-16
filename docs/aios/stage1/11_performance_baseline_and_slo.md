# Performance Baseline and Proposed SLO

## Measured DB baseline

Production DBでSELECT-only `EXPLAIN (ANALYZE, BUFFERS)`を実行。これはwarm-cache DB executionであり、network/API/render latencyを含まない。

| Query | Rows scanned/returned | Plan | Execution |
|---|---:|---|---:|
| Company list, org + active, updated desc limit 50 | 1,405 / 50 | Seq Scan + top-N sort | 0.880 ms |
| Deal list, org + first unit + active, limit 50 | 504 / 50 | Index Scan + top-N sort | 0.713 ms |
| Company name ILIKE `%クリニック%`, limit 50 | 458 observed before limit / 50 | Seq Scan | 0.882 ms |
| ObjectAssociation source lookup, absent ID | 0 / 0 | unique index scan | 2.419 ms |

Current dataset is small enough that sequential scans are sub-ms in warm cache. This does not validate 162k Clinic Lead scale or user-perceived latency.

## Index observations

- Company has `(organization_id, deleted_at, updated_at)` index but planner chose seq scan at 1.4k rows.
- Deal has business-unit/pipeline/stage index and used it; updated sort is still in-memory.
- leading-wildcard ILIKE has no trigram index and will scale poorly.
- polymorphic association has source/target composite indexes.

## Proposed SLO (not official)

| Path | p50 | p95 | Error |
|---|---:|---:|---:|
| authenticated list API | ≤300 ms | ≤800 ms | <1% |
| search API | ≤500 ms | ≤1,200 ms | <1% |
| detail page server response | ≤500 ms | ≤1,500 ms | <1% |
| command excluding external connector | ≤500 ms | ≤1,500 ms | <0.5% |
| connector async acknowledgment | ≤1 s | ≤2 s | <1% |

These numbers are PROPOSED and require official 09 acceptance confirmation.

## Required Stage2 load test

Seed anonymized/synthetic 10k/100k/250k Company/Hospital rows in isolated DB; test pagination, wildcard/fuzzy search, association fan-out, dashboard aggregation, DealLineItem revenue/gross profit, tenant concurrency, and cold-cache behavior. Prefer cursor pagination and `pg_trgm` only after query evidence. Measure browser→API→DB→render, not DB alone.

## UNVERIFIED

Production page navigation, Vercel function cold start, browser/mobile performance, connector latency, concurrent load and SLO alerting. Production UI was not exercised because deployment/team access was unavailable.

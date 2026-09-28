# Clinic DB Production Migration Runner v1

> 検証日: 2026-09-28
> 結果: localhost Docker ScratchでPASS。Production Supabase migrationは未実行。
> Production SQLiteは`mode=ro` + `PRAGMA query_only=ON`でのみ参照。

## Design

- keyset pagination (`id > cursor ORDER BY id LIMIT 1000`)で1 chunkだけを保持する。
- checkpointは`clinic_ops.import_logs.source_file`へ
  `clinic_sqlite:<sha256>:<phase>:<range_start>:<range_end>`として永続化する。
- chunk data COPYと`status='completed'` checkpoint更新は同一transactionでcommitする。
- failed chunkはdata/audit/checkpoint-completedを全rollbackし、headerだけ`failed`として残す。
- resume cursorは同一source SHA・phaseのcompleted `range_end`最大値。process memoryには依存しない。
- source SQLite idから`medical_key`をchunk単位で引き、targetの`clinic_master.clinics`をSSOTとして
  UUIDを再解決するため、restart後もHP/Maps/Comdesk FKが安定する。
- source hashは1 MiB blockでstreaming計算し、1.09 GB SQLiteを一括readしない。
- Production modeは`--execute`相当、project ref、source fingerprint一致、cutover gate clearを全て要求する。
  現実装のDB transport自体もlocalhost Docker以外を拒否する。

## Comdesk unresolved contract

`docs/clinic-db-review-resolution.md` 2.3節ではtarget `clinic_id`をnullableとしている。これは将来、
明示的にレビューしたunresolved sourceを原文保持できるようにするためであり、同節は未解決行を
export対象外と明記する。nullableであることはautomatic migrationのINSERT許可を意味しない。

PR #9の`scripts/clinic_db_importer/apply_migration.py`はsource `clinic_id=NULL`を無条件にtarget
`clinic_id=NULL`としてINSERTでき、さらにsource clinicがREVIEWでtarget UUIDを持たない場合も
同じNULLへ畳み込む。この挙動はDDL上は可能だが、unresolved判定を監査できない。

Runner v1はsource clinic FKが非NULLかつtarget UUIDへ解決できる行だけINSERTする。NULLまたは
REVIEW clinic参照は`MISSING_FK`相当のREVIEWとして自動INSERTしない。Production実測21行では、
5 INSERT / 16 REVIEWとなった。16件はEMPTY_MEDICAL_KEYでclinic本体がREVIEWになった行への参照である。
unit testとDocker integration testでNULL clinicをREVIEWしtargetへ0 INSERTとすることを固定した。

## Full-scale Scratch result

Source fingerprint before/after:

| field | value |
|---|---|
| SHA-256 | `5b8c37838006545498ec132e09e333dd6200ceccfce09b3b094af75899265c40` |
| mtime | `1790563202.84435` |
| size | `1,090,035,712` bytes |
| clinics | `162,258` |
| empty medical_key | `16` |
| duplicate medical_key groups | `0` |
| integrity_check | `ok` |

Target:

| item | result |
|---|---:|
| clinics | 162,242 |
| clinic REVIEW | 16 |
| hp_research | 814 |
| maps raw | 15,339 |
| maps seed | 13,954 |
| comdesk templates | 1 |
| comdesk original rows | 5 |
| comdesk unresolved REVIEW | 16 |
| import_log_items | 162,258 |
| FK orphan / UUIDv7 mismatch / duplicate target key | 0 |
| duplicate completed source marker | 0 |

## Failure and resume

chunk size 1,000でclinicsの4番目chunk (source id 3001–4000)をtarget column renameにより強制失敗した。
resume cursorは3000、completed=3、failed=1、target clinics=2,984、audit=3,000だった。
失敗chunkのdata追加は0で、schema復旧後は3001から再開して最終件数へ到達した。
その後のresumeを2回実行し、全data phaseが`chunks_processed=0`、全件数不変だった。

## Performance

- chunk size: 1,000
- resume full-scale elapsed: 141.23 seconds
- clinics throughput: 約1,149 source rows/sec (`162,258 / 141.23`)
- peak RSS: 121,520,128 bytes (約115.9 MiB、`/usr/bin/time -l`)
- streaming hash修正前の1.09 GB一括read peak RSS 1,108,033,536 bytesは解消した。

## Cutover and production protection

- `research_job_items`: PENDING 202 / RUNNING 0
- `research_jobs`: RUNNING 0
- cutover gate: **BLOCK**
- Production Supabase DDL/DML: 0/0（接続・migrationとも未実行）
- Production SQLite DDL/INSERT/UPDATE/DELETE: 0/0/0/0
- credentials committed: 0
- PII committed: 0（件数・fingerprint・設計結果のみ）

PENDING 202が解消され、worker停止・lock解放・結果反映を再確認するまでProduction executionは許可しない。

# Clinic DB Schema v1 — Scratch DB Validation

> 実施日: 2026-09-28
> ステータス: **Schema v1 SQL draftsを使い捨てローカルPostgreSQL 17に適用し、実DBで検証した。**
> Production Supabase・Production SQLiteへは一切接続・書き込みしていない。
> 再現手順は `scripts/validate-clinic-schema-v1.sh` を参照(このドキュメントの数値はこのスクリプトの
> 実行結果そのもの)。

---

## Postgres version / environment

| 項目 | 値 |
|---|---|
| PostgreSQL version | `PostgreSQL 17.11 (Debian 17.11-1.pgdg13+2)` on aarch64-unknown-linux-gnu |
| image | `postgres:17`(Docker Hub公式イメージ) |
| method | Docker container(colimaバックエンド経由。Docker Desktopは未インストールのため、
  既にhomebrewでインストール済みの`colima`を起動してDocker daemonを用意した。新規`brew install`は
  行っていない) |
| host/port | `127.0.0.1:55432`(localhost onlyでpublish。外部からは到達不可) |
| container | `clinic-schema-scratch-validate`(`--rm`は使わず、スクリプトの`trap cleanup EXIT`で
  必ず`docker rm -f`。既存volumeはmountせず、コンテナ内部ストレージのみ。実行後、コンテナと
  匿名volumeを完全に削除・確認済み) |
| production credentials used | **なし**。Supabase project URL/password/connection stringは
  一切参照していない。スクリプトはDB_HOSTが`127.0.0.1`/`localhost`以外なら起動時点で拒否する
  safety guardを持つ |

---

## SQL apply order

`docs/clinic-db-sql-drafts/README.md` の正式順序どおり:

```
001_create_clinic_master.sql
  → 002_create_clinic_ops.sql
    → 005_create_clinic_ops_extended.sql
      → 004_current_hp_rank_view.sql
      → 006_create_current_views.sql
```

`003_promotion_example.sql` はDDLではなくデータ操作の例示のため、Schema DDL検証対象から除外
(指示どおり)。

## DDL result

| ファイル | 結果 | 内容 |
|---|---|---|
| 001 | **OK** | `CREATE SCHEMA` ×1, `CREATE TABLE` ×1, `CREATE INDEX` ×7, `COMMENT` ×1 |
| 002 | **OK** | `CREATE SCHEMA` ×1, `CREATE TABLE` ×5, `CREATE INDEX` ×7 |
| 005 | **OK** | `CREATE TABLE` ×4, `CREATE INDEX` ×5 |
| 004 | **OK** | `CREATE VIEW` ×1, `ALTER VIEW` ×1, `COMMENT` ×1 |
| 006 | **OK** | `CREATE VIEW` ×4, `ALTER VIEW` ×4, `COMMENT` ×4 |

**errors: 0**(全SQL文がerror 0で完了)

### Schema assertions(catalog確認)

`information_schema.tables` / `information_schema.views` で全12テーブル・全5 VIEWの存在を確認:

- `clinic_master.clinics`
- `clinic_ops.hp_research`, `hp_rank_feedback`, `manual_override_events`, `maps_results`,
  `comdesk_templates`, `comdesk_original_rows`, `research_jobs`, `research_job_items`,
  `import_logs`, `import_log_items`, `_clinic_schema_migrations`
- VIEW: `clinic_ops.current_hp_rank`, `maps_current`, `manual_overrides_current`,
  `current_hp_website`, `current_official_website`

`pg_class.reloptions` で全5 VIEWに `{security_invoker=true}` が設定されていることも確認済み。

---

## Constraint tests(全て実DBで確認、目視ではない)

| # | 項目 | 結果 |
|---|---|---|
| medical_key | 非空一意 → PASS / `''` → FAIL / 空白のみ → FAIL / 重複 → FAIL | **全件期待通り** |
| legacy_uuid | NULL複数件 → PASS / 同一non-null UUID重複 → FAIL | **全件期待通り** |
| HP rank(machine_rank) | A/D → PASS / `UNKNOWN` → FAIL / `NO_HP` → FAIL | **全件期待通り** |
| fetch_status | SUCCESS/REVIEW/ERROR/NOT_FOUND → PASS / `VERIFIED`/`UNRESEARCHED` → FAIL | **全件期待通り** |
| manual_override_events | SET+non-null → PASS / CLEAR+NULL → PASS / SET+NULL → FAIL / CLEAR+non-null → FAIL / 未許可field → FAIL | **全件期待通り** |
| Jobs(research_jobs.status) | PAUSED/RUNNING/COMPLETED/RESET/BUDGET → PASS / 架空値(`PENDING`) → FAIL | **全件期待通り** |
| Jobs(research_job_items.state) | PENDING/RUNNING/DONE/CANCELLED → PASS / `ERROR`/`SKIPPED` → FAIL | **全件期待通り** |
| CANCELLED contract upgrade | 旧3-state CHECKへ005を再適用後、CANCELLED insert | **PASS** |
| Comdesk(headers/original_values) | 28要素 → PASS / 27要素 → FAIL / 29要素 → FAIL | **全件期待通り** |
| Comdesk重複 | `(source_hash, source_row_number)` 重複 → FAIL | **期待通り** |

---

## Views(behavior test結果)

| VIEW | 検証内容 | 結果 |
|---|---|---|
| `current_hp_rank` | machineのみ→machine値を返す。manual review追加→manualが勝つ。その後machine再計算追加→manualが維持される | **3ステップ全て期待通り** |
| `maps_current` | confirmed website event挿入→それを返す。NOT_FOUND/AMBIGUOUS/ERROR/URL空欄挿入→格下げしない。新しいconfirmed event挿入→更新される | **3ステップ全て期待通り**(下記「実際に見つかった不具合」参照。1回目の実行では2番目のステップで失敗し、修正後の再実行で全通過) |
| `manual_overrides_current` | `current_hp_website`/`current_official_website`のテストを通じて間接的に検証(SET/CLEARの最新解決が正しく機能) | **期待通り** |
| `current_hp_website` | manual未設定→machine URL(`fetch_status='SUCCESS'`の最新行)を返す。manual SET→manualを返す。manual CLEAR→machineへ戻る | **3ステップ全て期待通り** |
| `current_official_website` | manual未設定時、`current_hp_website`(machine HP URL)が`maps_current`より優先されることを確認 | **期待通り**(`docs/clinic-db-review-resolution.md` 1.3節のVIEW解決順`current_hp_website → maps_current`と一致) |

---

## 実際に見つかった不具合(scratch DB検証で発見、目視レビューでは見逃していた)

**`clinic_ops.maps_current` の `confirmed` 判定が空文字列URLをすり抜けていた。**

- 修正前のWHERE句: `AND m.maps_website_url IS NOT NULL`
- 問題: `maps_website_url = ''`(空文字列)は`IS NOT NULL`を通過してしまうため、
  「`MAPS_MATCHED_WEBSITE`だがURLが空欄」の後続eventが誤って`confirmed`と判定され、
  既存のconfirmed website(`https://confirmed.example.com`)を空文字列で上書きしてしまっていた。
  `docs/clinic-db-review-resolution.md` 3.2節の「URL非空」という要件を、実装が満たせていなかった
  (コメントには正しく書かれていたが、SQL自体が要件を満たしていなかった)。
- 修正後: `AND NULLIF(btrim(m.maps_website_url), '') IS NOT NULL`(空文字列・空白のみも除外)
- 修正ファイル: `docs/clinic-db-sql-drafts/006_create_current_views.sql`
- 修正後、同じテストシナリオを再実行し、confirmed website(`https://confirmed.example.com`)が
  正しく保護されることを確認した。

この不具合は前回までの「目視レビュー」(`docs/clinic-db-schema-v1.md` 7節)では検出できておらず、
**実DBでのbehavior testによって初めて発見された**。今回のscratch DB検証の主目的が達成されたことを
示す一例。

---

## FK tests

| テスト | 結果 |
|---|---|
| ops history(`hp_research`)が存在する`clinic_master.clinics`行のDELETE | **RESTRICTでFAIL(期待通り)** |
| `import_log_items`(rollback相当のclinic DELETE時) | 監査行自体は削除されず1行のまま残り、`clinic_id`列だけが自動的にNULLになることを確認(`ON DELETE SET NULL`が正しく機能) |

---

## Idempotency

001, 002, 005, 004, 006 の全5ファイルを**2回連続適用**し、2回目もerrorなく完了することを確認した
(`CREATE SCHEMA/TABLE IF NOT EXISTS`、`CREATE OR REPLACE VIEW`、`CREATE INDEX IF NOT EXISTS`、
`COMMENT ON`、`ALTER VIEW SET`がいずれも冪等な構文であるため)。**完全idempotentな設計であることを
実DBで確認済み**であり、single-apply専用として文書化する必要のある非冪等なSQLは今回発見されなかった。

---

## Known limitations

- 検証はDockerコンテナ内の使い捨てPostgreSQL 17単体で行った。Supabase固有の挙動(pooler、RLS、
  Data API、実際のconnection roleの権限)は今回のscratch DB検証の対象外(`docs/clinic-db-schema-v1.md`
  5節のRLS/GRANT方針は未検証のまま)。
- `research_jobs`/`research_job_items`の複数worker向け`SELECT ... FOR UPDATE SKIP LOCKED`パターンは
  未実装・未検証(`docs/clinic-db-runtime-vocab-v1.md`で設計方針のみ記載、実装は別工程)。
- `hp_research.features`からの`treatment_categories`/`confirmed_signals`投影(`current_hp_rank`
  VIEW)は、jsonbキー名が実装確定前の想定に基づくため、フィールド抽出自体の妥当性(jsonb構造が
  想定通りか)は検証していない(VIEWがエラーなく実行できることのみ確認)。
- 162,258件規模でのパフォーマンス特性(index効果、VIEWのLATERAL joinコスト等)は今回検証していない
  (今回はcorrectness検証のみ、fixtureは数件〜十数件規模)。

---

## Safety

- Production Supabase: DDL 0 / INSERT 0 / UPDATE 0 / DELETE 0
- Production SQLite: DDL 0 / INSERT 0 / UPDATE 0 / DELETE 0(今回は接続・読み取りも行っていない)
- CRM `public` schema: 変更0
- Prisma migrations: 変更0
- 162,258件import: 0
- 使い捨てPostgreSQLコンテナ・匿名volumeは検証終了後に完全削除・確認済み

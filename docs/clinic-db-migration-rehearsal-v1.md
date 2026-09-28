# Clinic DB Migration Rehearsal v1(Scratch PostgreSQL、End-to-End)

> 実施日: 2026-09-28
> ステータス: **Production SQLiteをREAD ONLY sourceとして、Schema v1 + Importerが
> 使い捨てScratch PostgreSQL 17上でEnd-to-Endに成立することを実証した。**
> Production Supabaseへは一切接続・書込みしていない。Production SQLiteへの書込みも0。

---

## Scratch Environment

| 項目 | 値 |
|---|---|
| PostgreSQL | `postgres:17`(公式イメージ、17.11) |
| method | Docker(colima、既にインストール済み・未起動だったため起動。検証後stop。新規install無し) |
| host/port | `127.0.0.1:55433`(localhost only) |
| container | `clinic-rehearsal-scratch`(使い捨て、検証終了後`docker rm -f`で完全削除・確認済み) |
| production credentials used | なし |

`scripts/clinic_db_importer/apply_migration.py`は`_assert_local_host()`で
`127.0.0.1`/`localhost`以外を起動時点で拒否するfail-closed guardを持つ。

Schema適用前に`scripts/validate-clinic-schema-v1.sh`(PR #7)を再実行し、**50/50 PASS**を
再確認してからmigrationを開始した。

---

## Source

| 項目 | 件数 |
|---|---:|
| clinics(source全件) | 162,258 |
| INSERT candidates | 162,242 |
| REVIEW(EMPTY_MEDICAL_KEY) | 16 |
| ERROR | 0 |

`docs/clinic-db-importer-dry-run-v1.md`のdry-run結果と完全一致。

---

## Scratch Target(migration適用後)

| テーブル | 件数 | 内訳 |
|---|---:|---|
| `clinic_master.clinics` | **162,242** | INSERT candidateのみ。16件のEMPTY_MEDICAL_KEYはINSERTしていない |
| `clinic_ops.hp_research` | **814** | raw historyそのまま(fetch_status/rank CHECK違反0件) |
| `clinic_ops.maps_results` | **29,293** | raw history 15,339件 + synthetic current seed 13,954件 |
| `clinic_ops.comdesk_templates` | **1** | |
| `clinic_ops.comdesk_original_rows` | **21** | |
| `clinic_ops.import_logs` | **1** | 単一batch、`status='completed'` |
| `clinic_ops.import_log_items` | **162,258** | 162,242 insert + 16 review。SKIPは0(target emptyのため) |

FK整合性チェック(孤児行の検出): `hp_research`/`maps_results`とも**孤児0件**。

---

## UUIDv7 Mapping(Scratch専用)

`clinic_id`は`docs/clinic-uuid-strategy.md` 4.3節の依存ゼロ参照実装
(`scripts/clinic_db_importer/uuid7.py`、変更なしでそのまま使用)で生成した。
同一migration run内で1つの`sqlite_id → clinic_id`辞書をメモリ上に保持し、
`clinic_master.clinics`本体・`hp_research`・`maps_results`(raw/seed両方)・
`comdesk_original_rows`のFK解決すべてに**同一のclinic_id**を使い回した
(FK孤児0件という結果がこの一貫性を裏付けている)。

**このUUIDv7はScratch専用であり、Production用IDとして確定していない。**
Production実装時は本番importer実行時に新たに採番する(Clinic Lead側のuuid6 dependency、
`docs/clinic-db-consumer-contract.md` 1節)。今回のマッピング自体はPII相当
(medical_key⇄clinic_id対応)を含むため、Gitには一切コミットしていない
(実行後にコンテナごと破棄、マッピングはプロセスのメモリ上にのみ存在)。

---

## Import Audit

`import_logs`:

```
batch_id: (実行毎に新規UUID)
source_file: 'clinic_sqlite:<source SHA-256>'   -- 冪等性判定に使うsource identityキー
status: completed
rows_total: 162258, rows_inserted: 162242, rows_skipped: 0, rows_review: 16
```

`import_log_items`(162,258件)は`insert`/`skip`/`review`の3値のみで構成され、SKIPは
target_emptyのため0件、REVIEW 16件は全て`clinic_id=NULL`・`reason='EMPTY_MEDICAL_KEY'`。

---

## HP

| 項目 | 結果 |
|---|---|
| count | 814(source全件をmigration) |
| FK missing | **0** |
| `fetch_status` CHECK violation | **0** |
| `machine_rank` CHECK violation | **0** |
| `fetch_status`分布 | `SUCCESS=636, REVIEW=153, ERROR=22, NOT_FOUND=3`(合計814) |
| `machine_rank`分布 | `A=127, B=266, C=211, D=32, NULL=178`(合計814、UNKNOWN/NO_HPはrank列へ入れずNULL) |

**独立したクロスチェック**: `machine_rank`のA/B/C/D分布(127/266/211/32)は
`docs/clinic-db-readonly-audit.md`が報告していたlegacy `clinics.hp_rank`分布と完全一致した
(同じ研究結果から双方が導出されているため、一致は健全性の証拠)。また`fetch_status=SUCCESS`
(636件)とlegacy `clinics.hp_status=VERIFIED`(643件)には**7件の差**があるが、これは
`docs/clinic-db-runtime-vocab-v1.md`で特定済みの`ACCESS_RESTRICTED`パス
(`src/enrichment/researcher.py`: Maps確認済みURLだがcontent解析未完了で
`hp_status="VERIFIED"`かつ`research_status="REVIEW"`となるケース)と**正確に一致する差分**であり、
異常ではなくコード分析の妥当性を裏付ける追加証拠である。

---

## Maps

| 項目 | 結果 |
|---|---|
| raw history投入 | 15,339件 |
| synthetic seed投入 | 13,954件(legacy `clinics.maps_presence_status`/`maps_website_url`いずれかが
非空の医院、重複投入なし) |
| FK missing | 0 |
| `maps_current`が同一状態を二重投入していないか | seedは`created_at=now()`
(raw historyの実タイムスタンプより常に新しい)で1医院につき1行のみ投入。raw historyとは
別个のtimestampを持つため物理的な重複行ではない |
| **confirmed website downgrade** | **0**(13,954件全件で実測、後述) |

**全13,954候補での突合結果**: `clinic_ops.maps_current`(migration後)と
legacy `clinics.maps_presence_status`/`maps_website_url`(SQLite)を`medical_key`で
突合した結果:

```
legacy seed candidates: 13,954
exact_match: 13,954
website_downgrade (legacy confirmed -> target lost it): 0
other_diff: 0
```

**13,954件全件が完全一致、downgrade 0件、その他差分0件**。synthetic seedのタイムスタンプを
「常に最新」にする設計(`docs/clinic-db-migration-rehearsal-v1.md`実装、
`docs/clinic-db-review-resolution.md` 3.2節のprotection ruleに準拠)が、実データで
意図通り機能することを確認した。

---

## Comdesk

| 項目 | 結果 |
|---|---|
| templates | 1件、28 headers、field_mapping有効 |
| original_rows | 21件、全て28要素original_values、`source_hash`+`source_row_number`重複なし |
| clinic FK | 21/21 解決(孤児0) |
| template FK | 21/21 解決 |

固定28列exportをScratch DBのみから再構築可能であることを、CHECK制約(28要素)が
全件通過したことで確認した(legacy SQLite実exportとのバイト単位比較は今回のスコープ外だが、
`original_values`のJSON内容はlegacy `row_json`をそのまま`sanitize_json_value`適用後に
COPYしたものであり、内容は保持されている)。

---

## Manual

`manual_overrides`(legacy) = 0件を再確認。`manual_override_events`へは**0件**投入
(推測INSERTは一切行っていない)。

---

## Data Equality(162,242件全件、field-by-field)

`medical_key`, `legacy_uuid`, `clinic_name`, `medical_type`, `prefecture`, `address`, `phone`,
`designation_date`, `registration_reason`, `owner_equal`, `age_probability`, `departments`,
`active`, `is_new`, `source_as_of_date`, `merge_hold`, `exclude_reason`, `source_payload`,
`first_seen_at`, `last_seen_at`、および`name_norm`/`name_prefix`/`phone_norm`/`address_norm`/
`tel_match_key`(normalizer再生成値)について、Python側で計算した期待値とScratch DBの実際の
格納値を162,242件全件で比較した。

```
missing target rows: 0
mismatch_by_field (scalar columns): NONE
timestamp mismatch (first_seen_at / last_seen_at): {0, 0}
departments (array) mismatch: 0
source_payload (jsonb) mismatch: 0
```

**全項目で不一致0件**。`clinic_id`(UUIDv7)はsourceに存在しないためfingerprint/比較対象から
除外した(指示どおり)。

**検証時に見つかった副産物(検証スクリプト側の誤り、移行結果自体の誤りではない)**:
最初の比較パスで`phone_norm`/`tel_match_key`に689/690件、`name_norm`/`name_prefix`に各1件の
「不一致」が出たが、原因は検証スクリプトが空文字列を一律NULL扱いに変換していたためだった
(電話番号が空の医院では`phone_norm`/`tel_match_key`が正しく空文字列になるが、これは
NULLとは異なる正常値)。検証ロジックを修正した結果、不一致は完全に0件になった。この経緯も
透明性のため記録する。

---

## Views(実migrationデータで検証)

| VIEW | 行数 | 結果 |
|---|---:|---|
| `current_hp_rank` | 162,242(1医院1行) | `final_rank`非NULLは636件(`fetch_status=SUCCESS`の件数と一致)。NULL/error行なし |
| `maps_current` | 162,242(1医院1行) | `is_confirmed=true`かつURL非NULLが10,311件。NULL/error行なし |
| `manual_overrides_current` | 0 | legacy 0件と整合 |
| `current_hp_website` | 162,242 | 636件が非NULL(machine URL経由、manual 0件のため`is_manual`は全件false) |
| `current_official_website` | 162,242 | 162,242件(hp優先、mapsへのfallback含む)。NULL/error行なし |

HP rank distributionは前述のHP節でlegacy summaryと突合済み。Maps current status/website は
前述のMaps節で13,954件全件をlegacy `clinics.maps_*`と突合済み(完全一致)。

---

## Idempotency

同一Scratch DBへ、同一Production SQLite(SHA-256完全一致)に対して**2回目のapply**を実行した。

```
1回目: idempotent_skip=False, success=True
       counts: clinics_insert=162242, hp_research=814, maps_raw=15339, maps_seed=13954,
               comdesk_templates=1, comdesk_original_rows=21, import_log_items=162258

2回目: idempotent_skip=True, success=True
       counts: insert=0, skip=162242, review=16, error=0
```

2回目実行後の全テーブル件数(1回目と完全不変):

| テーブル | 1回目後 | 2回目後 |
|---|---:|---:|
| clinics | 162,242 | **162,242**(不変) |
| hp_research | 814 | **814**(不変) |
| maps_results | 29,293 | **29,293**(不変) |
| comdesk_templates | 1 | **1**(不変) |
| comdesk_original_rows | 21 | **21**(不変) |
| import_logs | 1 | **1**(不変、2件目のbatch行は作成されない) |
| import_log_items | 162,258 | **162,258**(不変) |

**duplicate INSERTは一切発生しなかった。** 冪等性の実現方式:
`clinic_ops.import_logs`の`source_file`列にSQLiteのSHA-256を埋め込み、
`status='completed'`の既存batchが同一source識別子で見つかった場合、
HP/Maps/Comdesk(すべてappend-only historyテーブル)のINSERTを丸ごとskipする
「batch単位のidempotency guard」を実装した(`docs/clinic-db-importer-dry-run-v1.md`作成時点では
未実装だった機能。今回のrehearsalで追加)。`clinic_master.clinics`はこれに加えて
`medical_key`単位の存在チェックも二重に効く(defense in depth)。

---

## Failure Recovery(意図的な失敗テスト)

小さなfixture(3件の正常行 + 1件の`medical_key`重複行)で、mainトランザクションを
意図的に失敗させた。

```
Step 1 (batch header, 別トランザクション): import_logs へ status='running' でINSERT → 成功、即座にcommit
Step 2 (main transaction): BEGIN; COPY clinics (4行、うち1行がUNIQUE制約違反); ...
  → ERROR: duplicate key value violates unique constraint "clinics_medical_key_key"
  → トランザクション全体がabort(COMMITに到達せず)
Step 3 (別トランザクション): import_logs を status='failed' へUPDATE → 成功
```

**検証結果**:
- `rollback`: 3件の正常に見えた行(`MK-FAIL-1/2/3`)も含め、**0件**がテーブルに残った
  (COPY全体が1トランザクションのため、UNIQUE違反より前に成功したCOPY行も含めて完全ロールバック)
- `audit`: `import_logs`は`status='failed'`として正しく記録され、batch自体の存在は失われない
- `partial data`: 部分的に不整合な状態は一切残らなかった

さらに、**実データでの本番相当規模でも同じ境界を確認**した: NUL byte問題(下記)で
162,242件のCOPYが成功した直後に`hp_research`のCOPYで実際に失敗した際も、
既に成功していた162,242件の`clinics`行を含め**全件が正しくロールバックされ**(`clinic_master.clinics`
count=0を確認)、`import_logs`は`status='failed'`を正しく記録した。1万件規模でもこの
transaction/audit境界が破綻しないことを実証できた。

---

## 発見した実バグ(migration実行によってのみ発見できたもの)

### PostgreSQL jsonbはNUL byte(`\u0000`)を拒否する

162,242件規模の初回本番相当実行で、`hp_research`のCOPY中に以下のエラーで失敗した:

```
ERROR:  unsupported Unicode escape sequence
DETAIL:  \u0000 cannot be converted to text.
CONTEXT:  JSON data, line 1: ..."url": "https://www.kandacli.com/開院\u0000...
```

**原因**: legacyの`research_results.result_json`中のあるURL文字列に、スクレイピング由来と
思われるNUL文字(`\x00`)が混入していた。Python標準の`json.loads`/`json.dumps`はこれを
正当なJSON(`\u0000`エスケープ)として問題なく扱えるが、**PostgreSQLのjsonb入力関数は
`\u0000`を明示的に拒否する**(内部のC文字列表現がNUL終端のため、NUL自体を格納できない
という根本的な制約)。dry-run(PR #8)のJSON妥当性検証はPythonの`json.loads`基準だったため、
この問題を**検出できていなかった**(0 invalid JSONと報告していたが、それはPython視点で
正しい)。

**修正**: `scripts/clinic_db_importer/transform.py`に`strip_nul()`/`sanitize_json_value()`を
追加し、`pg_csv.field()`/`pg_csv.json_field()`/`pg_csv.text_array_field()`の**全ての
文字列直列化経路**で再帰的にNUL byteを除去するよう修正した(値を捏造せず、意味を持たない
制御文字を除去するだけ)。修正後、162,242件全件が問題なくCOPYできることを確認した。

この発見は、**目視レビューやPython単体でのJSON検証だけでは見つからず、実際にPostgreSQLへ
INSERTして初めて表面化した**、まさにこのrehearsalの目的どおりの成果である。

### `import_log_items.medical_key`のNOT NULL制約とEMPTY_MEDICAL_KEY行

smoke test(5行の小fixture)で、REVIEW判定された空medical_key行の監査ログ書き込みが
`medical_key`列のNOT NULL制約に違反して失敗した(`issues.medical_key`が`None`になるため)。
`docs/clinic-db-architecture.md` 3.5節の設計意図(監査スナップショットとして原文を保持する)
に立ち返り、EMPTY_MEDICAL_KEY行では変換後の`None`ではなく**元のSQLite生値(空文字列)**を
`import_log_items.medical_key`へ記録するよう修正した。本番相当データでもこの16件について
問題なく監査記録できることを確認済み。

---

## Performance

| 項目 | 値 |
|---|---|
| elapsed(スクリプト内計測) | **25.40秒**(clinics 162,258読込+分類+162,242 INSERT、hp_research 814件、maps_results 29,293件、comdesk 22件、import_log_items 162,258件のCOPY全体) |
| elapsed(`/usr/bin/time`実測、プロセス起動込み) | 25.96秒 |
| rows/sec(書き込み行ベース、354,629行 ÷ 25.40秒) | 約13,960 rows/sec |
| peak memory(maximum resident set size) | 約4.83 GB(5,061,591,040 bytes) |
| batch size | チャンク分割なし、単一トランザクションで全件一括(rehearsal規模では許容範囲) |
| PARALLEL_WORKERS | **使用せず**(逐次処理のみ。指示どおり並列worker禁止) |

**Production実装への示唆**: 約4.8GBのpeak memoryは、全162,258行をPythonの辞書リストとして
一度にメモリへ読み込む現在の実装(`rows = [dict(r) for r in conn.execute(...)]`)に起因する。
Production実装では`docs/clinic-db-migration-plan.md` STEP[10]で既に設計していた
「1,000〜5,000件単位のチャンク分割」を実際に適用し、ストリーミング処理へ変更することを推奨する
(今回のrehearsalは一括処理でも安全性・正確性を検証する目的のため、あえてchunkingを
実装しなかった)。

---

## Jobs

| 項目 | 件数 |
|---|---:|
| RUNNING jobs | 0 |
| RUNNING items | 0 |
| PENDING items | **202** |

`docs/clinic-db-importer-dry-run-v1.md`修正後の表現を踏襲する: **RUNNING activity gateはclear**
(`RUNNING jobs=0`かつ`RUNNING items=0`)。しかし`docs/clinic-db-review-resolution.md` 5節の
full cutover条件(`research_job_items.state IN ('PENDING','RUNNING') = 0`)は
**PENDING items 202件が残るため未達**。今回もこの202件を変更・削除・処理していない
(read-only再確認のみ)。

---

## Production Source Protection

| 項目 | 値 |
|---|---|
| SHA-256(全工程前後で完全一致) | `5b8c37838006545498ec132e09e333dd6200ceccfce09b3b094af75899265c40` |
| mtime | `Sep 28 11:40:02 2026`(完全一致) |
| size | `1,090,035,712 bytes`(完全一致) |
| count | 162,258 |
| duplicate(非空medical_key) | 0 |
| integrity | ok |

Schema apply → 初回migration(失敗、NUL byte) → コード修正 → 2回目migration(成功) →
idempotency再実行 → データ突合 → failure test、という一連の作業(Scratch DBへの操作を
何度も含む)の**前後を通じて**、Production SQLiteは一度も書き込まれていない
(読み取り専用接続のみ、`docs/clinic-db-importer-dry-run-v1.md`と同じWAL関連の注記が
today's作業にも適用される)。

---

## 成果物

- `scripts/clinic_db_importer/apply_migration.py`(新規): Scratch専用のapply importer
- `scripts/clinic_db_importer/pg_csv.py`(新規): PostgreSQL COPY用のCSV直列化(NUL sanitization含む)
- `scripts/clinic_db_importer/uuid7.py`(新規): Scratch専用UUIDv7参照実装(docs/clinic-uuid-strategy.md 4.3節と同一)
- `scripts/clinic_db_importer/transform.py`(更新): `strip_nul()` / `sanitize_json_value()`追加
- `scripts/clinic_db_importer/tests/test_pg_csv.py`(新規)、`test_transform.py`(NUL関連test追加)
- 本ドキュメント

UUIDv7マッピング・medical_key等のPIIを含む中間ファイルはGitへ一切含めていない
(全て`/tmp`上で作業し、コンテナごと破棄済み)。

---

## Safety

- Production Supabase: DDL 0 / INSERT 0 / UPDATE 0 / DELETE 0
- Production SQLite: DDL 0 / INSERT 0 / UPDATE 0 / DELETE 0
- CRM `public` schema: 変更0
- Prisma migrations: 変更0
- Clinic Lead repo code変更: 0

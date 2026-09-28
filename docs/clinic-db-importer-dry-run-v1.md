# Clinic DB Importer — Dry Run v1(書き込みゼロ)

> 実施日: 2026-09-28
> ステータス: **Production SQLite 162,258件をREAD ONLYで読み、Schema v1向けdecisionを判定した。
> PostgreSQL(Scratch/Supabaseいずれも)へのINSERTは一切行っていない。**
> 機械可読summary: `docs/clinic-db-importer-dry-run-v1.summary.json`(PIIなし、そのまま`git`管理)。
> 個別医院のreview/error明細(medical_key等を含む)はPII扱いとし、`/tmp`配下にのみ出力し
> **Gitには一切含めていない**。

---

## Architecture

```
scripts/clinic_db_importer/
  __init__.py
  reason_codes.py         クローズドな理由コードのenum
  sqlite_reader.py         read-only接続・baseline取得(SHA-256/mtime/size/count/整合性)
  normalizer_bridge.py     Clinic Lead既存normalizer関数のread-only import
  transform.py             date/boolean/numeric/JSON/UUIDのpure parse関数
  classify.py              INSERT/SKIP/REVIEW/ERROR決定ロジック(clinics/HP/Maps/Comdesk共通)
  hp_mapping.py            research_results → hp_research dry-run
  maps_mapping.py          google_maps_results → maps_results dry-run + synthetic seed算出
  comdesk_mapping.py       templates/comdesk_original_rows dry-run
  jobs_report.py           research_jobs/research_job_items のcutover gate件数(read-only)
  report.py                Tally集計・fingerprint・detail row書き出し(repo内書き込みを拒否するguard付き)
  run_dry_run.py           CLIエントリポイント
  tests/                   unit test 58件(pytest)
```

Production applyでも同じモジュール(`classify.py`, `transform.py`, `hp_mapping.py`等)を再利用できる
構成にしている。1つの巨大scriptにはせず、かつ過剰なレイヤー分割も避けた。

---

## Production Source(Protection)

### Before / After(完全一致)

| 項目 | 値 |
|---|---|
| SHA-256 | `5b8c37838006545498ec132e09e333dd6200ceccfce09b3b094af75899265c40`(before/after一致) |
| mtime | `1790563202.844...`(before/after一致) |
| size | `1,090,035,712 bytes`(before/after一致) |
| `clinics` count | `162,258` |
| `medical_key` empty | `16` |
| `medical_key` duplicate groups(非空) | `0` |
| `PRAGMA integrity_check` | `ok` |

2回のフルdry-run実行(下記Determinism参照)を挟んだ前後で、上記6項目すべてが完全一致することを
確認した。DDL/DML(INSERT/UPDATE/DELETE)は一切実行していない。

### 環境固有の注記(正直に開示)

このSQLiteファイルは **WAL(Write-Ahead Logging)journalモード**である。SQLiteの仕様上、
`mode=ro`(`SQLITE_OPEN_READONLY`)での厳密な読み取り専用オープンは、対応する`<file>-shm`が
**既に存在しない場合は失敗する**(データを一切変更しない場合でもOSレベルで`SQLITE_CANTOPEN`になる)。
本セッションの実行環境では`-shm`/`-wal`ファイルが毎回の呼び出しで永続しなかったため、
`sqlite_reader._ensure_wal_support_files()`が「`-shm`が無ければ、`PRAGMA query_only=ON`を
即座に設定した通常接続で軽い`SELECT 1`を1回だけ実行し、SQLiteが管理する空の`-shm`/`-wal`
補助ファイルだけを用意してから、以後は`mode=ro`接続に切り替える」処理を行う。

- この補助ファイル生成は、メインの`.sqlite3`ファイル自体には**1バイトも書き込まない**
  (上記のSHA-256/mtime完全一致で実証済み)。
- `-wal`ファイルは常に0バイトのまま(実際のトランザクションデータは一切書き込まれていない)。
- `PRAGMA query_only=ON`は、この軽量な通常接続を含め**全ての接続で、最初の1文として**設定して
  おり、以後どの接続でもINSERT/UPDATE/DELETE/DDL文は実行不可能(SQLite自体が拒否する)。
- これはSQLite WAL modeの一般的な既知動作であり、他のread-onlyツール(`sqlite3 -readonly`
  CLI含む)でも同じ制約に直面する。隠さず本ドキュメントに明記する。

---

## Master Dry-run(`clinics`、target_empty simulation)

| 項目 | 件数 |
|---|---:|
| total | 162,258 |
| INSERT candidate | **162,242** |
| SKIP | 0(下記参照) |
| REVIEW | **16** |
| ERROR | 0 |

REVIEW理由の内訳: `EMPTY_MEDICAL_KEY` = 16件(既知の空文字medical_keyと完全一致)。
**それ以外の理由コード(DUPLICATE_MEDICAL_KEY / MERGE_HOLD / UNRESOLVED_MERGE /
NORMALIZER_MISMATCH / INVALID_UUID / INVALID_JSON / INVALID_DATE / INVALID_NUMERIC /
OTHER_VALIDATION_ERROR)は0件**。162,258件全件を通して、この6項目以外の品質問題は
検出されなかった。

**SKIPについて**: 今回はtarget(Postgres)未接続のため、実データに対しては
`target_empty`(空のtargetへ移行する想定)simulationのみを実行した。`existing_key`
simulation(targetに既存medical_keyがある場合にSKIPになるロジック)は
`classify.py`のunit test(`test_existing_key_simulation_is_skip`等)で分離してテスト済み
(`docs/clinic-db-schema-v1.md`のtargetは現時点で空のため、実データへの適用は無意味であり
実施していない)。

---

## medical_key

| 項目 | 件数 |
|---|---:|
| NULL | 0 |
| empty | 16 |
| blank-only(空白のみ) | 0 |
| non-empty | 162,242 |
| duplicate(非空) | 0 |

16件の空文字は自動的にREVIEWへ分類され、medical_keyを推測生成することは一切していない。

---

## legacy_uuid

| 項目 | 件数 |
|---|---:|
| empty(→NULL) | 162,237 |
| valid(非空) | **21** |
| invalid | **0** |
| duplicate groups | **0** |

既知baseline(`docs/clinic-db-readonly-audit.md`: 非空21・valid21・invalid0・duplicate0)と
**完全一致**。

---

## Normalizers

Clinic Lead既存の`src.normalizer.clinic_name` / `src.normalizer.phone` / `src.normalizer.address`
を`normalizer_bridge.py`経由でread-only importし、162,258件全件について
`name_norm`/`name_prefix`/`phone_norm`/`tel_match_key`/`address_norm`を再生成し、
SQLite保存値と比較した。

| field | mismatch件数 |
|---|---:|
| name_norm | **0** |
| name_prefix | **0** |
| phone_norm | **0** |
| tel_match_key | **0** |
| address_norm | **0** |

**不一致は0件**。162,258件全てについて、Clinic Lead既存normalizerを同一ロジックで再適用した
結果が保存値と完全に一致した。これにより、Production apply時にこれらの列を**COPYせず
再生成する**方針(`docs/clinic-db-runtime-vocab-v1.md`の決定どおり)が、少なくとも現時点の
データに対しては安全であることを実データで確認できた。

---

## JSON Validation

`base_json` / `effective_json` / `departments_json` / `treatments_json` / `signals_json`
について162,258件全件をJSON解析した。**invalid JSONは0件**(全件がclinicsのREVIEW理由
`INVALID_JSON`に現れていないことで確認)。`docs/clinic-sqlite-to-postgres-mapping.md`が
既に報告していた実測(`treatments_json`/`signals_json`とも162,258/162,258 valid)と整合する。

---

## Date / Boolean / Numeric Transform

`designation_date` / `source_as_of_date` / `first_seen_at` / `last_seen_at`(date/timestamp
どちらの書式でも許容)、`age_probability`(numeric)、`owner_equal` / `active` / `is_new` /
`merge_hold`(boolean、SQLite上は`INTEGER`)について162,258件全件を変換した。

**parse失敗は0件**(`INVALID_DATE` / `INVALID_NUMERIC` / `invalid_boolean:*` のいずれも
clinicsのREVIEW理由に一度も現れていない)。暗黙変換で値を壊すことなく、全件が期待どおりの
型へ変換可能だった。

---

## HP Mapping Dry-run

`research_results`(814件)について、`fetch_status`(=`research_status`)がコード確定4値
(`SUCCESS`/`REVIEW`/`ERROR`/`NOT_FOUND`)に収まるか、`hp_rank`がA/B/C/D/NULL(UNKNOWN・NO_HPは
NULLへ)へ正しくマップできるか、`clinic_id`が実在するclinics行を指すかを検証した。

| 項目 | 件数 |
|---|---:|
| source rows | 814 |
| mappable(INSERT相当) | **814** |
| REVIEW | 0 |
| ERROR | 0 |

814件全件が問題なくマップ可能。`UNKNOWN`/`NO_HP`はrank列へ入れず、確認した範囲では
その他の未知のrank値も検出されなかった。

---

## Maps Mapping Dry-run

`google_maps_results`(15,339件)について、`clinic_id`のFK解決とJSON妥当性を検証した。

| 項目 | 件数 |
|---|---:|
| source rows | 15,339 |
| mappable(INSERT相当) | **15,339** |
| REVIEW | 0 |
| ERROR | 0 |
| synthetic current-seed candidates(`clinics.maps_*`由来) | **13,954** |

15,339件全件がFK解決・JSON妥当性の両方をクリアした。`clinics.maps_presence_status`または
`clinics.maps_website_url`のいずれかが非空の医院は13,954件あり、これが
`docs/clinic-db-review-resolution.md` 3.2節で設計した「legacy current stateをsynthetic
current-seed eventとして1件投入する」対象候補数になる(実際の投入は今回行っていない)。
`docs/clinic-db-readonly-audit.md`が既に報告していた同じ数値(13,954件)と一致する。

confirmed website保護ruleに必要な情報(`maps_status`, `maps_website_url`, `created_at`相当の
時刻)はすべての行で欠落なく取得できることを確認した。

---

## Comdesk Dry-run

| テーブル | 件数 | 結果 |
|---|---:|---|
| `templates` | 1 | **valid**(headers 28要素、mapping objectとも妥当なJSON) |
| `comdesk_original_rows` | 21 | **valid**(全21件が28要素のoriginal_values、有効なtemplate/clinic FK) |
| error | — | **0** |

21件全てについて、template link・clinic link・28要素original_values・source_hash/row_number
が揃っており、SQLiteなしで固定28列exportを再現可能な形へtransformできることを確認した。

---

## Manual Overrides

`manual_overrides`テーブルの件数を確認したところ **0 rows** だった。したがって
**0件migration**であり、`clinics.hp_rank`等からmanual historyを推測生成する処理は
一切実装していない(`docs/clinic-sqlite-to-postgres-mapping.md`の既存方針どおり)。

---

## Job Runtime(cutover gate、read-only)

| 項目 | 件数 |
|---|---:|
| RUNNING jobs | **0** |
| PAUSED jobs | 1 |
| COMPLETED jobs | 49 |
| RESET jobs | 7 |
| PENDING items | 202 |
| RUNNING items | **0** |
| DONE items | 2,636 |

`docs/clinic-db-review-resolution.md` 5節のfull cutover gate条件は
`research_job_items.state IN ('PENDING','RUNNING') = 0`(`RUNNING jobs = 0`も併せて)であり、
**PENDING items 202件が残っているため、full Production cutover gateは未達**。

正確には: **RUNNING activity gate(`RUNNING jobs=0` かつ `RUNNING items=0`)はclear**。
ただし**full Production cutover gateは未達**であり、この202件を処理完了させるか、
意図的に打ち切るかの業務判断が別途必要になる(今回は削除・停止・処理のいずれも行っていない、
read-only報告のみ)。

---

## UUIDv7

今回はtargetへのINSERTを行わないため、162,258個の本番`clinic_id`は確定生成していない。
UUIDv7 generator自体のcontract(`docs/clinic-uuid-strategy.md`)はunit test可能な形で
既に`docs/clinic-uuid-tests/test_uuid7_strategy.py`にdraftがある。正式方針は
Clinic Lead実runtime(Python 3.12.14)向けに`uuid6` dependencyを追加することであり
(`docs/clinic-db-consumer-contract.md` 1節)、**今回もClinic Leadの`requirements.txt`等を
変更していない**。Production実装時に別途、明示的な依存追加作業が必要。

---

## Determinism

同一SQLite(SHA-256完全一致)・同一commitのコードで、フルデータセット(162,258 + 814 + 15,339 +
22件)に対する dry-run を**2回連続実行**し、以下を比較した。

| fingerprint | run1 | run2 | 一致 |
|---|---|---|---|
| clinics | `eca8fd6c93aa7ea1...` | `eca8fd6c93aa7ea1...` | **一致** |
| hp_research | `f8c6672ad9d2556e...` | `f8c6672ad9d2556e...` | **一致** |
| maps_results | `06eaf618177699cc...` | `06eaf618177699cc...` | **一致** |
| comdesk | `34cb2f1115f4bffa...` | `34cb2f1115f4bffa...` | **一致** |

decision/reason-code集計(`summary["clinics"]`等)も2回の実行で完全に同一の辞書だった。
fingerprintはSHA-256(`report.Tally.fingerprint()`)で、実行順序に依存しないよう
`sorted()`したcounts dictをJSON化してハッシュ化している。

---

## Tests

`pytest scripts/clinic_db_importer/tests/` — **58 passed**。

- unit test: `classify.py`(15件、target_empty/existing_key双方)、`transform.py`(13件)、
  `normalizer_bridge.py`(6件、Clinic Lead実関数を直接呼び出して既知の変換結果と比較。
  リポジトリ不在環境では自動skip)、`hp_mapping.py`(7件)、`maps_mapping.py`(6件)、
  `comdesk_mapping.py`(6件)、`reason_codes.py`(2件、closed-set検証)、
  `report.py`のrepo内書き込み拒否ガード(2件)
- integration test: 5行の小さなfixture SQLite(clean 1件 + EMPTY_MEDICAL_KEY 1件 +
  MERGE_HOLD 1件 + INVALID_UUID 1件 + INVALID_JSON 1件)でdry-runし、期待どおりの
  decision/reason分布になることを確認(1件)
- determinism test: 同fixtureに対する2回実行でfingerprint一致を確認(1件)

Production SQLite全162,258件でのdeterminism確認は、pytestのunit/integration testとは別に
本ドキュメント作成時に手動実行して確認した(「Determinism」節参照)。CI等での自動化が
必要な場合は、Production SQLiteへの参照を環境変数化した追加testを別途用意できる
(今回はProduction pathをハードコードしないCLI引数設計のみ用意し、実行は手動)。

---

## Remaining Review / Error(概要のみ、明細は非公開)

REVIEW対象は`clinics`の16件(`EMPTY_MEDICAL_KEY`)のみ。HP/Maps/Comdesk/Job runtimeには
REVIEW/ERROR該当が1件も存在しない。個別医院の明細(medical_key・SQLite内部id・理由コード)は
`/tmp/clinic-dry-run-detail-run{1,2}/*.jsonl`に出力済みで、Gitには一切含めていない
(`report.write_detail_rows`がrepo内パスへの書き込みを例外で拒否するガードを持つ)。

---

## Limitations

- 今回はtarget(PostgreSQL、Scratch/Supabaseいずれも)へのINSERTを一切行っていないため、
  `existing_key` simulationの現実データへの適用結果は存在しない(unit testでのみ検証済み)。
- `merged_into`が設定されている行は本来「解決すればSKIP/INSERTになり得る」が、今回の
  1-pass classifierでは一律REVIEW(`UNRESOLVED_MERGE`)としている(2-pass UUID解決は
  今回のスコープ外)。ただし実データでは該当0件だった。
- `research_jobs.status`/`research_job_items.state`の複数worker向けatomic claim実装は
  このdry-runの対象外(`docs/clinic-db-runtime-vocab-v1.md`で設計方針のみ)。
- normalizer比較はSQLiteに実在する`clinic_name`/`phone`/`address`列をそのままClinic Lead
  関数へ渡した結果であり、Clinic Lead側のアプリ実行時に追加の前処理(トリム等)が
  加わっている可能性までは検証していない(それでも0件不一致だった)。

---

## Safety

- Production Supabase: DDL 0 / INSERT 0 / UPDATE 0 / DELETE 0
- Production SQLite: DDL 0 / INSERT 0 / UPDATE 0 / DELETE 0(SHA-256/mtime/size完全一致で実証)
- Clinic Lead repo code変更: 0(`git status`で確認)
- 162,258件のtarget INSERT: 0
- Scratch PostgreSQLへのINSERT: 0(今回は接続すらしていない)

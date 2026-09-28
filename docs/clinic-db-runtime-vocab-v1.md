# Clinic DB Runtime Vocabulary v1(コード確定版)

> 調査日: 2026-09-28
> Clinic Lead source: `/Users/maekawahiroyuki/Desktop/clinic-list-filter-complete`(read-only、変更なし)
> 目的: `docs/clinic-db-schema-v1.md` の Remaining Unknowns のうち、コードからREAD ONLYで確定可能な
> 4項目(hot_status / hp_research.fetch_status / job status・state / normalizer)を解消する。
> Supabase DDL/DML、Production SQLiteへの書き込み、Clinic Lead repoへの変更は一切行っていない。

---

## # hot_status

**producer**: `src/scoring/research_scoring.py:93`

```python
def hot_status(count):
    return "かなりアツい" if count>=3 else "アツい" if count==2 else "集客投資シグナルあり" if count==1 else "通常"
```

**inputs**: `count` = `len(signals)`(確定済みmarketing signalsの件数、`marketing_signal_count`と同値)。
呼び出し元は `src/enrichment/researcher.py`(`hot_status(len(signals))`、複数箇所)と
`src/scoring/research_scoring.py:555,569`。`signals` は `dedupe_signals()` で
`SIGNAL_NAMES`(同ファイル11行目)に含まれ`status=="CONFIRMED"`の項目だけに絞った結果。

**allowed values**: `"かなりアツい"`, `"アツい"`, `"集客投資シグナルあり"`, `"通常"`(4値、コード実測、他の値は存在しない)

**threshold**: `count>=3` → かなりアツい / `count==2` → アツい / `count==1` → 集客投資シグナルあり / それ以外(0) → 通常

**algorithm**: 純粋関数。`marketing_signal_count`のみを入力とし、外部状態・乱数・DB参照を持たない。

**version依存**: **なし(コード内に専用version定数は存在しない)**。`hp_rank_version`(`cfg["version"]`、
`research_scoring.py:547`)はHP rank計算専用のversionタグであり、`hot_status`の閾値ロジックとは無関係。
将来この閾値やSIGNAL_NAMESの構成が変わった場合の再現性を担保する専用versionは**コードに存在しない**
(推測で追加しない)。

**storage decision**: **DERIVABLE**。`marketing_signal_count`(または元のconfirmed signals一覧)さえ
保持していれば、`hot_status()`と同じ関数をいつでも再適用してcurrent値を再計算できる。Schema v1では
`clinic_ops.hp_research.features`にmachineの`marketing_signals`/`treatment_categories`等を
jsonbで保持済み(`docs/clinic-sqlite-to-postgres-mapping.md` 2節)のため、`hot_status`専用の物理列は
Schema v1に追加しない。VIEW(`clinic_ops.current_hp_rank`)へ追加する場合は、`features`から
signal件数を数え直す形になる。**version固定については、アプリ側に既存のversion定数がないため、
migration/importer実行時のClinic Lead repo git commit SHAを`model_version`または別途
`hot_status_algorithm_version`相当のタグとして記録することを推奨**(コードに存在しない値を
捏造しない代替案として)。

---

## # HP fetch status

**allowed values(コード確定、`research_results.result_json.research_status` → `hp_research.fetch_status`)**:

| 値 | 発生条件 | 発生箇所 |
|---|---|---|
| `SUCCESS` | HP本人確認に成功しcrawl完了 | `researcher.py:128`(`hp()`成功パス)、`researcher.py:213,225`(epark/media成功) |
| `REVIEW` | 候補ページはあるが本人確認未完了、またはaccess制限で内容解析未完了 | `researcher.py:175`(`reviews`が1件以上)、`researcher.py:167`(Maps確定URLがaccess制限で解析不能) |
| `ERROR` | 取得試行が失敗(`reviews`なし、`failures`あり) | `researcher.py:175`、`jobs.py:194`(未捕捉例外時のfallback) |
| `NOT_FOUND` | 候補ページも取得失敗もなし(検索結果ゼロ等) | `researcher.py:175`(`reviews`も`failures`もなし) |

**producer**: `src/enrichment/researcher.py` の `Researcher.hp()` メソッド(76-179行)。
`empty_hp_result(status, record)`(53-62行)が`research_status`と`hp_status`の両方に同じ`status`を
設定するが、成功パス(128行)だけは`hp_status="VERIFIED"`かつ`research_status="SUCCESS"`で**値が異なる**。

**machine event用statusとclinic current summary statusの違い(混同注意)**:

`clinics.hp_status`(current summary, `store.py:375`のenumsで確定)は
`{"VERIFIED","REVIEW","NOT_FOUND","ERROR","UNRESEARCHED"}`の5値。`UNRESEARCHED`は
「まだ一度も調査していない」ことを表す**初期値**であり、`research_results`行が存在する場合にしか
存在しない`research_status`(=`fetch_status`)には**現れない**(未調査の医院はそもそも
`research_results`行を持たないため)。逆に`research_status`の`SUCCESS`は`hp_status`には現れない
(`hp_status`側は同じ状況を`VERIFIED`と表現する)。

**readonly-audit実測との突合**: `docs/clinic-db-readonly-audit.md` 5節実測の`clinics.hp_status`分布
(`UNRESEARCHED=161,444, VERIFIED=643, REVIEW=146, ERROR=22, NOT_FOUND=3`)は`hp_status`(summary)の
分布であり、同節の`clinics.hp_rank`分布(`UNKNOWN=161,619, B=266, C=211, A=127, D=32, NO_HP=3`)とも
`research_status`(`fetch_status`)の分布とも**別の概念**である点に注意(3つとも異なるカラム)。
`research_results`は814行のみ存在するため、`fetch_status`の値はこの814行の範囲でのみ観測される
(今回はコード確認のみでSQLiteの再クエリは行っていない)。

**CHECK finalized**:

```sql
CONSTRAINT chk_hp_research_fetch_status
  CHECK (fetch_status IN ('SUCCESS', 'REVIEW', 'ERROR', 'NOT_FOUND'))
```

---

## # Jobs

### research_jobs.status

**producer/schema default**: `src/master/store.py:90` — `status TEXT NOT NULL DEFAULT 'PAUSED'`
(**新規job作成時点のデフォルトは`PAUSED`であり、`PENDING`ではない**)。

**allowed values(コード確定)**: `PAUSED`(default), `RUNNING`, `COMPLETED`, `RESET`, `BUDGET`

**producer箇所**:
- `PAUSED`: schema default(`store.py:90`)、`pause_job()`(`jobs.py:61`)、Stoppedによる一時停止(`jobs.py:188`)、
  クラッシュ後の`_run_locked`起動時recovery(`jobs.py:98`、実行中だったjobをPAUSEDへ戻す)
- `RUNNING`: `_run_locked`起動時(`jobs.py:99`)
- `COMPLETED`: 全item処理完了時(`jobs.py:113,126`)。`_run_locked`はjob.status=='COMPLETED'なら即return(終了済みjobは再開しない、94行)
- `RESET`: `reset_job()`(`jobs.py:73`)。`RUNNING`中のjobはreset不可(72行でValueError)
- `BUDGET`: `run_job`中に`BudgetReached`例外発生時(`jobs.py:188`)

**CHECK finalized**:

```sql
CONSTRAINT chk_research_jobs_status
  CHECK (status IN ('PAUSED', 'RUNNING', 'COMPLETED', 'RESET', 'BUDGET'))
CONSTRAINT chk_research_jobs_kind
  CHECK (kind IN ('hp', 'epark', 'media'))  -- jobs.py:22 `create_job()`のバリデーションと一致
```

### research_job_items.state

**producer/schema default**: `src/master/store.py:94` — `state TEXT NOT NULL DEFAULT 'PENDING'`

**allowed values(コード確定)**: `PENDING`(default), `RUNNING`, `DONE`, `CANCELLED`
(**`ERROR`/`SKIPPED`という状態は存在しない**。成否は`state='DONE'`のときの`result`列の値
(`research_status`と同じ語彙: `SUCCESS`/`REVIEW`/`ERROR`/`NOT_FOUND`、kindがepark/mediaの場合は
それぞれのvalues)で表現される。Schema v1の前回draftで仮置きしていた
`CHECK (state IN ('PENDING','RUNNING','DONE','CANCELLED','ERROR','SKIPPED'))`のように
`ERROR`/`SKIPPED`をstateへ混ぜるのは誤りであり、本文書で訂正する)

**producer箇所**:
- `PENDING`: schema default(`store.py:94`)、`create_job()`での一括INSERT(`jobs.py:38`)、
  クラッシュ後recovery(`jobs.py:97`、`RUNNING`だった行を`PENDING`へ戻す)、
  `BudgetReached`/`Stopped`発生時のrevert(`jobs.py:187`、そのitemは未完了のまま次回に持ち越す)
- `RUNNING`: 単一worker経路のclaim(`jobs.py:116`)、複数worker経路の条件付きclaim
  (`jobs.py:142`、`WHERE ... AND state='PENDING'`のUPDATE + `rowcount`で排他確認)
- `DONE`: `_research_one()`の最後(`jobs.py:202`)。成功・例外いずれの経路でも最終的に`DONE`になり、
  結果の詳細は`result`列(text)に記録される
- `CANCELLED`: 未処理のまま意図的に終了したterminal state。`reset_job()`が同一transaction内で
  `PENDING -> CANCELLED`とし、削除せずhistorical cancellation auditを保持する。workerのclaim条件は
  `state='PENDING'`のため再claim対象外。`DONE`（調査処理完了）とは区別する

### State transitions

| FROM | TO | trigger |
|---|---|---|
| (schema default) | `research_jobs.status = 'PAUSED'` | `create_job()`でjob行INSERT |
| (schema default) | `research_job_items.state = 'PENDING'` | `create_job()`でitem行一括INSERT |
| `PAUSED` / `RESET` / 他(`COMPLETED`以外) | `RUNNING`(job) | `run_job()`呼び出し(`_run_locked`開始時、事前にクラッシュ回復processingあり) |
| `RUNNING`(job、クラッシュ後残存) | `PAUSED`(job) | 新しい`_run_locked`開始時のrecovery(`jobs.py:98`) |
| `RUNNING`(item、クラッシュ後残存) | `PENDING`(item) | 新しい`_run_locked`開始時のrecovery(`jobs.py:97`) |
| `PENDING`(item) | `RUNNING`(item) | workerがclaim(単一/複数レーン、`jobs.py:116,142`) |
| `PENDING`(item) | `CANCELLED`(item) | `reset_job()`または明示的historical repair。未処理の意図的終了 |
| `RUNNING`(item) | `DONE`(item) | `_research_one()`が正常/例外いずれかで完了(`jobs.py:202`) |
| `RUNNING`(item) | `PENDING`(item) | `_research_one()`内で`BudgetReached`/`Stopped`発生(`jobs.py:187`、そのitemは未完了のまま保持) |
| `RUNNING`(job) | `COMPLETED`(job) | 全item完了(PENDING/RUNNINGが0件、`jobs.py:113,126`) |
| `RUNNING`(job) | `BUDGET`(job) | `_research_one()`中に`BudgetReached`(`jobs.py:188`) |
| `RUNNING`(job) | `PAUSED`(job) | `_research_one()`中に`Stopped`(`jobs.py:188`)、または`pause_job()`明示呼び出し(`jobs.py:61`、`COMPLETED`以外いつでも可) |
| `COMPLETED`以外 | `RESET`(job) | `reset_job()`明示呼び出し。`RUNNING`中は不可(ValueError、`jobs.py:72`) |
| `COMPLETED` | (変化なし) | `_run_locked`は`status=='COMPLETED'`なら即return(`jobs.py:94`、終了済みjobは再開しない) |
| `CANCELLED`(item) | (変化なし) | terminal。worker claim対象外 |

Cutover gateは`PENDING=0 AND RUNNING items=0 AND RUNNING jobs=0`。`CANCELLED`はterminalなので
`PENDING`/`RUNNING`として数えず、gateをblockしない。

**claim方式(現行実装)**: 単一プロセス内の複数スレッド(`ThreadPoolExecutor`、`PARALLEL_WORKERS=2`)が
`_WRITE_LOCK`(Pythonの`threading.Lock`)とSQLiteの`BEGIN IMMEDIATE`トランザクションを組み合わせて、
`UPDATE research_job_items SET state='RUNNING' WHERE ... AND state='PENDING'`の`rowcount`で
排他制御している(`jobs.py:140-143`)。複数プロセス/複数PC対応(PostgreSQL)ではこの単一プロセス内
lockの前提が崩れるため、`docs/clinic-db-review-resolution.md` 5節で設計した
`SELECT ... FOR UPDATE SKIP LOCKED`パターンへの置き換えが必要(現行コードのlock方式をそのまま
Postgresへ移植することはできない、要実装)。

---

## # Normalizer contract

| 生成列 | producer function | source file | input | 備考 |
|---|---|---|---|---|
| `name_norm` | `normalize_clinic_name(clinic_name)` | `src/normalizer/clinic_name.py:32` | `clinic_name`のみ | `loose`引数はfalseで呼ばれる(`store.py:210`) |
| `name_prefix` | `name_norm[:2]` | `src/master/store.py:227` | `name_norm`(上記の出力) | 独立関数ではなくstore.py内でのスライス |
| `phone_norm` | `normalize_phone(phone)` | `src/normalizer/phone.py:12` | `phone`のみ | 内線表記除去、数字のみ抽出 |
| `tel_match_key` | `tel_match_key(phone)` | `src/normalizer/phone.py:5` | `phone`のみ | 先頭0を1つだけ除去した統合専用key |
| `address_norm` | `normalize_address(address)` | `src/normalizer/address.py:18` | `address`のみ | 漢数字→算用数字、丁目/番地/号→ハイフン統一、casefold |

**producer呼び出し箇所(確定)**: `src/master/store.py:210,227`

```python
n, p, a = normalize_clinic_name(data.get("clinic_name")), normalize_phone(data.get("phone")), normalize_address(data.get("address"))
...
"phone_norm":p, "tel_match_key":tel_match_key(data.get("phone")), "name_norm":n, "name_prefix":n[:2], "address_norm":a, ...
```

**dependency**: いずれも`unicodedata`/`re`標準ライブラリのみに依存する純粋関数。DB・ネットワーク・
乱数への依存なし。`normalize_address`は`normalize_clinic_name`と同じ`VARIANTS`(旧字体正規化辞書、
`src/normalizer/clinic_name.py:4`)を共有する。

**deterministic性**: **完全にdeterministic**。同じ入力文字列に対し常に同じ出力を返す(条件分岐は
すべて入力文字列のパターンのみに依存し、外部状態や現在時刻等を参照しない)。

**version**: **コード内に専用version定数は存在しない**(hot_status同様)。将来これらの関数の
正規化ルールが変更された場合、過去に生成された`name_norm`等の値は新ルールと食い違う可能性がある。
`search_projection_version`には、この正規化ロジックを含むClinic Lead repoの**git commit SHA**
(移行/生成実行時点のもの)を記録することを推奨する。これによりコードに存在しないversion番号を
捏造せず、かつ再現性の追跡が可能になる。

**migration strategy(確定: 再生成 + 検証、COPYしない)**:

1. **決定: SQLiteに保存済みの`name_norm`/`phone_norm`/`address_norm`/`tel_match_key`/`name_prefix`
   の値はCOPYせず、Postgres移行時に同じ関数(`src.normalizer.*`、Clinic Lead既存コードをそのまま
   importerから呼び出す)で`clinic_name`/`phone`/`address`から**再生成**する。**理由**: これらは
   既に移行される`clinic_name`/`phone`/`address`だけから決定できる純粋関数であり、再生成する方が
   「2つの独立した値がドリフトする」リスクを避けられる。
2. **検証方法(162,258件全件)**: 移行時に各行について
   - `regenerated.name_norm == sqlite.name_norm`
   - `regenerated.name_prefix == sqlite.name_prefix`
   - `regenerated.phone_norm == sqlite.phone_norm`
   - `regenerated.tel_match_key == sqlite.tel_match_key`
   - `regenerated.address_norm == sqlite.address_norm`
   を比較し、**不一致行を全て列挙してREVIEWへ回す**(自動INSERTしない)。同じ関数・同じ入力であれば
   本来100%一致するはずであり、不一致が見つかった場合は「SQLite側の値が過去のnormalizerロジックで
   生成された後、元の`clinic_name`/`phone`/`address`だけが後から編集され、normalize列が
   再計算されずに残っている(drift)」等の実データ品質問題を検出したことになる。この検証は
   migrationのためだけでなく、legacy側のデータ品質チェックとしても有用。
   Supabase実データへのapplyは今回行わない。検証はstaging環境(`clinic_staging`)で実施する設計とする
   (`docs/clinic-db-migration-plan.md` STEP[3]〜[8]の枠組みに追加する)。

---

## # Remaining Unknowns(更新後)

| # | 項目 | 状態 |
|---|---|---|
| 1 | Supabase実際のDB role構成 | **未解消**(今回スコープ外、実環境確認が必要) |
| 2 | `postal_code` / `clinic_name_kana`の業務判断 | **未解消**(今回スコープ外、業務側判断が必要) |

上記2項目のみ残る。`docs/clinic-db-schema-v1.md`の旧Remaining Unknowns 1/2/3/6(hot_status /
fetch_status / job status・state / normalizer)は本文書で解消済み。

---

## Safety

Supabase DDL/DML: 0(全て0)。Production SQLite DDL/DML: 0(読み取りアクセスも今回は行っていない、
既存`docs/clinic-db-readonly-audit.md`の実測値のみ再利用)。Clinic Lead repo code変更: 0
(read-onlyでの検索・閲覧のみ、`git status`変更なし)。CRM `public` schema / Prisma migrations変更: 0。

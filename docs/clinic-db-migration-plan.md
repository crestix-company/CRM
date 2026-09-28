# Clinic Master 162,258件移行計画(DRAFT)

> ステータス: **設計のみ。まだ実行しない。Production SQLite / Supabase Productionへは一切適用していない。**
> 本計画は `docs/clinic-db-architecture.md` の schema設計を前提とする。
> Clinic Production SQLite (`~/CrestixData/clinic-lead/clinics.sqlite3`) には今回のセッションで一切アクセスしていない。
> 実カラム名等は「要確認」として残す。

対象件数: **162,258件**(ユーザー提供値)、`medical_key` 重複 **0件**(ユーザー提供値、ソース側で確認済み)。

---

## 移行パイプライン(11ステップ)

```
[1] SQLite backup
      ↓
[2] logical snapshot (時点固定エクスポート)
      ↓
[3] staging import (clinic_staging schema へ、production tableへは直接入れない)
      ↓
[4] medical_key duplicate check (staging上で再検証)
      ↓
[5] row count 照合 (162,258件)
      ↓
[6] prefecture count 照合
      ↓
[7] UUID count 照合 (legacy_uuid)
      ↓
[8] critical column比較 (source vs staging サンプル/チェックサム)
      ↓
[9] promotion (staging → clinic_master.clinics)
      SKIP / INSERT / REVIEW の3分岐
      ↓
[10] retry-safe / idempotent 実行(batch_idで再実行しても安全)
      ↓
[11] rollback手順(batch単位)
```

### [1] SQLite backup

- `clinics.sqlite3` の読み取り専用コピーを別ストレージに取得(実行はClinic Lead側の権限で行う。
  本セッションはこのファイルに触れていない)。
- バックアップにはタイムスタンプ + チェックサム(sha256)を付与し、どの時点のスナップショットかを追跡可能にする。

### [2] logical snapshot

- SQLiteから固定時点のデータをエクスポート(CSV/Parquet等、フォーマットはClinic側ツールに合わせる、要確認)。
- スナップショットファイルにも sha256 を記録し、[1]のバックアップとの対応関係を明示する。

### [3] staging import

- **本番 `clinic_master.clinics` に直接INSERTしない。** 必ず `clinic_staging.clinics_raw`
  (別スキーマ、production権限とは別ロールで書き込み)へロードする。
- staging importが壊れていても本番データには一切影響しない設計。

### [4] medical_key duplicate check(staging再検証)

```sql
SELECT medical_key, COUNT(*) AS cnt
FROM clinic_staging.clinics_raw
GROUP BY medical_key
HAVING COUNT(*) > 1;
```
ソース側で0件と確認済みでも、文字コード正規化(全角/半角、trim漏れ等)により見かけ上重複が生じる
ケースがあるため、staging投入後に**必ず再検証**する。

### [5] row count 照合

`SELECT COUNT(*) FROM clinic_staging.clinics_raw;` = 162,258 と一致するか確認。不一致ならこの時点で停止。

### [6] prefecture count 照合

ソース側の都道府県別件数集計とstaging側の集計を突合(`GROUP BY prefecture`)。値の表記揺れ(要確認: 
都道府県名 vs JISコード)もここで検出する。

### [7] UUID count 照合

`legacy_uuid` の非NULL件数・一意件数がソースと一致するか確認。フォーマット不正(NULL、空文字、
UUID形式でない値)を洗い出す。

### [8] critical column比較

`medical_key` をキーにした代表列(clinic_name, phone, address等)のサンプリング比較、または列単位の
チェックサム比較(`md5(coalesce(col,'') )` の集計値比較等)。CRM側で過去Excelインポート時に文字コード
(Shift-JIS等)関連の問題が扱われていた実績があるため(`iconv-lite` 依存、`LEGACY_EXCEL_IMPORT_ENABLED`等)、
**文字コード起因の文字化けは重点チェック項目とする**。

### [9] promotion(staging → production)

`medical_key` を基準に3分岐。**UUIDv7の生成責任は常にPython側**であり、DBは値を受け取るだけ
(`gen_random_uuid()` 等のDB側生成は使わない。STEP4 / `docs/clinic-uuid-strategy.md` 参照)。

| 分岐 | 条件 | アクション | UUIDv7発行 |
|---|---|---|---|
| SKIP | production に同一 `medical_key` が既に存在 | 何もしない(上書きしない) | **発行しない**(既存clinic_idをそのまま維持) |
| INSERT | production に存在しない新規 `medical_key` | `clinic_master.clinics` へ挿入。`imported_batch_id` に今回のbatch_idを記録 | Python側で新規UUIDv7を発行し、INSERT文に渡す |
| REVIEW | `medical_key` が欠落/不正、または重複キー内で内容が食い違う | production へはINSERTしない。`clinic_ops.import_log_items` にdecision='review'で記録 | UUIDv7を発行してよいが**productionへは絶対にINSERTしない**。発行だけして使われない"orphan ID"は無害(UUIDはグローバルな採番台帳を消費しないため、破棄しても後続処理に一切影響しない) |

`import_log_items.clinic_id`は、INSERTでは新規発行したID、SKIPでは既存医院のID、REVIEWではNULLを
記録する。rollback済みINSERTのIDだけは、医院行の削除時に`ON DELETE SET NULL`でNULLへ変わる。

**手順(Python側が主導、SQLはPythonから発行されるパラメータ化クエリの例)**:

1. Pythonが `clinic_staging.clinics_raw` から `medical_key` 単位で新規行(`clinic_master.clinics` に
   未存在)を抽出する(下記SELECTで判定用データを取得)。
2. 新規行1件ごとに Python側で `clinic_id = uuidv7()` を生成する(DBラウンドトリップなし)。
3. `clinic_id` を含めた明示的なVALUESでバルクINSERTする(`execute_values` / `COPY` 等、DB側ではUUIDを
   一切生成しない)。

Draft SQL例(`docs/clinic-db-sql-drafts/003_promotion_example.sql` に配置、Python側の疑似コード込み):

```sql
-- (a) 新規対象の抽出(Pythonがこれを実行し、結果行ごとにUUIDv7を生成する)
SELECT s.*
FROM clinic_staging.clinics_raw s
LEFT JOIN clinic_master.clinics c ON c.medical_key = s.medical_key
WHERE c.medical_key IS NULL          -- 新規のみ
  AND s.medical_key IS NOT NULL      -- 欠落除外(REVIEWへ)
  AND s.review_flag IS NOT TRUE;     -- 内容不整合フラグが立っていない

-- (b) Pythonがclinic_idを付与した上で明示VALUESでINSERT(例。実運用はexecute_values等でバッチ化)
INSERT INTO clinic_master.clinics
  (clinic_id, medical_key, legacy_uuid, clinic_name, prefecture, address, phone, website,
   source, imported_batch_id, created_at, updated_at)
VALUES
  (:clinic_id, :medical_key, :legacy_uuid, :clinic_name, :prefecture, :address, :phone, :website,
   'legacy_sqlite', :batch_id, now(), now());
```

**重要: UUIDv7のtimestampが表す意味**

INSERTされる `clinic_id`(UUIDv7)が内部に持つタイムスタンプは、**「Supabase移行時刻(=ID生成時刻)」を
表すのであって、医院の開業日や既存データの作成日を意味しない**。162,258件の移行はある特定の実行時刻に
集中して行われるため、これらのUUIDv7は互いに近い(あるいはミリ秒単位で同一の)タイムスタンプ帯に密集する。
これは想定通りの挙動であり、業務上の日時管理は常に `created_at` / `updated_at` を参照すること
(STEP4.3、および `docs/clinic-uuid-strategy.md` 参照)。

### [10] retry-safe / idempotent 実行

- promotion SQLは `batch_id` 単位で冪等になるよう設計する。同じ `batch_id` で再実行しても
  「既にINSERT済みのmedical_keyは対象外(上のLEFT JOIN条件で自然にスキップされる)」ため、
  途中失敗からの再実行が安全。
- 大量件数(162,258件)は一括1トランザクションではなく、**チャンク分割(例: 1,000〜5,000件単位)**で
  コミットし、失敗時に途中から再開できるようにする。

### [11] rollback手順(正式決定、前リビジョンから変更)

**方針転換**: 前リビジョンは「先に`import_log_items`をDELETEしてから`clinic_master.clinics`を
DELETEする」手順だったが、これは**rollbackのたびに監査履歴自体を消してしまう**問題があった。
正式には **`import_log_items` は一切DELETEしない**。

**hard DELETE rollbackの実行可能期間は、PRE-CUTOVERかつ対象医院について`hp_research` /
`hp_rank_feedback` / `maps_results`等のops業務データがまだ1行も生成されていない期間に限定する。**
この2条件を両方満たす場合のみ、`imported_batch_id`単位のhard rollbackを許可する。

POST-CUTOVER、またはPRE-CUTOVERでもops業務データ生成後はhard DELETE rollbackを禁止する。
通常のops FKは`ON DELETE RESTRICT`であり、参照中の医院DELETEはDBが拒否する。これを回避するために
ops履歴や監査履歴をDELETEして強制rollbackしてはならない。復旧には、previous SQLite backup、
DB backup / PITR、corrective migration、または`status` / deactivationを使用する。

- 対象は「当該batchで**新規にINSERTされた** `clinic_master.clinics` 行」のみ。
  ```sql
  DELETE FROM clinic_master.clinics WHERE imported_batch_id = :batch_id;
  ```
  `imported_batch_id` は promotion時のINSERTでのみセットされ、SKIP分岐(既存行)ではそもそも
  更新されない(`docs/clinic-db-architecture.md` STEP3参照の通り、既存行への書き込みは発生しない)ため、
  この条件は「今回新規追加した行だけ」に自然に絞り込まれる。**既存行(他batch・過去データ)は
  この条件に一致せず、絶対にDELETEされない**。
- `clinic_ops.import_log_items.clinic_id` は `ON DELETE SET NULL` のFKに変更済み
  (`docs/clinic-db-architecture.md` 3.5節)。したがって上記DELETEを実行すると、対応する
  `import_log_items` 行は**自動的に`clinic_id`だけがNULLになり、行自体は削除されない**。
  rollback後も `batch_id` / `medical_key` / `decision` / `reason` / `created_at` は保持される。
- `import_log_items.batch_id` は `clinic_ops.import_logs(batch_id)` への `ON DELETE RESTRICT` FKを
  持つため、`import_logs` 側のbatch行自体は(監査の起点として)恒久的に削除できない。
- rollback完了後、`clinic_ops.import_logs.status` を `'rolled_back'` へ更新できる設計にする
  (`status`カラムは元々 `'running' | 'completed' | 'failed' | 'rolled_back'` を許容、
  `docs/clinic-db-architecture.md` 3.4節)。**今回はこのUPDATEも実DBへは適用しない**。SQL例:
  ```sql
  -- 実行はしない。将来のrollback runbookとしての設計例。
  -- UPDATE clinic_ops.import_logs SET status = 'rolled_back', finished_at = now() WHERE batch_id = :batch_id;
  ```
- rollbackは自動実行にせず、事前にバックアップ([1])を確認したうえで手動実行する運用とする。
- staging (`clinic_staging`) は promotion 前段階のため、staging自体の破棄はいつでも無害に実行できる。

---

## STEP 9. 性能設計(index候補)

過剰indexを避ける方針のもと、**検索/filter用途が明示されている列のみ**を候補とする。

| テーブル | index | 目的 |
|---|---|---|
| `clinic_master.clinics` | UNIQUE (`medical_key`) | dedup / lookup(必須) |
| `clinic_master.clinics` | UNIQUE (`legacy_uuid`)(条件付き、STEP8検証後に確定) | 既存データとの突合 |
| `clinic_master.clinics` | btree (`prefecture`) | 都道府県別フィルタ(IS/FS/CS業務での絞り込み想定) |
| `clinic_ops.hp_research` | btree (`clinic_id`, `created_at` DESC) | append-only履歴から「医院ごとの最新machine行」をVIEW(`current_hp_rank`)が高速に取得するため(必須級) |
| `clinic_ops.hp_rank_feedback` | btree (`clinic_id`, `reviewed_at` DESC) | append-only履歴から「医院ごとの最新レビュー行」をVIEWが高速に取得するため(必須級) |
| `clinic_ops.maps_results` | btree (`clinic_id`) | JOIN用 |
| `clinic_ops.maps_results` | btree (`maps_status`) | 未調査/要再調査の抽出 |
| `clinic_ops.import_logs` | btree (`started_at`) | 直近batchの参照 |
| `clinic_ops.import_log_items` | btree (`batch_id`) | batch単位の監査照会 |
| `clinic_ops.import_log_items` | btree (`clinic_id`) | FK・突合用(NULL許容のためpartial可) |

**見送り候補(過剰indexとして除外、要件が明確になったら追加検討)**:
- `phone` / `website` への単独index — 現時点で完全一致検索の具体的なユースケースが未確認のため保留。

---

## Supabase変更ログ(このドキュメント作成時点)

DDL: 0 / INSERT: 0 / UPDATE: 0 / DELETE: 0 — Supabaseへは一切接続・変更していない。
SQLite (`clinics.sqlite3`) へのアクセス: 0。

# Clinic Identity: UUIDv7 生成戦略(正式確定・DRAFT)

> ステータス: **設計確定。実装・Supabaseへの適用はまだ行っていない。**
> Supabase (`xtspgevvntpidkmyfwes`) へのDDL/DMLは0件。Clinic Production SQLite
> (`~/CrestixData/clinic-lead/clinics.sqlite3`)・Clinic Lead側リポジトリへは一切アクセスしていない。

---

## 1. 適用範囲(重要な前提)

この戦略が対象とするのは **`clinic_master.clinics.clinic_id` のみ**。

`clinic_ops` 側の各テーブルが持つ行サロゲートキー(`hp_research.id` / `hp_rank_feedback.id` /
`maps_results.id` / `import_logs.batch_id` / `import_log_items.id`)は、医院の同一性を表す
Identity概念とは無関係の**単なる行識別子**であり、本ドキュメントのUUIDv7/Python生成ルールの対象外。
これらは引き続きDB側 `DEFAULT gen_random_uuid()`(UUIDv4)のままでよい
(`docs/clinic-db-sql-drafts/002_create_clinic_ops.sql` 参照)。

`clinic_id` が持つ意味(他カラムとの混同禁止)は `docs/clinic-db-architecture.md` STEP4.0を正とする:

| カラム | 役割 |
|---|---|
| `clinic_id` | システム内部PK。UUIDv7、Python生成。 |
| `medical_key` | 医院同一性/重複判定の正本。 |
| `legacy_uuid` | 既存システム(SQLite/Comdesk等)由来UUIDの保持のみ。 |

---

## 2. 正式決定事項

| 項目 | 決定 |
|---|---|
| UUIDバージョン | **UUIDv7**(RFC 9562) |
| 生成場所 | **Clinic Lead側 Pythonアプリケーション**(importer / application層) |
| DB側default | **使用しない**。`clinic_id uuid NOT NULL PRIMARY KEY` のみ、`DEFAULT gen_random_uuid()`等は排除 |
| UUIDv4混在 | **禁止**。`clinic_id` を生成する経路をPython側のUUIDv7実装1本に統一することで担保する |
| created_at/updated_at | UUIDv7のtimestampとは独立に、必ず別カラムで保持(3節参照) |

---

## 3. なぜDB defaultを使わないか

`gen_random_uuid()` はUUIDv4を返す(PostgreSQL 17時点でUUIDv7を直接生成する組み込み関数は存在しない)。
DB側でデフォルト生成を許すと、実装ミスや別経路からのINSERT(手動SQL、別ツール等)によって
UUIDv4が紛れ込む余地が生まれる。これを構造的に防ぐため、`clinic_id` は**常にアプリケーションが
明示的に値を渡す**設計とし、DB側は「型と`NOT NULL PRIMARY KEY`制約」だけを持つ。

副次的な利点(要件どおり):
- `clinic_id` がINSERT前に確定するため、同じ値をHP/Maps/Feedback等の関連テーブルへ
  DBラウンドトリップなしで渡せる。
- 複数PC/複数プロセス/Agentから並行してIDを生成しても、DB側の採番シーケンスに依存しないため
  衝突・競合が発生しない(4節で定量評価)。

---

## 4. Python実装方針

### 4.1 バージョン判定

Python 3.14 で標準ライブラリ `uuid` モジュールに `uuid.uuid7()` が追加された(RFC 9562準拠のUUID
バージョン6/7/8サポート)。**要確認: Clinic Lead側の実行環境が Python 3.14 以上かどうか**。
3.14未満の環境が混在する可能性があるため、以下の優先順位で実装する。

```python
import sys

def _select_uuid7_impl():
    if sys.version_info >= (3, 14):
        import uuid
        return uuid.uuid7          # 標準ライブラリ、追加依存なし
    else:
        import uuid6                # フォールバック(4.2節参照)
        return uuid6.uuid7
```

このように**呼び出し側は `clinic_id_gen.uuid7()` という単一のインターフェースだけを使う**構成にし、
Python 3.14への移行が完了したら内部実装だけ切り替わる(呼び出し側コードの変更不要)ようにする。

### 4.2 フォールバックライブラリ(Python < 3.14の場合)

Web検索で確認した現況(確認日: 本セッション実施時点):

| 項目 | 内容 |
|---|---|
| library名 | `uuid6`([PyPI](https://pypi.org/project/uuid6/) / [GitHub: oittaa/uuid6-python](https://github.com/oittaa/uuid6-python)) |
| 最新version | 2025.0.1(2025-07-04リリース、確認時点) |
| license | MIT |
| 対応Python | >= 3.9 |
| 依存 | なし(pure Python、追加の依存パッケージなし) |
| maintenance状況 | 週間ダウンロード数が多く(popular判定)、活発にメンテナンスされている実績を確認。ただし**採用時点で改めてPyPI/GitHubの最新状態を再確認すること**(本ドキュメントはこのセッション時点のスナップショット) |
| version固定方針 | `requirements.txt`/lockファイルで**厳密ピン留め**(例: `uuid6==2025.0.1`)。Python 3.14移行が完了次第、依存自体を削除する前提のため、更新は最小限にとどめる |
| fallback(依存追加そのものを避けたい場合) | 4.3節の自前実装(追加依存ゼロ)を採用する |

### 4.3 自前実装(依存ゼロ・最終fallback)

社内ポリシーで外部ライブラリの新規追加が難しい場合に備え、RFC 9562準拠の最小実装を示す
(乱数源は`os.urandom`、CSPRNG)。

```python
import os
import time
import uuid


def uuid7() -> uuid.UUID:
    """RFC 9562準拠のUUIDv7を生成する(追加依存なしの参照実装)。"""
    unix_ts_ms = time.time_ns() // 1_000_000
    rand = os.urandom(10)  # rand_a(12bit) + rand_b(62bit) = 74bit分の乱数源として16byte中10byteを使用

    b = bytearray(16)
    b[0:6] = unix_ts_ms.to_bytes(6, "big")
    b[6] = 0x70 | (rand[0] & 0x0F)          # version=7 (0111) + rand_aの上位4bit
    b[7] = rand[1]                          # rand_aの残り8bit
    b[8] = 0x80 | (rand[2] & 0x3F)          # variant=10 + rand_bの上位6bit
    b[9:16] = rand[3:10]                    # rand_bの残り56bit

    return uuid.UUID(bytes=bytes(b))
```

この実装は標準ライブラリ(`os`, `time`, `uuid`)のみに依存し、外部パッケージを一切追加しない。
`uuid.UUID` インスタンスを返すため、そのままPostgreSQLの `uuid` 型カラムへ格納可能(psycopg2/psycopg3/
asyncpg等は `uuid.UUID` を自動的にuuid型として扱う)。

---

## 5. 衝突耐性の定量評価(162,258件一括生成を想定)

RFC 9562 UUIDv7のビット構成(バージョン/バリアントの固定4bitを除く):
- `rand_a`: 12 bit
- `rand_b`: 62 bit
- 合計ランダムビット数: **74 bit**(単純ランダム方式。単調カウンタ方式(spec上のOption)は今回不採用、
  4.1/4.2/4.3のいずれの実装もCSPRNGによる純粋ランダムで74bit分のエントロピーを持つ)

**最悪ケース**(162,258件すべてが同一ミリ秒に生成されたと仮定。実際にはPython側の処理時間により
複数ミリ秒に分散するため、これは安全側に倒した上限評価):

誕生日近似式: `P ≈ n² / (2 × 2^74)`

- `n = 162,258` → `n² ≈ 2.633 × 10^10`
- `2 × 2^74 ≈ 3.778 × 10^22`
- `P ≈ 6.97 × 10^-13`

→ **実質ゼロ**(1兆分の1を大きく下回る)。同一ミリ秒に全件が集中する非現実的な最悪ケースでも
衝突確率は無視できる水準であり、複数PC・複数プロセス・複数Agentから並行生成しても安全と判断できる。

---

## 6. 順序性の意味(誤解しないこと)

UUIDv7は**「生成時刻に近い順」であり、厳密な連番・完全な時系列順ではない**。理由:
- 同一ミリ秒内で生成された複数UUIDの相対順序は `rand_a`/`rand_b` のランダム値次第であり、
  生成順と一致する保証はない(本実装は単調カウンタ方式を採用していないため)。
- 複数PC/プロセスから並行生成した場合、システムクロックのわずかなズレにより厳密な時系列が
  逆転する可能性がある。

したがって、UUIDv7は「だいたい時刻順に並ぶ(index局所性のため)」という性能特性のために採用するのであって、
**業務上の並び順・登録順の表示には使わない**。並び順が必要な場面は常に `created_at` を使う。

---

## 7. UUIDv7 timestampの意味(162,258件移行時の重要な注意)

移行時に新規生成される `clinic_id`(UUIDv7)のタイムスタンプ部分は、**「Supabase移行時刻
(= ID生成時刻)」を表すのであって、医院の開業日や元データの作成日を意味しない**。
162,258件は特定の実行ウィンドウに集中して生成されるため、これらのUUIDv7は互いに近い時刻帯に
密集することになるが、これは想定通りであり異常ではない。業務日時は常に `created_at` / `updated_at`
(および必要であれば元データ由来の日時カラムを別途保持)で管理する。

---

## 8. Import責任(SKIP / INSERT / REVIEW とUUID発行)

| 分岐 | UUIDv7発行 | 備考 |
|---|---|---|
| **既存 medical_key(SKIP)** | **発行しない** | 既存の`clinic_id`をそのまま維持。新規UUIDは無駄に消費しない |
| **新規 medical_key(INSERT)** | 発行し、そのままINSERT | 発行と使用が1対1で対応 |
| **ambiguous(REVIEW)** | 発行してもよいが**production(`clinic_master.clinics`)へは絶対にINSERTしない** | 人手判断後、確定すればINSERT/再分類。破棄されたUUIDは「orphan」になるが、UUIDはグローバルな採番台帳を消費しない値であるため、**使われなかったUUIDを気にする必要はない**(BIGINT IDENTITYの欠番と違い、後続の採番にも一切影響しない) |

監査は `clinic_ops.import_log_items`(`docs/clinic-db-architecture.md` 3.5節)に
`medical_key` / `clinic_id`(NULL許容) / `decision` として記録する。

---

## 9. テスト設計

Clinic Lead側リポジトリに実装する際のテスト設計ドラフトを `docs/clinic-uuid-tests/test_uuid7_strategy.py`
に用意した(このCRM repo内のdraftであり、Clinic Lead側リポジトリへは配置していない)。要件との対応:

| # | 要件 | テスト |
|---|---|---|
| 1 | UUIDv7が生成できる | `test_generates_uuid` |
| 2 | 生成値がUUIDとしてvalid | `test_is_valid_uuid` |
| 3 | version == 7 | `test_version_is_7` |
| 4 | 大量生成して重複0 | `test_bulk_generation_no_duplicates`(162,258件相当を生成し重複0を確認) |
| 5 | 連続生成時に概ね時間順 | `test_roughly_time_ordered`(厳密な連番ではないことを踏まえた緩やかな検証) |
| 6 | PostgreSQL uuid型へ格納可能な形式 | `test_postgres_uuid_format_compatible` |
| 7 | 既存medical_key時はUUIDを生成してINSERTしない | `test_existing_medical_key_skips_generation` |
| 8 | 新規medical_key時だけUUIDv7生成 | `test_new_medical_key_generates_once` |
| 9 | legacy_uuidは変更しない | `test_legacy_uuid_untouched_on_promotion` |
| 10 | FK不整合データが拒否される設計 | `test_fk_violation_rejected`(`clinic_master.clinics`に存在しない`clinic_id`を`clinic_ops`側へ挿入しようとするとFK違反になることを確認。実DBに繋がずSQL文字列/例外設計として検証、または将来ローカルPostgresでの結合テストとして実装) |

---

## 参考(このドキュメント作成にあたり参照した一次情報)

- [What's new in Python 3.14](https://docs.python.org/3/whatsnew/3.14.html) — `uuid.uuid7()` 標準ライブラリ追加の確認
- [uuid — Python 3.14 documentation](https://docs.python.org/3/library/uuid.html)
- [uuid6 · PyPI](https://pypi.org/project/uuid6/) — version / license / 依存関係の確認
- [GitHub: oittaa/uuid6-python](https://github.com/oittaa/uuid6-python) — license(MIT)の確認

---

## Supabase / Production SQLite 変更ログ

DDL: 0 / INSERT: 0 / UPDATE: 0 / DELETE: 0(Supabase)。SQLiteへのアクセス: 0。

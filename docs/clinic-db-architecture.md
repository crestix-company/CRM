# Clinic Lead × Supabase 共存アーキテクチャ設計(DRAFT)

> ステータス: **設計のみ。Supabaseへの適用は未実施。**
> DDL/DML は一切実行していない。本ドキュメントおよび `docs/clinic-db-sql-drafts/` のSQLはすべてlocal draftであり、
> `prisma/migrations/` には配置しない(Prismaの管理対象と混同させないため)。
>
> 対象Supabaseプロジェクト: `xtspgevvntpidkmyfwes`(CRM)
> 本ドキュメントはCRM repo (`~/Desktop/crestix-crm-audit`) 内で管理する。Clinic Lead側リポジトリ・
> Production SQLite (`~/CrestixData/clinic-lead/clinics.sqlite3`) には一切アクセスしていない。
>
> **UUID方針は正式確定(このリビジョンで反映)**。`clinic_id` は **UUIDv7 / Python(Clinic Lead側)生成 /
> DB defaultなし** に統一。詳細な生成実装・テスト設計は `docs/clinic-uuid-strategy.md` を参照。

---

## STEP 1. 既存CRM schema ownership(確定事項)

- `public` スキーマは **CRM / Prisma の専有管理領域**。
- `prisma/schema.prisma` は `datasource.url` のみを指定し、`directUrl` / `multiSchema` / `@@schema` を
  一切使用していない。→ Prismaは**`public` 単一スキーマしか認識しない**。
- `prisma/migrations/` 配下の21ディレクトリ(unique migration 21件、rolled-backによる `_prisma_migrations` の
  差分2件は確認済み・整合)が `public` の全79 model + `_prisma_migrations` 管理テーブル(合計80 table)を管理する。
- **ルール**: 将来にわたり、Clinic側のテーブル・スキーマを `prisma/schema.prisma` に追加しない。
  Prismaのmigrate diffエンジンはschema.prismaに書かれていないスキーマの存在を一切認識しないため、
  この制約を守る限り `prisma migrate dev` / `deploy` / `db push` はどれも `clinic_master` / `clinic_ops` に
  **構造的に触れることができない**。
- 逆に、CRM側の79テーブルもClinic側のmigrationツールから変更されないよう、STEP 5のロール分離で担保する。

---

## STEP 2. clinic_master 設計

### 2.1 目的

`clinic_master` は医院Masterデータの **Single Source of Truth (SSOT)**。将来CRM(`public`)・IS/FS/CS業務・
HP調査・Maps調査など複数システムから参照される中心テーブル群を保持する。

### 2.2 中心テーブル: `clinic_master.clinics`

既存SQLite (`clinics.sqlite3`) の実カラムは今回参照していない(Clinic Production DBに触れない制約のため)。
以下は今回のやり取りで明示された必須項目 + 一般的なMaster設計として妥当な項目のみを設計し、
**不明な項目はすべて「要確認」と明記する**。

```
clinic_master.clinics
------------------------------------------------------------------
column              type            null  default        note
------------------------------------------------------------------
clinic_id           uuid            NOT NULL PK           内部PK。**UUIDv7、Python(Clinic Lead側)で生成し
                                                            INSERT時に渡す。DB側の `DEFAULT gen_random_uuid()`
                                                            は使用しない**(UUIDv4混在防止)。STEP4参照。既存UUIDとは別物。
medical_key         text            NOT NULL UNIQUE       外部/業務キー。dedupの正本。
legacy_uuid         uuid            NULL     UNIQUE?       既存SQLite/Comdesk等の既存UUIDをそのまま保持
                                                            (要確認: SQLite側が本当にUUID形式か、他の識別子かは
                                                            repo/Production を見ていないため未確定)
clinic_name         text            NOT NULL
clinic_name_kana    text            NULL                  要確認(SQLiteに存在するか不明)
prefecture          text            NULL                  正規化方法は要確認(都道府県名 or JISコード)
address             text            NULL
postal_code         text            NULL                  要確認
phone               text            NULL
website             text            NULL
status              text            NULL                  要確認(廃業/休止等のフラグがSQLiteにあるか不明)
source               text           NOT NULL DEFAULT 'legacy_sqlite'
imported_batch_id   uuid            NULL                   STEP8のrollback設計で使用
created_at          timestamptz     NOT NULL DEFAULT now()
updated_at          timestamptz     NOT NULL DEFAULT now()
------------------------------------------------------------------
```

制約:
- `UNIQUE (medical_key)` — dedupの一次防衛線。
- `legacy_uuid` にUNIQUE制約を張るかは要確認(SQLite側でUUIDが本当に一意かソースを見ないと断定できないため、
  移行時のSTEP8バリデーションで実測してから確定する)。

未確定項目(要確認リスト):
- カナ名、診療科/カテゴリ、休診情報、郵便番号正規化、SQLite側の主キー型(INTEGER/TEXT/UUID)、
  既存UUIDが本当に「UUID型」として妥当な文字列か(SQLiteはtype affinityが緩いため文字列格納の可能性あり)。

---

## STEP 3. clinic_ops 設計

`clinic_ops` は運用系データ(HP調査・ランク付け・Maps調査・import履歴)を保持する。**正式決定: すべて
`clinic_master.clinics.clinic_id` への cross-schema FOREIGN KEY を張る**(前リビジョンでは「FKなし」を
暫定推奨していたが、今回の指示で正式にFK採用へ変更)。

対象(`ON DELETE RESTRICT`を基本とするテーブル):
- `clinic_ops.hp_research.clinic_id`
- `clinic_ops.hp_rank_feedback.clinic_id`
- `clinic_ops.maps_results.clinic_id`

例外(`ON DELETE SET NULL`。3.5節参照):
- `clinic_ops.import_log_items.clinic_id`

ON DELETE挙動: 上記3テーブルは **RESTRICT を基本とする**(NO ACTIONも許容範囲だが、即時に拒否され
RESTRICTのほうが意図が明確なため採用)。**CASCADE DELETEは禁止**。理由: `clinic_master.clinics` の
1行削除が `clinic_ops` 側の調査履歴・feedback履歴を連鎖的に消してしまうのは監査上望ましくない。
削除したい場合は、まず `clinic_ops` 側の関連行を明示的に処理してから行う運用とする。

`import_log_items` だけは例外的に `ON DELETE SET NULL` を採用する。理由は3.5節・rollback設計
(`docs/clinic-db-migration-plan.md` STEP[11])を参照。rollbackで `clinic_master.clinics` の
新規行を削除しても、`import_log_items` の監査行(`batch_id`/`medical_key`/`decision`/`reason`/
`created_at`)自体は消えず、`clinic_id`列だけがNULLになる。

migration順序への影響: `clinic_master` のテーブルが先に存在しないとFKを張れないため、
`clinic_ops` のmigrationは常に `clinic_master` のmigrationより後に適用する(SQL draftの
`001_create_clinic_master.sql` → `002_create_clinic_ops.sql` の順序は既にこれを満たす)。
`clinic_master` / `clinic_ops` は同じClinic側migrationツールが管理するため(STEP5)、この順序依存は
CRM Prisma側の独立性には影響しない。

### 3.1 `clinic_ops.hp_research`(machine側の調査・スコア履歴、append-only)

**正式決定(前リビジョンから変更)**: machine側の調査結果とランクスコアは、このテーブルに
**append-only(追記のみ、UPDATE/DELETEしない)**で蓄積する。1医院につき複数行(調査/採点の実行ごとに1行)。
`UNIQUE(clinic_id)` は設けない(元々設けていなかったが、ここで明示的に「append-onlyである」ことを確定する)。

```
id                  uuid         NOT NULL PK
clinic_id           uuid         NOT NULL   -- FK -> clinic_master.clinics(clinic_id) ON DELETE RESTRICT
url                 text         NULL
fetch_status        text         NOT NULL   -- e.g. 'pending' | 'ok' | 'error' | 'no_site'
fetched_at          timestamptz  NULL
content_ref         text         NULL       -- 本文/スナップショットの保存先参照(実体は別ストレージ想定)
error_detail        text         NULL
machine_rank        int          NULL       -- この調査/採点実行時点のmachineランク
machine_score       numeric      NULL
model_version       text         NULL
features            jsonb        NULL
created_at          timestamptz  NOT NULL DEFAULT now()
```

`updated_at` は持たない(append-onlyのため、行は作成後に変更されない前提)。「現在のmachineランク」は
常に「その医院に対する最新の`created_at`を持つ行」として3.2節末尾のVIEWから解決する。

### 3.2 `clinic_ops.hp_rank_feedback`(人間レビューのappend-only履歴)

**正式決定(前リビジョンから変更)**: 従来「1医院1行、machine再計算時にUPDATE」としていた設計を撤回し、
**人間レビューのappend-only履歴**に変更する。`UNIQUE(clinic_id)` は**削除**。レビューのたびに新しい行を
INSERTし、過去のレビュー行は**DELETE/UPDATEしない**(監査上の完全な履歴として保持)。

```
id                          uuid         NOT NULL PK
clinic_id                   uuid         NOT NULL   -- FK -> clinic_master.clinics(clinic_id) ON DELETE RESTRICT
manual_rank                 int          NOT NULL
reviewer                    text         NOT NULL
reason                      text         NULL
reviewed_at                 timestamptz  NOT NULL DEFAULT now()
machine_rank_at_review      int          NULL       -- レビュー時点でのmachineランクのスナップショット
machine_score_at_review     numeric      NULL
model_version_at_review     text         NULL
features_snapshot           jsonb        NULL
created_at                  timestamptz  NOT NULL DEFAULT now()
```

`machine_rank_at_review` 等は「レビュー実施時、hp_researchの最新行が何だったか」を固定して記録する
スナップショットであり、`hp_research` 側が後から新しい行を追加しても**このレビュー行は変化しない**
(不変の監査証跡)。`manual_rank`/`reviewer`/`reason`もINSERT後は不変。

**`manual_rank` 保護ルール(必須設計原則、append-only化により自動的に満たされる)**:

1. machine側の再計算は `clinic_ops.hp_research` への**INSERTのみ**で完結し、`hp_rank_feedback` の
   行には一切触れない。UPDATE文自体が存在しないため、「manual系カラムに触れないようUPDATE文を
   注意深く書く」という前リビジョンの運用ルールが**不要**になった(append-onlyであること自体が保護になる)。
2. `final_rank`(医院ごとの「今のランク」)はテーブルに固定保存せず、**VIEW/queryで解決する**
   (下記参照)。manualの最新行があれば `manual_rank`、なければ `hp_research` 側の最新 `machine_rank`。
3. 過去のレビュー履歴は削除・上書きしない。監査要件は自然に満たされる(履歴テーブルそのものが監査ログ)。

### 3.2.1 `final_rank` 解決VIEW(`clinic_ops.current_hp_rank`)

`docs/clinic-db-sql-drafts/004_current_hp_rank_view.sql` にdraftを配置。ロジック:

- 医院ごとに `hp_research` の最新行(`machine_rank IS NOT NULL` かつ `created_at` 最大)を取得。
- 医院ごとに `hp_rank_feedback` の最新行(`reviewed_at` 最大)を取得。
- `final_rank = COALESCE(最新manual_rank, 最新machine_rank)`。

machine側が新しい調査行を追加しても(=`hp_research`にINSERT)、`hp_rank_feedback`の過去レビューは
一切変更されないため、**machine再計算によって過去のmanual reviewが消える・上書きされることは構造上ない**。

### 3.3 `clinic_ops.maps_results`

```
clinic_id           uuid         NOT NULL
place_id            text         NULL
maps_status         text         NOT NULL   -- 'found' | 'not_found' | 'ambiguous' | 'error'
latitude            numeric      NULL
longitude           numeric      NULL
rating              numeric      NULL
review_count        int          NULL
fetched_at          timestamptz  NULL
created_at          timestamptz  NOT NULL DEFAULT now()
updated_at          timestamptz  NOT NULL DEFAULT now()
```

### 3.4 `clinic_ops.import_logs`

```
batch_id            uuid         NOT NULL PK
source_file         text         NOT NULL
started_at          timestamptz  NOT NULL DEFAULT now()
finished_at         timestamptz  NULL
status               text        NOT NULL   -- 'running' | 'completed' | 'failed' | 'rolled_back'
rows_total          int          NULL
rows_inserted       int          NULL
rows_skipped        int          NULL
rows_review         int          NULL
rows_error          int          NULL
error_detail        text         NULL
```

### 3.5 `clinic_ops.import_log_items`(新規、推奨追加)

SKIP / INSERT / REVIEW の**行単位監査**を残すためのテーブル。`clinic_ops.import_logs` はbatch集計のみのため、
個々の医院がどう判定されたかを追跡するにはこちらを使う。

```
id                  uuid         NOT NULL PK
batch_id            uuid         NOT NULL   -- FK -> clinic_ops.import_logs(batch_id) ON DELETE RESTRICT
medical_key         text         NOT NULL   -- 監査用スナップショット(下記「例外理由」参照)
clinic_id           uuid         NULL       -- INSERT確定行のみ非NULL。REVIEW/SKIP、rollback後はNULL
decision            text         NOT NULL   -- 'skip' | 'insert' | 'review'
reason              text         NULL
created_at          timestamptz  NOT NULL DEFAULT now()
```

**FK設計(正式決定、前リビジョンから変更)**:

- `batch_id` → `clinic_ops.import_logs(batch_id)` に `ON DELETE RESTRICT` のFKを新規に追加する。
  以前は「FKなし、値参照のみ」だったが、batch単位の監査完全性を担保するため正式にFK化する。
  `import_logs` 側の行を削除できないため、batch監査ログは恒久的に保持される。
- `clinic_id` → `clinic_master.clinics(clinic_id)` は `ON DELETE RESTRICT` から **`ON DELETE SET NULL`
  に変更**(他の`clinic_ops`テーブルとは異なる、意図的な例外)。

**なぜ`import_log_items`だけ`SET NULL`にするか(前リビジョンの`RESTRICT`から変更した理由)**:
`RESTRICT`のままだと、rollback時に「このbatchで新規INSERTされた`clinic_master.clinics`行」を
削除しようとした瞬間、その行を参照する`import_log_items`行がFK違反でDELETEをブロックしてしまう。
これを回避するために前リビジョンでは「先に`import_log_items`をDELETEしてから`clinic_master.clinics`を
DELETEする」手順にしていたが、それでは**rollbackのたびに監査履歴自体が消えてしまう**という問題があった。
`SET NULL`にすることで、`clinic_master.clinics`側の行を削除しても`import_log_items`側は
`batch_id`/`medical_key`/`decision`/`reason`/`created_at`を保持したまま`clinic_id`列だけが
自動的にNULLになり、**「どのmedical_keyが、いつ、どのbatchで、どう判定されたか」という監査事実は
rollback後も消えない**(`docs/clinic-db-migration-plan.md` STEP[11]参照)。

**medical_keyをこのテーブルにのみ例外的に重複保存する理由**:
`clinic_ops` の他テーブル(`hp_research`/`hp_rank_feedback`/`maps_results`)は `clinic_id` のみで参照し、
`medical_key` を重複保存しない方針を優先する(正本は`clinic_master.clinics`の1箇所に保つため)。
ただし本テーブルは import/audit 専用であり、REVIEW行のように `clinic_id` がまだ存在しない(=NULLの)
行についても「どの医院の判定だったか」を人間が追跡できる必要があるため、`medical_key` のスナップショットを
例外的に直接持つ。

---

## STEP 4. Identity設計(正式確定)

### 4.0 役割の明文化

| カラム | 役割 |
|---|---|
| `clinic_id` | **システム内部PK**。UUIDv7、Python(Clinic Lead側)生成。DB内での正規参照キー。 |
| `medical_key` | **医院同一性 / 重複判定**の正本。`TEXT NOT NULL UNIQUE`。dedup・再import時の判定基準。 |
| `legacy_uuid` | **既存システム(SQLite / Comdesk等)由来UUIDの保持**。データを失わないための保管のみが目的で、
内部参照キーとしては使わない。 |

この3つを**混同しない**ことが設計の大前提。`clinic_id` は「Postgres内でこの行をどう指すか」だけを表し、
医院としての同一性判定は常に `medical_key` で行う。`legacy_uuid` は移行元システムとの追跡可能性のためだけに存在し、
新規ロジックの主キーとして使わない。

### 4.1 medical_key

- `medical_key` は**業務上の一意キー**であり、dedup・再import時の判定基準。`UNIQUE` 制約を張る(DB制約として必須)。
- 移行/運用中に「同一medical_keyだが内容が食い違う」ケースが発生しうるため、`medical_key` 自体は
  変更不能な安定キーとして扱い、内容不一致はSTEP8の REVIEW フローで人手判断する。

### 4.2 内部PK: UUIDv7 採用(確定)

前リビジョンではUUID(v7想定) vs BIGINTの比較を提示していたが、**今回UUIDv7で正式確定**。

確定事項:
- 生成場所: **Clinic Lead側Pythonアプリケーション**(DB側では生成しない)
- DB定義: `clinic_id uuid NOT NULL PRIMARY KEY`(`DEFAULT gen_random_uuid()` は**使用しない**)
- UUIDv4は一切混在させない(生成経路をPython側のUUIDv7実装1つに統一することで担保。詳細は
  `docs/clinic-uuid-strategy.md`)

狙う性質(全て満たす設計):
- 生成時刻順に近い形で並ぶ(UUIDv7のtimestampビットによる)
- PostgreSQL btree indexと相性が良い(先頭48bitが時刻のため、ランダムなUUIDv4よりページ分割が少ない)
- 複数PC / batch / Agentから安全に生成できる(衝突確率は`docs/clinic-uuid-strategy.md`で定量的に検証)
- DB INSERT前に`clinic_id`が確定する(HP/Maps/Feedbackなど複数テーブルへ同じ`clinic_id`をラウンドトリップなしで渡せる)

**注意(画面表示・業務上の並び順について)**:
UUIDv7は「時刻に近い順」であって**厳密な連番ではない**。画面上の一覧表示や業務上の「登録日時順」ソートは
UUIDv7に依存せず、**必ず `created_at` カラムを使う**。理由は STEP見出し「created_at / updated_at」を参照。

**既存UUIDとの分離(重要・再掲)**:
`clinic_id`(新規UUIDv7・内部PK)と `legacy_uuid`(既存SQLite/Comdesk由来UUID)は**別カラム・別意味論**。
既存UUIDをそのまま内部PKに流用しない。理由:
- 既存UUIDの生成規則・一意性保証がSQLite側でどう運用されていたか未確認(要確認事項)。
- 内部PKの生成規則(UUIDv7)を新規に統一することで、将来の性能特性(局所性)をコントロールできる。
- 既存UUIDは「由来情報」として `legacy_uuid` に保持し、Clinic側の過去データとの突合・監査に使う。

### 4.3 created_at / updated_at(UUIDv7と混同しない)

UUIDv7が内部にミリ秒精度のタイムスタンプを持っていても、**業務上の日時管理は必ず `created_at` /
`updated_at` で別途行う**。理由:
- UUIDのtimestampは「ID生成時刻(=多くの場合は移行/import実行時刻)」であり、業務日時(開業日、
  元データの作成日等)とは無関係(STEP8参照)。
- import時刻と元データの日時が異なるケースがある。
- `created_at`/`updated_at` は人間にとって読みやすく、SQLでのfilter/sortが簡単。
- 将来の監査要件にはtimestamptz型の明示カラムが必須。

`created_at timestamptz NOT NULL DEFAULT now()`、`updated_at timestamptz NOT NULL DEFAULT now()`
(updateはアプリ側で明示的に更新する運用とする)。

---

## STEP 5. Migration ownership 設計

| スキーマ | 責任 | ツール |
|---|---|---|
| `public` | CRM repo | Prisma (`prisma/migrations/`) |
| `clinic_master` / `clinic_ops` | Clinic Lead側 | **専用SQL migration(別ツール)** |

### 5.1 ツール比較

| 方式 | Pros | Cons |
|---|---|---|
| CRM Prismaに同居させ `multiSchema` を有効化 | ツールを1つに統一できる | CRM repoとClinic repoの変更が同一migration履歴に混ざり、責任分界が壊れる。Clinic側はPython中心のためNode依存が増える。**非推奨** |
| Alembic(SQLAlchemy) | Python生態系と親和性が高い。Clinic Lead側がSQLAlchemyを使っているなら自然 | Clinic側のORM構成に依存(要確認) |
| 素のSQL migrationファイル + 軽量ランナー | 依存が最小、schema単位で完全に独立、レビューしやすい | ランナー自体を自作/選定する必要がある(`dbmate` 等の既製ツールで代替可) |

**推奨: 素のSQL migrationファイル(連番管理) + 専用トラッキングテーブル**。
Alembicが既にClinic Lead側で使われているなら、それを優先してよい(要確認、Clinic repoを見ていないため断定不可)。

### 5.2 独立性の担保(構造的な分離)

1. マイグレーション追跡テーブルをPrismaの `_prisma_migrations`(public所属)とは**別に**、
   `clinic_ops._clinic_schema_migrations` のようにClinic側スキーム内に置く。
2. Clinic側migrationツールの接続ロールには `public` への `CREATE`/`ALTER`/`DROP` 権限を一切付与しない
   (STEP11のロール分離)。
3. CRM Prisma側は前述の通り `multiSchema` を有効化しない限り、`clinic_master`/`clinic_ops` の存在を
   認識しないため、`prisma migrate deploy` / `prisma db push` の対象に**構造的に入らない**。
4. 将来もし誰かがCRMの `schema.prisma` に `multiSchema` やclinic系modelを追加しようとした場合、
   レビューで必ず差し戻す運用ルールをCLAUDE.md等に明記することを推奨。

### 5.3 UUIDv7生成責任の所在

UUIDv7の生成は **DB migrationの責務ではなく、Clinic Lead側のapplication/importerの責務**。
SQL migration側は `clinic_id uuid NOT NULL PRIMARY KEY` という「型と制約」だけを定義し、値の生成ロジックは
一切持たない(`DEFAULT gen_random_uuid()` を含め、DB側でUUIDを生成する仕組みを設けない)。
生成実装の詳細・ライブラリ選定・テスト設計は `docs/clinic-uuid-strategy.md` を参照。

---

## STEP 6. RLS設計(有効化はまだしない)

### 6.1 public(CRM)

- 現状: RLS disabled 80/80、policy 0件。
- CRMのDB接続はPrisma経由の単一ロール(Supabase標準の `postgres` / pooler用ロールで、通常 `BYPASSRLS` 属性を
  持つ)。→ RLSを有効化してもポリシー0件(deny-by-default)で**CRMの動作に機能的影響は出ない見込み**
  (ロールのBYPASSRLS属性は実地確認が必要、要確認)。
- 将来案: `public` にRLSを有効化 + ポリシー0件からスタートし、CRMが業務利用を再開する際に
  必要なポリシーだけ追加する。

### 6.2 clinic_master / clinic_ops

- 設計方針: **Supabase Data API(PostgREST/GraphQL)の "exposed schemas" に含めない**。
  これにより `anon` / `authenticated` ロール経由のHTTPアクセス経路自体が存在しなくなり、
  RLS以前の層で「ブラウザから直接アクセスできない」を担保できる。
- アクセスは常に **server-side(Python backend)からの直接Postgres接続**のみを前提とする。
  ブラウザ・フロントエンドからSupabaseクライアント経由でこれらschemaに触れる経路は作らない。
- RLSはexposeしていない間は必須ではないが、**多層防御として最初から有効化しておくことを推奨**
  (ポリシーはmigration/runtimeロール向けに許可、それ以外は拒否)。
- 将来、ダッシュボード等でブラウザから `authenticated` 経由のアクセスが必要になった場合のみ、
  「Data API expose + RLSポリシー追加」を**同時に**行う(exposeだけ先行させない)。

---

## STEP 7. Connection設計(Python / 複数PC運用)

| 方式 | 特徴 | 向いている用途 |
|---|---|---|
| Direct connection (5432) | フルPostgres機能(prepared statement、advisory lock、COPY等)。同時接続数上限が低い | migration実行、大量一括import(COPYベース) |
| Transaction pooler (Supavisor/pgbouncer transaction mode, 6543等) | 多数の短命接続を効率よく捌く。セッション状態(一時テーブル、SET、advisory lock)が引き継がれない | 複数PCからの通常read/write、HP research/Maps調査の書き込み |
| Session pooler | セッション状態を保持しつつ接続をプールする。同時接続数は直接接続に近い制約 | セッション状態が必要な処理だが直接接続を避けたい場合 |

**推奨**:
- **通常運用(複数PCからのread/write、HP research、rank feedback書き込み)**: Transaction pooler。
  ステートレスな短いクエリが中心のため、多数クライアントからの同時アクセスに強い。
- **162,258件の一括import(STEP8)・migration実行**: Direct connection。
  `COPY` を使った高速バルクロードや長時間トランザクションはtransaction pooler経由だと制約が出やすいため、
  信頼できる単一マシンから直接接続で実行する。
- Vercel環境変数は今回設定しない(前提どおり)。接続文字列の管理方法(secrets store等)はVercel移管確定後に設計する。

---

## Supabase変更ログ(このドキュメント作成時点)

DDL: 0 / INSERT: 0 / UPDATE: 0 / DELETE: 0 — Supabaseへは一切接続・変更していない。

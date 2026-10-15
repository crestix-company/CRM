# Requirements Tracking 更新案

## 結論

正式要件13文書とStage1で実際に取得した証跡だけを根拠に、`requirements_tracking.xlsx` のローカル更新案を作成した。原本は変更していない。正式要件との照合だけでは実装受入を証明できないため、Acceptance Criteria、未実査の外部連携、Target Architecture確定、実装工程は完了扱いにしていない。

## ファイルと完全性

| 項目 | 値 |
|---|---|
| 原本 | `.codex-input/requirements_tracking.xlsx` |
| ローカル更新案 | `.codex-input/output/requirements_tracking_stage1_proposed.xlsx` |
| 原本 SHA-256 | `023176572e030a4f9e8c553e0a92775182435743815e1ac85ae8e3163deb8b3a` |
| 更新案 SHA-256 | `5fe75475c3a26ed80ab0bb822ca6582a730adcaef072623fef2f4294991c8d87` |
| 更新日として記録 | 2026-10-15 |
| Google Drive原本 | 未更新 |
| Git | `.codex-input/` 配下のため未追跡・未コミット |

XLSX内部で変更したZIP entryは `xl/worksheets/sheet1.xml` のみである。`計画表` の対象セル106件だけに値変更があり、行数、列数、数式、スタイル、数値書式、既存日程、シート名・順序、freeze pane、merge、filter、data validation、他シートは変更していない。ExcelまたはGoogle Sheetsで開いた際の集計値は既存数式による再計算を前提とし、集計数式そのものやキャッシュ値を直接上書きしていない。

## 更新ルール

- `I列`: 実績ステータス。許可済み選択肢だけを使用
- `Q列`: Stage1で完了証跡を取得した行だけ確認日を設定
- `R列`: 監査文書またはREAD ONLY調査の証跡を記録
- `O/P列`: 既存日程・数式を変更しない
- 正式要件との照合のみで、実装、受入試験、運用承認を完了扱いにしない
- 外部サービスの本番権限・API実査がない項目は `確認待ち`
- Target Architectureの案作成と正式決定を分離する

## ステータス変更

### 完了へ更新

| 行 | ID | 更新前 | 更新後 | 根拠 |
|---:|---|---|---|---|
| 19 | CRM-DB-02 | 進行中 | 完了 | PR #13とproduction catalogのRelation/FK照合 |
| 20 | CRM-DB-03 | 進行中 | 完了 | Index/Unique/idempotency/deletedAt/Audit/RLS/grant棚卸し |
| 21 | CRM-DB-04 | 未着手 | 完了 | Open PRのSchema/Migration/依存差分 |
| 22 | CRM-DB-05 | 確認待ち | 完了 | Production READ ONLY counts/duplicate/FK/orphan検査 |
| 23 | CRM-UI-01 | 進行中 | 完了 | 53 page route sourceと用途の一覧化 |
| 24 | CRM-UI-02 | 未着手 | 完了 | IS/FS/CS dashboardと不足画面の整理 |
| 25 | CRM-UI-03 | 未着手 | 完了 | 主要CRUD fieldの整理 |
| 27 | CRM-AUTH-01 | 進行中 | 完了 | Session/OrganizationRole/BU read rule/permission catalog |
| 28 | CRM-AUTH-02 | 未着手 | 完了 | Audit明示記録とcoverage gap |
| 31 | CRM-INT-03 | 未着手 | 完了 | Email/Conversation/Notification/Reminderの構造棚卸し |
| 32 | CRM-INT-04 | 未着手 | 完了 | Import/export/legacy dry-run経路 |
| 36–41 | GAP-01–06 | 未着手 | 完了 | 病院・案件・カルテ・Task・Meeting・商品/契約差分 |
| 43–48 | GAP-08–13 | 未着手 | 完了 | KPI・Knowledge・権限・通知・CS・全体分類 |
| 97 | REQ-10 | 未着手 | 完了 | 技術裁量と要承認事項の分離 |

行11–18および29は既存の `完了` を維持し、正式文書または調査証跡をQ/R列に追記した。

### 完了にしなかった更新

| 行 | ID | 更新前 | 更新後 | 残件 |
|---:|---|---|---|---|
| 26 | CRM-UI-04 | 未着手 | 確認待ち | 実機mobile/viewport/自然言語検索E2E |
| 30 | CRM-INT-02 | 未着手 | 確認待ち | Google Workspace実環境API/権限 |
| 33 | CRM-INT-05 | 未着手 | 確認待ち | CloudSign/Comdesk/決済/Bolt実環境API |
| 42 | GAP-07 | 未着手 | 進行中 | `crestix-cf`/Bolt実査とauthority確定 |
| 98 | ARCH-01 | 未着手 | 確認待ち | Target Architectureのowner review/正式確定 |
| 99 | ARCH-02 | 未着手 | 進行中 | Clinic Lead→CRM cutoverとID方針の承認 |
| 100 | ARCH-03 | 未着手 | 進行中 | 正式ERDとMigration review |
| 147 | PROD-07 | 未着手 | 進行中 | browser/API/AI jobの実測 |

## 集計差分

| 指標 | 更新前 | 更新案 |
|---|---:|---:|
| 完了 | 9 | 33 |
| 進行中 | 4 | 4 |
| 確認待ち | 3 | 6 |
| 未着手 | 128 | 101 |
| 計画表全体（既存数式による理論値） | 9.31% | 27.64% |
| 要件整理 | 70.00% | 80.00% |
| 現行CRM把握 | 35.56% | 94.44% |
| GAP判定 | 0.00% | 89.29% |
| Target Architecture | 0.00% | 22.50% |
| Production Maturity | 0.00% | 4.55% |

実装フェーズ（P1〜P4）はすべて0%のまま変更していない。正式要件09のAC/S/R/F/AI/MM/TMは要件との紐付けまでを証跡化したが、実装・E2E・業務受入がないため受入完了にはしていない。

## 残件

- 画面のruntime/browser確認とmobile実機確認
- Google Workspace、CloudSign、Comdesk、決済、Boltの実環境権限/API確認
- `crestix-cf`を含む会計SOTと責任境界の確定
- Clinic Lead SystemからCRMへの段階的authority移管、cutover、rollback設計
- 第一営業部の本番Organization/User/BusinessUnit identity確定
- 質問表の未回答事項（情報分類、Trash後の保持期間）
- Target Architecture、正式ERD、Migration計画のowner承認
- 正式Acceptance Criteriaに基づく実装後E2E・業務受入

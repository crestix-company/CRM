# Stage1 完了承認に必要な未解決事項

## 判定

Stage1のREAD ONLY調査・要件照合・設計準備の成果はレビュー可能な状態にある。一方、Stage1の正式完了承認は**保留**とする。これは調査資料の作成完了と、正式要件の機能受入・本番是正の完了を区別するためである。特にP0のData API露出、組織対応、分類レビュー、Clinic Lead SystemとのSOT境界が未決である。

この文書は`official_00.docx`〜`official_12.docx`を規範とし、Stage1成果物17件（00〜15とREADME）を2026-10-16時点で再照合した承認票である。DB値は2026-10-15前後のREAD ONLY観測であり、現在値の保証ではない。

## 成果物17件の最終照合

「確認済み」は調査成果の存在・出典追跡を確認した意味であり、正式要件の機能受入完了を意味しない。

| 成果物 | 照合結果 | 未解決 / 承認ゲート |
|---|---|---|
| `00_scope_and_sources.md` | 要件00・調査制約と整合 | Stage完了の意味を「調査完了」に限定。Vercel/UI等のUNVERIFIEDは維持 |
| `01_runtime_and_deployment_inventory.md` | repo/runtime棚卸しを記録 | 本番SHA、環境変数存在、Vercel team設定は権限待ち。値/秘密は成果物へ出さない |
| `02_crm_ui_api_inventory.md` | 既存機能保持・tenant境界と整合 | 実機モバイル/検索E2E、外部API実接続は未確認 |
| `03_db_schema_relations.md` | DB構造・Relation/FKを記録 | loose referenceは個別設計を要する。DB調査値は観測時点 |
| `04_data_quality_counts.md` | 調査時点の件数・候補分類を記録 | Deal未知件数の範囲差を再集計して訂正するまで確定値にしない |
| `05_security_grants_rls.md` | P0所見を記録。即時本番変更禁止は妥当 | RLS 0/80、anon/auth広範GRANTの影響実証とPreview試験が未完了。`17_preview_rls_grant_data_api_test_design.md`参照 |
| `06_first_sales_department_mapping.md` | 候補ID・根拠・運用影響を記録 | Crestix第一事業部への対応はINFERRED。名称/権限/membershipの確定は縞谷・業務責任者承認待ち |
| `07_restaurant_cleanup_candidates.md` | PIIを避けた候補一覧と依存集計 | 235 Company / 375 active Dealは全件HUMAN_REVIEW。削除承認ではない |
| `08_data_cleanup_dry_run_plan.md` | 復旧・履歴保全・Dry-run順と整合 | retention/Trash/法務確認および二者レビュー待ち。apply禁止 |
| `09_requirements_traceability_matrix.md` | 正式要件の実装差分を整理 | 「一致」は調査状態の一致に限り、受入完了へ読み替えない |
| `10_target_architecture_delta.md` | KEEP/EXTEND/LINK/NEW等を整理 | Clinic連携方向、責務、migration境界は本票のSOT判断まで案 |
| `11_performance_baseline_and_slo.md` | 測定できた局所baselineを記録 | SLO閾値を代表者が承認しBrowser/E2E確認するまで受入未確認 |
| `12_risks_decisions_release_gates.md` | Blockerと決定者を分離 | 本書の上位P0/P1決定が未完。Stage2 DoR未達 |
| `13_open_pr_inventory_and_merge_plan.md` | PR #1〜#18をREAD ONLY評価 | 推奨分類は提案。PR操作なし。#18 Draft維持。check状態は再取得時に変化し得る |
| `14_official_requirements_conformance.md` | Official 00〜12全文との照合を記録 | Stage1証跡と機能受入を区分。原本は未変更 |
| `15_requirements_tracking_update_proposal.md` | 計画表ローカル提案との差分を記録 | Drive原本未更新。完了表示は確認済み実績だけ |
| `README.md` | 読み順・主要事実・残件を集約 | 本票とPreview設計書のリンク追記後、数値・用語を再照合 |

### 正式要件との照合結論

- **一致（調査方法/方針）**: 既存CRM資産をKEEPし、破壊的変更を避け、Human Gate・監査・Dry-run・既存ID保持を前提にした点。
- **不一致/是正設計が必要**: 80/80 public base tablesでRLS無効、anon/authが広範な権限を持つ観測。tenant isolationをDB/Data APIで実証できていない。
- **不足**: Clinic/Hospitalの正本連携、Hospital hierarchy、Contract/Billing、Meeting/Minutes、AI Artifact/Human Gate、Retention等の実装/受入。
- **未確認**: 第一営業部のID対応、分類精度、人手レビュー、実機・外部API、本番環境設定とSHA、Calendarの実OAuth切替。

Stage1は**監査資料の作成完了**、**Stage2着手承認は条件付き保留**。正式機能要件の完了は主張しない。

## 1. 第一営業部とDB組織の候補

| 候補 | Organization ID | BusinessUnit ID | 観測根拠 | 評価 |
|---|---|---|---|---|
| Crestix「第一事業部」 | `88cc2f88-64ac-40d8-94eb-9f402412f9cd` | `8036a665-d413-4857-81cd-a5ad041d0309` | Crestix内で最も近い名称。504 active / 448 deleted Deal。医療候補246、飲食0、不明258。 | **第一候補・INFERRED**。正式対応ではない。active BusinessUnitMembership 0件という運用矛盾 |
| サンプル組織「第1事業部」 | `588bd30f-5f05-4cfa-9f7f-118a8a8c0a11` | `312fe4c1-c4c4-41cd-bb12-46dadeb208d4` | 表記は近いが別Organization。15 active Deals。 | 別組織。Crestix運用に流用しない。テスト/調査データか確認 |
| サンプル組織「営業チーム」 | 同上 | Team IDはStage1根拠資料に未記録 | Teamはサンプル組織に1件のみ。CrestixにTeamなし。 | ID候補として使えない。IDはUNVERIFIED |

「第一営業部」という完全一致のCrestix BusinessUnit/Teamは未確認。Crestix HD事業部（`5beaaff8-d556-4053-81bd-65585d1218b1`）は飲食候補active Deal 375件が集中するため第一営業部候補ではない。

**影響範囲**: CRM UI絞り込み・初期値、Deal/Company attribution、active member閲覧、Clinic Lead連携owner/team、KPI/売上集計、移行対象抽出。IDや所属の一括変更は過去実績・監査・通知を壊すおそれがあるため不可。

**承認質問（縞谷/業務責任者）**: 「第一営業部」はCrestix第一事業部と同じか。選択肢: (A) 同じと認定し名称維持、(B) 別組織としてOrgNode/BusinessUnitを新設、(C) 既存組織を別名へ改称。推奨は業務実態確認後に(A)、別階層が必要と確認された場合のみ(B)。Membership 0件が意図的か、対象メンバー・有効日も確認する。

## 2. 医療・飲食・不明分類と人手確認

| Entity / observed scope | 医療候補 | 飲食候補 | 不明/その他 | 人手レビュー対象 / 解釈 |
|---|---:|---:|---:|---|
| Crestix active Company（分類母数1,405） | 246 | 235 | 924 | 235飲食候補は全件確認。不明924件もClinic-first対象判定のため仕分け要 |
| 第一事業部 active Deal（504） | 246 | 0 | 258 | 258不明の分類要。医療候補246件も実態を確認 |
| HD事業部 active Deal（1,595） | 33 | 375 | 1,187 | 375飲食候補は全件確認。不明1,187件を仕分け |
| cleanup候補 Company | — | 235 | — | 全235件がHUMAN_REVIEW。関連履歴・依存を確認するまで整理対象にしない |
| cleanup候補 active Deal | — | 375 | — | 全375件がHUMAN_REVIEW。WON 80、金額情報付きLineItem 145、Participant 997等の実績を保護 |

分類精度（precision/recall）は**未測定**。強いキーワード規則は候補抽出で、真値の人手ラベル・誤検出率・見落とし率がない。mixed 0は混在なしの証明ではない。Company分類母数1,405件と全体active Company 1,413件との差8件も母集団定義を再照合する。

Deal分類表の2 BusinessUnit合計は2,099件で、active Deal総数2,129との差30件が未解決。記載上の不明は2 unit合計1,445件（258+1,187）。既存資料の「1,460件超」は表から再現できないため、1,445/1,460超いずれも全体確定値にしない。他Unit/NULL/除外条件をREAD ONLYで再集計する。

**明示的なcleanup人手レビュー最低数**はCompany 235 + active Deal 375 = **610 entity records**。一意顧客数ではない。Clinic-firstの仕分けを含める場合、医療候補279 + 飲食候補610 + 不明Company 924 + 2 unit内不明Deal 1,445 = 最大2,648 entity recordsというスコープ見積りになるが、範囲差・重複未照合のため確定件数ではない。まず正解ラベル付きsampleで規則を校正し、その後の全件二者レビュー対象を代表者が決める。WON/金額/監査/履歴/外部ID依存は人手確認必須、KEEPを既定とする。

## 3. Clinic Lead System / CRM のSoT・ID・連携案

正式要件02の「医院/法人/担当者はCRMが正本」を維持する。Clinic Lead Systemの既存稼働を即時停止したり、そのDBをCRMへ無承認複製する意味ではない。二重書込み・恒久dual-SOTは採らない。

| 選択肢 | 仕組み | 整合性 / リスク | 判断 |
|---|---|---|---|
| A. CRM最終SoT、Clinic Leadは期限付き移行source/bridge | 初期は承認済みone-wayのClinic Lead→CRM提案/取込。CRMで人が承認した値を正とする。cutover後は必要最小限をCRM→Clinic Leadへread-only投影 | 要件整合。field authority、競合処理、期限を定めないと一時的二重正本が続く | **推奨**。縞谷がauthority/cutover、前川が同期方式を設計 |
| B. 即時CRM一本化 | 照合・承認・移行後にClinic Lead write pathを段階停止 | 最終像は明快だが、品質/受入/権限/rollback不明のままの切替は欠落・停止リスク | 現状は非推奨。選ぶ場合も段階移行DoR必須 |
| C. Clinic Lead恒久SoT、CRMは参照先 | Clinic Leadで変更してCRMへ同期 | 正式要件02に不一致 | 不採用。正式要件変更は縞谷承認が必要で、Stage1では要件変更しない |

**ID方針案**: CRM既存Company/Deal/Contact UUIDとClinic Leadのclinic UUIDをそれぞれ保持し、再採番・同一視しない。Clinic UUID → CRM Company/HospitalProfile UUIDを明示linkする。法人と医院が別recordなら別々にlinkする。Link案は`source_system`, `source_id`, `target_type`, `target_id`, `mapping_status`, `confidence`, `valid_from/to`, `last_seen_at`, `approved_by`, `source_version`を保持し、external ID unique scope、merge/unlink履歴、provenanceを設計する。domain/name/address等による自動統合は禁止し、候補提示＋人の承認と監査を要する。内部実装方式は前川、業務上の同一性・正本は縞谷の判断。

**承認質問（縞谷）**: A/Bどちらのcutoverを選ぶか、項目別編集正本、CRM承認前のデータ扱い、二重書込みを止める時点、rollback条件は何か。推奨は期限・終了条件を付けたA。

## 4. Stage2 Definition of Ready

以下すべてを満たす前にStage2本番実装へ進まない。isolated Previewでの設計・検証コードも対象環境の別承認が必要。

| Gate | 成立条件 | Owner |
|---|---|---|
| Formal scope | Official 00〜12の範囲・順序・DoDへ合意。未回答を仮決めせず保留を明記 | 縞谷 |
| P0 DB security | Data API利用者、runtime DB role/BYPASSRLS、schema exposure、GRANT確認。Previewでanon/auth/tenant越境negative tests・rollback・smoke成功 | 前川（設計/証跡）、縞谷（risk/release） |
| Organization mapping | 「第一営業部」対応先、対象member、データ範囲、変更可否の決裁記録 | 縞谷/第一営業部責任者 |
| Classification | 対象母数、rule version、精度サンプル、人手review owner、mixed/unknown/WON/金銭履歴の扱い合意 | 縞谷/データ責任者 |
| SoT/link | CRM最終SoT、Clinic Leadの項目別authority、ID link、同期方向、重複処理、rollback/cutover承認 | 縞谷（業務）、前川（技術） |
| Data lifecycle | 情報区分、30日Trash後、法務/財務/audit retention、restore policy回答済み | 縞谷 |
| Acceptance | Official AC、tenant isolation、Human Gate、監査、性能/mobile/E2E閾値・証跡owner明記 | 縞谷（業務AC）、前川（試験） |
| Delivery | Preview DB/credentials owner、masked/synthetic fixture、migration review/rollback、CI、staged rollout承認 | 前川。production gateは縞谷 |
| Integrations | Calendar v1保護、Vercel deployment/secret owner、外部API権限/fallback確認 | 縞谷（接続変更）、前川（技術） |
| Audit trail | 承認者・決定日・対象要件・例外・残リスクの記録場所確定 | 縞谷/前川 |

### 承認責務

**縞谷（業務・経営判断）**: Stage1正式完了/既知制約受容、第一営業部対応、組織名/階層/member、医療/飲食分類と保持、Clinic Lead/CRM項目別SoT/cutover、Clinic IDと顧客の同一性、権限role/例外、Human Gate/承認者/SLA、契約・WON/Yomi・財務定義、情報区分/外部公開/Retention、Stage2優先順位/受入基準、本番release/rollback可否。

**前川（正式要件の意味を変えない技術判断）**: Link実装、内部UUID生成、schema/API/service境界、index/queue/cache、migration構成/可逆性、Preview test/CI/監視、性能計測、実装分割/依存順。tenant isolation、監査性、既存ID保持、正式業務定義は裁量で変更しない。

## 優先承認質問

| 優先 | 質問 | 選択肢 | 推奨案 | 判断が必要な理由 |
|---|---|---|---|---|
| P0 | anon/auth Data API露出の対応方針は | Previewで段階修正 / Data API停止可能性を検証 / production即時変更 | production変更は実証・決裁まで保留し、速やかに責任者へリスク共有。Preview試験を最優先 | 全80 public表RLS無効・広範GRANT観測。無計画REVOKE/RLSはruntime停止し得る |
| P1 | 第一営業部はどのUnitか | Crestix第一事業部 / 新規階層 / 別Unit・名称 | 既存第一事業部を第一候補に業務実態を確認してから認定 | 名前・医療候補分布は状況証拠だがmembership 0で証明されない |
| P1 | Clinic正本とcutoverは | CRM最終SoT＋期限付きbridge / 即時CRM一本化 / Clinic Lead恒久正本 | 期限/終了条件付きの期限付きbridge | official_02はCRMを正本とする一方、Clinic Leadは独立稼働 |
| P1 | 分類をどこまで人が見るか | cleanup候補610のみ / unknown全件 / Clinic-first層を段階 | precision sample後に医療候補と飲食/履歴依存を二者確認、unknownを段階化 | 候補精度・母数差が不明で自動cleanup危険 |
| P1 | 30日Trash後の保持/情報区分は | 現行案 / 延長 / 種別別retention | 法務/業務責任者が契約・財務・医療関連区分ごとに決裁 | 未回答を技術者が補完できず、復元/監査/規制影響がある |
| P1 | Stage2最初のsliceは | Security/RLS / Clinic link / Sales Yomi/Meeting | P0 security proof後にClinic linkのread-only vertical slice | tenant境界を先にし、二重正本を避けつつ利用価値を検証 |

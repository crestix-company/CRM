# Official Requirements Conformance

## Authority and classification

`official_00.docx`〜`official_12.docx`を2026-10-15に全文確認した。業務目的、Source of Truth、Human Gate、正式受注、Yomi、権限、監査、Phase順序はこの13文書を一次資料とする。`Crestix_AI_OS_requirements.md`は作業指示・追加運用制約、`requirements_tracking.xlsx`は計画管理資料であり、正式要件と矛盾する場合は正式文書を優先する。

| Class | Meaning |
|---|---|
| 一致 | 現行実装またはStage1判断が正式要件と矛盾せず、根拠を確認できた |
| 不一致 | 現行状態または初回監査判断が正式要件と衝突する |
| 不足 | 再利用可能な基盤はあるが、正式要件を満たす機能・データ・試験がない |
| 未確認 | 外部環境、業務owner判断、実機/E2E等がなく判定できない |

「一致」はStage1の調査結果に対する判定で、対象機能の実装・受入・本番検証完了を意味しない。

## Source register

| Source | Formal role | SHA-256 prefix | Read status |
|---|---|---|---|
| official_00 | 読む順番、変更統制、実装原則 | `ff4e41ed85a6` | VERIFIED |
| official_01 | 最上位要件、判断基準、Phase、DoD | `a33a810cc38e` | VERIFIED |
| official_02 | 構成、SOT、既存/新規データモデル | `75d0a71a36ea` | VERIFIED |
| official_03 | 画面、UX、Hospital Chart、Meeting/Task UI | `80403c5751e2` | VERIFIED |
| official_04 | AI Agent、入出力、Human Gate、禁止事項 | `15b61535bdf8` | VERIFIED |
| official_05 | Event、承認、通知、配布 | `42ad82928895` | VERIFIED |
| official_06 | 外部連携、移行、Retention | `6b3844454089` | VERIFIED |
| official_07 | Phase1 backlog、実装順、Definition of Ready | `ffffe769fd6b` | VERIFIED |
| official_08 | Phase2〜4 roadmap、release flow | `140b6a498338` | VERIFIED |
| official_09 | AC/S/R/F/AI/MM/TM受入条件 | `5523b63de263` | VERIFIED |
| official_10 | 技術確認、技術裁量、縞谷承認事項 | `6ef32a9c43e6` | VERIFIED |
| official_11 | 参照資料と旧運用の扱い | `15b42d4802f5` | VERIFIED |
| official_12 | Minutes/Task詳細仕様 | `be426eaf4117` | VERIFIED |

原本は`.codex-input/`から読み取り、Gitへ追加していない。

## Formal requirement vs current CRM

| Requirement family | Formal requirement | Current evidence | Class | Stage2 implication |
|---|---|---|---|---|
| Existing asset reuse | CRMを捨てずCompany/Contact/Deal/Calendar/KPI/Task/Delivery等を再利用 | 79 Prisma models、主要UI/APIあり | 一致 | additive extensionを維持 |
| Customer SOT | 医院・法人・担当者はCRMが正本 | Clinic Leadは別Supabaseで稼働しCRMとのauthority/cutover未定 | 不一致 | Clinic Leadは移行中の供給元/bridgeとし、最終authorityをCRMへ寄せる計画が必要 |
| Contact terminology | 内部modelはContact、顧客人物表示は担当者 | `crmObjectLabels.CONTACT = 担当者`、modelはContact | 一致 | regression testを追加 |
| Hospital hierarchy | 法人→複数医院、医院属性、複数担当/案件/商材/契約 | Company/associationはあるがHospitalProfile/CorporateGroupなし | 不足 | Companyを残しadditive profile/hierarchy |
| Opportunity | Dealをサービス単位の1案件として扱う | Deal基盤とline itemあり | 一致 | Deal=1 opportunityを集計契約に固定 |
| Revenue / gross profit | 売上・粗利・fee後売上等を分離し契約時点をsnapshot | DealLineItemに売上/粗利はあるがContract/FeeSnapshotなし | 不足 | 集計はLineItemを維持し契約/fee snapshot追加 |
| Attribution | IS/FS/支援者と履歴を保持 | DealParticipant 10,676、SalesPerformanceEvent 94 | 一致 | backfill/cleanupで履歴を改変しない |
| Sales/Yomi | 1 Yomi field、最新値公式、確定eventのみ自動、履歴保持 | ForecastCategory/legacyProgressあり。正式分類map・履歴・CloudSign eventなし | 不足 | ForecastCategory再利用＋event history |
| Loss/reapproach | 主因1＋副因、再接触/対象外、人が確定 | primary loss reasonはあるが副因/再接触一式なし | 不足 | loss relationとnurturing event追加 |
| Next Action / Task | owner/due/purpose/completion criteria/source/dependency/evidence | Task/Reminderあり。purpose/completion criteria/dependency/evidence不足 | 不足 | 既存Taskを共通entityとして拡張 |
| Appointment/Calendar | 既存Calendarを継続利用しアポ→Deal/通知/E1準備を接続 | Booking/Calendar同期あり。E1準備/Transcript接続なし | 不足 | #18はDraft維持、旧接続を保護して段階拡張 |
| Meeting/Minutes/Decision | 会議、文字起こし、版付き議事録、決定、配布履歴を構造化 | MeetingBookingのみ。専用entityなし | 不足 | MeetingRecord/Minutes/Decision/Distribution新規 |
| Contract/WON | CloudSign executedが正式受注、雛形版・承認・旧版を保持 | ContractRecord/CloudSign連携なし | 不足 | executed event前のWON禁止を設計 |
| Billing/payment | 予定と実績、fee、未収、差額を別管理 | LineItemの一部日付/金額のみ | 不足 | BillingSchedule/FeeSnapshot/PaymentとBolt連携 |
| CS | Deliveryを土台にKPI/初期計画/月次/更新/解約/cross-sell | DeliveryProject/CROSS_SELLあり。CSPlan/Human Gate不足 | 不足 | 既存Deliveryを拡張 |
| KPI/Review | 量・率・時間＋本人振り返り＋上長FB | KPI/targets/action plansあり。ReviewReport/AI/人レビュー不足 | 不足 | 既存KPIをKEEP、ReviewをNEW |
| Knowledge/search | 承認済Knowledge＋Drive、出典、自然言語横断検索 | entity/RAG/横断検索なし | 不足 | KnowledgeItemとsource index追加 |
| AI governance | fact/inference/proposal/insufficient、input refs/version/approval/correction | AIArtifact/agent共通基盤なし | 不足 | 全Agentより先に共通Artifact/Human Gate |
| Event bus | OperationalEvent、Retry/DLQ/Correlation/idempotency | OperationalEventと個別idempotencyあり、共通Retry/DLQなし | 不足 | outbox/event deliveryを追加 |
| Authorization | 役割＋部署＋個別例外、AIはuser権限継承＋Agent scope | app層org scopeあり。RLS 0/80、anon/authに広範grant | 不一致 | Data API露出確認、least privilege/RLSをP0 gateにする |
| BU visibility | active org memberはactive BUを横断閲覧 | read pathはmembership ACLにしていない | 一致 | #15でread ACLへ退行させない |
| Audit/approval | before/after/approver、重要AI利用と変更を監査 | AuditLog 79件、write pathの一部のみ。Approvalなし | 不足 | command coverage test＋approval domain |
| Notification | CRMを正本、重要度別Chat/Email、再通知/配布失敗 | Notification/Reminderあり、channel adapter/再通知一式なし | 不足 | Google Chat/Emailを初期channelにする |
| Mobile | 医院/Task/Yomi/承認/Meeting/AI相談を実用可能にする | responsive sourceはあるが実機受入なし | 未確認 | breakpoint/real-device E2E |
| Retention | 一般30日Trash＋論理削除＋監査、契約/財務保持 | 一部`deleted_at`のみ。Trash/restore/種別policyなし | 不足 | retention決定後にrestore-first実装 |
| External integrations | Drive/Docs/Slides/Meet/CloudSign/Comdesk/決済/BoltのAPI/Fallback | Calendar以外はmainで未確認または未実装 | 未確認 | 実環境API/権限/Rate Limit調査 |
| Release | test→責任者review→limited→KPI/bug→full→rollback | local CIは通過。環境/limited/rollback未実証 | 未確認 | environment/flag/rollback gateを確定 |
| Phase4 monitoring | 法務・同意・privacy・短期raw retentionを先に確認 | Calendar以外未調査 | 未確認 | Phase1と並行調査、実装はPhase4 |

## Formal acceptance status

| IDs | Current status | Classification / evidence |
|---|---|---|
| AC-01 | NOT MET | 不足。営業→契約→入金→CSの同一data lineはContract/Billing不在 |
| AC-02 | PARTIAL | 不足。AuditLogはあるが全重要command coverageなし |
| AC-03 | AT RISK | 不一致。app org predicateはあるがDB/Data API境界が正式権限要件を満たさない |
| AC-04 | NOT MET | 不足。自然言語横断検索・source linkなし |
| AC-05 | PARTIAL | 不足。Calendar sync errorはあるが全integration共通可視化なし |
| AC-06 | UNVERIFIED | 未確認。実機mobile acceptance未実施 |
| S-01〜S-04 | NOT MET / PARTIAL | Booking/Calendarは再利用可。E1/E2 AI、Doc/Slides、Fact区分は未実装 |
| S-05 | NOT MET | CloudSign executed event未実装 |
| R-01〜R-03 | PARTIAL | Forecast/日時基盤はあるが正式Yomi map/historyとLeadTime event不足 |
| R-04〜R-05 | NOT MET | Review UI、本人入力、上長FB未実装 |
| F-01〜F-04 | NOT MET | Contract/Billing/Fee snapshot/PDF ACL/未収action history不足 |
| AI-01〜AI-04 | NOT MET | 共通AIArtifact、承認、訂正履歴なし |
| MM-01〜MM-04 | NOT MET | Minutes/Decision/Distributionと顧客送信gateなし |
| TM-01〜TM-02 | PARTIAL | Task一覧/owner/due/priorityはある。purpose/source/completion等不足 |
| TM-03〜TM-06 | NOT MET | 重要度別escalation、evidence gate、meeting review、automation candidate不足 |

受入条件を満たすとの完了判定は一件も追加していない。Stage1で完了したのは調査・分類・提案であり、機能実装/受入ではない。

## Confirmed questionnaire decisions

| Decision | Source | Result |
|---|---|---|
| CS AIの新サービス候補 | `縞谷に確認したいこと!I2` | 候補生成可。松岡・縞谷の承認後に開始 |
| 初期通知channel | `縞谷に確認したいこと!I3` | Google ChatまたはEmail。社内chat＋AI会話は希望案 |
| 情報区分の詳細 | `縞谷に確認したいこと!I4` | 未回答。完了扱い不可 |
| 30日Trash後の長期保持 | `縞谷に確認したいこと!I5` | 未回答。完了扱い不可 |

## PR #19 judgment changes from formal review

- Stage1の現行再利用、Human Gate、SOT、監査、dry-run-first、段階release方針は正式要件と一致。
- Clinic Leadを恒久的な別SOTとする初回表現は不一致。Target Architectureを「現行bridge/供給元→CRM最終SOT、authority/cutover要設計」へ修正した。
- #12 UUIDv7は正式要件の明示mandateではなく、前川が決めてよいID内部方式。既存ID保持と外部ID mappingを壊さない条件付きMERGE_CANDIDATE。
- #13は正式要件のDB差分確認に直接一致し、本番FK/疎結合参照の根拠を追加済み。
- #14〜#17はOrgNode/Hospital/Approval/Human Gateの方向は一致するが、正式要件の「設定値をmaster化」「role＋部署＋個人例外」「縞谷承認」を満たす実証がなく、既存判断を維持する。
- #18は既存Calendar継続利用と旧接続保護に一致するが、実環境cutover未確認のためDraft/HOLDを維持する。

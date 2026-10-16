# Scope and Sources

## Audit identity

- Audit date: 2026-10-15 (Asia/Tokyo)
- Repository: `crestix-company/CRM`
- Branch: `audit/aios-stage1-db-inventory`
- Base / audited SHA: `0c3045acde47bf8a0c2ba4e983d3d0a6e147df36` (`origin/main`と一致)
- Production Supabase ref: `xtspgevvntpidkmyfwes` (`CRM`, PostgreSQL 17.6, ACTIVE_HEALTHY)
- Method: source/GitHub/Vercel/Supabase read-only inspection. DB SQLはすべて`BEGIN READ ONLY`と`ROLLBACK`で実行した。
- Prohibited actions performed: none. DB DML/DDL、Migration、Seed、Calendar設定変更、deploy、PR merge/closeは未実施。

## Input completeness

初回監査時は統合Markdown 1件のみだったが、2026-10-15の再監査で依頼された15件をすべて確認した。

| Expected | Observed | Status |
|---|---|---|
| `official_00.docx`〜`official_12.docx` | 13/13 | **VERIFIED / FULL TEXT REVIEWED** |
| `Crestix_AI_OS_requirements.md` | 1/1、17,047 bytes | VERIFIED |
| `requirements_tracking.xlsx` | 1/1、8 sheets / 計画表154 rows | VERIFIED |

`.codex-input/`は`.git/info/exclude`で除外されている。原本は読み取り専用で使用し、Git treeへ追加していない。正式要件との照合結果は`14_official_requirements_conformance.md`、計画表のローカル更新案は`15_requirements_tracking_update_proposal.md`に記録する。

## Evidence hierarchy

規範上のSource of Truthは`official_00.docx`〜`official_12.docx`である。実装状態は別軸で、次の観測証跡により判定する。

1. READ ONLY production catalog/count query（観測時点の事実）
2. audited main source / Prisma / migrations
3. GitHub PR metadata/diff and CI status
4. `requirements_tracking.xlsx`の確認済み回答/計画行
5. 統合Markdownの追加運用要件・作業指示
6. 推奨・推定（PROPOSED / INFERRED）

正式要件にない観測・推定を仕様として確定せず、正式要件との一致だけで実装/受入完了とは判定しない。

## Stage A〜D result

| Stage | Result | Limitation |
|---|---|---|
| A 現状事実 | COMPLETE WITH BLOCKERS | Vercel対象team権限なし。production UI browser計測なし |
| B データ実態 | COMPLETE READ ONLY | 医療/飲食はkeyword candidate。業務担当の全件レビュー未実施 |
| C 正式要件Gap | COMPLETE FOR STAGE1 | 全13文書を照合。機能受入は未実装/未確認として分離 |
| D 設計準備 | COMPLETE AS PROPOSAL | migration/applyは一切未実施 |

## Secret handling

DB URL、API key、OAuth token、暗号鍵、cookie、メール/電話、会社名の候補一覧は保存していない。飲食候補は内部UUIDの一方向pseudonymのみ。Organization/BusinessUnit IDは組織mappingに必要な非secret識別子として記録した。

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

依頼された15件のうち、`.codex-input/`で確認できたのは次の1件のみ。

| Expected | Observed | Status |
|---|---|---|
| `official_00.docx`〜`official_12.docx` | 0/13 | **MISSING / UNVERIFIED** |
| `Crestix_AI_OS_requirements.md` | 1/1、17,047 bytes | VERIFIED |
| 質問事項管理xlsx（統合Markdownに記載） | 0/1 | **MISSING / UNVERIFIED** |

`.codex-input/`は`.git/info/exclude`で除外され、Git tree/history/LFSにも原本は存在しなかった。したがって本監査は統合Markdownを作業指示・二次索引として実施したが、00〜12原本の完全要件との逐語照合は完了していない。`09_requirements_traceability_matrix.md`の原文列はこの制約を明示する。

## Evidence hierarchy

1. READ ONLY production catalog/count query（観測時点の事実）
2. audited main source / Prisma / migrations
3. GitHub PR metadata/diff and CI status
4. 統合Markdownの要件索引
5. 推奨・推定（PROPOSED / INFERRED）

原本未確認事項を正式仕様として確定しない。

## Stage A〜D result

| Stage | Result | Limitation |
|---|---|---|
| A 現状事実 | COMPLETE WITH BLOCKERS | Vercel対象team権限なし。production UI browser計測なし |
| B データ実態 | COMPLETE READ ONLY | 医療/飲食はkeyword candidate。業務担当の全件レビュー未実施 |
| C 正式要件Gap | PARTIAL | official 00〜12欠落のため完全traceabilityはBLOCKED |
| D 設計準備 | COMPLETE AS PROPOSAL | migration/applyは一切未実施 |

## Secret handling

DB URL、API key、OAuth token、暗号鍵、cookie、メール/電話、会社名の候補一覧は保存していない。飲食候補は内部UUIDの一方向pseudonymのみ。Organization/BusinessUnit IDは組織mappingに必要な非secret識別子として記録した。

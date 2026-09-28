"""DRAFT ONLY. 未実行・未配置。

Clinic Lead側リポジトリに実装する際のテスト設計ドラフト。このファイルはCRM repo内のdocsとして
置いており、Clinic Lead側リポジトリへは配置していない(Clinic repoには一切触れていない)。

対応する要件は docs/clinic-uuid-strategy.md 9節「テスト設計」を参照。
`clinic_id_gen.uuid7()` は docs/clinic-uuid-strategy.md 4節の実装(標準ライブラリ優先 / uuid6
フォールバック / 依存ゼロ最終フォールバック)を指す想定のインターフェース。

実行するにはClinic Lead側リポジトリで pytest 環境と `clinic_id_gen` モジュールの実体が必要なため、
このファイル単体では実行できない(意図的に。実装が固まった段階でClinic Lead側にコピーして使う)。
"""

from __future__ import annotations

import uuid

import pytest

# Clinic Lead側実装が確定したら、実際のモジュールパスに差し替える。
# from clinic_lead.identity import clinic_id_gen


# --- 1. UUIDv7が生成できる ---------------------------------------------------
def test_generates_uuid():
    value = clinic_id_gen.uuid7()
    assert value is not None


# --- 2. 生成値がUUIDとしてvalid ----------------------------------------------
def test_is_valid_uuid():
    value = clinic_id_gen.uuid7()
    assert isinstance(value, uuid.UUID)
    # 文字列表現がUUID標準形式(8-4-4-4-12)であることも確認する
    assert uuid.UUID(str(value)) == value


# --- 3. version == 7 ---------------------------------------------------------
def test_version_is_7():
    value = clinic_id_gen.uuid7()
    assert value.version == 7


# --- 4. 大量生成して重複0(162,258件相当) -------------------------------------
def test_bulk_generation_no_duplicates():
    n = 162_258
    values = [clinic_id_gen.uuid7() for _ in range(n)]
    assert len(values) == len(set(values))


# --- 5. 連続生成時に概ね時間順(厳密な連番ではない点に注意) -------------------
def test_roughly_time_ordered():
    """UUIDv7は「概ね時間順」であって厳密な連番ではない
    (docs/clinic-uuid-strategy.md 6節)。ここでは先頭48bit(unix_ts_ms)が
    非減少であることだけを緩やかに確認し、rand_a/rand_bの順序までは要求しない。
    """
    values = [clinic_id_gen.uuid7() for _ in range(1000)]
    timestamps_ms = [v.int >> 80 for v in values]  # 先頭48bit
    # 非減少(同一msでの逆転は許容、大幅な逆行がないことだけ確認)
    assert timestamps_ms == sorted(timestamps_ms)


# --- 6. PostgreSQL uuid型へ格納可能な形式 -------------------------------------
def test_postgres_uuid_format_compatible():
    value = clinic_id_gen.uuid7()
    # psycopg2/psycopg3/asyncpg等はuuid.UUIDインスタンスをuuid型として自動アダプトする。
    # ここでは "16byteのUUID" かつ標準のUUID文字列表現になっていることだけを確認する。
    assert len(value.bytes) == 16
    assert len(str(value)) == 36  # 8-4-4-4-12 + ハイフン4個


# --- 7. 既存medical_key時はUUIDを生成してINSERTしない -------------------------
def test_existing_medical_key_skips_generation(mocker):
    """promotionロジック(SKIP分岐)がclinic_id_gen.uuid7()を呼ばないことを確認する。
    実装側の promote_row(...) は docs/clinic-db-migration-plan.md STEP[9] の疑似コードを想定。
    """
    spy = mocker.patch.object(clinic_id_gen, "uuid7")
    existing = {"medical_key": "MK-0001", "clinic_id": uuid.uuid4()}

    result = promote_row(staging_row={"medical_key": "MK-0001"}, existing_clinic=existing)

    spy.assert_not_called()
    assert result.decision == "skip"
    assert result.clinic_id == existing["clinic_id"]


# --- 8. 新規medical_key時だけUUIDv7生成 --------------------------------------
def test_new_medical_key_generates_once(mocker):
    spy = mocker.patch.object(clinic_id_gen, "uuid7", return_value=uuid.uuid4())

    result = promote_row(staging_row={"medical_key": "MK-9999"}, existing_clinic=None)

    spy.assert_called_once()
    assert result.decision == "insert"
    assert result.clinic_id == spy.return_value


# --- 9. legacy_uuidは変更しない -----------------------------------------------
def test_legacy_uuid_untouched_on_promotion():
    original_legacy_uuid = uuid.uuid4()
    staging_row = {"medical_key": "MK-0002", "legacy_uuid": original_legacy_uuid}

    result = promote_row(staging_row=staging_row, existing_clinic=None)

    assert result.legacy_uuid == original_legacy_uuid


# --- 10. FK不整合データが拒否される設計 ---------------------------------------
def test_fk_violation_rejected():
    """clinic_master.clinicsに存在しないclinic_idをclinic_ops側へ挿入しようとすると
    FK制約違反(psycopg2.errors.ForeignKeyViolation等)になることを確認する。
    実DB接続が必要なため、ローカルPostgresを使った結合テストとして実装する想定
    (このドラフトではインターフェースのみ提示)。
    """
    nonexistent_clinic_id = uuid.uuid4()

    with pytest.raises(Exception):  # 実装確定後、具体的な例外クラスに差し替える
        insert_hp_research(clinic_id=nonexistent_clinic_id, url="https://example.com")

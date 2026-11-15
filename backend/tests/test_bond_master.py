"""Offline tests for the domestic bond master file manager."""

import io
import json
import zipfile

import pytest

from src.integrations import bond_master
from src.integrations.bond_master import BondMasterFileManager

EXPORT_ROWS = [
    {
        "bond_type": "F9",
        "bond_class_code": "02",
        "pdno": "KR101701D716",
        "name": "국민주택2종17-01",
        "bond_interest_class_code": "12",
        "listed_date": "20170102",
        "issue_date": "20170131",
        "maturity_date": "20270131",
    },
    {"pdno": "KR103502GE97", "name": "국고03125-3406(24-4)"},
    {"pdno": "not-a-bond-code", "name": "skipped"},
]

MST_LINE = (
    "C0"
    + "01"
    + "KR103502GE97"
    + "국고03125-3406(24-4)"
    + "11"
    + "20240610"
    + "20240610"
    + "20340610"
)


@pytest.fixture()
def manager(tmp_path):
    return BondMasterFileManager(data_dir=str(tmp_path))


@pytest.fixture()
def fake_download(monkeypatch):
    """Serve a zipped bond_code.mst instead of hitting the network."""
    calls = []

    def fake_urlretrieve(url, filename):
        calls.append(url)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zf:
            zf.writestr("bond_code.mst", (MST_LINE + "\n").encode("cp949"))
        with open(filename, "wb") as handle:
            handle.write(buffer.getvalue())

    monkeypatch.setattr(
        bond_master.urllib.request, "urlretrieve", fake_urlretrieve
    )
    return calls


def _write_json_export(manager):
    path = manager.data_dir / "bond_codes.json"
    path.write_text(json.dumps(EXPORT_ROWS, ensure_ascii=False), "utf-8")
    return path


def test_json_export_is_parsed_as_json(manager):
    path = _write_json_export(manager)

    assert manager.get_local_master_file() == path
    rows = manager.get_bond_codes()

    assert [row["pdno"] for row in rows] == ["KR101701D716", "KR103502GE97"]
    assert rows[0]["name"] == "국민주택2종17-01"
    assert rows[0]["bond_type"] == "F9"
    assert rows[0]["maturity_date"] == "20270131"
    # Missing fields come back as None, never NaN.
    assert rows[1]["bond_type"] is None


def test_json_export_does_not_count_as_downloaded(manager):
    _write_json_export(manager)

    assert manager._find_raw_master_file() is None


def test_refresh_downloads_when_only_json_export_exists(
    manager, fake_download
):
    _write_json_export(manager)

    result = manager.refresh_and_export(output_format="csv", force=False)

    assert len(fake_download) == 1
    assert result["ok"] is True
    assert result["source_file"].endswith("bond_code.mst")
    assert result["row_count"] == 1


def test_refresh_skips_download_when_raw_master_exists(
    manager, fake_download
):
    (manager.data_dir / "bond_code.mst").write_bytes(
        (MST_LINE + "\n").encode("cp949")
    )

    result = manager.refresh_and_export(output_format="json", force=False)

    assert fake_download == []
    assert result["ok"] is True


def test_csv_export_round_trip_keeps_fields(manager, fake_download):
    manager.download_bond_master(force=True)
    out = manager.save_to_csv()
    (manager.data_dir / "bond_code.mst").unlink()

    assert manager.get_local_master_file() == out
    rows = manager.get_bond_codes()

    assert rows == [
        {
            "pdno": "KR103502GE97",
            "name": "국고03125-3406(24-4)",
            "bond_type": "C0",
            "bond_class_code": "01",
            "bond_interest_class_code": "11",
            "listed_date": "20240610",
            "issue_date": "20240610",
            "maturity_date": "20340610",
        }
    ]


def test_committed_snapshot_has_names():
    """The JSON shipped in the repo loads with real bond names."""
    rows = BondMasterFileManager().get_bond_codes()

    assert len(rows) > 1000
    assert all(row["name"] for row in rows[:100])
    assert all(row["pdno"].startswith("KR") for row in rows[:100])

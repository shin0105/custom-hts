"""Domestic bond master file downloader and parser."""

from __future__ import annotations

import csv
import json
import logging
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional, List, Dict, Any

import pandas as pd

logger = logging.getLogger(__name__)


class BondMasterFileManager:
    """Manager for downloading and parsing domestic bond master files."""

    BASE_URL = "https://new.real.download.dws.co.kr/common/master"
    DEFAULT_ZIP_URL = f"{BASE_URL}/bond_code.mst.zip"

    # Filename candidates are tried in order. Exact filename may vary by KIS publication.
    FILE_CANDIDATES = [
        "bond_code.mst.zip",
        "bond_code.zip",
        "domestic_bond_code.zip",
        "domestic_bond_code.mst.zip",
    ]

    # Normalised exports written by save_to_csv / save_to_json. They are
    # readable fallbacks, but never count as a downloaded master file.
    EXPORT_CSV = "bond_codes.csv"
    EXPORT_JSON = "bond_codes.json"

    # Row fields kept when reading a normalised export back in.
    MASTER_FIELDS = (
        "bond_type",
        "bond_class_code",
        "pdno",
        "name",
        "bond_interest_class_code",
        "listed_date",
        "issue_date",
        "maturity_date",
    )

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            self.data_dir = (
                Path(__file__).parent.parent.parent
                / "data"
                / "kr_bond_master"
            )
        else:
            self.data_dir = Path(data_dir)

        self.data_dir.mkdir(parents=True, exist_ok=True)

    def download_bond_master(
        self,
        force: bool = False,
        source_url: Optional[str] = None,
    ) -> Optional[Path]:
        """
        Download and extract bond master file.

        Args:
            force: Force re-download.
            source_url: Optional direct URL override.

        Returns:
            Extracted file path or None on failure.
        """
        existing = self._find_raw_master_file()
        if existing and not force:
            logger.info("Bond master already exists: %s", existing)
            return existing

        urls: List[str] = []
        if source_url:
            urls.append(source_url)
        urls.append(self.DEFAULT_ZIP_URL)
        urls.extend([f"{self.BASE_URL}/{name}" for name in self.FILE_CANDIDATES])

        for url in urls:
            zip_path = self.data_dir / Path(url).name
            try:
                logger.info("Downloading bond master from %s", url)
                urllib.request.urlretrieve(url, str(zip_path))

                with zipfile.ZipFile(zip_path, "r") as zf:
                    zf.extractall(self.data_dir)

                if zip_path.exists():
                    zip_path.unlink()

                extracted = self._find_raw_master_file()
                if extracted:
                    logger.info("Bond master ready: %s", extracted)
                    return extracted
            except Exception as e:
                logger.warning("Failed bond master download attempt (%s): %s", url, e)
                if zip_path.exists():
                    try:
                        zip_path.unlink()
                    except Exception:
                        pass

        logger.error("Failed to download bond master from all candidate URLs")
        return None

    def parse_bond_master(
        self,
        auto_download: bool = False,
        force_download: bool = False,
        source_url: Optional[str] = None,
    ) -> Optional[pd.DataFrame]:
        """
        Parse bond master into DataFrame.

        Returns DataFrame with at least:
        - pdno
        - name
        """
        master_file = self._find_local_master_file()
        if auto_download:
            # Only a downloaded master counts here: the committed JSON
            # export must not stop a refresh on a fresh clone.
            if force_download or not self._find_raw_master_file():
                master_file = self.download_bond_master(
                    force=force_download, source_url=source_url
                )
        if not master_file:
            logger.error("No local bond master file found")
            return None

        try:
            suffix = master_file.suffix.lower()
            if master_file.suffix.lower() == ".mst":
                return self._parse_bond_mst(master_file)

            if suffix == ".json":
                return self._parse_json_export(master_file)

            if suffix in {".csv", ".tsv"}:
                delimiter = "," if suffix == ".csv" else "\t"
                # save_to_csv writes utf-8-sig; strip the BOM on read.
                with open(
                    master_file, "r", encoding="utf-8-sig", newline=""
                ) as f:
                    rows = list(csv.DictReader(f, delimiter=delimiter))
                return self._normalize_rows(rows)

            # Generic text-like parser: find KR********** code in each line.
            rows: List[Dict[str, Any]] = []
            with open(master_file, "r", encoding="cp949", errors="ignore") as f:
                for raw in f:
                    line = raw.strip()
                    if not line:
                        continue
                    code = self._extract_code(line)
                    if not code:
                        continue
                    name = line.replace(code, "").strip(" ,|\t-")
                    rows.append({"pdno": code, "name": name})

            df = pd.DataFrame(rows)
            if df.empty:
                logger.warning("Parsed bond master is empty: %s", master_file)
                return df

            df = df.drop_duplicates(subset=["pdno"]).reset_index(drop=True)
            return df
        except Exception as e:
            logger.error("Failed to parse bond master %s: %s", master_file, e)
            return None

    def save_to_csv(
        self,
        output_file: Optional[str] = None,
        auto_download: bool = False,
        force_download: bool = False,
        source_url: Optional[str] = None,
    ) -> Optional[Path]:
        """Parse and save normalized bond master as UTF-8 CSV."""
        df = self.parse_bond_master(
            auto_download=auto_download,
            force_download=force_download,
            source_url=source_url,
        )
        if df is None:
            return None

        if output_file is None:
            out_path = self.data_dir / "bond_codes.csv"
        else:
            out_path = Path(output_file)

        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(out_path, index=False, encoding="utf-8-sig")
            logger.info("Saved bond codes CSV: %s (%d rows)", out_path, len(df))
            return out_path
        except Exception as e:
            logger.error("Failed to save bond codes CSV: %s", e)
            return None

    def save_to_json(
        self,
        output_file: Optional[str] = None,
        auto_download: bool = False,
        force_download: bool = False,
        source_url: Optional[str] = None,
    ) -> Optional[Path]:
        """Parse and save normalized bond master as JSON."""
        df = self.parse_bond_master(
            auto_download=auto_download,
            force_download=force_download,
            source_url=source_url,
        )
        if df is None:
            return None

        if output_file is None:
            out_path = self.data_dir / "bond_codes.json"
        else:
            out_path = Path(output_file)

        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(
                json.dumps(df.to_dict(orient="records"), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            logger.info("Saved bond codes JSON: %s (%d rows)", out_path, len(df))
            return out_path
        except Exception as e:
            logger.error("Failed to save bond codes JSON: %s", e)
            return None

    def refresh_and_export(
        self,
        output_format: str = "csv",
        force: bool = False,
        source_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Download latest bond master and export to csv/json.

        Returns:
            Dict with output_file, source_file, row_count.
        """
        fmt = output_format.lower()
        if fmt not in {"csv", "json"}:
            raise ValueError("output_format must be 'csv' or 'json'")

        if fmt == "csv":
            output = self.save_to_csv(
                auto_download=True,
                force_download=force,
                source_url=source_url,
            )
        else:
            output = self.save_to_json(
                auto_download=True,
                force_download=force,
                source_url=source_url,
            )

        if output is None:
            return {
                "ok": False,
                "output_format": fmt,
                "output_file": None,
                "source_file": str(self._find_local_master_file())
                if self._find_local_master_file()
                else None,
                "row_count": 0,
            }

        df = self.parse_bond_master(auto_download=False)
        return {
            "ok": True,
            "output_format": fmt,
            "output_file": str(output),
            "source_file": str(self._find_local_master_file()),
            "row_count": 0 if df is None else int(len(df)),
        }

    def get_bond_codes(
        self,
        auto_download: bool = False,
        force_download: bool = False,
        source_url: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get normalized bond code rows as list of dicts."""
        df = self.parse_bond_master(
            auto_download=auto_download,
            force_download=force_download,
            source_url=source_url,
        )
        if df is None:
            return []
        return df.to_dict(orient="records")

    def get_local_master_file(self) -> Optional[Path]:
        """Get discovered local bond master file path."""
        return self._find_local_master_file()

    def _parse_bond_mst(self, file_path: Path) -> pd.DataFrame:
        """
        Parse bond_code.mst using the provided fixed-width slicing logic.
        """
        rows: List[Dict[str, Any]] = []
        with open(file_path, "r", encoding="cp949", errors="ignore") as f:
            for raw in f:
                row = raw.strip()
                if not row or len(row) < 26:
                    continue

                # Some files contain trailing status flag (e.g. 'N') after spaces.
                # Keep provided slicing logic, but trim that trailing flag first.
                if (not row[-8:].isdigit()) and row[-1:].isalpha():
                    row = row[:-1].rstrip()

                bond_type = row[0:2].strip()
                bond_cls_code = row[2:4].strip()
                code = row[4:16].strip()
                rdmp_date = row[-8:].strip()
                pblc_date = row[-16:-8].strip()
                lstn_date = row[-24:-16].strip()
                bond_int_cls_code = row[-26:-24].strip()
                sname = row[16:-26].rstrip()

                if not self._extract_code(code):
                    continue

                rows.append(
                    {
                        "bond_type": bond_type,
                        "bond_class_code": bond_cls_code,
                        "pdno": code,
                        "name": sname,
                        "bond_interest_class_code": bond_int_cls_code,
                        "listed_date": lstn_date,
                        "issue_date": pblc_date,
                        "maturity_date": rdmp_date,
                    }
                )

        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.drop_duplicates(subset=["pdno"]).reset_index(drop=True)
        return df

    def _parse_json_export(self, file_path: Path) -> pd.DataFrame:
        """Read a list-of-records JSON written by save_to_json."""
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError("bond master JSON must be a list of records")
        records = [row for row in payload if isinstance(row, dict)]
        return self._normalize_rows(records)

    def _find_raw_master_file(self) -> Optional[Path]:
        """Find a downloaded (not exported) master file."""
        raw_mst = self.data_dir / "bond_code.mst"
        if raw_mst.exists():
            return raw_mst

        exports = {self.EXPORT_CSV, self.EXPORT_JSON}
        patterns = [
            "*bond*code*.mst",
            "*bond*code*.txt",
            "*bond*code*.tsv",
            "*bond*code*.csv",
            "*bond*code*",
        ]
        for pattern in patterns:
            for match in sorted(self.data_dir.glob(pattern)):
                if (
                    match.is_file()
                    and match.name not in exports
                    and match.suffix.lower() not in {".zip", ".json"}
                ):
                    return match
        return None

    def _find_local_master_file(self) -> Optional[Path]:
        """Find the best readable master: raw first, then exports."""
        raw_mst = self.data_dir / "bond_code.mst"
        if raw_mst.exists():
            return raw_mst

        export_csv = self.data_dir / self.EXPORT_CSV
        if export_csv.exists():
            return export_csv

        raw = self._find_raw_master_file()
        if raw:
            return raw

        export_json = self.data_dir / self.EXPORT_JSON
        if export_json.exists():
            return export_json
        return None

    def _normalize_rows(self, rows: List[Dict[str, Any]]) -> pd.DataFrame:
        normalized: List[Dict[str, Any]] = []
        seen = set()

        code_keys = [
            "pdno",
            "code",
            "bond_code",
            "stnd_iscd",
            "표준종목코드",
            "종목코드",
        ]
        name_keys = [
            "name",
            "bond_name",
            "bond_isnm",
            "ksd_bond_item_name",
            "종목명",
            "채권종목명",
        ]

        for row in rows:
            code = ""
            for key in code_keys:
                value = row.get(key)
                if value:
                    code = str(value).strip()
                    break
            if not code or not self._extract_code(code):
                continue
            code = self._extract_code(code) or code
            if code in seen:
                continue

            name = ""
            for key in name_keys:
                value = row.get(key)
                if value:
                    name = str(value).strip()
                    break

            seen.add(code)
            record: Dict[str, Any] = {"pdno": code, "name": name}
            # Keep type/date fields from normalised exports so the bond
            # page's filters still work without bond_code.mst.
            for field in self.MASTER_FIELDS:
                if field in record:
                    continue
                value = row.get(field)
                if value is not None and str(value).strip():
                    record[field] = str(value).strip()
            normalized.append(record)

        df = pd.DataFrame(normalized)
        # Rows missing a field would otherwise carry NaN into the API.
        return df.astype(object).where(df.notna(), None)

    @staticmethod
    def _extract_code(text: str) -> Optional[str]:
        import re

        match = re.search(r"(KR[0-9A-Z]{10})", text)
        if not match:
            return None
        return match.group(1)


bond_master_file_manager = BondMasterFileManager()

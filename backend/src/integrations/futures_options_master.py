"""Domestic futures/options master file downloader and parser."""

from __future__ import annotations

import json
import logging
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class FuturesOptionsMasterFileManager:
    """Manager for domestic futures/options master files."""

    BASE_URL = "https://new.real.download.dws.co.kr/common/master"

    MARKET_FILES = {
        "index": "fo_idx_code_mts.mst.zip",
        "stock": "fo_stk_code_mts.mst.zip",
        "commodity": "fo_com_code.mst.zip",
    }

    MARKET_COLUMNS = {
        "index": [
            "info_type",
            "short_code",
            "standard_code",
            "name_kr",
            "atm_class_code",
            "strike_price",
            "month_class_code",
            "underlying_short_code",
            "underlying_name_kr",
        ],
        "stock": [
            "info_type",
            "short_code",
            "standard_code",
            "name_kr",
            "atm_class_code",
            "strike_price",
            "month_class_code",
            "underlying_short_code",
            "underlying_name_kr",
        ],
        "commodity": [
            "commodity_type",
            "info_type",
            "short_code",
            "standard_code",
            "name_kr",
            "atm_class_code",
            "strike_price",
            "month_class_code",
            "underlying_short_code",
            "underlying_name_kr",
        ],
    }

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            self.data_dir = (
                Path(__file__).parent.parent.parent
                / "data"
                / "kr_futures_options_master"
            )
        else:
            self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def download_market_master(
        self,
        market: str,
        force: bool = False,
        source_url: Optional[str] = None,
    ) -> Optional[Path]:
        """Download and extract one market master file."""
        market_key = (market or "").strip().lower()
        if market_key not in self.MARKET_FILES:
            logger.error(
                "Unknown futures/options market: %s (valid: %s)",
                market,
                list(self.MARKET_FILES.keys()),
            )
            return None

        zip_name = self.MARKET_FILES[market_key]
        expected_mst = self.data_dir / zip_name.replace(".zip", "")
        if expected_mst.exists() and not force:
            return expected_mst

        url = source_url or f"{self.BASE_URL}/{zip_name}"
        zip_path = self.data_dir / Path(url).name
        try:
            logger.info("Downloading %s futures/options master from %s", market_key, url)
            urllib.request.urlretrieve(url, str(zip_path))
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(self.data_dir)
            if zip_path.exists():
                zip_path.unlink()
        except Exception as e:
            logger.error(
                "Failed to download futures/options master for %s (%s): %s",
                market_key,
                url,
                e,
            )
            if zip_path.exists():
                try:
                    zip_path.unlink()
                except Exception:
                    pass
            return None

        extracted = self._find_market_master_file(market_key)
        if extracted is None:
            logger.error("Extracted master file not found for market: %s", market_key)
            return None
        return extracted

    def download_all_markets(self, force: bool = False) -> Dict[str, bool]:
        """Download and extract all supported futures/options masters."""
        result: Dict[str, bool] = {}
        for market in self.MARKET_FILES:
            result[market] = self.download_market_master(market, force=force) is not None
        return result

    def parse_market_master(
        self,
        market: str,
        auto_download: bool = False,
        force_download: bool = False,
        source_url: Optional[str] = None,
    ) -> Optional[pd.DataFrame]:
        """Parse one market master into DataFrame."""
        market_key = (market or "").strip().lower()
        if market_key not in self.MARKET_FILES:
            return None

        master_file = self._find_market_master_file(market_key)
        if auto_download and (force_download or not master_file):
            master_file = self.download_market_master(
                market_key, force=force_download, source_url=source_url
            )
        if not master_file:
            return None

        try:
            if market_key in {"index", "stock"}:
                df = pd.read_table(
                    master_file,
                    sep="|",
                    encoding="cp949",
                    header=None,
                    dtype=str,
                    engine="python",
                )
                expected_cols = self.MARKET_COLUMNS[market_key]
                if df.shape[1] >= len(expected_cols):
                    df = df.iloc[:, : len(expected_cols)]
                df.columns = expected_cols
                df = df.fillna("")
                return df

            if market_key == "commodity":
                return self._parse_commodity_master(master_file)
        except Exception as e:
            logger.error(
                "Failed to parse futures/options master %s (%s): %s",
                market_key,
                master_file,
                e,
            )
            return None

        return None

    def parse_all_markets(
        self,
        auto_download: bool = False,
        force_download: bool = False,
    ) -> Dict[str, pd.DataFrame]:
        """Parse all futures/options master files."""
        out: Dict[str, pd.DataFrame] = {}
        for market in self.MARKET_FILES:
            df = self.parse_market_master(
                market,
                auto_download=auto_download,
                force_download=force_download,
            )
            if df is not None:
                out[market] = df
        return out

    def refresh_and_export(
        self,
        market: str = "all",
        output_format: str = "csv",
        force: bool = False,
    ) -> Dict[str, Any]:
        """Download latest files and export normalized outputs."""
        market_key = (market or "all").strip().lower()
        fmt = output_format.lower().strip()
        if fmt not in {"csv", "json"}:
            raise ValueError("output_format must be 'csv' or 'json'")

        target_markets = (
            list(self.MARKET_FILES.keys())
            if market_key == "all"
            else [market_key]
        )
        if any(m not in self.MARKET_FILES for m in target_markets):
            raise ValueError("market must be one of: all/index/stock/commodity")

        outputs: Dict[str, Any] = {}
        for m in target_markets:
            master_file = self.download_market_master(m, force=force)
            df = self.parse_market_master(m, auto_download=False)
            if not master_file or df is None:
                outputs[m] = {
                    "ok": False,
                    "source_file": str(master_file) if master_file else None,
                    "output_file": None,
                    "row_count": 0,
                }
                continue

            if fmt == "csv":
                out_path = self.data_dir / f"{m}_fo_master.csv"
                df.to_csv(out_path, index=False, encoding="utf-8-sig")
            else:
                out_path = self.data_dir / f"{m}_fo_master.json"
                out_path.write_text(
                    json.dumps(df.to_dict(orient="records"), ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )

            outputs[m] = {
                "ok": True,
                "source_file": str(master_file),
                "output_file": str(out_path),
                "row_count": int(len(df)),
            }

        all_ok = all(item.get("ok") for item in outputs.values()) if outputs else False
        return {
            "ok": all_ok,
            "market": market_key,
            "output_format": fmt,
            "markets": outputs,
        }

    def get_market_rows(
        self,
        market: str,
        auto_download: bool = False,
        force_download: bool = False,
    ) -> List[Dict[str, Any]]:
        """Get normalized rows for one market."""
        df = self.parse_market_master(
            market,
            auto_download=auto_download,
            force_download=force_download,
        )
        if df is None or df.empty:
            return []
        return df.to_dict(orient="records")

    def get_local_master_file(self, market: str) -> Optional[Path]:
        """Get discovered local master file path for market."""
        return self._find_market_master_file((market or "").strip().lower())

    def _find_market_master_file(self, market: str) -> Optional[Path]:
        if market not in self.MARKET_FILES:
            return None
        zip_name = self.MARKET_FILES[market]
        mst_name = zip_name.replace(".zip", "")
        preferred = self.data_dir / mst_name
        if preferred.exists():
            return preferred
        stem = Path(mst_name).stem
        for candidate in sorted(self.data_dir.glob(f"{stem}*")):
            if candidate.is_file() and candidate.suffix.lower() != ".zip":
                return candidate
        return None

    def _parse_commodity_master(self, file_path: Path) -> pd.DataFrame:
        rows: List[Dict[str, str]] = []
        with open(file_path, "r", encoding="cp949", errors="ignore") as f:
            for raw in f:
                row = raw.rstrip("\n\r")
                if not row:
                    continue
                base = row.ljust(68)
                rows.append(
                    {
                        "commodity_type": base[0:1].strip(),
                        "info_type": base[1:2].strip(),
                        "short_code": base[2:11].strip(),
                        "standard_code": base[11:23].strip(),
                        # Upstream parser uses 23:55 for name in this file format.
                        "name_kr": base[23:55].strip(),
                        "atm_class_code": base[55:56].strip(),
                        "strike_price": base[56:64].strip(),
                        "month_class_code": base[64:65].strip(),
                        "underlying_short_code": base[65:68].strip(),
                        "underlying_name_kr": base[68:].strip(),
                    }
                )
        return pd.DataFrame(rows, columns=self.MARKET_COLUMNS["commodity"]).fillna("")


futures_options_master_file_manager = FuturesOptionsMasterFileManager()

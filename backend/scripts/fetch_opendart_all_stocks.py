#!/usr/bin/env python3
"""Bulk fetch OPENDART financials for all Korean stocks and write CSVs."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Ensure backend/src is importable
ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from src.integrations.opendart import opendart_client  # noqa: E402


def parse_amount(value: Any) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text == "-":
        return None
    neg = False
    if text.startswith("(") and text.endswith(")"):
        neg = True
        text = text[1:-1]
    text = text.replace(",", "")
    try:
        num = float(text)
    except ValueError:
        return None
    return -num if neg else num


def parse_raw_items(items: List[Dict[str, Any]]) -> Dict[str, Dict[str, Optional[float]]]:
    parsed = {"BS": {}, "IS": {}, "CF": {}}
    for item in items:
        sj_div = item.get("sj_div")
        if sj_div not in parsed:
            continue
        account_nm = str(item.get("account_nm", "")).strip()
        if not account_nm:
            continue
        parsed[sj_div][account_nm] = parse_amount(item.get("thstrm_amount"))
    return parsed


def subtract_dicts(
    current: Dict[str, Optional[float]],
    *prevs: Dict[str, Optional[float]],
) -> Dict[str, Optional[float]]:
    result: Dict[str, Optional[float]] = {}
    for key, val in current.items():
        if val is None:
            result[key] = None
            continue
        total = val
        for prev in prevs:
            prev_val = prev.get(key)
            if prev_val is None:
                continue
            total -= prev_val
        result[key] = total
    return result


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: List[Dict[str, Any]], columns: List[str]) -> None:
    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return default


def save_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def read_existing_rows(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def write_csv_with_schema(
    path: Path, rows: List[Dict[str, Any]], columns: List[str]
) -> None:
    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def append_row_with_schema(
    csv_path: Path,
    schema_path: Path,
    row: Dict[str, Any],
    base_columns: List[str],
) -> None:
    schema = load_json(schema_path, {"columns": base_columns})
    columns = schema.get("columns", base_columns)
    columns_set = set(columns)

    new_keys = [key for key in row.keys() if key not in columns_set]
    if new_keys:
        columns = base_columns + sorted(
            {key for key in columns if key not in base_columns}.union(new_keys)
        )
        schema = {"columns": columns}
        save_json(schema_path, schema)

        existing = read_existing_rows(csv_path)
        existing.append(row)
        write_csv_with_schema(csv_path, existing, columns)
        return

    ensure_dir(csv_path.parent)
    file_exists = csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def iter_stock_codes(
    limit: Optional[int] = None,
    symbols: Optional[List[str]] = None,
) -> List[Tuple[str, str]]:
    if symbols:
        codes = [s.strip().zfill(6) for s in symbols if s.strip()]
        pairs = [(code, opendart_client.get_corp_code(code) or "") for code in codes]
        return pairs

    if not opendart_client._corp_code_cache or opendart_client._should_refresh_corp_code_cache():
        opendart_client.download_corp_code_list()

    pairs = [
        (code, corp)
        for code, corp in opendart_client._corp_code_cache.items()
        if code.isdigit() and len(code) == 6
    ]
    pairs.sort(key=lambda x: x[0])
    if limit:
        pairs = pairs[:limit]
    return pairs


def fetch_for_stock(
    symbol: str,
    year: int,
    fs_div: str,
    quarters: List[int],
    sleep_sec: float,
    retries: int,
    retry_sleep: float,
) -> Tuple[Dict[int, Dict[str, Dict[str, Optional[float]]]], Optional[str]]:
    raw_by_quarter: Dict[int, Dict[str, Dict[str, Optional[float]]]] = {}
    corp_name: Optional[str] = None
    for quarter in sorted(set(quarters)):
        raw_list = None
        for attempt in range(retries + 1):
            raw_list = opendart_client.get_financial_statement_raw(
                symbol, year, quarter, fs_div
            )
            if raw_list is not None:
                break
            if attempt < retries:
                time.sleep(retry_sleep)
        if raw_list is None:
            raise RuntimeError(
                f"DART API error or rate limit for {symbol} {year}Q{quarter} {fs_div}"
            )
        if raw_list and not corp_name:
            corp_name = raw_list[0].get("corp_name")
        parsed = parse_raw_items(raw_list)
        raw_by_quarter[quarter] = parsed
        time.sleep(sleep_sec)
    return raw_by_quarter, corp_name


def build_rows_for_stock(
    year: int,
    raw_by_quarter: Dict[int, Dict[str, Dict[str, Optional[float]]]],
    target_periods: Set[str],
) -> Tuple[
    Dict[str, Dict[str, Dict[str, Optional[float]]]],
    Dict[str, Dict[str, Dict[str, Optional[float]]]],
]:
    """Returns (quarterly_rows, annual_rows) keyed by period -> statement."""
    quarterly_rows: Dict[str, Dict[str, Dict[str, Optional[float]]]] = {}
    annual_rows: Dict[str, Dict[str, Dict[str, Optional[float]]]] = {}

    q1 = raw_by_quarter.get(1, {"BS": {}, "IS": {}, "CF": {}})
    q2 = raw_by_quarter.get(2, {"BS": {}, "IS": {}, "CF": {}})
    q3 = raw_by_quarter.get(3, {"BS": {}, "IS": {}, "CF": {}})
    q4 = raw_by_quarter.get(4, {"BS": {}, "IS": {}, "CF": {}})

    # Balance sheet is point-in-time
    bs_q1 = q1["BS"]
    bs_q2 = q2["BS"]
    bs_q3 = q3["BS"]
    bs_q4 = q4["BS"]

    # Income and cashflow: Q2 and Q4 are cumulative, Q3 is standalone per user spec
    is_q1 = q1["IS"]
    is_q2 = subtract_dicts(q2["IS"], q1["IS"])
    is_q3 = q3["IS"]
    is_q4 = subtract_dicts(q4["IS"], q2["IS"], q3["IS"])

    cf_q1 = q1["CF"]
    cf_q2 = subtract_dicts(q2["CF"], q1["CF"])
    cf_q3 = q3["CF"]
    cf_q4 = subtract_dicts(q4["CF"], q2["CF"], q3["CF"])

    quarter_map = {
        1: {
            "balance_sheet": bs_q1,
            "income_statement": is_q1,
            "cashflow_statement": cf_q1,
        },
        2: {
            "balance_sheet": bs_q2,
            "income_statement": is_q2,
            "cashflow_statement": cf_q2,
        },
        3: {
            "balance_sheet": bs_q3,
            "income_statement": is_q3,
            "cashflow_statement": cf_q3,
        },
        4: {
            "balance_sheet": bs_q4,
            "income_statement": is_q4,
            "cashflow_statement": cf_q4,
        },
    }

    for quarter, payload in quarter_map.items():
        period = f"{year}Q{quarter}"
        if period in target_periods:
            quarterly_rows[period] = payload

    # Annual (year) uses Q4 cumulative for IS/CF and Q4 for BS
    annual_period = f"{year}Y"
    if annual_period in target_periods:
        annual_rows[annual_period] = {
            "balance_sheet": bs_q4,
            "income_statement": q4["IS"],
            "cashflow_statement": q4["CF"],
        }

    return quarterly_rows, annual_rows


def quarter_dependencies(period: str) -> List[int]:
    if period.endswith("Q1"):
        return [1]
    if period.endswith("Q2"):
        return [1, 2]
    if period.endswith("Q3"):
        return [3]
    if period.endswith("Q4"):
        return [2, 3, 4]
    if period.endswith("Y"):
        return [4]
    raise ValueError(f"Unsupported period format: {period}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch OPENDART data for all Korean stocks."
    )
    parser.add_argument("--years", nargs="+", type=int, required=True)
    parser.add_argument("--sleep", type=float, default=0.3)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--retry-sleep", type=float, default=30.0)
    parser.add_argument(
        "--periods",
        nargs="+",
        default=None,
        help="Optional periods like 2025Q2 2025Q3 2025Y. If omitted, all quarters + Y for each year.",
    )
    parser.add_argument(
        "--output-root",
        type=str,
        default=str(ROOT / "database" / "raw_data"),
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--symbols", nargs="+", default=None, help="Optional list of stock codes to fetch"
    )
    args = parser.parse_args()

    output_root = Path(args.output_root)
    stock_pairs = iter_stock_codes(limit=args.limit, symbols=args.symbols)
    if not stock_pairs:
        print("No stock codes found. Ensure OPENDART corp codes are available.")
        sys.exit(1)

    total = len(stock_pairs)
    print(f"Found {total} stock codes to process.")

    requested_periods = args.periods or []
    for year in args.years:
        progress_dir = output_root / "progress"
        progress_path = progress_dir / f"opendart_{year}.json"
        progress = load_json(
            progress_path,
            {"done": [], "failed": {}, "period_done": {}},
        )
        done_symbols = set(progress.get("done", []))
        failed_map: Dict[str, str] = progress.get("failed", {})
        period_done = progress.get("period_done", {})

        if requested_periods:
            periods = [p for p in requested_periods if p.startswith(f"{year}")]
            if not periods:
                print(f"[{year}] No requested periods matched this year. Skipping.")
                continue
        else:
            periods = [f"{year}Q{q}" for q in (1, 2, 3, 4)] + [f"{year}Y"]

        period_set = set(periods)
        required_quarters: Set[int] = set()
        for period in periods:
            for quarter in quarter_dependencies(period):
                required_quarters.add(quarter)

        for idx, (symbol, corp_code) in enumerate(stock_pairs, 1):
            done_for_all_periods = True
            for period in periods:
                done_list = set(period_done.get(period, []))
                if symbol not in done_list:
                    done_for_all_periods = False
                    break
            if done_for_all_periods:
                if idx % 25 == 0 or idx == total:
                    print(f"[{year}] Processed {idx}/{total} stocks (skipping done)")
                continue

            for fs_div in ("CFS", "OFS"):
                try:
                    raw_by_quarter, corp_name = fetch_for_stock(
                        symbol,
                        year,
                        fs_div,
                        list(required_quarters),
                        args.sleep,
                        args.retries,
                        args.retry_sleep,
                    )
                    quarterly_rows, annual_rows = build_rows_for_stock(
                        year, raw_by_quarter, period_set
                    )

                    for period, statement_payload in quarterly_rows.items():
                        period_dir = output_root / str(year) / period
                        for statement, values in statement_payload.items():
                            row = {
                                "symbol": symbol,
                                "corp_code": corp_code,
                                "corp_name": corp_name or "",
                                "fs_div": fs_div,
                                "period": period,
                            }
                            row.update(values)
                            csv_path = period_dir / f"{statement}.csv"
                            schema_path = period_dir / f"{statement}.schema.json"
                            append_row_with_schema(
                                csv_path,
                                schema_path,
                                row,
                                ["symbol", "corp_code", "corp_name", "fs_div", "period"],
                            )

                    for period, statement_payload in annual_rows.items():
                        period_dir = output_root / str(year) / period
                        for statement, values in statement_payload.items():
                            row = {
                                "symbol": symbol,
                                "corp_code": corp_code,
                                "corp_name": corp_name or "",
                                "fs_div": fs_div,
                                "period": period,
                            }
                            row.update(values)
                            csv_path = period_dir / f"{statement}.csv"
                            schema_path = period_dir / f"{statement}.schema.json"
                            append_row_with_schema(
                                csv_path,
                                schema_path,
                                row,
                                ["symbol", "corp_code", "corp_name", "fs_div", "period"],
                            )
                except Exception as exc:
                    failed_map[symbol] = str(exc)
                    progress["failed"] = failed_map
                    save_json(progress_path, progress)
                    raise

            done_symbols.add(symbol)
            for period in periods:
                done_list = set(period_done.get(period, []))
                done_list.add(symbol)
                period_done[period] = sorted(done_list)
            if symbol in failed_map:
                failed_map.pop(symbol, None)
            progress["done"] = sorted(done_symbols)
            progress["failed"] = failed_map
            progress["period_done"] = period_done
            save_json(progress_path, progress)

            if idx % 25 == 0 or idx == total:
                print(f"[{year}] Processed {idx}/{total} stocks")

        print(f"Completed year {year}. Output in {output_root / str(year)}")


if __name__ == "__main__":
    main()

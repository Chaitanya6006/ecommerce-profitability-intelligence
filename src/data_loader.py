"""
Data Ingestion and Loading Module.
Ensures raw dataset acquisition from public source, caching, and safe loading.
Preserves original raw data integrity without modifications.
"""

import os
import urllib.request
import pandas as pd
from pathlib import Path
from src.config import (
    RAW_DATA_DIR,
    RAW_ORDERS_XLSX,
    RAW_ORDERS_CSV,
    RAW_RETURNS_CSV,
    ORDERS_SOURCE_URL,
    RETURNS_SOURCE_URL,
)


def ensure_raw_datasets(force_download: bool = False) -> None:
    """
    Downloads the Global Superstore Orders and Returns files if not already present.
    If automatic download fails, logs clear manual instructions.
    """
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Download Orders dataset if missing
    if force_download or (not RAW_ORDERS_XLSX.exists() and not RAW_ORDERS_CSV.exists()):
        print(f"Downloading raw Orders dataset from: {ORDERS_SOURCE_URL}")
        try:
            req = urllib.request.Request(
                ORDERS_SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=30) as response, open(
                RAW_ORDERS_XLSX, "wb"
            ) as out_file:
                out_file.write(response.read())
            print(f"Successfully downloaded Orders dataset: {RAW_ORDERS_XLSX} ({RAW_ORDERS_XLSX.stat().st_size} bytes)")
        except Exception as e:
            print(f"ERROR: Automatic download of Orders failed: {e}")
            print(
                "\nMANUAL ACTION REQUIRED:\n"
                f"1. Download the Global Superstore Orders dataset manually.\n"
                f"2. Place the file at: {RAW_ORDERS_XLSX.resolve()}\n"
            )
            raise

    # 2. Download Returns dataset if missing
    if force_download or not RAW_RETURNS_CSV.exists():
        print(f"Downloading raw Returns dataset from: {RETURNS_SOURCE_URL}")
        try:
            req = urllib.request.Request(
                RETURNS_SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=30) as response, open(
                RAW_RETURNS_CSV, "wb"
            ) as out_file:
                out_file.write(response.read())
            print(f"Successfully downloaded Returns dataset: {RAW_RETURNS_CSV} ({RAW_RETURNS_CSV.stat().st_size} bytes)")
        except Exception as e:
            print(f"ERROR: Automatic download of Returns failed: {e}")
            print(
                "\nMANUAL ACTION REQUIRED:\n"
                f"1. Download the Global Superstore Returns CSV manually.\n"
                f"2. Place the file at: {RAW_RETURNS_CSV.resolve()}\n"
            )
            raise


def load_raw_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Loads raw Orders and Returns datasets into Pandas DataFrames.
    If RAW_ORDERS_CSV exists, loads it for optimal I/O speed.
    Otherwise, loads RAW_ORDERS_XLSX and caches an exact raw CSV copy for fast subsequent runs.
    """
    ensure_raw_datasets()

    # Load Orders
    if RAW_ORDERS_CSV.exists():
        print(f"Loading raw Orders from CSV cache: {RAW_ORDERS_CSV}")
        df_orders = pd.read_csv(RAW_ORDERS_CSV, encoding="utf-8", low_memory=False)
    elif RAW_ORDERS_XLSX.exists():
        print(f"Loading raw Orders from Excel: {RAW_ORDERS_XLSX} (this may take ~10-15 seconds)...")
        df_orders = pd.read_excel(RAW_ORDERS_XLSX, sheet_name="Orders")
        # Cache raw CSV without altering any values for fast subsequent loads
        print(f"Caching exact raw Orders to CSV: {RAW_ORDERS_CSV}")
        df_orders.to_csv(RAW_ORDERS_CSV, index=False, encoding="utf-8")
    else:
        raise FileNotFoundError(f"Neither {RAW_ORDERS_CSV} nor {RAW_ORDERS_XLSX} found.")

    # Load Returns
    print(f"Loading raw Returns from CSV: {RAW_RETURNS_CSV}")
    df_returns = pd.read_csv(RAW_RETURNS_CSV, encoding="utf-8")

    return df_orders, df_returns


if __name__ == "__main__":
    orders, returns = load_raw_data()
    print(f"\nOrders Loaded Successfully: {orders.shape[0]:,} rows, {orders.shape[1]} columns")
    print(f"Returns Loaded Successfully: {returns.shape[0]:,} rows, {returns.shape[1]} columns")

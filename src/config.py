"""
Centralized Configuration Module for E-Commerce Profitability Intelligence Platform.
Defines project paths, dataset filenames, database URLs, and environment constants.
"""

from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DOCS_DIR = PROJECT_ROOT / "docs"
SQL_DIR = PROJECT_ROOT / "sql"

# Raw Data Paths
RAW_ORDERS_XLSX = RAW_DATA_DIR / "Global_Superstore_Orders_2016.xlsx"
RAW_ORDERS_CSV = RAW_DATA_DIR / "Global_Superstore_Orders_2016.csv"
RAW_RETURNS_CSV = RAW_DATA_DIR / "Global_Superstore_Returns_2016.csv"

# Public Dataset Download URLs
ORDERS_SOURCE_URL = (
    "https://raw.githubusercontent.com/ApurvaW/Global-Retail-Sales-and-Profit-using-Tableau"
    "/master/Global%20Superstore%20Orders%202016.xlsx"
)
RETURNS_SOURCE_URL = (
    "https://raw.githubusercontent.com/ApurvaW/Global-Retail-Sales-and-Profit-using-Tableau"
    "/master/Global%20Superstore%20Returns%202016.csv"
)

# Database Configurations
SQLITE_DB_PATH = DATA_DIR / "ecommerce_profitability.db"
SQLITE_URL = f"sqlite:///{SQLITE_DB_PATH}"

# Default PostgreSQL Connection URL (can be overridden via environment variable)
POSTGRES_URL_DEFAULT = "postgresql://postgres:postgres@localhost:5432/ecommerce_profitability"

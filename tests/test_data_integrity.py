"""
Automated Pipeline Integrity & Data Quality Tests.
Validates raw file availability, database row counts, reconciliation deltas,
and referential integrity using Python standard unittest.
"""

import unittest
import sqlite3
import pandas as pd
from pathlib import Path

from src.config import (
    RAW_ORDERS_CSV,
    RAW_ORDERS_XLSX,
    RAW_RETURNS_CSV,
    SQLITE_DB_PATH,
    PROCESSED_DATA_DIR,
)
from src.db_connector import get_sqlite_connection


class TestDataWarehouseIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Ensure connection and load summary benchmarks."""
        cls.conn = get_sqlite_connection()
        cls.cursor = cls.conn.cursor()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_01_raw_files_exist(self):
        """Verify that immutable raw files are preserved."""
        self.assertTrue(
            RAW_ORDERS_CSV.exists() or RAW_ORDERS_XLSX.exists(),
            "Raw orders dataset file is missing.",
        )
        self.assertTrue(RAW_RETURNS_CSV.exists(), "Raw returns dataset file is missing.")

    def test_02_database_file_exists(self):
        """Verify that the SQLite analytical data warehouse is populated."""
        self.assertTrue(SQLITE_DB_PATH.exists(), "SQLite database file does not exist.")
        self.assertGreater(SQLITE_DB_PATH.stat().st_size, 1_000_000, "Database size suspiciously small.")

    def test_03_table_counts(self):
        """Verify expected record counts across all star schema tables."""
        tables_expected = {
            "dim_customers": 17415,
            "dim_products": 3788,
            "dim_geography": 3856,
            "dim_shipping_mode": 4,
            "dim_date": 1468,
            "fact_returns": 1079,
            "fact_orders": 51290,
        }
        for table, expected_count in tables_expected.items():
            count = self.cursor.execute(f"SELECT COUNT(*) FROM {table};").fetchone()[0]
            self.assertEqual(
                count,
                expected_count,
                f"Mismatch in {table}: expected {expected_count}, got {count}",
            )

    def test_04_financial_reconciliation(self):
        """Verify that DB aggregates match raw transaction totals to 0.00 delta."""
        db_sales, db_profit = self.cursor.execute(
            "SELECT ROUND(SUM(sales), 2), ROUND(SUM(profit), 2) FROM fact_orders;"
        ).fetchone()

        # Compare against raw CSV
        df_raw = pd.read_csv(RAW_ORDERS_CSV, usecols=["Sales", "Profit"])
        raw_sales = round(float(df_raw["Sales"].sum()), 2)
        raw_profit = round(float(df_raw["Profit"].sum()), 2)

        self.assertAlmostEqual(db_sales, raw_sales, delta=0.5, msg="Sales volume mismatch")
        self.assertAlmostEqual(db_profit, raw_profit, delta=0.5, msg="Profit volume mismatch")

    def test_05_referential_integrity(self):
        """Verify zero orphaned foreign keys in fact_orders."""
        queries = [
            ("dim_customers", "customer_key"),
            ("dim_products", "product_key"),
            ("dim_geography", "geography_key"),
            ("dim_shipping_mode", "shipping_mode_key"),
            ("dim_date", "order_date_key"),
        ]
        for dim_tbl, key_col in queries:
            dim_key = "date_key" if "date" in key_col else key_col
            sql = f"""
                SELECT COUNT(*) FROM fact_orders f
                LEFT JOIN {dim_tbl} d ON f.{key_col} = d.{dim_key}
                WHERE d.{dim_key} IS NULL;
            """
            orphans = self.cursor.execute(sql).fetchone()[0]
            self.assertEqual(orphans, 0, f"Found {orphans} orphaned FKs for {dim_tbl}")

    def test_06_processed_csv_exports(self):
        """Verify that processed dimensional CSVs exist for Power BI."""
        expected_csvs = [
            "dim_customers.csv",
            "dim_products.csv",
            "dim_geography.csv",
            "dim_date.csv",
            "dim_shipping_mode.csv",
            "fact_orders.csv",
            "fact_returns.csv",
        ]
        for fname in expected_csvs:
            p = PROCESSED_DATA_DIR / fname
            self.assertTrue(p.exists(), f"Processed CSV missing: {fname}")
            self.assertGreater(p.stat().st_size, 0, f"Processed CSV empty: {fname}")


if __name__ == "__main__":
    unittest.main()

"""
Automated Analytical Output & KPI Verification Tests.
Tests analytical outputs, statistical boundaries, financial KPI reconciliation,
and figure file integrity using standard unittest.
"""

import unittest
import pandas as pd
from pathlib import Path

from src.config import PROJECT_ROOT, PROCESSED_DATA_DIR

ANALYTICS_DIR = PROCESSED_DATA_DIR / "analytics"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"


class TestAdvancedAnalytics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Ensure analytics files are loaded."""
        cls.kpis = pd.read_csv(ANALYTICS_DIR / "executive_kpis.csv").iloc[0]
        cls.cat = pd.read_csv(ANALYTICS_DIR / "category_profitability.csv")
        cls.disc = pd.read_csv(ANALYTICS_DIR / "discount_tier_analysis.csv")
        cls.rfm = pd.read_csv(ANALYTICS_DIR / "customer_rfm_segments.csv")
        cls.cohort = pd.read_csv(ANALYTICS_DIR / "cohort_retention_annual.csv")
        cls.monthly = pd.read_csv(ANALYTICS_DIR / "monthly_sales_growth.csv")

    def test_01_analytics_output_files_exist(self):
        """Verify that all 12 analytical output CSVs exist and are non-empty."""
        expected_files = [
            "executive_kpis.csv",
            "category_profitability.csv",
            "top_margin_bleeders.csv",
            "discount_tier_analysis.csv",
            "category_discount_elasticity.csv",
            "customer_rfm_segments.csv",
            "cohort_retention_annual.csv",
            "cohort_retention_monthly.csv",
            "monthly_sales_growth.csv",
            "order_basket_quartiles.csv",
            "shipping_mode_performance.csv",
            "regional_profitability.csv",
        ]
        for fname in expected_files:
            p = ANALYTICS_DIR / fname
            self.assertTrue(p.exists(), f"Analytics output missing: {fname}")
            self.assertGreater(p.stat().st_size, 0, f"Analytics output empty: {fname}")

    def test_02_executive_kpi_values(self):
        """Verify exact enterprise benchmarks against verified source."""
        self.assertAlmostEqual(self.kpis["total_sales_usd"], 12642501.91, delta=0.5)
        self.assertAlmostEqual(self.kpis["net_profit_usd"], 1467457.29, delta=0.5)
        self.assertEqual(int(self.kpis["total_distinct_orders"]), 25728)
        self.assertEqual(int(self.kpis["total_line_items"]), 51290)
        self.assertEqual(int(self.kpis["total_unique_customers"]), 17415)
        self.assertAlmostEqual(self.kpis["profit_margin_pct"], 11.61, delta=0.1)
        self.assertAlmostEqual(self.kpis["order_return_rate_pct"], 4.19, delta=0.1)

    def test_03_discount_tier_degradation(self):
        """Verify observed margin degradation from no discount to deep discount."""
        no_disc = self.disc[self.disc["discount_tier"].str.contains("No Discount")].iloc[0]
        deep_disc = self.disc[self.disc["discount_tier"].str.contains("Deep Discount")].iloc[0]

        # 0% discount must have high positive margin and 0% unprofitable lines
        self.assertGreater(no_disc["net_profit_margin_pct"], 20.0)
        self.assertEqual(no_disc["unprofitable_order_lines_pct"], 0.0)

        # >40% discount must have negative margin and >90% unprofitable lines
        self.assertLess(deep_disc["net_profit_margin_pct"], -50.0)
        self.assertGreater(deep_disc["unprofitable_order_lines_pct"], 90.0)

    def test_04_customer_rfm_completeness(self):
        """Verify that RFM personas partition 100% of customers."""
        total_customers = self.rfm["customer_count"].sum()
        self.assertEqual(total_customers, 17415)

        # Margin Drainers persona must have strictly negative net profit
        drainers = self.rfm[self.rfm["rfm_segment"].str.contains("Margin Drainers")].iloc[0]
        self.assertLess(drainers["total_segment_profit_usd"], 0)

    def test_05_cohort_retention_bounds(self):
        """Verify cohort retention rate boundaries."""
        # Year 0 retention must be 100%
        base_retention = self.cohort[self.cohort["year_index"] == 0]["retention_rate_pct"]
        for rate in base_retention:
            self.assertEqual(rate, 100.0)

        # Subsequent retention must be strictly within [0%, 100%]
        for rate in self.cohort["retention_rate_pct"]:
            self.assertGreaterEqual(rate, 0.0)
            self.assertLessEqual(rate, 100.0)

    def test_06_figures_generated(self):
        """Verify that all 5 publication visual reports exist and are non-empty."""
        expected_figs = [
            "monthly_sales_profit_trend.png",
            "category_profitability_breakdown.png",
            "discount_vs_profit_margin.png",
            "customer_segments_distribution.png",
            "cohort_retention_heatmap.png",
        ]
        for f in expected_figs:
            fig_path = FIGURES_DIR / f
            self.assertTrue(fig_path.exists(), f"Figure missing: {f}")
            self.assertGreater(fig_path.stat().st_size, 50_000, f"Figure unexpectedly small: {f}")


if __name__ == "__main__":
    unittest.main()

"""
Automated Statistical Pipeline & Hypothesis Testing Verification.
Validates analytical units, test statistics, p-values, effect sizes,
contingency table assumptions, and report generation using standard unittest.
"""

import unittest
from pathlib import Path

from src.config import PROJECT_ROOT
from src.statistical_analysis import (
    load_and_prepare_data,
    test_two_group_discount_margin,
    test_multi_group_discount_margin,
    calculate_spearman_correlation,
    test_discount_vs_returns,
)

STAT_FIGURES_DIR = PROJECT_ROOT / "reports" / "figures" / "statistical"
REPORT_PATH = PROJECT_ROOT / "reports" / "statistical_analysis_report.md"


class TestStatisticalAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Prepare datasets and execute test suite once."""
        cls.df_lines, cls.df_orders = load_and_prepare_data(random_seed=42)
        cls.res_two = test_two_group_discount_margin(cls.df_lines)
        cls.res_multi = test_multi_group_discount_margin(cls.df_lines)
        cls.res_sp = calculate_spearman_correlation(cls.df_lines, cls.df_orders)
        cls.res_ret = test_discount_vs_returns(cls.df_orders)

    def test_01_sample_sizes_and_units(self):
        """Verify explicit sample sizes and absence of nulls."""
        self.assertEqual(len(self.df_lines), 51290, "Line-level observation count mismatch.")
        self.assertEqual(len(self.df_orders), 25728, "Order-level observation count mismatch.")
        self.assertFalse(self.df_lines[["sales", "profit", "discount"]].isna().any().any())
        self.assertFalse(self.df_orders[["order_sales", "order_profit", "weighted_discount"]].isna().any().any())

    def test_02_two_group_welch_and_effect_size(self):
        """Verify Two-Group Welch t-test results and large effect size."""
        self.assertGreater(self.res_two["mean_undiscounted"], 20.0)
        self.assertLess(self.res_two["mean_discounted"], -15.0)
        self.assertGreater(self.res_two["welch_t_stat"], 100.0)
        self.assertLess(self.res_two["welch_p_val"], 1e-10)
        self.assertGreater(self.res_two["hedges_g"], 1.0, "Effect size should be large.")

    def test_03_multi_group_kruskal_and_eta_squared(self):
        """Verify multi-group Kruskal-Wallis test and variance explanation."""
        self.assertEqual(len(self.res_multi["groups_summary"]), 5)
        self.assertGreater(self.res_multi["kruskal_h_stat"], 10000.0)
        self.assertLess(self.res_multi["kruskal_p"], 1e-10)
        self.assertGreater(self.res_multi["eta_squared"], 0.50, "Eta-squared should exceed 0.50.")
        self.assertEqual(len(self.res_multi["pairwise_posthoc"]), 10, "5 groups should yield 10 pairwise comparisons.")

    def test_04_spearman_rank_correlation(self):
        """Verify negative monotonic correlation between discount and margin."""
        rho_line = self.res_sp["line_level"]["spearman_rho"]
        rho_order = self.res_sp["order_level"]["spearman_rho"]

        self.assertTrue(-0.75 <= rho_line <= -0.60, f"Line rho out of expected bounds: {rho_line}")
        self.assertTrue(-0.75 <= rho_order <= -0.60, f"Order rho out of expected bounds: {rho_order}")
        self.assertLess(self.res_sp["line_level"]["spearman_p"], 1e-10)
        self.assertLess(self.res_sp["order_level"]["spearman_p"], 1e-10)

    def test_05_chi_square_returns_independence(self):
        """Verify Chi-Square assumptions (cell counts >= 5) and failure to reject H0."""
        self.assertTrue(self.res_ret["all_expected_ge_5"], "Chi-Square cell count assumption violated.")
        self.assertEqual(self.res_ret["dof"], 2)
        # Empirical finding: discount does not significantly drive returns
        self.assertGreater(self.res_ret["p_value"], 0.05, "Chi-Square should fail to reject H0.")
        self.assertLess(self.res_ret["cramers_v"], 0.05, "Effect size should be negligible.")

    def test_06_statistical_artifacts_exist(self):
        """Verify that all 4 statistical figures and the report file exist and are valid."""
        figures = [
            "discount_group_distributions.png",
            "profit_margin_ci_comparison.png",
            "discount_vs_profit_margin_spearman.png",
            "return_rate_by_discount_group.png",
        ]
        for f in figures:
            p = STAT_FIGURES_DIR / f
            self.assertTrue(p.exists(), f"Figure missing: {f}")
            self.assertGreater(p.stat().st_size, 50_000, f"Figure unexpectedly small: {f}")

        self.assertTrue(REPORT_PATH.exists(), "Statistical analysis markdown report missing.")
        self.assertGreater(REPORT_PATH.stat().st_size, 5_000, "Statistical report file too small.")


if __name__ == "__main__":
    unittest.main()

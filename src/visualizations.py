"""
Executive Visualizations Module.
Generates publication-quality charts from validated analytical SQL outputs.
Saves all visual artifacts to reports/figures/ for GitHub presentation.
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from src.config import PROJECT_ROOT, PROCESSED_DATA_DIR

REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
ANALYTICS_DIR = PROCESSED_DATA_DIR / "analytics"


def set_visual_style() -> None:
    """Applies clean, high-contrast typography and theme settings."""
    sns.set_theme(style="whitegrid", font="sans-serif")
    plt.rcParams.update(
        {
            "figure.autolayout": True,
            "axes.titlesize": 14,
            "axes.titleweight": "bold",
            "axes.labelsize": 11,
            "axes.labelweight": "semibold",
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "figure.dpi": 300,
        }
    )


def plot_monthly_trend() -> Path:
    """
    1. Monthly Net Sales and Net Profit Trend (2012–2015).
    Demonstrates revenue seasonality and margin pacing.
    """
    df = pd.read_csv(ANALYTICS_DIR / "monthly_sales_growth.csv")
    df["year_month"] = pd.to_datetime(df["year_month"])

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Sales Area / Line
    color_sales = "#1f77b4"
    ax1.plot(df["year_month"], df["monthly_sales"] / 1000, color=color_sales, linewidth=2.5, label="Net Sales ($K)")
    ax1.fill_between(df["year_month"], df["monthly_sales"] / 1000, alpha=0.15, color=color_sales)
    ax1.set_ylabel("Monthly Sales ($ in Thousands USD)", color=color_sales)
    ax1.tick_params(axis="y", labelcolor=color_sales)
    ax1.yaxis.set_major_formatter("${x:,.0f}K")

    # Profit Secondary Axis
    ax2 = ax1.twinx()
    color_profit = "#2ca02c"
    ax2.plot(df["year_month"], df["monthly_profit"] / 1000, color=color_profit, linewidth=2, linestyle="--", label="Net Profit ($K)")
    ax2.set_ylabel("Monthly Net Profit ($ in Thousands USD)", color=color_profit)
    ax2.tick_params(axis="y", labelcolor=color_profit)
    ax2.yaxis.set_major_formatter("${x:,.0f}K")

    ax1.set_title("Enterprise Pacing: Monthly Net Sales & Profit Trend (2012–2015)", pad=15)
    ax1.set_xlabel("Order Month")
    ax1.grid(True, linestyle=":", alpha=0.6)

    # Combined Legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=True)

    out_path = FIGURES_DIR / "monthly_sales_profit_trend.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    return out_path


def plot_category_profitability() -> Path:
    """
    2. Sub-Category Net Profitability Breakdown.
    Highlights profitable lines vs margin bleeders (Tables, Bookcases).
    """
    df = pd.read_csv(ANALYTICS_DIR / "category_profitability.csv")
    df = df.sort_values(by="total_net_profit", ascending=True).reset_index(drop=True)

    colors = ["#d62728" if p < 0 else "#2ca02c" for p in df["total_net_profit"]]

    fig, ax = plt.subplots(figsize=(11, 7))
    bars = ax.barh(df["sub_category"], df["total_net_profit"] / 1000, color=colors, height=0.7)

    ax.axvline(0, color="black", linewidth=1, linestyle="-")
    ax.set_title("Sub-Category Cumulative Net Profit Contribution ($ in Thousands USD)", pad=15)
    ax.set_xlabel("Net Profit ($ in Thousands USD)")
    ax.set_ylabel("Merchandise Sub-Category")
    ax.xaxis.set_major_formatter("${x:,.0f}K")

    # Add data labels
    for bar in bars:
        width = bar.get_width()
        ha = "left" if width >= 0 else "right"
        offset = 3 if width >= 0 else -3
        ax.annotate(
            f"${width:,.1f}K",
            xy=(width, bar.get_y() + bar.get_height() / 2),
            xytext=(offset, 0),
            textcoords="offset points",
            ha=ha,
            va="center",
            fontsize=8.5,
            fontweight="semibold",
        )

    out_path = FIGURES_DIR / "category_profitability_breakdown.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    return out_path


def plot_discount_vs_margin() -> Path:
    """
    3. Discount Tier vs Profit Margin and Loss Propensity.
    Visually documents the margin cliff when discount rates exceed 20%.
    """
    df = pd.read_csv(ANALYTICS_DIR / "discount_tier_analysis.csv")

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Margin Bar Chart
    colors = ["#2ca02c" if m >= 0 else "#d62728" for m in df["net_profit_margin_pct"]]
    bars = ax1.bar(df["discount_tier"], df["net_profit_margin_pct"], color=colors, width=0.55, alpha=0.85, label="Net Margin %")
    ax1.set_ylabel("Net Profit Margin (%)", color="#333333")
    ax1.axhline(0, color="black", linewidth=1)
    ax1.set_xticks(range(len(df)))
    ax1.set_xticklabels(df["discount_tier"], rotation=15, ha="right")
    ax1.set_title("Discount Bracket Margin Cliff & Loss-Making Transaction Ratio", pad=15)

    # Line Chart for Unprofitable Percentage
    ax2 = ax1.twinx()
    ax2.plot(df["discount_tier"], df["unprofitable_order_lines_pct"], color="#ff7f0e", marker="o", linewidth=2.5, label="% Unprofitable Transactions")
    ax2.set_ylabel("% of Order Lines Incurring Net Loss", color="#ff7f0e")
    ax2.tick_params(axis="y", labelcolor="#ff7f0e")
    ax2.set_ylim(0, 105)

    # Value labels
    for bar in bars:
        height = bar.get_height()
        va = "bottom" if height >= 0 else "top"
        ax1.annotate(
            f"{height:.1f}%",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3 if height >= 0 else -10),
            textcoords="offset points",
            ha="center",
            va=va,
            fontweight="bold",
            fontsize=9,
        )

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", frameon=True)

    out_path = FIGURES_DIR / "discount_vs_profit_margin.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    return out_path


def plot_customer_rfm_segments() -> Path:
    """
    4. Customer RFM Segmentation: Customer Share vs Profit Contribution.
    """
    df = pd.read_csv(ANALYTICS_DIR / "customer_rfm_segments.csv")
    df = df.sort_values(by="total_segment_profit_usd", ascending=True)

    fig, ax = plt.subplots(figsize=(11, 6))
    colors = ["#d62728" if p < 0 else "#1f77b4" for p in df["total_segment_profit_usd"]]
    bars = ax.barh(df["rfm_segment"], df["total_segment_profit_usd"] / 1000, color=colors, height=0.65)

    ax.axvline(0, color="black", linewidth=1)
    ax.set_title("Customer RFM Personas: Total Net Profit Contribution ($ in Thousands USD)", pad=15)
    ax.set_xlabel("Net Profit Contribution ($ in Thousands USD)")
    ax.set_ylabel("RFM Segment Persona")
    ax.xaxis.set_major_formatter("${x:,.0f}K")

    for bar in bars:
        width = bar.get_width()
        ha = "left" if width >= 0 else "right"
        offset = 3 if width >= 0 else -3
        ax.annotate(
            f"${width:,.0f}K",
            xy=(width, bar.get_y() + bar.get_height() / 2),
            xytext=(offset, 0),
            textcoords="offset points",
            ha=ha,
            va="center",
            fontsize=9,
            fontweight="bold",
        )

    out_path = FIGURES_DIR / "customer_segments_distribution.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    return out_path


def plot_cohort_retention_heatmap() -> Path:
    """
    5. Annual Customer Cohort Retention Heatmap.
    Visualizes repeat customer retention across multi-year vintages.
    """
    df = pd.read_csv(ANALYTICS_DIR / "cohort_retention_annual.csv")

    pivot_retention = df.pivot(
        index="cohort_year", columns="year_index", values="retention_rate_pct"
    )

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.heatmap(
        pivot_retention,
        annot=True,
        fmt=".1f",
        cmap="Blues",
        cbar_kws={"label": "Retention Rate (%)"},
        linewidths=1,
        linecolor="white",
        ax=ax,
        vmin=0,
        vmax=100,
    )

    ax.set_title("Customer Cohort Retention Matrix (Annual Acquisition Vintage)", pad=15)
    ax.set_xlabel("Years Elapsed Since First Purchase (Year Index)")
    ax.set_ylabel("Cohort Vintage (First Order Year)")
    ax.set_xticklabels([f"Year {int(c)}" for c in pivot_retention.columns])

    out_path = FIGURES_DIR / "cohort_retention_heatmap.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    return out_path


def generate_all_visualizations() -> list[Path]:
    """Orchestrates generation of all visual reporting artifacts."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    set_visual_style()

    print("\n" + "=" * 70)
    print("GENERATING EXECUTIVE VISUALIZATION REPORTS")
    print("=" * 70)

    plots = [
        plot_monthly_trend(),
        plot_category_profitability(),
        plot_discount_vs_margin(),
        plot_customer_rfm_segments(),
        plot_cohort_retention_heatmap(),
    ]

    for p in plots:
        print(f"  [OK] Generated Chart: {p.relative_to(PROJECT_ROOT)} ({p.stat().st_size:,} bytes)")

    print("=" * 70 + "\n")
    return plots


if __name__ == "__main__":
    generate_all_visualizations()

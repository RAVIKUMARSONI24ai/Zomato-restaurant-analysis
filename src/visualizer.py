"""
Visualization module for Zomato Restaurant Analysis.
Generates clean, aesthetic, publication-ready figures for reports and GitHub README.
"""
from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Aesthetic styling configuration
PALETTE_PRIMARY = "#E23744"   # Zomato Red
PALETTE_SECONDARY = "#1E293B" # Deep Slate
PALETTE_ACCENT = "#0EA5E9"    # Sky Blue
PALETTE_SUCCESS = "#10B981"   # Emerald
PALETTE_AMBER = "#F59E0B"     # Amber
BG_COLOR = "#FFFFFF"

plt.rcParams.update({
    "font.sans-serif": ["Segoe UI", "Arial", "Helvetica", "DejaVu Sans"],
    "font.family": "sans-serif",
    "figure.facecolor": BG_COLOR,
    "axes.facecolor": BG_COLOR,
    "axes.edgecolor": "#CBD5E1",
    "axes.linewidth": 0.8,
    "grid.color": "#F1F5F9",
    "grid.linestyle": "--",
    "grid.alpha": 0.7,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 10.5,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
})

DEFAULT_FIGURES_DIR = Path(__file__).resolve().parent.parent / "reports" / "figures"


def save_or_show(fig: plt.Figure, filename: Optional[str] = None, output_dir: Optional[Path] = None):
    """Saves figure with tight layout or shows if no filename is passed."""
    if filename:
        target_dir = output_dir if output_dir else DEFAULT_FIGURES_DIR
        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / filename
        fig.savefig(file_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        return str(file_path)
    else:
        plt.show()
        return None


def plot_ratings_distribution(df: pd.DataFrame, filename: Optional[str] = "01_ratings_distribution.png"):
    """Plots clean distribution of restaurant ratings."""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    
    rated_df = df[df["rating"].notna()]
    mean_val = rated_df["rating"].mean()
    median_val = rated_df["rating"].median()
    
    sns.histplot(
        rated_df["rating"],
        bins=20,
        kde=True,
        color=PALETTE_PRIMARY,
        edgecolor="white",
        linewidth=1.2,
        alpha=0.8,
        ax=ax
    )
    
    ax.axvline(mean_val, color="#B91C1C", linestyle="--", linewidth=1.5, label=f"Mean: {mean_val:.2f}")
    ax.axvline(median_val, color=PALETTE_SECONDARY, linestyle="-", linewidth=1.8, label=f"Median: {median_val:.2f}")
    
    ax.set_title("Distribution of Restaurant Ratings", pad=12, loc="left", color="#0F172A")
    ax.set_xlabel("Rating (out of 5.0)", labelpad=8)
    ax.set_ylabel("Number of Restaurants", labelpad=8)
    ax.legend(frameon=True, facecolor="#F8FAFC", edgecolor="#E2E8F0")
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    
    return save_or_show(fig, filename)


def plot_top_cuisines(df: pd.DataFrame, filename: Optional[str] = "02_top_cuisines.png", top_n: int = 10):
    """Plots horizontal bar chart of top cuisines."""
    from analysis import get_top_cuisines
    cuisines_agg = get_top_cuisines(df, top_n=top_n)
    
    fig, ax = plt.subplots(figsize=(9, 5))
    
    colors = [PALETTE_PRIMARY if i == 0 else "#475569" for i in range(len(cuisines_agg))]
    
    bars = ax.barh(
        cuisines_agg["cuisine"][::-1],
        cuisines_agg["restaurant_count"][::-1],
        color=colors[::-1],
        height=0.65,
        edgecolor="none"
    )
    
    # Annotate bar counts
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + (cuisines_agg["restaurant_count"].max() * 0.01),
            bar.get_y() + bar.get_height() / 2,
            f"{int(width):,}",
            va="center",
            ha="left",
            fontsize=9,
            color="#334155",
            fontweight="semibold"
        )
        
    ax.set_title(f"Top {top_n} Most Popular Cuisines", pad=14, loc="left", color="#0F172A")
    ax.set_xlabel("Restaurant Count", labelpad=8)
    ax.set_ylabel("", labelpad=0)
    ax.set_xlim(0, cuisines_agg["restaurant_count"].max() * 1.12)
    ax.grid(axis="x", linestyle="--", alpha=0.6)
    
    return save_or_show(fig, filename)


def plot_online_order_comparison(df: pd.DataFrame, filename: Optional[str] = "03_online_order_vs_rating.png"):
    """Compares ratings and volume between online ordering enabled vs disabled."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))
    
    # 1. Rating comparison boxplot
    sns.boxplot(
        data=df,
        x="online_order",
        y="rating_imputed",
        hue="online_order",
        legend=False,
        palette=[PALETTE_PRIMARY, "#94A3B8"],
        width=0.45,
        fliersize=2.5,
        boxprops=dict(alpha=0.9),
        ax=ax1
    )
    ax1.set_title("Rating Distribution by Online Order", loc="left", pad=10, fontsize=11)
    ax1.set_xlabel("Online Ordering Available", labelpad=6)
    ax1.set_ylabel("Rating (Imputed)", labelpad=6)
    ax1.grid(axis="y", linestyle="--", alpha=0.6)
    
    # 2. Total count share pie/donut
    order_counts = df["online_order"].value_counts()
    colors = [PALETTE_PRIMARY, "#E2E8F0"]
    wedges, texts, autotexts = ax2.pie(
        order_counts,
        labels=[f"{k} ({v:,})" for k, v in order_counts.items()],
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2)
    )
    for at in autotexts:
        at.set_fontsize(9.5)
        at.set_fontweight("bold")
        
    ax2.set_title("Online Ordering Adoption", loc="center", pad=10, fontsize=11)
    
    fig.suptitle("Impact of Online Ordering Availability", fontsize=13, fontweight="bold", y=1.03, color="#0F172A")
    plt.tight_layout()
    return save_or_show(fig, filename)


def plot_cost_vs_rating(df: pd.DataFrame, filename: Optional[str] = "04_cost_vs_rating_scatter.png"):
    """Scatter plot illustrating relation between dining cost for two and customer ratings."""
    fig, ax = plt.subplots(figsize=(9, 5))
    
    clean_sample = df.dropna(subset=["rating", "cost_for_two"]).copy()
    
    scatter = ax.scatter(
        clean_sample["cost_for_two"],
        clean_sample["rating"],
        c=clean_sample["votes"],
        cmap="Reds",
        alpha=0.7,
        s=35,
        edgecolors="none"
    )
    
    # Trendline
    z = np.polyfit(clean_sample["cost_for_two"], clean_sample["rating"], 1)
    p = np.poly1d(z)
    x_range = np.linspace(clean_sample["cost_for_two"].min(), clean_sample["cost_for_two"].max(), 100)
    ax.plot(x_range, p(x_range), color=PALETTE_SECONDARY, linewidth=2, linestyle="--", label=f"Trend (Slope: +{z[0]*1000:.2f}/₹1k)")
    
    cbar = plt.colorbar(scatter, ax=ax, pad=0.02)
    cbar.set_label("Review Votes Count", rotation=270, labelpad=14, fontsize=9.5)
    
    ax.set_title("Cost For Two vs Restaurant Rating", pad=12, loc="left", color="#0F172A")
    ax.set_xlabel("Approximate Cost for Two People (₹)", labelpad=8)
    ax.set_ylabel("Rating (out of 5.0)", labelpad=8)
    ax.legend(frameon=True, facecolor="#F8FAFC", edgecolor="#E2E8F0", loc="lower right")
    ax.grid(True, linestyle="--", alpha=0.5)
    
    return save_or_show(fig, filename)


def plot_top_chains(df: pd.DataFrame, filename: Optional[str] = "05_top_restaurant_chains.png", top_n: int = 10):
    """Plots top restaurant brands by branch count."""
    from analysis import get_top_chains
    chains_df = get_top_chains(df, top_n=top_n)
    
    fig, ax = plt.subplots(figsize=(9, 5))
    
    bars = ax.barh(
        chains_df["name"][::-1],
        chains_df["outlets"][::-1],
        color=PALETTE_SECONDARY,
        height=0.6,
        edgecolor="none"
    )
    
    for bar, rating in zip(bars, chains_df["avg_rating"][::-1]):
        width = bar.get_width()
        ax.text(
            width + 0.15,
            bar.get_y() + bar.get_height() / 2,
            f"{int(width)} outlets (Rating: {rating:.1f})",
            va="center",
            ha="left",
            fontsize=8.5,
            color="#334155"
        )
        
    ax.set_title(f"Top {top_n} Restaurant Brands by Presence", pad=12, loc="left", color="#0F172A")
    ax.set_xlabel("Number of Outlets / Locations", labelpad=8)
    ax.set_xlim(0, chains_df["outlets"].max() * 1.35)
    ax.grid(axis="x", linestyle="--", alpha=0.6)
    
    return save_or_show(fig, filename)


def plot_top_locations(df: pd.DataFrame, filename: Optional[str] = "06_top_locations_by_restaurants.png", top_n: int = 10):
    """Plots top dining hotspots by restaurant concentration."""
    from analysis import get_location_summary
    loc_df = get_location_summary(df, min_count=5).head(top_n)
    
    fig, ax = plt.subplots(figsize=(9, 5))
    
    sns.barplot(
        data=loc_df,
        y="location",
        x="restaurant_count",
        hue="location",
        legend=False,
        palette="ch:s=-.2,r=.6",
        ax=ax
    )
    
    for i, p in enumerate(ax.patches):
        width = p.get_width()
        avg_cost = loc_df.iloc[i]["avg_cost"]
        ax.annotate(
            f"{int(width)} (Avg: ₹{int(avg_cost):,})",
            (width + 2, p.get_y() + p.get_height() / 2),
            ha="left",
            va="center",
            fontsize=8.5,
            color="#334155"
        )
        
    ax.set_title(f"Top {top_n} Food Hubs by Restaurant Density", pad=12, loc="left", color="#0F172A")
    ax.set_xlabel("Number of Restaurants", labelpad=8)
    ax.set_ylabel("", labelpad=0)
    ax.set_xlim(0, loc_df["restaurant_count"].max() * 1.25)
    ax.grid(axis="x", linestyle="--", alpha=0.6)
    
    return save_or_show(fig, filename)


def generate_all_visualizations(df: pd.DataFrame):
    """Generates all 6 core publication figures in one call."""
    print("Generating aesthetic figures...")
    plot_ratings_distribution(df)
    plot_top_cuisines(df)
    plot_online_order_comparison(df)
    plot_cost_vs_rating(df)
    plot_top_chains(df)
    plot_top_locations(df)
    print("All figures successfully saved to reports/figures/.")


if __name__ == "__main__":
    from data_loader import load_clean_data
    clean_df = load_clean_data()
    generate_all_visualizations(clean_df)

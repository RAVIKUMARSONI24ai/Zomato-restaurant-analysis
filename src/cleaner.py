"""
Data cleaning and preprocessing module for Zomato Restaurant Analysis.
Transforms raw messy data into a standardized, analysis-ready format.
"""
import re
from pathlib import Path
from typing import Optional, Tuple, Any
import numpy as np
import pandas as pd

DEFAULT_PROCESSED_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "zomato_cleaned.csv"


def clean_rate(val: Any) -> Optional[float]:
    """
    Cleans raw rate string.
    Examples:
        '4.1/5' -> 4.1
        'NEW'   -> np.nan
        '-'     -> np.nan
    """
    if pd.isna(val):
        return np.nan
    val_str = str(val).strip()
    if val_str in ("NEW", "-", ""):
        return np.nan
    match = re.search(r"(\d+(\.\d+)?)", val_str)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return np.nan
    return np.nan


def clean_cost(val: Any) -> Optional[float]:
    """
    Cleans approx_cost_for_two_people string.
    Example: '1,200' -> 1200.0
    """
    if pd.isna(val):
        return np.nan
    val_str = str(val).replace(",", "").strip()
    try:
        return float(val_str)
    except ValueError:
        return np.nan


def categorize_cost(cost: float) -> str:
    """Categorizes cost for two into intuitive price tiers."""
    if pd.isna(cost):
        return "Unknown"
    if cost <= 400:
        return "Budget (< ₹400)"
    elif cost <= 800:
        return "Mid-Range (₹400 - ₹800)"
    elif cost <= 1500:
        return "Premium (₹800 - ₹1,500)"
    else:
        return "Luxury (> ₹1,500)"


def categorize_rating(rate: float) -> str:
    """Categorizes rating into quality tiers."""
    if pd.isna(rate):
        return "Unrated / New"
    if rate < 3.5:
        return "Below Average (< 3.5)"
    elif rate < 4.0:
        return "Good (3.5 - 3.9)"
    elif rate < 4.5:
        return "Very Good (4.0 - 4.4)"
    else:
        return "Exceptional (4.5 - 5.0)"


def clean_zomato_data(
    df: pd.DataFrame,
    save_path: Optional[Path | str] = None
) -> Tuple[pd.DataFrame, dict]:
    """
    Executes the complete cleaning pipeline on raw Zomato data.
    
    Returns:
        Tuple[pd.DataFrame, dict]: Cleaned dataframe and metadata metrics on cleaning.
    """
    initial_rows = len(df)
    
    # 1. Deduplicate records
    df = df.drop_duplicates(subset=["name", "address", "location"], keep="first").copy()
    duplicates_removed = initial_rows - len(df)
    
    # 2. Clean numeric columns
    df["rating"] = df["rate"].apply(clean_rate)
    df["cost_for_two"] = df["approx_cost_for_two_people"].apply(clean_cost)
    df["votes"] = pd.to_numeric(df["votes"], errors="coerce").fillna(0).astype(int)
    
    # Impute missing cost using median by rest_type where available
    median_cost_overall = df["cost_for_two"].median()
    df["cost_for_two"] = df.groupby("rest_type")["cost_for_two"].transform(
        lambda s: s.fillna(s.median() if not pd.isna(s.median()) else median_cost_overall)
    )
    df["cost_for_two"] = df["cost_for_two"].fillna(median_cost_overall)
    
    # Impute missing rating with overall median rating
    median_rating = df["rating"].median()
    df["rating_imputed"] = df["rating"].fillna(median_rating)
    
    # 3. Clean categorical text
    text_cols = ["name", "location", "rest_type", "cuisines", "listed_in_type", "listed_in_city"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace({"nan": "Not Available", "None": "Not Available"})
            
    # Standardize online_order and book_table
    df["online_order"] = df["online_order"].fillna("No").str.strip().str.capitalize()
    df["book_table"] = df["book_table"].fillna("No").str.strip().str.capitalize()
    
    # 4. Feature Engineering
    df["cost_category"] = df["cost_for_two"].apply(categorize_cost)
    df["rating_category"] = df["rating"].apply(categorize_rating)
    
    # Primary cuisine & count of cuisines
    def parse_primary_cuisine(val: Any) -> str:
        if pd.isna(val) or str(val).strip() in ("Not Available", "nan", ""):
            return "Other"
        return str(val).split(",")[0].strip()

    def count_cuisines(val: Any) -> int:
        if pd.isna(val) or str(val).strip() in ("Not Available", "nan", ""):
            return 0
        return len(str(val).split(","))

    df["primary_cuisine"] = df["cuisines"].apply(parse_primary_cuisine)
    df["cuisine_count"] = df["cuisines"].apply(count_cuisines)
    
    # Save cleaned data
    out_file = Path(save_path) if save_path else DEFAULT_PROCESSED_PATH
    out_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_file, index=False)
    
    metrics = {
        "initial_rows": initial_rows,
        "final_rows": len(df),
        "duplicates_removed": duplicates_removed,
        "clean_ratings_count": int(df["rating"].notna().sum()),
        "imputed_ratings_count": int(df["rating"].isna().sum()),
        "output_file": str(out_file),
    }
    
    return df, metrics


if __name__ == "__main__":
    from data_loader import load_raw_data
    raw = load_raw_data()
    cleaned_df, stats = clean_zomato_data(raw)
    print("Data cleaning completed successfully:")
    for k, v in stats.items():
        print(f"  - {k}: {v}")

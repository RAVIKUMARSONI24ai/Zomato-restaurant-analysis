"""
Core analytical module for Zomato Restaurant Analysis.
Computes KPIs, distribution metrics, aggregations, and comparative insights.
"""
from typing import Dict, Any, List
import pandas as pd
import numpy as np


def get_key_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculates top-level KPI metrics for the executive overview."""
    total_records = len(df)
    unique_brands = df["name"].nunique()
    
    rated_df = df[df["rating"].notna()]
    avg_rating = round(float(rated_df["rating"].mean()), 2) if not rated_df.empty else 0.0
    median_rating = round(float(rated_df["rating"].median()), 2) if not rated_df.empty else 0.0
    
    avg_cost = round(float(df["cost_for_two"].mean()), 0)
    median_cost = round(float(df["cost_for_two"].median()), 0)
    
    online_order_pct = round(float((df["online_order"] == "Yes").mean() * 100), 1)
    book_table_pct = round(float((df["book_table"] == "Yes").mean() * 100), 1)
    total_votes = int(df["votes"].sum())
    
    return {
        "total_restaurants": total_records,
        "unique_brands": unique_brands,
        "avg_rating": avg_rating,
        "median_rating": median_rating,
        "avg_cost_for_two": avg_cost,
        "median_cost_for_two": median_cost,
        "online_order_pct": online_order_pct,
        "book_table_pct": book_table_pct,
        "total_votes": total_votes,
    }


def get_top_cuisines(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Parses comma-separated cuisines and aggregates counts and mean ratings.
    """
    records = []
    for _, row in df.iterrows():
        cuisines_str = str(row.get("cuisines", ""))
        rating = row.get("rating")
        cost = row.get("cost_for_two")
        
        if cuisines_str and cuisines_str != "Not Available":
            for c in cuisines_str.split(","):
                c_clean = c.strip()
                if c_clean:
                    records.append({"cuisine": c_clean, "rating": rating, "cost_for_two": cost})
                    
    cuisine_df = pd.DataFrame(records)
    if cuisine_df.empty:
        return pd.DataFrame()
        
    agg = cuisine_df.groupby("cuisine").agg(
        restaurant_count=("rating", "count"),
        avg_rating=("rating", "mean"),
        avg_cost=("cost_for_two", "mean")
    ).reset_index()
    
    agg["avg_rating"] = agg["avg_rating"].round(2)
    agg["avg_cost"] = agg["avg_cost"].round(0)
    agg["share_pct"] = ((agg["restaurant_count"] / len(df)) * 100).round(1)
    
    return agg.sort_values(by="restaurant_count", ascending=False).head(top_n)


def get_location_summary(df: pd.DataFrame, min_count: int = 15) -> pd.DataFrame:
    """Aggregates restaurant density, rating, and affordability by neighborhood/location."""
    loc_agg = df.groupby("location").agg(
        restaurant_count=("name", "count"),
        avg_rating=("rating_imputed", "mean"),
        avg_cost=("cost_for_two", "mean"),
        online_order_pct=("online_order", lambda s: round((s == "Yes").mean() * 100, 1)),
        book_table_pct=("book_table", lambda s: round((s == "Yes").mean() * 100, 1)),
        total_votes=("votes", "sum")
    ).reset_index()
    
    loc_agg["avg_rating"] = loc_agg["avg_rating"].round(2)
    loc_agg["avg_cost"] = loc_agg["avg_cost"].round(0)
    
    filtered = loc_agg[loc_agg["restaurant_count"] >= min_count]
    return filtered.sort_values(by="restaurant_count", ascending=False)


def get_online_order_impact(df: pd.DataFrame) -> pd.DataFrame:
    """Analyzes differences between restaurants with online ordering vs offline only."""
    res = df.groupby("online_order").agg(
        count=("name", "count"),
        avg_rating=("rating_imputed", "mean"),
        median_rating=("rating_imputed", "median"),
        avg_cost=("cost_for_two", "mean"),
        avg_votes=("votes", "mean")
    ).reset_index()
    
    res["pct_of_total"] = ((res["count"] / len(df)) * 100).round(1)
    res["avg_rating"] = res["avg_rating"].round(2)
    res["avg_cost"] = res["avg_cost"].round(0)
    res["avg_votes"] = res["avg_votes"].round(0)
    return res


def get_table_booking_impact(df: pd.DataFrame) -> pd.DataFrame:
    """Analyzes differences between restaurants with table booking vs walk-in only."""
    res = df.groupby("book_table").agg(
        count=("name", "count"),
        avg_rating=("rating_imputed", "mean"),
        median_rating=("rating_imputed", "median"),
        avg_cost=("cost_for_two", "mean"),
        avg_votes=("votes", "mean")
    ).reset_index()
    
    res["pct_of_total"] = ((res["count"] / len(df)) * 100).round(1)
    res["avg_rating"] = res["avg_rating"].round(2)
    res["avg_cost"] = res["avg_cost"].round(0)
    res["avg_votes"] = res["avg_votes"].round(0)
    return res


def get_top_chains(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Identifies top restaurant brands by branch count and customer ratings."""
    chains = df.groupby("name").agg(
        outlets=("location", "nunique"),
        avg_rating=("rating_imputed", "mean"),
        avg_cost=("cost_for_two", "mean"),
        total_votes=("votes", "sum")
    ).reset_index()
    
    chains["avg_rating"] = chains["avg_rating"].round(2)
    chains["avg_cost"] = chains["avg_cost"].round(0)
    
    return chains.sort_values(by=["outlets", "avg_rating"], ascending=[False, False]).head(top_n)


def get_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates correlation between numerical variables."""
    numeric_df = df[["rating_imputed", "cost_for_two", "votes", "cuisine_count"]].copy()
    numeric_df.columns = ["Rating", "Cost For Two", "Votes", "Cuisine Variety"]
    return numeric_df.corr().round(3)

"""
Business & Commercial Intelligence Module for Zomato.
Provides market opportunity gap analysis, commission/GMV revenue modeling,
and competitor benchmarking for restaurateurs and Zomato category managers.
"""
from typing import Dict, Any, List
import pandas as pd
import numpy as np


def compute_market_opportunity_matrix(df: pd.DataFrame, min_city_presence: int = 5) -> pd.DataFrame:
    """
    Computes White-Space / Opportunity Index across Location and Cuisine combinations.
    Identifies high-demand, low-competition zones for partner acquisition.
    """
    records = []
    for _, row in df.iterrows():
        cuisines_str = str(row.get("cuisines", ""))
        location = row.get("location")
        rating = row.get("rating_imputed")
        cost = row.get("cost_for_two")
        
        if cuisines_str and cuisines_str != "Not Available" and pd.notna(location):
            for c in cuisines_str.split(","):
                c_clean = c.strip()
                if c_clean:
                    records.append({
                        "location": location,
                        "cuisine": c_clean,
                        "rating": rating,
                        "cost_for_two": cost
                    })
                    
    long_df = pd.DataFrame(records)
    if long_df.empty:
        return pd.DataFrame()
        
    grouped = long_df.groupby(["location", "cuisine"]).agg(
        supply_count=("rating", "count"),
        avg_rating=("rating", "mean"),
        avg_cost=("cost_for_two", "mean")
    ).reset_index()
    
    # Filter out very obscure combinations
    grouped = grouped[grouped["supply_count"] >= 1].copy()
    
    # Market Opportunity Score formula:
    # High average customer rating + lower existing restaurant count = higher opportunity for new onboarding
    grouped["opportunity_score"] = (
        (grouped["avg_rating"] ** 2) / np.log2(grouped["supply_count"] + 2)
    ).round(2)
    
    def classify_quadrant(row):
        is_high_rating = row["avg_rating"] >= 3.9
        is_low_supply = row["supply_count"] <= 6
        if is_high_rating and is_low_supply:
            return "High Opportunity (Underserved)"
        elif is_high_rating and not is_low_supply:
            return "Proven Hotspot (High Demand)"
        elif not is_high_rating and is_low_supply:
            return "Niche / Developing"
        else:
            return "Saturated / High Competition"
            
    grouped["market_quadrant"] = grouped.apply(classify_quadrant, axis=1)
    grouped["avg_rating"] = grouped["avg_rating"].round(2)
    grouped["avg_cost"] = grouped["avg_cost"].round(0)
    
    return grouped.sort_values(by="opportunity_score", ascending=False)


def simulate_platform_revenue(
    df: pd.DataFrame,
    commission_rate: float = 0.20,
    table_booking_fee: float = 35.0,
    avg_delivery_orders_monthly: int = 450,
    avg_tables_booked_monthly: int = 80
) -> Dict[str, Any]:
    """
    Simulates Zomato platform GMV and revenue generation across partner restaurants.
    
    Args:
        df: Cleaned restaurant dataframe
        commission_rate: Percentage commission taken on online deliveries (e.g. 20%)
        table_booking_fee: Fee earned per table reservation (in INR)
        avg_delivery_orders_monthly: Estimated monthly deliveries per online-enabled restaurant
        avg_tables_booked_monthly: Estimated monthly bookings per table-enabled restaurant
    """
    online_count = int((df["online_order"] == "Yes").sum())
    booking_count = int((df["book_table"] == "Yes").sum())
    
    # Average order value is estimated around 55% of approx_cost_for_two
    avg_aov = float(df[df["online_order"] == "Yes"]["cost_for_two"].mean() * 0.55) if online_count > 0 else 350.0
    
    monthly_delivery_orders = online_count * avg_delivery_orders_monthly
    monthly_delivery_gmv = monthly_delivery_orders * avg_aov
    monthly_commission_revenue = monthly_delivery_gmv * commission_rate
    
    monthly_table_bookings = booking_count * avg_tables_booked_monthly
    monthly_booking_revenue = monthly_table_bookings * table_booking_fee
    
    monthly_total_revenue = monthly_commission_revenue + monthly_booking_revenue
    annual_total_revenue = monthly_total_revenue * 12
    annual_gmv = monthly_delivery_gmv * 12
    
    return {
        "online_partners": online_count,
        "table_booking_partners": booking_count,
        "estimated_aov": round(avg_aov, 0),
        "monthly_orders": int(monthly_delivery_orders),
        "monthly_gmv": round(monthly_delivery_gmv, 0),
        "annual_gmv": round(annual_gmv, 0),
        "monthly_revenue": round(monthly_total_revenue, 0),
        "annual_revenue": round(annual_total_revenue, 0),
        "delivery_commission_share_pct": round((monthly_commission_revenue / monthly_total_revenue) * 100, 1) if monthly_total_revenue > 0 else 0.0
    }


def benchmark_restaurant(df: pd.DataFrame, restaurant_name: str) -> Dict[str, Any]:
    """
    Compares a given restaurant against its neighborhood and cuisine peers.
    """
    matches = df[df["name"].str.lower() == restaurant_name.lower()]
    if matches.empty:
        return {"found": False, "message": f"Restaurant '{restaurant_name}' not found."}
        
    sample = matches.iloc[0]
    loc = sample["location"]
    cuisine = sample["primary_cuisine"]
    rate = sample["rating_imputed"]
    cost = sample["cost_for_two"]
    
    loc_peers = df[df["location"] == loc]
    cuisine_peers = df[df["primary_cuisine"] == cuisine]
    
    loc_avg_rate = round(float(loc_peers["rating_imputed"].mean()), 2)
    loc_avg_cost = round(float(loc_peers["cost_for_two"].mean()), 0)
    cuisine_avg_rate = round(float(cuisine_peers["rating_imputed"].mean()), 2)
    cuisine_avg_cost = round(float(cuisine_peers["cost_for_two"].mean()), 0)
    
    # Competitive verdict
    if rate >= loc_avg_rate and cost <= loc_avg_cost:
        positioning = "🌟 Value Champion (Higher rating than neighbors at lower/equal cost)"
    elif rate >= loc_avg_rate and cost > loc_avg_cost:
        positioning = "💎 Premium Destination (Justifies premium price with superior ratings)"
    elif rate < loc_avg_rate and cost <= loc_avg_cost:
        positioning = "🏷️ Budget Play (Competitive pricing but room for service/quality improvement)"
    else:
        positioning = "⚠️ High Risk / Overpriced (Priced above average but lagging in customer ratings)"
        
    return {
        "found": True,
        "name": sample["name"],
        "location": loc,
        "primary_cuisine": cuisine,
        "rating": rate,
        "cost_for_two": cost,
        "outlets": len(matches),
        "loc_avg_rating": loc_avg_rate,
        "loc_avg_cost": loc_avg_cost,
        "cuisine_avg_rating": cuisine_avg_rate,
        "cuisine_avg_cost": cuisine_avg_cost,
        "rating_diff_from_local": round(rate - loc_avg_rate, 2),
        "cost_diff_from_local": round(cost - loc_avg_cost, 0),
        "positioning": positioning
    }

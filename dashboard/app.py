"""
Zomato Restaurant Analysis & Market Intelligence Dashboard
Built with Streamlit and Plotly for clean, uncluttered interactive exploration.
Includes Business White-Space Analytics, Revenue Simulation, and ML Rating Predictor.
"""
from pathlib import Path
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Ensure src is importable
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_metrics import compute_market_opportunity_matrix, simulate_platform_revenue, benchmark_restaurant
from ml_model import RestaurantRatingPredictor

# -----------------------------------------------------------------------------
# App Configuration & Modern Clean Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Zomato Analytics | Insights & Business Intelligence",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main {
        background-color: #F8FAFC;
    }
    
    /* Metrics Card Styling */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 16px 20px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: transform 0.15s ease-in-out;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #CBD5E1;
        transform: translateY(-2px);
    }
    div[data-testid="stMetric"] label {
        font-size: 0.80rem !important;
        font-weight: 600 !important;
        color: #64748B !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        color: #0F172A !important;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #FFFFFF;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        color: #475569;
        font-size: 0.90rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #E23744 !important;
        color: #FFFFFF !important;
    }
    
    /* Header hero */
    .hero-container {
        padding: 14px 0 6px 0;
        margin-bottom: 12px;
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #0F172A;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .hero-title span {
        color: #E23744;
    }
    .hero-subtitle {
        font-size: 0.98rem;
        color: #64748B;
        margin-top: 3px;
        font-weight: 400;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Data Loading & ML Model Caching
# -----------------------------------------------------------------------------
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "zomato_cleaned.csv"

@st.cache_data
def get_cleaned_data():
    if not DATA_PATH.exists():
        from src.data_loader import load_raw_data
        from src.cleaner import clean_zomato_data
        raw = load_raw_data()
        df, _ = clean_zomato_data(raw, save_path=DATA_PATH)
        return df
    return pd.read_csv(DATA_PATH)

@st.cache_resource
def get_trained_ml_model(df):
    model = RestaurantRatingPredictor()
    metrics = model.train(df)
    return model, metrics

df_all = get_cleaned_data()
ml_model, ml_metrics = get_trained_ml_model(df_all)

# -----------------------------------------------------------------------------
# Sidebar: Clean & Intuitive Filters
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔍 Filter Restaurants")
    
    locations = sorted([loc for loc in df_all["location"].unique() if loc != "Not Available"])
    selected_locations = st.multiselect(
        "Select Locations",
        options=locations,
        default=[],
        help="Leave empty to analyze all locations."
    )
    
    all_cuisines = sorted(df_all["primary_cuisine"].dropna().unique().tolist())
    selected_cuisine = st.selectbox(
        "Primary Cuisine",
        options=["All Cuisines"] + all_cuisines,
        index=0
    )
    
    price_tiers = ["Budget (< ₹400)", "Mid-Range (₹400 - ₹800)", "Premium (₹800 - ₹1,500)", "Luxury (> ₹1,500)"]
    selected_tiers = st.multiselect(
        "Price Categories",
        options=price_tiers,
        default=price_tiers
    )
    
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        online_choice = st.selectbox("Online Order", ["All", "Yes", "No"], index=0)
    with col_sb2:
        table_choice = st.selectbox("Book Table", ["All", "Yes", "No"], index=0)
        
    min_rating = st.slider("Minimum Rating", min_value=2.0, max_value=5.0, value=2.0, step=0.1)
    
    st.markdown("---")
    st.caption("Zomato Analytics & ML Intelligence Engine • v2.0.0")

# -----------------------------------------------------------------------------
# Data Filtering Logic
# -----------------------------------------------------------------------------
filtered_df = df_all.copy()

if selected_locations:
    filtered_df = filtered_df[filtered_df["location"].isin(selected_locations)]

if selected_cuisine != "All Cuisines":
    filtered_df = filtered_df[filtered_df["primary_cuisine"] == selected_cuisine]

if selected_tiers:
    filtered_df = filtered_df[filtered_df["cost_category"].isin(selected_tiers)]

if online_choice != "All":
    filtered_df = filtered_df[filtered_df["online_order"] == online_choice]

if table_choice != "All":
    filtered_df = filtered_df[filtered_df["book_table"] == table_choice]

filtered_df = filtered_df[filtered_df["rating_imputed"] >= min_rating]

# -----------------------------------------------------------------------------
# Main Header
# -----------------------------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div class="hero-title">Zomato <span>Market Intelligence</span></div>
    <div class="hero-subtitle">Comprehensive exploratory analytics, white-space gap analysis, and predictive rating intelligence.</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Top KPI Metric Cards
# -----------------------------------------------------------------------------
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

total_count = len(filtered_df)
avg_rating = filtered_df["rating"].dropna().mean()
avg_cost = filtered_df["cost_for_two"].mean()
online_pct = (filtered_df["online_order"] == "Yes").mean() * 100 if total_count > 0 else 0
total_votes = filtered_df["votes"].sum()

with kpi1:
    st.metric("Total Restaurants", f"{total_count:,}")
with kpi2:
    st.metric("Average Rating", f"{avg_rating:.2f} ★" if pd.notna(avg_rating) else "N/A")
with kpi3:
    st.metric("Avg Cost for Two", f"₹{avg_cost:,.0f}" if pd.notna(avg_cost) else "N/A")
with kpi4:
    st.metric("Online Delivery", f"{online_pct:.1f}%")
with kpi5:
    st.metric("Total Reviews", f"{total_votes:,}")

st.write("")

# -----------------------------------------------------------------------------
# Clean Tabs Navigation
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Executive Overview",
    "🍲 Cuisines & Hotspots",
    "📈 Pricing & Delivery",
    "🎯 Market Gap & White Spaces",
    "🤖 Success Predictor & Simulator",
    "🔍 Restaurant Explorer & Export"
])

# -----------------------------------------------------------------------------
# Tab 1: Executive Overview
# -----------------------------------------------------------------------------
with tab1:
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.subheader("Restaurant Rating Distribution")
        rated_data = filtered_df.dropna(subset=["rating"])
        if not rated_data.empty:
            fig_hist = px.histogram(
                rated_data,
                x="rating",
                nbins=20,
                color_discrete_sequence=["#E23744"],
                labels={"rating": "Customer Rating (out of 5.0)", "count": "Restaurants Count"},
                opacity=0.85
            )
            fig_hist.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(l=20, r=20, t=30, b=20),
                bargap=0.08,
                xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
                yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("No rated restaurants in current selection.")
            
    with col_t2:
        st.subheader("Price Tier Breakdown")
        tier_counts = filtered_df["cost_category"].value_counts().reset_index()
        tier_counts.columns = ["Price Tier", "Count"]
        
        fig_pie = px.pie(
            tier_counts,
            names="Price Tier",
            values="Count",
            hole=0.45,
            color_discrete_sequence=["#E23744", "#334155", "#0EA5E9", "#F59E0B"]
        )
        fig_pie.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("Restaurant Types Distribution")
    type_counts = filtered_df["rest_type"].value_counts().head(8).reset_index()
    type_counts.columns = ["Restaurant Type", "Count"]
    
    fig_types = px.bar(
        type_counts,
        x="Restaurant Type",
        y="Count",
        color="Count",
        color_continuous_scale="Reds",
        text="Count"
    )
    fig_types.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        coloraxis_showscale=False
    )
    fig_types.update_traces(textposition="outside")
    st.plotly_chart(fig_types, use_container_width=True)

# -----------------------------------------------------------------------------
# Tab 2: Cuisines & Hotspots
# -----------------------------------------------------------------------------
with tab2:
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        st.subheader("Top 10 Most Common Cuisines")
        cuisine_records = []
        for c_str in filtered_df["cuisines"].dropna():
            if c_str != "Not Available":
                for item in c_str.split(","):
                    c_clean = item.strip()
                    if c_clean:
                        cuisine_records.append(c_clean)
        top_c_series = pd.Series(cuisine_records).value_counts().head(10).reset_index()
        top_c_series.columns = ["Cuisine", "Total Offerings"]
        
        fig_c = px.bar(
            top_c_series,
            x="Total Offerings",
            y="Cuisine",
            orientation="h",
            color_discrete_sequence=["#E23744"],
            text="Total Offerings"
        )
        fig_c.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis=dict(autorange="reversed"),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        fig_c.update_traces(textposition="outside")
        st.plotly_chart(fig_c, use_container_width=True)
        
    with col_c2:
        st.subheader("Top Dining Hotspots by Restaurant Count")
        top_locs = filtered_df["location"].value_counts().head(10).reset_index()
        top_locs.columns = ["Location", "Restaurants"]
        
        fig_loc = px.bar(
            top_locs,
            x="Restaurants",
            y="Location",
            orientation="h",
            color_discrete_sequence=["#1E293B"],
            text="Restaurants"
        )
        fig_loc.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis=dict(autorange="reversed"),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        fig_loc.update_traces(textposition="outside")
        st.plotly_chart(fig_loc, use_container_width=True)

# -----------------------------------------------------------------------------
# Tab 3: Pricing & Delivery
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("Correlation: Cost for Two vs Customer Rating")
    fig_scatter = px.scatter(
        filtered_df,
        x="cost_for_two",
        y="rating_imputed",
        size="votes",
        color="cost_category",
        hover_name="name",
        hover_data=["location", "primary_cuisine", "online_order", "book_table"],
        labels={"cost_for_two": "Approx Cost for Two (₹)", "rating_imputed": "Rating (out of 5.0)"},
        color_discrete_sequence=["#10B981", "#0EA5E9", "#F59E0B", "#E23744"]
    )
    fig_scatter.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9")
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("#### 🛵 Online Delivery Advantage")
        deliv_grp = filtered_df.groupby("online_order").agg(
            Avg_Rating=("rating_imputed", "mean"),
            Avg_Cost=("cost_for_two", "mean"),
            Avg_Votes=("votes", "mean")
        ).round(2).reset_index()
        st.dataframe(deliv_grp, use_container_width=True, hide_index=True)
        
    with col_m2:
        st.markdown("#### 📅 Table Booking Advantage")
        book_grp = filtered_df.groupby("book_table").agg(
            Avg_Rating=("rating_imputed", "mean"),
            Avg_Cost=("cost_for_two", "mean"),
            Avg_Votes=("votes", "mean")
        ).round(2).reset_index()
        st.dataframe(book_grp, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# Tab 4: Market Gap & White Spaces (Business / Category Team Intelligence)
# -----------------------------------------------------------------------------
with tab4:
    st.markdown("### 🎯 White-Space & Expansion Opportunity Matrix")
    st.write(
        "Identifies underserved culinary markets across dining neighborhoods. "
        "Combinations with high average consumer ratings and low restaurant count represent prime expansion opportunities."
    )
    
    opp_df = compute_market_opportunity_matrix(filtered_df)
    
    if not opp_df.empty:
        # Filter by quadrant
        quadrants = ["All Quadrants"] + sorted(opp_df["market_quadrant"].unique().tolist())
        selected_quad = st.selectbox("Filter by Opportunity Quadrant", quadrants, index=0)
        
        plot_opp_df = opp_df if selected_quad == "All Quadrants" else opp_df[opp_df["market_quadrant"] == selected_quad]
        
        fig_opp = px.scatter(
            plot_opp_df.head(40),
            x="supply_count",
            y="avg_rating",
            size="opportunity_score",
            color="market_quadrant",
            hover_name="cuisine",
            hover_data=["location", "avg_cost", "opportunity_score"],
            labels={
                "supply_count": "Existing Restaurant Count (Competition)",
                "avg_rating": "Average Rating (Quality / Demand Indicator)",
                "market_quadrant": "Market Segment"
            },
            color_discrete_map={
                "High Opportunity (Underserved)": "#10B981",
                "Proven Hotspot (High Demand)": "#0EA5E9",
                "Saturated / High Competition": "#E23744",
                "Niche / Developing": "#94A3B8"
            }
        )
        fig_opp.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9")
        )
        st.plotly_chart(fig_opp, use_container_width=True)
        
        st.markdown("#### 📋 Top Underserved Cuisine-Locality Pairings")
        st.dataframe(
            plot_opp_df[["location", "cuisine", "supply_count", "avg_rating", "avg_cost", "opportunity_score", "market_quadrant"]]
            .rename(columns={
                "location": "Location",
                "cuisine": "Cuisine",
                "supply_count": "Outlets",
                "avg_rating": "Avg Rating",
                "avg_cost": "Avg Cost (₹)",
                "opportunity_score": "Opportunity Score",
                "market_quadrant": "Quadrant"
            }).head(15),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Insufficient data for white-space opportunity mapping.")
        
    st.markdown("---")
    st.markdown("### 💰 Zomato Platform Commission & GMV Simulator")
    st.caption("Estimate network gross merchandise value and platform revenue based on commission rates.")
    
    col_sim1, col_sim2, col_sim3 = st.columns(3)
    with col_sim1:
        sim_commission = st.slider("Delivery Commission Rate (%)", 10.0, 30.0, 20.0, 1.0) / 100.0
    with col_sim2:
        sim_booking_fee = st.slider("Table Booking Fee (₹ per reservation)", 10.0, 100.0, 35.0, 5.0)
    with col_sim3:
        sim_monthly_orders = st.number_input("Est. Monthly Orders per Restaurant", min_value=50, max_value=2000, value=450, step=50)
        
    rev_result = simulate_platform_revenue(
        filtered_df,
        commission_rate=sim_commission,
        table_booking_fee=sim_booking_fee,
        avg_delivery_orders_monthly=sim_monthly_orders
    )
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Estimated Monthly GMV", f"₹{rev_result['monthly_gmv']:,.0f}")
    with c2:
        st.metric("Annual Network GMV", f"₹{rev_result['annual_gmv']:,.0f}")
    with c3:
        st.metric("Estimated Annual Revenue", f"₹{rev_result['annual_revenue']:,.0f}")
    with c4:
        st.metric("Delivery Commission Share", f"{rev_result['delivery_commission_share_pct']}%")

# -----------------------------------------------------------------------------
# Tab 5: Success Predictor & Simulator (ML Model & Competitor Benchmarking)
# -----------------------------------------------------------------------------
with tab5:
    st.markdown("### 🤖 Restaurant Rating Predictor (Random Forest Machine Learning)")
    st.write(
        f"Predict how your restaurant concept would perform on Zomato based on platform attributes. "
        f"(Model Accuracy: MAE = **{ml_metrics['MAE']}** rating points, R² = **{ml_metrics['R2']}**)"
    )
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        p_location = st.selectbox("Target Location", locations, index=0)
        p_type = st.selectbox("Restaurant Type", [
            "Quick Bites", "Casual Dining", "Cafe", "Delivery",
            "Dessert Parlor", "Pub", "Microbrewery", "Fine Dining", "Bakery"
        ], index=1)
        p_cost = st.slider("Approx Cost for Two People (₹)", min_value=150, max_value=4000, value=750, step=50)
        
    with col_p2:
        p_online = st.radio("Online Ordering Enabled?", ["Yes", "No"], horizontal=True)
        p_table = st.radio("Table Reservation Enabled?", ["Yes", "No"], horizontal=True)
        p_cuisines_count = st.slider("Number of Cuisines Offered", 1, 6, 2)
        
    test_input = {
        "location": p_location,
        "rest_type": p_type,
        "cost_for_two": p_cost,
        "online_order": p_online,
        "book_table": p_table,
        "cuisine_count": p_cuisines_count
    }
    
    pred_rating, pred_tier = ml_model.predict(test_input)
    
    st.markdown("#### 🎯 Prediction Results")
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.metric("Expected Customer Rating", f"{pred_rating:.2f} ★")
    with col_res2:
        st.metric("Performance Classification", pred_tier)
        
    # Feature Importance Drivers
    st.markdown("#### 💡 What Drives Higher Ratings on Zomato?")
    fi_plot_df = ml_model.feature_importance_df.head(8)
    fig_fi = px.bar(
        fi_plot_df,
        x="Importance",
        y="Feature_Label",
        orientation="h",
        color_discrete_sequence=["#E23744"],
        labels={"Importance": "Relative Predictive Importance", "Feature_Label": ""}
    )
    fig_fi.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        yaxis=dict(autorange="reversed"),
        margin=dict(l=20, r=20, t=10, b=20)
    )
    st.plotly_chart(fig_fi, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 🏆 Competitor Benchmarking Scorecard")
    sample_names = sorted(df_all["name"].unique().tolist())
    selected_name = st.selectbox("Select Restaurant to Benchmark", options=sample_names, index=0)
    
    bench = benchmark_restaurant(df_all, selected_name)
    if bench["found"]:
        b1, b2, b3 = st.columns(3)
        with b1:
            st.metric("Restaurant Rating", f"{bench['rating']:.2f} ★", delta=f"{bench['rating_diff_from_local']:+.2f} vs Local Avg")
        with b2:
            st.metric("Cost for Two", f"₹{bench['cost_for_two']:,.0f}", delta=f"₹{bench['cost_diff_from_local']:+,.0f} vs Local Avg", delta_color="inverse")
        with b3:
            st.metric("Local Competitors", f"{bench['outlets']} Outlets")
            
        st.info(f"**Competitive Positioning**: {bench['positioning']}")

# -----------------------------------------------------------------------------
# Tab 6: Restaurant Explorer & Data Export Center
# -----------------------------------------------------------------------------
with tab6:
    st.subheader("Interactive Restaurant Explorer")
    search_query = st.text_input("🔍 Search by Restaurant Name or Cuisine", placeholder="e.g., Truffles, Biryani, Italian...")
    
    display_df = filtered_df.copy()
    if search_query:
        mask = (
            display_df["name"].str.contains(search_query, case=False, na=False) |
            display_df["cuisines"].str.contains(search_query, case=False, na=False)
        )
        display_df = display_df[mask]
        
    cols_to_show = ["name", "location", "rating", "cost_for_two", "cuisines", "rest_type", "online_order", "book_table", "votes"]
    rename_dict = {
        "name": "Restaurant Name",
        "location": "Location",
        "rating": "Rating",
        "cost_for_two": "Cost for 2 (₹)",
        "cuisines": "Cuisines",
        "rest_type": "Type",
        "online_order": "Online Order",
        "book_table": "Book Table",
        "votes": "Votes"
    }
    
    st.dataframe(
        display_df[cols_to_show].rename(columns=rename_dict).sort_values(by="Rating", ascending=False),
        use_container_width=True,
        hide_index=True,
        height=450
    )
    
    col_down1, col_down2 = st.columns([1, 4])
    with col_down1:
        csv_data = display_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Filtered Data (CSV)",
            data=csv_data,
            file_name="zomato_filtered_data.csv",
            mime="text/csv",
        )
    with col_down2:
        st.caption(f"Showing {len(display_df):,} matching restaurants available for export.")

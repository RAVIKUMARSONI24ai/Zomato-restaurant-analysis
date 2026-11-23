"""
Zomato Restaurant Analysis Dashboard
Built with Streamlit and Plotly for clean, uncluttered interactive exploration.
"""
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# App Configuration & Modern Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Zomato Analytics | Insights Dashboard",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Clean CSS
st.markdown("""
<style>
    /* Global styles */
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
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: #64748B !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 1.85rem !important;
        font-weight: 700 !important;
        color: #0F172A !important;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #FFFFFF;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 18px;
        font-weight: 600;
        color: #475569;
    }
    .stTabs [aria-selected="true"] {
        background-color: #E23744 !important;
        color: #FFFFFF !important;
    }
    
    /* Header hero */
    .hero-container {
        padding: 20px 0 10px 0;
        margin-bottom: 15px;
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
        font-size: 1.0rem;
        color: #64748B;
        margin-top: 4px;
        font-weight: 400;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Data Loading & Caching
# -----------------------------------------------------------------------------
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "zomato_cleaned.csv"

@st.cache_data
def get_cleaned_data():
    if not DATA_PATH.exists():
        # Fallback to run cleaner if not processed yet
        from src.data_loader import load_raw_data
        from src.cleaner import clean_zomato_data
        raw = load_raw_data()
        df, _ = clean_zomato_data(raw, save_path=DATA_PATH)
        return df
    return pd.read_csv(DATA_PATH)

df_all = get_cleaned_data()

# -----------------------------------------------------------------------------
# Sidebar: Clean & Intuitive Filters
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔍 Filter Restaurants")
    
    # Location Filter
    locations = sorted([loc for loc in df_all["location"].unique() if loc != "Not Available"])
    selected_locations = st.multiselect(
        "Select Locations",
        options=locations,
        default=[],
        help="Leave empty to analyze all locations."
    )
    
    # Cuisine Filter
    all_cuisines = sorted(df_all["primary_cuisine"].dropna().unique().tolist())
    selected_cuisine = st.selectbox(
        "Primary Cuisine",
        options=["All Cuisines"] + all_cuisines,
        index=0
    )
    
    # Price Tier Filter
    price_tiers = ["Budget (< ₹400)", "Mid-Range (₹400 - ₹800)", "Premium (₹800 - ₹1,500)", "Luxury (> ₹1,500)"]
    selected_tiers = st.multiselect(
        "Price Categories",
        options=price_tiers,
        default=price_tiers
    )
    
    # Online Order & Table Booking
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        online_choice = st.selectbox("Online Order", ["All", "Yes", "No"], index=0)
    with col_sb2:
        table_choice = st.selectbox("Book Table", ["All", "Yes", "No"], index=0)
        
    # Minimum Rating Slider
    min_rating = st.slider("Minimum Rating", min_value=2.0, max_value=5.0, value=2.0, step=0.1)
    
    st.markdown("---")
    st.caption("Clean Zomato Restaurant Analytics Engine • v1.0.0")

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
    <div class="hero-title">Zomato <span>Restaurant Intelligence</span></div>
    <div class="hero-subtitle">Comprehensive exploratory analysis and market dynamics across dining hubs.</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Key Metric KPI Cards
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
# Clean Tabs Layout
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Executive Overview",
    "🍲 Cuisines & Hotspots",
    "📈 Pricing & Delivery Insights",
    "🔍 Restaurant Explorer"
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
                plot_bgcolor="white",
                paper_bgcolor="white",
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
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Secondary row: Restaurant Type distribution
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
        plot_bgcolor="white",
        paper_bgcolor="white",
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
            plot_bgcolor="white",
            paper_bgcolor="white",
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
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis=dict(autorange="reversed"),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        fig_loc.update_traces(textposition="outside")
        st.plotly_chart(fig_loc, use_container_width=True)

# -----------------------------------------------------------------------------
# Tab 3: Pricing & Delivery Insights
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
        color_discrete_sequence=["#10B981", "#0EA5E9", "#F59E0B", "#E23744"],
        trendline="ols"
    )
    fig_scatter.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9")
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Comparison Metrics
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
# Tab 4: Restaurant Explorer & Finder
# -----------------------------------------------------------------------------
with tab4:
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
    
    st.caption(f"Showing {len(display_df):,} matching restaurants.")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Superstore Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f1117; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1a1d27;
        border-right: 1px solid #2d2f3e;
    }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e2130 0%, #252840 100%);
        border: 1px solid #2d3055;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    div[data-testid="metric-container"] label {
        color: #8b90a8 !important;
        font-size: 0.78rem !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        font-weight: 600 !important;
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #e8eaf6 !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-size: 0.82rem !important;
    }

    /* Section headers */
    .section-header {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #5c6bc0;
        margin-bottom: 4px;
        margin-top: 8px;
    }
    
    /* Chart container */
    .chart-card {
        background: #1a1d27;
        border-radius: 12px;
        border: 1px solid #2d2f3e;
        padding: 4px;
    }
    
    /* Divider */
    hr { border-color: #2d2f3e !important; }
    
    /* Dataframe */
    .dataframe { background-color: #1a1d27 !important; }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Title */
    h1 { color: #e8eaf6 !important; font-weight: 800 !important; letter-spacing: -0.02em; }
    h2, h3 { color: #c5cae9 !important; }
</style>
""", unsafe_allow_html=True)

# ── Data loading ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("superstore.csv")
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Ship Date"]  = pd.to_datetime(df["Ship Date"])
    df["Year"]       = df["Order Date"].dt.year
    df["Month"]      = df["Order Date"].dt.to_period("M").astype(str)
    df["Month_dt"]   = df["Order Date"].dt.to_period("M").dt.to_timestamp()
    df["Profit Margin"] = (df["Profit"] / df["Sales"] * 100).round(2)
    return df

df = load_data()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Filters")
    st.markdown("---")

    years = sorted(df["Year"].unique())
    selected_years = st.multiselect(
        "📅 Year", years, default=years,
        help="Select one or more years"
    )

    regions = sorted(df["Region"].unique())
    selected_regions = st.multiselect(
        "🌎 Region", regions, default=regions
    )

    categories = sorted(df["Category"].unique())
    selected_categories = st.multiselect(
        "📦 Category", categories, default=categories
    )

    segments = sorted(df["Segment"].unique())
    selected_segments = st.multiselect(
        "👥 Segment", segments, default=segments
    )

    st.markdown("---")
    st.markdown(
        "<div style='color:#5c6bc0;font-size:0.75rem;text-align:center'>"
        "Superstore Sales Dataset<br>2014 – 2017 · 9,994 orders"
        "</div>",
        unsafe_allow_html=True,
    )

# ── Filtered data ──────────────────────────────────────────────────────────────
filtered = df[
    df["Year"].isin(selected_years) &
    df["Region"].isin(selected_regions) &
    df["Category"].isin(selected_categories) &
    df["Segment"].isin(selected_segments)
]

# Previous period (for delta)
all_years = sorted(df["Year"].unique())
prev_years = [y - 1 for y in selected_years if y - 1 in all_years]
prev = df[
    df["Year"].isin(prev_years) &
    df["Region"].isin(selected_regions) &
    df["Category"].isin(selected_categories) &
    df["Segment"].isin(selected_segments)
]

def delta(curr, prev_val):
    if prev_val == 0:
        return None
    return f"{((curr - prev_val) / prev_val * 100):+.1f}%"

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("# 📊 Sales Performance Dashboard")
st.markdown(
    "<p style='color:#8b90a8;margin-top:-8px;font-size:0.95rem'>"
    "Interactive analytics for the Superstore dataset · use the sidebar to slice by year, region, category & segment"
    "</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ── Guard: empty filter ────────────────────────────────────────────────────────
if filtered.empty:
    st.warning("⚠️ No data matches your filters. Please adjust the sidebar selections.")
    st.stop()

# ── KPI Cards ──────────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">Key Performance Indicators</p>', unsafe_allow_html=True)

total_revenue = filtered["Sales"].sum()
total_orders  = filtered["Order ID"].nunique()
avg_order_val = filtered.groupby("Order ID")["Sales"].sum().mean()
total_profit  = filtered["Profit"].sum()
profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0

prev_revenue = prev["Sales"].sum()
prev_orders  = prev["Order ID"].nunique()
prev_profit  = prev["Profit"].sum()
prev_aov     = prev.groupby("Order ID")["Sales"].sum().mean() if not prev.empty else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("💰 Total Revenue",    f"${total_revenue:,.0f}",  delta(total_revenue, prev_revenue))
c2.metric("🛒 Total Orders",     f"{total_orders:,}",       delta(total_orders,  prev_orders))
c3.metric("🧾 Avg Order Value",  f"${avg_order_val:,.0f}",  delta(avg_order_val, prev_aov))
c4.metric("📈 Total Profit",     f"${total_profit:,.0f}",   delta(total_profit,  prev_profit))
c5.metric("📉 Profit Margin",    f"{profit_margin:.1f}%",   None)

st.markdown("---")

# ── Plotly theme helper ────────────────────────────────────────────────────────
COLORS  = ["#5c6bc0", "#42a5f5", "#66bb6a", "#ffa726", "#ef5350", "#ab47bc", "#26c6da"]
LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#c5cae9", size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(gridcolor="#2d2f3e", zerolinecolor="#2d2f3e"),
    yaxis=dict(gridcolor="#2d2f3e", zerolinecolor="#2d2f3e"),
)

# ── Monthly Revenue Trend ──────────────────────────────────────────────────────
st.markdown('<p class="section-header">📅 Monthly Revenue & Profit Trend</p>', unsafe_allow_html=True)
st.caption("Track how sales and profit evolve month-over-month. Upward slopes indicate growth; diverging lines signal margin pressure.")

monthly = (
    filtered.groupby("Month_dt")
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
    .reset_index()
    .sort_values("Month_dt")
)

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=monthly["Month_dt"], y=monthly["Sales"],
    name="Revenue", line=dict(color="#5c6bc0", width=2.5),
    fill="tozeroy", fillcolor="rgba(92,107,192,0.1)",
    hovertemplate="<b>%{x|%b %Y}</b><br>Revenue: $%{y:,.0f}<extra></extra>",
))
fig_trend.add_trace(go.Scatter(
    x=monthly["Month_dt"], y=monthly["Profit"],
    name="Profit", line=dict(color="#66bb6a", width=2, dash="dot"),
    hovertemplate="<b>%{x|%b %Y}</b><br>Profit: $%{y:,.0f}<extra></extra>",
))
fig_trend.update_layout(
    **LAYOUT, 
    title="Monthly Revenue vs Profit", 
    height=320,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig_trend, width='stretch')
st.markdown("---")

# ── Category + Region ─────────────────────────────────────────────────────────
st.markdown('<p class="section-header">📦 Sales & Profit by Category and Region</p>', unsafe_allow_html=True)
st.caption("Compare revenue performance across product categories and geographic regions. Hover for exact figures.")

col_left, col_right = st.columns(2)

with col_left:
    cat = (
        filtered.groupby("Category")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .reset_index().sort_values("Sales", ascending=True)
    )
    fig_cat = go.Figure()
    fig_cat.add_trace(go.Bar(
        y=cat["Category"], x=cat["Sales"], name="Revenue",
        orientation="h", marker_color="#5c6bc0",
        hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>",
    ))
    fig_cat.add_trace(go.Bar(
        y=cat["Category"], x=cat["Profit"], name="Profit",
        orientation="h", marker_color="#66bb6a",
        hovertemplate="<b>%{y}</b><br>Profit: $%{x:,.0f}<extra></extra>",
    ))
    fig_cat.update_layout(**LAYOUT, title="By Category", height=280,
                           barmode="group",
                           legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_cat, width='stretch')

with col_right:
    reg = (
        filtered.groupby("Region")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .reset_index().sort_values("Sales", ascending=True)
    )
    fig_reg = go.Figure()
    fig_reg.add_trace(go.Bar(
        y=reg["Region"], x=reg["Sales"], name="Revenue",
        orientation="h", marker_color="#42a5f5",
        hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>",
    ))
    fig_reg.add_trace(go.Bar(
        y=reg["Region"], x=reg["Profit"], name="Profit",
        orientation="h", marker_color="#ffa726",
        hovertemplate="<b>%{y}</b><br>Profit: $%{x:,.0f}<extra></extra>",
    ))
    fig_reg.update_layout(**LAYOUT, title="By Region", height=280,
                           barmode="group",
                           legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_reg, width='stretch')

st.markdown("---")

# ── Sub-category deep dive + Segment pie ──────────────────────────────────────
st.markdown('<p class="section-header">🔍 Sub-Category Profit Analysis & Segment Mix</p>', unsafe_allow_html=True)
st.caption("Sub-categories with negative profit (red bars) are drag items — often caused by heavy discounting. Segment mix shows where revenue is coming from.")

col_sub, col_seg = st.columns([3, 2])

with col_sub:
    sub = (
        filtered.groupby("Sub-Category")["Profit"].sum()
        .reset_index().sort_values("Profit")
    )
    sub["color"] = sub["Profit"].apply(lambda x: "#ef5350" if x < 0 else "#66bb6a")
    fig_sub = go.Figure(go.Bar(
        x=sub["Profit"], y=sub["Sub-Category"],
        orientation="h",
        marker_color=sub["color"],
        hovertemplate="<b>%{y}</b><br>Profit: $%{x:,.0f}<extra></extra>",
    ))
    fig_sub.update_layout(**LAYOUT, title="Profit by Sub-Category", height=380)
    st.plotly_chart(fig_sub, width='stretch')

with col_seg:
    seg = filtered.groupby("Segment")["Sales"].sum().reset_index()
    fig_seg = go.Figure(go.Pie(
        labels=seg["Segment"], values=seg["Sales"],
        hole=0.55,
        marker=dict(colors=COLORS),
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f} (%{percent})<extra></extra>",
        textfont=dict(color="#e8eaf6"),
    ))
    fig_seg.update_layout(**LAYOUT, title="Revenue by Segment", height=380,
                           showlegend=True,
                           legend=dict(orientation="v", yanchor="middle", y=0.5))
    st.plotly_chart(fig_seg, width='stretch')

st.markdown("---")

# ── Discount vs Profit scatter ─────────────────────────────────────────────────
st.markdown('<p class="section-header">🎯 Discount vs Profit Margin</p>', unsafe_allow_html=True)
st.caption("Each dot is an order. High discounts (right side) strongly correlate with negative profit margins — a key business insight to surface.")

sample = filtered.sample(min(2000, len(filtered)), random_state=42)
fig_scatter = px.scatter(
    sample, x="Discount", y="Profit Margin",
    color="Category", size="Sales",
    color_discrete_sequence=COLORS,
    opacity=0.65,
    hover_data={"Order ID": True, "Sales": ":,.0f", "Discount": ":.0%", "Profit Margin": ":.1f"},
    labels={"Discount": "Discount Rate", "Profit Margin": "Profit Margin (%)"},
    title="Discount Rate vs Profit Margin (sample of up to 2,000 orders)",
)
fig_scatter.add_hline(y=0, line_dash="dash", line_color="#ef5350", opacity=0.6,
                       annotation_text="Break-even", annotation_font_color="#ef5350")
fig_scatter.update_layout(**LAYOUT, height=360)
st.plotly_chart(fig_scatter, width='stretch')

st.markdown("---")

# ── Top 10 Products ───────────────────────────────────────────────────────────
st.markdown('<p class="section-header">🏆 Top 10 Products by Revenue</p>', unsafe_allow_html=True)
st.caption("The highest-grossing individual products in the selected filters. Profit Margin column reveals whether top sellers are also profitable.")

top10 = (
    filtered.groupby("Sub-Category")
    .agg(
        Revenue=("Sales", "sum"),
        Orders=("Order ID", "nunique"),
        Profit=("Profit", "sum"),
        Avg_Discount=("Discount", "mean"),
    )
    .reset_index()
    .sort_values("Revenue", ascending=False)
    .head(10)
)
top10["Profit Margin %"] = (top10["Profit"] / top10["Revenue"] * 100).round(1)
top10["Revenue"]         = top10["Revenue"].round(0).astype(int)
top10["Profit"]          = top10["Profit"].round(0).astype(int)
top10["Avg_Discount"]    = (top10["Avg_Discount"] * 100).round(1)

top10_display = top10.rename(columns={
    "Sub-Category": "Product Category",
    "Avg_Discount":  "Avg Discount %",
})

st.dataframe(
    top10_display.style
    .format({"Revenue": "${:,}", "Profit": "${:,}", "Profit Margin %": "{:.1f}%", "Avg Discount %": "{:.1f}%"})
    .background_gradient(subset=["Revenue"],        cmap="Blues")
    .background_gradient(subset=["Profit Margin %"], cmap="RdYlGn")
    .set_properties(**{"background-color": "#1a1d27", "color": "#e8eaf6"}),
    width='stretch',
    hide_index=True,
)

st.markdown("---")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(
    "<div style='text-align:center;color:#5c6bc0;font-size:0.78rem;padding:8px'>"
    "Built with Streamlit · Plotly · Pandas &nbsp;|&nbsp; Superstore Sales Dataset"
    "</div>",
    unsafe_allow_html=True,
)
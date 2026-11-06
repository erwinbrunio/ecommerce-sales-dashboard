import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ==============================================================================
# 1. PAGE CONFIGURATION & LAYOUT
# Must be the very first Streamlit command executed
# ==============================================================================
st.set_page_config(
    page_title="Executive Sales & Commercial Performance Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------------------
# Helper Functions: Formatting
# ------------------------------------------------------------------------------
def format_currency_compact(val: float) -> str:
  """Formats values into compact notation (Millions/Thousands) for executive cards."""
  if abs(val) >= 1_000_000:
    return f"₱{val / 1_000_000:.2f}M"
  elif abs(val) >= 1_000:
    return f"₱{val / 1_000:.2f}K"
  else:
    return f"₱{val:,.2f}"

# ==============================================================================
# 2. HIGH-PERFORMANCE DATA INGESTION
# Cached in memory to eliminate redundant disk reads across filter updates
# ==============================================================================
@st.cache_data
def load_analytical_data():
  # Robust loader: prefer high-speed Parquet, fallback to CSV if needed
  parquet_path = "clean_data/fact_sales.parquet"
  csv_path = "clean_data/fact_sales.csv"

  if os.path.exists(parquet_path):
    df = pd.read_parquet(parquet_path)
  elif os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
  else:
    st.error(
        f"Data file not found. Ensure '{parquet_path}' exists in your"
        " directory."
    )
    st.stop()

  # Ensure date formats match Streamlit calendar widgets
  df["order_date"] = pd.to_datetime(df["order_date"]).dt.date
  df["year_month"] = df["year_month"].astype(str)

  # Optimize categorical columns for fast memory indexing during filtering
  categorical_dims = [
      "category",
      "sales_channel",
      "region_name",
      "loyalty_tier",
      "order_status",
  ]
  for col in categorical_dims:
    if col in df.columns:
      df[col] = df[col].astype("category")

  return df


# Ingest fact table once into RAM
fact_df = load_analytical_data()


# ==============================================================================
# 3. SIDEBAR CONTROLS & GLOBAL FILTERS
# ==============================================================================
st.sidebar.header("🎯 Dashboard Filters")

# 1. Date Range Picker
min_date = fact_df["order_date"].min()
max_date = fact_df["order_date"].max()

date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# Defensive guard: prevents unpacking crash while user clicks the first date
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
  start_date, end_date = date_range
else:
  start_date, end_date = min_date, max_date

# 2. Geographic Region Filter
all_regions = sorted(fact_df["region_name"].dropna().unique())
selected_regions = st.sidebar.multiselect(
    "Region", options=all_regions, default=all_regions
)

# 3. Department / Category Filter
all_categories = sorted(fact_df["category"].dropna().unique())
selected_categories = st.sidebar.multiselect(
    "Product Category", options=all_categories, default=all_categories
)

# 4. Sales Channel Filter
all_channels = sorted(fact_df["sales_channel"].dropna().unique())
selected_channels = st.sidebar.multiselect(
    "Sales Channel", options=all_channels, default=all_channels
)


# ==============================================================================
# 4. REACTIVE FILTER PIPELINE & BANNER
# ==============================================================================
# Defensive fallback: If user clears all options, default back to showing all data
regions_filter = selected_regions if selected_regions else all_regions
categories_filter = selected_categories if selected_categories else all_categories
channels_filter = selected_channels if selected_channels else all_channels

filter_mask = (
    (fact_df["order_date"] >= start_date)
    & (fact_df["order_date"] <= end_date)
    & (fact_df["region_name"].isin(regions_filter))
    & (fact_df["category"].isin(categories_filter))
    & (fact_df["sales_channel"].isin(channels_filter))
)

filtered_df = fact_df.loc[filter_mask]

# ==============================================================================
# HEADER SECTION WITH TOP-RIGHT LOGO
# ==============================================================================
# Use an asymmetric ratio (e.g., 5:1 or 6:1) to allocate space between title & logo
header_col, logo_col = st.columns([5, 1], vertical_alignment="center")

with header_col:
  st.title("💼 Executive Sales Dashboard")
  st.markdown(
      "Interactive executive dashboard monitoring e-commerce net revenue,"
      " orders, AOV, and customer distributions."
  )

with logo_col:
  # Render the logo pinned to the right
  # Use width to restrict size so it doesn't overpower the title
  st.image("assets/logo Erwin Brunio.jpg", width=220)

st.divider()

#st.title("💼 Commercial Sales & Performance Dashboard")
#st.caption(
#    f"Analyzing **{len(filtered_df):,}** line items across"
#    f" **{filtered_df['order_id'].nunique():,}** orders fulfilled from"
#    f" `{start_date}` to `{end_date}`."
#)
#st.divider()


# ==============================================================================
# 5. TOP-ROW EXECUTIVE KPI METRIC CARDS
# ==============================================================================
st.subheader("Key Performance Indicators")

total_net_rev = filtered_df["net_revenue"].sum()
total_orders = filtered_df["order_id"].nunique()
calculated_aov = total_net_rev / total_orders if total_orders > 0 else 0.0

total_cogs = filtered_df["cogs"].sum()
total_gross_profit = filtered_df["gross_profit"].sum()
gross_margin_pct = (
    (total_gross_profit / total_net_rev) * 100 if total_net_rev > 0 else 0.0
)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
    label="Total Net Revenue",
    value=format_currency_compact(total_net_rev),  # Displays: ₱6.82M
    help=f"Exact Net Sales: ₱{total_net_rev:,.2f}",  # Hover displays: ₱6,823,900.13
)

with kpi2:
  st.metric(
      label="Total Orders",
      value=f"{total_orders:,}",
      help="Unique order transactions completed across active channels.",
  )

with kpi3:
  st.metric(
      label="Average Order Value (AOV)",
      value=f"₱{calculated_aov:,.2f}",
      help="Average customer net spending per order.",
  )

with kpi4:
  st.metric(
      label="Gross Profit Margin",
      value=f"{gross_margin_pct:.1f}%",
      help="Share of revenue retained after Cost of Goods Sold (COGS).",
  )

st.markdown("---")


# ==============================================================================
# 6. VISUALIZATION SUITE (5 CORE CHARTS)
# ==============================================================================

# ------------------------------------------------------------------------------
# CHART 1: Monthly Net Revenue & Order Volume Trend (Dual-Axis)
# ------------------------------------------------------------------------------
st.markdown("### 📈 Sales Performance & Volume Trajectory")

monthly_perf = (
    filtered_df.groupby("year_month")
    .agg(net_revenue=("net_revenue", "sum"), total_orders=("order_id", "nunique"))
    .reset_index()
    .sort_values("year_month")
)

fig_trend = make_subplots(specs=[[{"secondary_y": True}]])

# Primary Axis: Monthly Net Revenue (Bars)
fig_trend.add_trace(
    go.Bar(
        x=monthly_perf["year_month"],
        y=monthly_perf["net_revenue"],
        name="Net Revenue (₱)",
        marker_color="#1f77b4",
        opacity=0.8,
        hovertemplate="%{x}<br>Net Revenue: ₱%{y:,.2f}<extra></extra>",
    ),
    secondary_y=False,
)

# Secondary Axis: Order Volume (Line)
fig_trend.add_trace(
    go.Scatter(
        x=monthly_perf["year_month"],
        y=monthly_perf["total_orders"],
        name="Total Orders",
        mode="lines+markers",
        line=dict(color="#ff7f0e", width=3),
        marker=dict(size=6),
        hovertemplate="%{x}<br>Orders: %{y:,}<extra></extra>",
    ),
    secondary_y=True,
)

fig_trend.update_layout(
    title_text="Monthly Revenue (Bars) vs. Total Orders Fulfilled (Line)",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=20, r=20, t=50, b=20),
    height=400,
)
fig_trend.update_yaxes(
    title_text="Net Revenue (₱)", secondary_y=False, showgrid=True
)
fig_trend.update_yaxes(
    title_text="Unique Orders", secondary_y=True, showgrid=False
)

st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# ------------------------------------------------------------------------------
# ROW 2: Category/Product Performance & Regional Revenue
# ------------------------------------------------------------------------------
row2_left, row2_right = st.columns(2)

with row2_left:
  st.markdown("### 🏷️ Department & Product Breakdown")
  view_choice = st.radio(
      "Select Granularity:",
      ["By Category", "Top 10 Products"],
      horizontal=True,
      label_visibility="collapsed",
  )

  if view_choice == "By Category":
    cat_summary = (
        filtered_df.groupby("category", observed=False)["net_revenue"]
        .sum()
        .reset_index()
        .sort_values(by="net_revenue", ascending=True)
    )
    fig_cat = px.bar(
        cat_summary,
        x="net_revenue",
        y="category",
        orientation="h",
        title="Net Revenue Contribution by Product Category",
        color="net_revenue",
        color_continuous_scale="Blues",
        labels={"net_revenue": "Net Revenue (₱)", "category": "Department"},
    )
  else:
    top10_prods = (
        filtered_df.groupby("product_name", observed=False)["net_revenue"]
        .sum()
        .reset_index()
        .sort_values(by="net_revenue", ascending=True)
        .tail(10)
    )
    fig_cat = px.bar(
        top10_prods,
        x="net_revenue",
        y="product_name",
        orientation="h",
        title="Top 10 Best-Selling Products by Revenue",
        color="net_revenue",
        color_continuous_scale="Teal",
        labels={
            "net_revenue": "Net Revenue (₱)",
            "product_name": "Product Name",
        },
    )

  fig_cat.update_layout(
      height=380, margin=dict(l=10, r=20, t=40, b=20), showlegend=False
  )
  fig_cat.update_xaxes(tickprefix="₱", showgrid=True)
  st.plotly_chart(fig_cat, use_container_width=True)

with row2_right:
  st.markdown("### 🗺️ Revenue by Customer Region")
  reg_summary = (
      filtered_df.groupby("region_name", observed=False)["net_revenue"]
      .sum()
      .reset_index()
      .sort_values(by="net_revenue", ascending=True)
  )

  fig_reg = px.bar(
      reg_summary,
      x="net_revenue",
      y="region_name",
      orientation="h",
      title="Commercial Revenue by Geographic Region",
      color="net_revenue",
      color_continuous_scale="Purples",
      labels={"net_revenue": "Net Revenue (₱)", "region_name": "Region"},
  )
  fig_reg.update_layout(
      height=380, margin=dict(l=10, r=20, t=40, b=20), showlegend=False
  )
  fig_reg.update_xaxes(tickprefix="₱", showgrid=True)
  st.plotly_chart(fig_reg, use_container_width=True)

st.markdown("---")

# ------------------------------------------------------------------------------
# ROW 3: Customer Spend Distribution & Operational Friction
# ------------------------------------------------------------------------------
row3_left, row3_right = st.columns(2)

with row3_left:
  st.markdown("### 💳 Customer Spend / AOV Distribution")
  # Aggregate spend to the order basket grain
  order_baskets = (
      filtered_df.groupby("order_id")
      .agg(
          order_total=("net_revenue", "sum"), channel=("sales_channel", "first")
      )
      .reset_index()
  )

  fig_dist = px.box(
      order_baskets,
      x="channel",
      y="order_total",
      color="channel",
      points="outliers",
      title="Order Spend Distribution (AOV Spread) by Channel",
      labels={"order_total": "Order Total (₱)", "channel": "Sales Channel"},
  )
  fig_dist.update_layout(
      height=380, margin=dict(l=20, r=20, t=40, b=20), showlegend=False
  )
  fig_dist.update_yaxes(tickprefix="₱", showgrid=True)
  st.plotly_chart(fig_dist, use_container_width=True)

with row3_right:
  st.markdown("### ⚠️ Cancellations & Returns")
  # Deduplicate to order level before counting transactional statuses
  monthly_friction = (
      filtered_df.drop_duplicates(subset=["order_id"])
      .groupby(["year_month", "order_status"], observed=False)
      .size()
      .unstack(fill_value=0)
      .reset_index()
  )

  # Defensive column initialization if a status has 0 occurrences in filtered slice
  for status_col in ["Cancelled", "Returned"]:
    if status_col not in monthly_friction.columns:
      monthly_friction[status_col] = 0

  fig_frict = go.Figure()
  fig_frict.add_trace(
      go.Scatter(
          x=monthly_friction["year_month"],
          y=monthly_friction["Cancelled"],
          name="Cancelled Orders",
          mode="lines+markers",
          line=dict(color="#d62728", width=2.5),
      )
  )
  fig_frict.add_trace(
      go.Scatter(
          x=monthly_friction["year_month"],
          y=monthly_friction["Returned"],
          name="Returned Orders",
          mode="lines+markers",
          line=dict(color="#9467bd", width=2.5, dash="dot"),
      )
  )

  fig_frict.update_layout(
      title="Cancellations vs. Returns (Monthly)",
      hovermode="x unified",
      height=380,
      margin=dict(l=20, r=20, t=40, b=20),
      legend=dict(
          orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
      ),
  )
  fig_frict.update_yaxes(title_text="Number of Incidents", showgrid=True)
  st.plotly_chart(fig_frict, use_container_width=True)
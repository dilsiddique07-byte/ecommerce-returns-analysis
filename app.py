import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Page configuration
st.set_page_config(page_title="E-Commerce Sales & Returns Analytics", layout="wide")

st.title("📦 E-Commerce Sales, Returns & Customer Analysis")
st.markdown("Interactive analytical dashboard to track revenue, customer purchasing, and product return patterns.")

# 1. Data Generation / Loading
@st.cache_data
def get_data():
    np.random.seed(42)
    n = 1200
    categories = ['Electronics', 'Clothing', 'Home & Kitchen', 'Footwear', 'Beauty']
    regions = ['North', 'South', 'East', 'West']
    
    dates = pd.date_range(start="2025-01-01", periods=180, freq='D')
    
    data = {
        'Order_ID': [f'ORD-{1000 + i}' for i in range(n)],
        'Date': np.random.choice(dates, n),
        'Category': np.random.choice(categories, n, p=[0.25, 0.30, 0.20, 0.15, 0.10]),
        'Region': np.random.choice(regions, n),
        'Price': np.random.randint(200, 5000, n),
        'Quantity': np.random.randint(1, 4, n),
    }
    df = pd.DataFrame(data)
    df['Total_Sales'] = df['Price'] * df['Quantity']
    
    # Return probability based on category (Clothing & Footwear return more)
    return_probs = {'Electronics': 0.12, 'Clothing': 0.35, 'Home & Kitchen': 0.08, 'Footwear': 0.28, 'Beauty': 0.05}
    df['Returned'] = df['Category'].apply(lambda cat: np.random.choice([1, 0], p=[return_probs[cat], 1 - return_probs[cat]]))
    df['Return_Status'] = df['Returned'].map({1: 'Returned', 0: 'Delivered'})
    return df

df = get_data()

# 2. Sidebar Filters
st.sidebar.header("Filter Data")
selected_region = st.sidebar.multiselect("Select Region", options=df['Region'].unique(), default=df['Region'].unique())
selected_category = st.sidebar.multiselect("Select Category", options=df['Category'].unique(), default=df['Category'].unique())

filtered_df = df[(df['Region'].isin(selected_region)) & (df['Category'].isin(selected_category))]

# 3. Top KPI Cards
total_orders = len(filtered_df)
total_sales = filtered_df['Total_Sales'].sum()
total_returns = filtered_df['Returned'].sum()
return_rate = (total_returns / total_orders * 100) if total_orders > 0 else 0
lost_revenue = filtered_df[filtered_df['Returned'] == 1]['Total_Sales'].sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Orders", f"{total_orders:,}")
c2.metric("Total Revenue", f"₹{total_sales:,.0f}")
c3.metric("Return Rate", f"{return_rate:.1f}%")
c4.metric("Revenue Lost in Returns", f"₹{lost_revenue:,.0f}")

st.divider()

# 4. Charts & Visualizations
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Return Rate by Category")
    cat_summary = filtered_df.groupby('Category').agg(
        Total=('Returned', 'count'),
        Returns=('Returned', 'sum')
    ).reset_index()
    cat_summary['Return_Rate_%'] = (cat_summary['Returns'] / cat_summary['Total']) * 100
    
    fig_bar = px.bar(
        cat_summary, 
        x='Category', 
        y='Return_Rate_%', 
        color='Return_Rate_%',
        text_auto='.1f',
        color_continuous_scale='Reds',
        title="Category-wise Return Percentage"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("🗺️ Revenue by Region & Delivery Status")
    fig_pie = px.sunburst(
        filtered_df, 
        path=['Region', 'Return_Status'], 
        values='Total_Sales',
        title="Sales Distribution & Return Breakdown"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# 5. Timeline Analysis
st.subheader("📈 Monthly Sales vs Returns Trend")
monthly_df = filtered_df.copy()
monthly_df['Month'] = pd.to_datetime(monthly_df['Date']).dt.to_period('M').astype(str)
trend = monthly_df.groupby(['Month', 'Return_Status'])['Total_Sales'].sum().reset_index()

fig_line = px.line(
    trend, 
    x='Month', 
    y='Total_Sales', 
    color='Return_Status', 
    markers=True,
    title="Monthly Revenue Trend (Delivered vs Returned)"
)
st.plotly_chart(fig_line, use_container_width=True)

# 6. Raw Data Table
with st.expander("🔍 View Raw Transactions Data"):
    st.dataframe(filtered_df)

#Save cleaned dataset locally
filtered_df.to_csv("cleaned_ecommerce_data.csv",index=False)
st.sidebar.download_button("Download Cleaned Data (CSV)",data=filtered_df.to_csv(index=False), file_name="cleaned_ecommorce_data.csv", mime="text/csv")
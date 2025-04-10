import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.dates as mdates  # Import mdates for date formatting
import geopandas as gpd
from shapely.geometry import Point
import os

# === CONFIG DASHBOARD ===
st.set_page_config(
    page_title="Brazil E-Commerce Dashboard",
    layout="wide",
    page_icon="📦"
)

# Apply custom CSS for consistent styling
st.markdown(
    """
    <style>
    body {
        background-color: #f5f5f5;
        font-family: 'Arial', sans-serif;
    }
    .stMetric {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stMarkdown h2 {
        color: #2c3e50;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Set a consistent Seaborn style
sns.set_style("whitegrid")

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the CSV file
csv_path = os.path.join(current_dir, "main_data.csv")

# Load the dataset
df = pd.read_csv(csv_path)

# Convert 'order_purchase_timestamp' to datetime format
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'], errors='coerce')

# Drop rows with invalid datetime values
df = df.dropna(subset=['order_purchase_timestamp'])

# === SIDEBAR ===
min_date = df['order_purchase_timestamp'].min()
max_date = df['order_purchase_timestamp'].max()
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://www.pngmart.com/files/23/Shop-PNG-Isolated-File.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# === HEADER ===
st.title("📊 **Brazil E-Commerce Customer Dashboard**")
st.markdown(
    """
    Analisis berdasarkan segmentasi kota, penjualan produk, dan keterlambatan pengiriman.
    """,
    unsafe_allow_html=True
)

def get_metrics(df):
    total_products = df['order_item_id'].count()
    total_revenue = df['revenue'].sum()
    return total_revenue, total_products

# === PLOT FUNCTIONS ===

def plot_daily_orders(df, start_date, end_date):
    # Ensure the timestamp column is in datetime format
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'], errors='coerce')
    
    # Filter the dataframe based on the selected date range
    filtered_df = df[
        (df['order_purchase_timestamp'] >= pd.to_datetime(start_date)) &
        (df['order_purchase_timestamp'] <= pd.to_datetime(end_date))
    ]
    
    # Check if the filtered DataFrame is empty
    if filtered_df.empty:
        st.warning("No data available for the selected date range.")
        return
    
    # Group by date and count the number of orders
    daily_orders = filtered_df.groupby(filtered_df['order_purchase_timestamp'].dt.date)['order_id'].count()
    
    # Plot the data
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(daily_orders.index, daily_orders.values, marker='o', linestyle='-', color='#6A0DAD')  # Purple line
    
    # Format the x-axis for better readability
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    
    ax.set_title('Daily Orders', fontsize=16, color='#6A0DAD')
    ax.set_xlabel('Tanggal', fontsize=12, color='#6A0DAD')
    ax.set_ylabel('Jumlah Pesanan', fontsize=12, color='#6A0DAD')
    
    st.pyplot(fig)

def plot_heatmap(df):
    # Ensure the required columns exist
    if not {'lon', 'lat', 'segment_kota'}.issubset(df.columns):
        st.error("The dataset is missing required columns: 'lon', 'lat', or 'segment_kota'.")
        return

    # 🧭 Create geometry column from coordinates
    geometry = [Point(xy) for xy in zip(df['lon'], df['lat'])]

    # 🌍 Create GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the full path to the shapefile
    shapefile_path = os.path.join(current_dir, "ne_110m_admin_0_countries", "ne_110m_admin_0_countries.shp")

    # Load shapefile for Brazil
    try:
        world = gpd.read_file(shapefile_path)
    except FileNotFoundError:
        st.error("Shapefile not found. Please check the file path.")
        return

    brazil = world[world['ADMIN'] == 'Brazil']

    # 🧼 Filter points within Brazil's boundaries
    gdf_brazil = gdf[gdf.within(brazil.geometry.unary_union)]

    # 🎨 Plot segmentation heatmap
    fig, ax = plt.subplots(figsize=(12, 10))
    brazil.plot(ax=ax, color='lightgray', edgecolor='white')

    gdf_brazil.plot(
        ax=ax,
        column='segment_kota',  # Ensure this column exists in your dataset
        legend=True,
        markersize=35,
        alpha=0.7,
        cmap='Purples'  # Purple gradient
    )

    plt.title("📍 Heatmap Segmentasi Kota berdasarkan RFM (GeoPandas)", fontsize=14, color='#6A0DAD')
    plt.axis("off")
    plt.tight_layout()
    st.pyplot(fig)

def plot_amount_by_segment(df):
    # Ensure the required columns exist
    if not {'segment_kota', 'customer_city'}.issubset(df.columns):
        st.error("The dataset is missing required columns: 'segment_kota' or 'customer_city'.")
        return

    # Group by 'segment_kota' and count the number of unique cities
    kota_per_segment = df.groupby('segment_kota')['customer_city'].nunique().reset_index()
    kota_per_segment.columns = ['segment_kota', 'jumlah_kota']  # Rename columns for clarity

    # Create a custom color palette
    max_value = kota_per_segment['jumlah_kota'].max()
    colors = ['#D8BFD8' if jumlah_kota < max_value else '#6A0DAD' for jumlah_kota in kota_per_segment['jumlah_kota']]  # Purple shades

    # Plot the data
    plt.figure(figsize=(8, 6))
    sns.barplot(data=kota_per_segment, x='segment_kota', y='jumlah_kota', palette=colors)

    plt.title('Jumlah Kota per Segmen Kota (RFM)', fontsize=14, color='#6A0DAD')
    plt.xlabel('Segment Kota', fontsize=12, color='#6A0DAD')
    plt.ylabel('Jumlah Kota (Unik)', fontsize=12, color='#6A0DAD')
    plt.xticks(rotation=15)
    plt.tight_layout()
    st.pyplot(plt.gcf())

def plot_heatmap_revenue(df):
    # Top 10 cities and categories
    top_kota = df.groupby('customer_city')['revenue'].sum().nlargest(10).index
    top_kategori = df.groupby('product_category_name')['revenue'].sum().nlargest(10).index

    # Filter
    filtered_df = df[
        df['customer_city'].isin(top_kota) &
        df['product_category_name'].isin(top_kategori)
    ]

    # Pivot and plot top 10
    pivot_top10 = filtered_df.pivot_table(index='customer_city', columns='product_category_name', values='revenue', fill_value=0)

    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot_top10, cmap='Purples', annot=True, fmt='.0f', linewidths=0.5)  # Purple gradient
    plt.title('Heatmap Revenue - Top 10 Kota & Produk', fontsize=14, color='#6A0DAD')
    plt.xlabel('Kategori Produk', fontsize=12, color='#6A0DAD')
    plt.ylabel('Kota', fontsize=12, color='#6A0DAD')
    plt.tight_layout()
    st.pyplot(plt.gcf())

def plot_heatmap_revenue_bottom(df):
    # Group by customer_city and product_category_name, then calculate revenue
    bottom10_combos = df.groupby(['customer_city', 'product_category_name'])['revenue'].sum() \
        .reset_index() \
        .sort_values(by='revenue').head(10)

    # Check if bottom10_combos is empty
    if bottom10_combos.empty:
        st.warning("No data available for the bottom 10 heatmap.")
        return

    # Pivot and plot bottom 10
    pivot_bottom10 = bottom10_combos.pivot_table(
        index='customer_city', 
        columns='product_category_name', 
        values='revenue', 
        fill_value=0
    )

    # Check if pivot table is empty
    if pivot_bottom10.empty:
        st.warning("No data available to generate the heatmap for the bottom 10.")
        return

    # Plot bottom 10 heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot_bottom10, cmap='Purples', annot=True, fmt='.0f', linewidths=0.5)  # Purple gradient
    plt.title('Heatmap Revenue - Bottom 10 Kota & Produk', fontsize=14, color='#6A0DAD')
    plt.xlabel('Kategori Produk', fontsize=12, color='#6A0DAD')
    plt.ylabel('Kota', fontsize=12, color='#6A0DAD')
    plt.tight_layout()
    st.pyplot(plt.gcf())

def plot_late_delivery(df):
    # Ensure the required columns exist
    if not {'lon', 'lat', 'delay'}.issubset(df.columns):
        st.error("The dataset is missing required columns: 'lon', 'lat', or 'delay'.")
        return

    # Create geometry column from 'lon' and 'lat'
    try:
        df['geometry'] = [Point(xy) for xy in zip(df['lon'], df['lat'])]
    except Exception as e:
        st.error(f"Error creating geometry column: {e}")
        return

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')

    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the full path to the shapefile
    shapefile_path = os.path.join(current_dir, "ne_110m_admin_0_countries", "ne_110m_admin_0_countries.shp")

    # Load shapefile for Brazil
    try:
        world = gpd.read_file(shapefile_path)
    except FileNotFoundError:
        st.error("Shapefile not found. Please check the file path.")
        return

    brazil = world[world['ADMIN'] == 'Brazil']

    # Filter points within Brazil's boundaries
    gdf_brazil_only = gdf[gdf.within(brazil.geometry.unary_union)]

    # Check if filtered GeoDataFrame is empty
    if gdf_brazil_only.empty:
        st.warning("No data available for late delivery heatmap.")
        return

    # Plot
    fig, ax = plt.subplots(figsize=(8, 8))  # Reduced figure size

    # Base map: Brazil
    brazil.plot(ax=ax, color='lightgray', edgecolor='white')

    # Points for late deliveries
    gdf_brazil_only.plot(
        ax=ax,
        column='delay',
        cmap='Purples',  # Purple gradient
        legend=True,
        markersize=40,
        alpha=0.7
    )

    plt.title("Heatmap Rata-rata Keterlambatan per Kota di Brazil (GeoPandas)", fontsize=12, color='#6A0DAD')
    plt.axis('off')
    plt.tight_layout()
    st.pyplot(fig)

# Calculate metrics
total_revenue, total_products = get_metrics(df)

# === INTEGRATE INTO DASHBOARD ===
# Add a prominent title for the KPI section
st.markdown("## 📈 **Ringkasan KPI**")  # Larger and bold title at the top

# Create two columns for metrics
col1, col2 = st.columns(2)

# Add content to the first column
with col1:
    col1.metric("💰 Total Revenue", f"R$ {total_revenue:,.2f}", delta=None)
    
# Add content to the second column
with col2:
    col2.metric("📦 Produk Terjual", f"{total_products:,} pcs", delta=None)

# === DAILY ORDERS PLOT SECTION ===
st.markdown("## 📅 **Daily Orders**")
plot_daily_orders(df, start_date, end_date)

# === HEATMAP AND SEGMENTATION BAR PLOT SECTION ===
st.markdown("## 📊 **Visualisasi Data untuk Segmentasi Kota**")

# Create two columns
col1, col2 = st.columns(2)

# Add the heatmap to the first column
with col1:
    st.markdown("#### 📍 **Heatmap Segmentasi Kota**")
    plot_heatmap(df)

# Add the bar plot to the second column
with col2:
    st.markdown("#### 📊 **Jumlah Kota per Segmen Kota**")
    plot_amount_by_segment(df)

# === HEATMAP REVENUE SECTION ===
st.markdown("## 📊 **Heatmap Revenue untuk Top dan Bottom Kota & Produk**")

# Create two columns
col1, col2 = st.columns(2)

# Add the top 10 heatmap to the first column
with col1:
    st.markdown("#### 🔝 **Heatmap Revenue - Top 10 Kota & Produk**")
    plot_heatmap_revenue(df)

# Add the bottom 10 heatmap to the second column
with col2:
    st.markdown("#### 🔻 **Heatmap Revenue - Bottom 10 Kota & Produk**")
    plot_heatmap_revenue_bottom(df)

# === LATE DELIVERY HEATMAP SECTION ===
st.markdown("## 📍 **Heatmap Keterlambatan Pengiriman**")
plot_late_delivery(df)
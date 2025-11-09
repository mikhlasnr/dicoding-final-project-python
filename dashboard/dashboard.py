import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import folium
from folium.plugins import HeatMap

# Konfigurasi halaman
st.set_page_config(
    page_title="E-Commerce Dashboard - Olist",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    """Load dan prepare data untuk dashboard"""
    # Path relatif dari lokasi dashboard.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(current_dir)
    data_dir = os.path.join(base_dir, 'data')

    # Load all_data.csv
    csv_path = os.path.join(current_dir, 'all_data.csv')
    df = pd.read_csv(csv_path)

    # Konversi kolom tanggal
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['order_date'] = pd.to_datetime(df['order_date'])

    return df, data_dir

# Load data
df, data_dir = load_data()

# Load data tambahan untuk analisis kategori dan geospatial
@st.cache_data
def load_category_data():
    """Load data untuk analisis kategori produk"""
    try:
        order_items_df = pd.read_csv(os.path.join(data_dir, 'order_items_dataset.csv'))
        products_df = pd.read_csv(os.path.join(data_dir, 'products_dataset.csv'))
        product_category_df = pd.read_csv(os.path.join(data_dir, 'product_category_name_translation.csv'))

        # Cleaning products
        products_df['product_category_name'] = products_df['product_category_name'].fillna('uncategorized')

        # Mapping kategori ke English
        if {'product_category_name','product_category_name_english'}.issubset(set(product_category_df.columns)):
            category_map = dict(zip(product_category_df['product_category_name'],
                                   product_category_df['product_category_name_english']))
            products_df['product_category_en'] = products_df['product_category_name'].map(category_map)
            products_df['product_category_en'] = products_df['product_category_en'].fillna(products_df['product_category_name'])
        else:
            products_df['product_category_en'] = products_df.get('product_category_name', 'uncategorized')

        # Hitung GMV per item
        order_items_df['item_gmv'] = order_items_df['price'] + order_items_df['freight_value']

        # Gabungkan order_items dengan products
        order_items_products = order_items_df.merge(
            products_df[['product_id', 'product_category_en']],
            on='product_id',
            how='left'
        )

        return order_items_products
    except Exception as e:
        st.warning(f"Tidak dapat memuat data kategori: {e}")
        return None

@st.cache_data
def load_geolocation_data():
    """Load data geolocation untuk peta"""
    try:
        geolocation_df = pd.read_csv(os.path.join(data_dir, 'geolocation_dataset.csv'))
        customers_df = pd.read_csv(os.path.join(data_dir, 'customers_dataset.csv'))
        sellers_df = pd.read_csv(os.path.join(data_dir, 'sellers_dataset.csv'))

        # Agregasi geolocation per zip code prefix
        geo_agg = geolocation_df.groupby('geolocation_zip_code_prefix', as_index=False).agg({
            'geolocation_lat': 'mean',
            'geolocation_lng': 'mean'
        })

        # Gabungkan customer dengan geolocation
        customers_geo = customers_df.merge(
            geo_agg,
            left_on='customer_zip_code_prefix',
            right_on='geolocation_zip_code_prefix',
            how='left'
        )

        # Gabungkan seller dengan geolocation
        sellers_geo = sellers_df.merge(
            geo_agg,
            left_on='seller_zip_code_prefix',
            right_on='geolocation_zip_code_prefix',
            how='left'
        )

        return customers_geo, sellers_geo, geo_agg
    except Exception as e:
        st.warning(f"Tidak dapat memuat data geolocation: {e}")
        return None, None, None

# Load data tambahan
order_items_products = load_category_data()
customers_geo, sellers_geo, geo_agg = load_geolocation_data()

# Sidebar
st.sidebar.title("📊 Navigasi Dashboard")
st.sidebar.markdown("---")

# Filter tanggal
st.sidebar.subheader("🔍 Filter Data")
min_date = df['order_date'].min().date()
max_date = df['order_date'].max().date()

date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Filter state
states = ['Semua'] + sorted(df['customer_state'].unique().tolist())
selected_state = st.sidebar.selectbox("Pilih State", states)

# Apply filters
df_filtered = df.copy()
if len(date_range) == 2:
    df_filtered = df_filtered[
        (df_filtered['order_date'].dt.date >= date_range[0]) &
        (df_filtered['order_date'].dt.date <= date_range[1])
    ]

if selected_state != 'Semua':
    df_filtered = df_filtered[df_filtered['customer_state'] == selected_state]

# Header
st.markdown('<h1 class="main-header">📊 E-Commerce Dashboard - Olist</h1>', unsafe_allow_html=True)
st.markdown("---")

# ==================== OVERVIEW METRICS ====================
st.header("📈 Overview Metrics")

col1, col2, col3, col4 = st.columns(4)

total_orders = len(df_filtered)
total_gmv = df_filtered['order_gmv'].sum()
avg_aov = df_filtered['order_gmv'].mean()
total_customers = df_filtered['customer_unique_id'].nunique()

with col1:
    st.metric(
        label="Total Orders",
        value=f"{total_orders:,}",
        delta=None
    )

with col2:
    st.metric(
        label="Total GMV",
        value=f"R$ {total_gmv:,.2f}",
        delta=None
    )

with col3:
    st.metric(
        label="Average Order Value (AOV)",
        value=f"R$ {avg_aov:.2f}",
        delta=None
    )

with col4:
    st.metric(
        label="Total Customers",
        value=f"{total_customers:,}",
        delta=None
    )

st.markdown("---")

# ==================== TREN BULANAN ====================
st.header("📅 Tren Bulanan: Orders, GMV, dan AOV")

# Agregasi bulanan
monthly_df = df_filtered.groupby('order_date', as_index=False).agg({
    'order_id': 'nunique',
    'order_gmv': 'sum'
}).rename(columns={'order_id': 'orders', 'order_gmv': 'gmv'})

monthly_df['aov'] = monthly_df['gmv'] / monthly_df['orders']
monthly_df = monthly_df.sort_values('order_date')

# Plot tren dengan Plotly
fig_tren = go.Figure()

# Orders
fig_tren.add_trace(go.Scatter(
    x=monthly_df['order_date'],
    y=monthly_df['orders'],
    mode='lines+markers',
    name='Orders',
    line=dict(color='#72BCD4', width=3),
    marker=dict(size=8)
))

# GMV (dalam ribuan)
fig_tren.add_trace(go.Scatter(
    x=monthly_df['order_date'],
    y=monthly_df['gmv'] / 1000,
    mode='lines+markers',
    name='GMV (x1000 R$)',
    line=dict(color='#4C9A2A', width=3),
    marker=dict(size=8),
    yaxis='y2'
))

fig_tren.update_layout(
    title='Tren Bulanan: Orders dan GMV (2016-2018)',
    xaxis_title='Bulan',
    yaxis_title='Orders / GMV (x1000 R$)',
    yaxis2=dict(
        title='GMV (x1000 R$)',
        overlaying='y',
        side='right'
    ),
    hovermode='x unified',
    height=400,
    legend=dict(x=0.02, y=0.98),
    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'),
    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray')
)

st.plotly_chart(fig_tren, use_container_width=True)

# AOV Chart - dengan label nilai di setiap titik seperti di notebook
fig_aov = go.Figure()

fig_aov.add_trace(go.Scatter(
    x=monthly_df['order_date'],
    y=monthly_df['aov'],
    mode='lines+markers',
    name='AOV',
    line=dict(color='#D36C6C', width=3),
    marker=dict(size=8),
    fill='tonexty'
))

avg_aov_monthly = monthly_df['aov'].mean()
fig_aov.add_hline(
    y=avg_aov_monthly,
    line_dash="dash",
    line_color="gray",
    annotation_text=f"Rata-rata AOV: R$ {avg_aov_monthly:.2f}"
)

# Tambahkan label nilai pada setiap titik seperti di notebook
for idx, row in monthly_df.iterrows():
    offset = 5 if row['aov'] >= avg_aov_monthly else -8
    fig_aov.add_annotation(
        x=row['order_date'],
        y=row['aov'] + offset,
        text=f"R$ {row['aov']:.2f}",
        showarrow=False,
        font=dict(size=9, color='#333333'),
        bgcolor='white',
        bordercolor='gray',
        borderwidth=0.5,
        borderpad=3
    )

fig_aov.update_layout(
    title='Tren Bulanan: Average Order Value (AOV) (2016-2018)',
    xaxis_title='Bulan',
    yaxis_title='AOV (R$)',
    hovermode='x unified',
    height=400
)

st.plotly_chart(fig_aov, use_container_width=True)

st.markdown("---")

# ==================== ANALISIS KATEGORI PRODUK ====================
st.header("📦 Analisis Kategori Produk")

if order_items_products is not None:
    # Filter order_items berdasarkan order_id yang ada di df_filtered
    order_items_filtered = order_items_products[
        order_items_products['order_id'].isin(df_filtered['order_id'])
    ].copy()

    # Analisis kategori produk
    category_agg = order_items_filtered.groupby('product_category_en', as_index=False).agg({
        'item_gmv': 'sum',
        'order_id': 'nunique',
        'freight_value': 'sum',
        'price': 'sum'
    }).rename(columns={'order_id': 'orders'})

    # Hitung freight ratio
    category_agg['freight_ratio'] = category_agg['freight_value'] / (category_agg['price'].replace(0, np.nan))

    # Top 10 kategori berdasarkan GMV
    top_categories_gmv = category_agg.sort_values('item_gmv', ascending=False).head(10).reset_index(drop=True)

    # Top 10 kategori berdasarkan Volume
    top_categories_volume = category_agg.sort_values('orders', ascending=False).head(10).reset_index(drop=True)

    # Visualisasi 1: Top 10 Kategori berdasarkan GMV dan Volume
    col1, col2 = st.columns(2)

    with col1:
        fig_gmv = px.bar(
            top_categories_gmv,
            x='item_gmv',
            y='product_category_en',
            orientation='h',
            title='Top 10 Kategori berdasarkan GMV',
            labels={'item_gmv': 'GMV (R$)', 'product_category_en': 'Kategori'},
            color='item_gmv',
            color_continuous_scale='Blues'
        )
        fig_gmv.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
        # Tambahkan label nilai GMV pada setiap bar seperti di notebook
        for i, (idx, row) in enumerate(top_categories_gmv.iterrows()):
            fig_gmv.add_annotation(
                x=row['item_gmv'],
                y=row['product_category_en'],
                text=f" R$ {row['item_gmv']:,.0f}",
                showarrow=False,
                xanchor='left',
                font=dict(size=9, color='black', family='Arial Black')
            )
        st.plotly_chart(fig_gmv, use_container_width=True)

    with col2:
        fig_vol = px.bar(
            top_categories_volume,
            x='orders',
            y='product_category_en',
            orientation='h',
            title='Top 10 Kategori berdasarkan Volume Order',
            labels={'orders': 'Jumlah Order', 'product_category_en': 'Kategori'},
            color='orders',
            color_continuous_scale='Greens'
        )
        fig_vol.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
        # Tambahkan label nilai orders pada setiap bar seperti di notebook
        for i, (idx, row) in enumerate(top_categories_volume.iterrows()):
            fig_vol.add_annotation(
                x=row['orders'],
                y=row['product_category_en'],
                text=f" {row['orders']:,.0f}",
                showarrow=False,
                xanchor='left',
                font=dict(size=9, color='black', family='Arial Black')
            )
        st.plotly_chart(fig_vol, use_container_width=True)

    # Visualisasi 2: Freight Ratio
    col1, col2 = st.columns(2)

    with col1:
        # Freight Ratio untuk Top 10 Kategori GMV
        plot_fr_gmv = top_categories_gmv.copy()
        plot_fr_gmv['freight_ratio_pct'] = plot_fr_gmv['freight_ratio'] * 100

        fig_fr_gmv = px.bar(
            plot_fr_gmv,
            x='freight_ratio_pct',
            y='product_category_en',
            orientation='h',
            title='Freight Ratio untuk Top 10 Kategori GMV',
            labels={'freight_ratio_pct': 'Freight Ratio (%)', 'product_category_en': 'Kategori'},
            color='freight_ratio_pct',
            color_continuous_scale='Reds'
        )
        fig_fr_gmv.add_vline(x=20, line_dash="dash", line_color="orange",
                             annotation_text="Threshold 20%")
        fig_fr_gmv.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
        # Tambahkan label nilai freight ratio pada setiap bar seperti di notebook
        for i, (idx, row) in enumerate(plot_fr_gmv.iterrows()):
            fig_fr_gmv.add_annotation(
                x=row['freight_ratio_pct'],
                y=row['product_category_en'],
                text=f" {row['freight_ratio_pct']:.2f}%",
                showarrow=False,
                xanchor='left',
                font=dict(size=9, color='black', family='Arial Black')
            )
        st.plotly_chart(fig_fr_gmv, use_container_width=True)

    with col2:
        # Top 10 Kategori dengan Freight Ratio Tertinggi
        high_freight = category_agg[category_agg['freight_ratio'] > 0.3].sort_values(
            'freight_ratio', ascending=False
        ).head(10).reset_index(drop=True)

        if len(high_freight) > 0:
            high_freight['freight_ratio_pct'] = high_freight['freight_ratio'] * 100

            fig_high_fr = px.bar(
                high_freight,
                x='freight_ratio_pct',
                y='product_category_en',
                orientation='h',
                title='Top 10 Kategori dengan Freight Ratio Tertinggi (>30%)',
                labels={'freight_ratio_pct': 'Freight Ratio (%)', 'product_category_en': 'Kategori'},
                color='freight_ratio_pct',
                color_continuous_scale='Reds'
            )
            fig_high_fr.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
            # Tambahkan label nilai freight ratio dan GMV pada setiap bar seperti di notebook
            for i, (idx, row) in enumerate(high_freight.iterrows()):
                fig_high_fr.add_annotation(
                    x=row['freight_ratio_pct'],
                    y=row['product_category_en'],
                    text=f" {row['freight_ratio_pct']:.2f}% (GMV: R$ {row['item_gmv']:,.0f})",
                    showarrow=False,
                    xanchor='left',
                    font=dict(size=9, color='black', family='Arial Black')
                )
            st.plotly_chart(fig_high_fr, use_container_width=True)
        else:
            st.info("Tidak ada kategori dengan freight ratio > 30%")
else:
    st.info("ℹ️ Analisis kategori produk memerlukan data tambahan dari tabel order_items dan products. Fitur ini akan ditampilkan jika data tersedia.")

st.markdown("---")

# ==================== RFM ANALYSIS ====================
st.header("👥 RFM Analysis - Segmentasi Pelanggan")

# Hitung RFM
rfm_df = df_filtered.groupby('customer_unique_id', as_index=False).agg({
    'order_purchase_timestamp': 'max',
    'order_id': 'nunique',
    'order_gmv': 'sum'
})

rfm_df.columns = ['customer_unique_id', 'max_order_timestamp', 'frequency', 'monetary']

# Hitung Recency
recent_date = df_filtered['order_purchase_timestamp'].max()
rfm_df['max_order_timestamp'] = pd.to_datetime(rfm_df['max_order_timestamp'])
rfm_df['recency'] = (recent_date - rfm_df['max_order_timestamp']).dt.days

# Normalisasi RFM scores
rfm_df['r_rank'] = rfm_df['recency'].rank(ascending=False)
rfm_df['f_rank'] = rfm_df['frequency'].rank(ascending=True)
rfm_df['m_rank'] = rfm_df['monetary'].rank(ascending=True)

rfm_df['r_rank_norm'] = (rfm_df['r_rank'] / rfm_df['r_rank'].max()) * 100
rfm_df['f_rank_norm'] = (rfm_df['f_rank'] / rfm_df['f_rank'].max()) * 100
rfm_df['m_rank_norm'] = (rfm_df['m_rank'] / rfm_df['m_rank'].max()) * 100

# Hitung RFM Score
rfm_df['RFM_score'] = (0.15 * rfm_df['r_rank_norm'] +
                       0.28 * rfm_df['f_rank_norm'] +
                       0.57 * rfm_df['m_rank_norm'])
rfm_df['RFM_score'] = rfm_df['RFM_score'] * 0.05

# Segmentasi
rfm_df['customer_segment'] = np.where(
    rfm_df['RFM_score'] > 4.5, "Top customers",
    np.where(rfm_df['RFM_score'] > 4, "High value customer",
    np.where(rfm_df['RFM_score'] > 3, "Medium value customer",
    np.where(rfm_df['RFM_score'] > 1.6, 'Low value customers', 'Lost customers'))))

# Distribusi segmentasi
customer_segment_df = rfm_df.groupby('customer_segment', as_index=False).agg({
    'customer_unique_id': 'nunique',
    'monetary': 'mean',
    'frequency': 'mean',
    'recency': 'mean'
}).rename(columns={'customer_unique_id': 'customer_count'})

segment_order = ["lost customers", "Low value customers", "Medium value customer",
                 "High value customer", "Top customers"]
customer_segment_df['customer_segment'] = pd.Categorical(
    customer_segment_df['customer_segment'],
    categories=segment_order,
    ordered=True
)
customer_segment_df = customer_segment_df.sort_values('customer_segment')

# Visualisasi distribusi segment dengan anotasi nilai seperti di notebook
fig_rfm = px.bar(
    customer_segment_df,
    x='customer_count',
    y='customer_segment',
    orientation='h',
    title='Distribusi Customer Segment berdasarkan RFM Score',
    labels={'customer_count': 'Jumlah Customer', 'customer_segment': 'Customer Segment'},
    color='customer_count',
    color_continuous_scale='Blues'
)

fig_rfm.update_layout(height=400)
# Tambahkan anotasi nilai pada setiap bar seperti di notebook
for i, (idx, row) in enumerate(customer_segment_df.iterrows()):
    fig_rfm.add_annotation(
        x=row['customer_count'],
        y=row['customer_segment'],
        text=f"  {row['customer_count']:,}",
        showarrow=False,
        xanchor='left',
        font=dict(size=10, color='black')
    )
st.plotly_chart(fig_rfm, use_container_width=True)

# Visualisasi Top 5 Customers by Recency, Frequency, dan Monetary
st.subheader("🏆 Top 5 Customers berdasarkan RFM Parameters")

col1, col2 = st.columns(2)

 # Top 5 by Recency
top_recency = rfm_df.nsmallest(5, 'recency').reset_index(drop=True)
fig_recency = px.bar(
    top_recency,
    x='recency',
    y='customer_unique_id',
    orientation='h',
    title='Top 5 Customers by Recency (days)',
    labels={'recency': 'Recency (days)', 'customer_unique_id': 'Customer ID'},
    color='recency',
    color_continuous_scale='Blues_r'
)
fig_recency.update_layout(height=300, yaxis={'categoryorder': 'total ascending'})
fig_recency.update_xaxes(range=[0, 15])

# Tambahkan label nilai recency pada setiap bar seperti di notebook
for i, (idx, row) in enumerate(top_recency.iterrows()):
    fig_recency.add_annotation(
        x=row['recency'],
        y=row['customer_unique_id'],
        text=f" {row['recency']:.0f} days",
        showarrow=False,
        xanchor='left',
        font=dict(size=9, color='black', family='Arial Black')
    )
st.plotly_chart(fig_recency, use_container_width=True)
with col1:
    # Top 5 by Frequency
    top_frequency = rfm_df.nlargest(5, 'frequency').reset_index(drop=True)
    fig_frequency = px.bar(
        top_frequency,
        x='frequency',
        y='customer_unique_id',
        orientation='h',
        title='Top 5 Customers by Frequency',
        labels={'frequency': 'Frequency', 'customer_unique_id': 'Customer ID'},
        color='frequency',
        color_continuous_scale='Greens'
    )
    fig_frequency.update_layout(height=300, yaxis={'categoryorder': 'total ascending'})
    # Tambahkan label nilai frequency pada setiap bar seperti di notebook
    for i, (idx, row) in enumerate(top_frequency.iterrows()):
        fig_frequency.add_annotation(
            x=row['frequency'],
            y=row['customer_unique_id'],
            text=f" {row['frequency']:.0f}x",
            showarrow=False,
            xanchor='left',
            font=dict(size=9, color='black', family='Arial Black')
        )
    st.plotly_chart(fig_frequency, use_container_width=True)

with col2:
  # Top 5 by Monetary
  top_monetary = rfm_df.nlargest(5, 'monetary').reset_index(drop=True)
  fig_monetary = px.bar(
      top_monetary,
      x='monetary',
      y='customer_unique_id',
      orientation='h',
      title='Top 5 Customers by Monetary',
      labels={'monetary': 'Monetary (R$)', 'customer_unique_id': 'Customer ID'},
      color='monetary',
      color_continuous_scale='Reds'
  )
  fig_monetary.update_layout(height=300, yaxis={'categoryorder': 'total ascending'})
  # Tambahkan label nilai monetary pada setiap bar seperti di notebook
  for i, (idx, row) in enumerate(top_monetary.iterrows()):
      fig_monetary.add_annotation(
          x=row['monetary'],
          y=row['customer_unique_id'],
          text=f" R$ {row['monetary']:,.0f}",
          showarrow=False,
          xanchor='left',
          font=dict(size=9, color='black', family='Arial Black')
      )
  st.plotly_chart(fig_monetary, use_container_width=True)

st.markdown("---")

# ==================== GEOSPATIAL ANALYSIS ====================
st.header("🗺️ Geospatial Analysis")

# Siapkan data customer_transactions_geo dan seller_transactions_geo terlebih dahulu
customer_transactions_geo = None
seller_transactions_geo = None

if customers_geo is not None and geo_agg is not None:
    # Agregasi transaksi per customer location (dengan zip code untuk peta)
    customer_transactions_geo_data = df_filtered.groupby(['customer_zip_code_prefix', 'customer_city', 'customer_state'], as_index=False).agg({
        'order_id': 'nunique',
        'order_gmv': 'sum'
    }).rename(columns={'order_id': 'order_count'})

    # Gabungkan dengan koordinat
    customer_transactions_geo = customer_transactions_geo_data.merge(
        geo_agg,
        left_on='customer_zip_code_prefix',
        right_on='geolocation_zip_code_prefix',
        how='left'
    )

    # Filter hanya yang punya koordinat valid
    customer_transactions_geo = customer_transactions_geo[
        customer_transactions_geo['geolocation_lat'].notna() &
        customer_transactions_geo['geolocation_lng'].notna()
    ]

# Siapkan data seller_transactions_geo
if sellers_geo is not None and geo_agg is not None:
    # Agregasi seller per zip code prefix (seperti di notebook)
    seller_transactions = sellers_geo.groupby(['seller_zip_code_prefix', 'seller_city', 'seller_state'], as_index=False).agg({
        'seller_id': 'nunique'
    }).rename(columns={'seller_id': 'seller_count'})

    # Gabungkan dengan koordinat
    seller_transactions_geo = seller_transactions.merge(
        geo_agg,
        left_on='seller_zip_code_prefix',
        right_on='geolocation_zip_code_prefix',
        how='left'
    )

    # Filter hanya yang punya koordinat valid
    seller_transactions_geo = seller_transactions_geo[
        seller_transactions_geo['geolocation_lat'].notna() &
        seller_transactions_geo['geolocation_lng'].notna()
    ]

# Agregasi per kota (menggabungkan semua zip code dalam satu kota) - seperti di notebook
customer_transactions_by_city = None
seller_transactions_by_city = None

if customer_transactions_geo is not None and len(customer_transactions_geo) > 0:
    # Agregasi customer transactions per kota (menggabungkan semua zip code)
    customer_transactions_by_city = customer_transactions_geo.groupby(['customer_city', 'customer_state'], as_index=False).agg({
        'order_count': 'sum',  # Jumlahkan semua order dari berbagai zip code dalam satu kota
        'order_gmv': 'sum',    # Jumlahkan semua GMV dari berbagai zip code dalam satu kota
        'geolocation_lat': 'mean',  # Rata-rata koordinat latitude untuk kota tersebut
        'geolocation_lng': 'mean'   # Rata-rata koordinat longitude untuk kota tersebut
    })

if seller_transactions_geo is not None and len(seller_transactions_geo) > 0:
    # Agregasi seller transactions per kota (menggabungkan semua zip code)
    seller_transactions_by_city = seller_transactions_geo.groupby(['seller_city', 'seller_state'], as_index=False).agg({
        'seller_count': 'sum',  # Jumlahkan semua seller dari berbagai zip code dalam satu kota
        'geolocation_lat': 'mean',  # Rata-rata koordinat latitude untuk kota tersebut
        'geolocation_lng': 'mean'   # Rata-rata koordinat longitude untuk kota tersebut
    })

# Visualisasi bar chart Top 10 Kota Customer dan Seller (side by side seperti di notebook)
col1, col2 = st.columns(2)

with col1:
    if customer_transactions_by_city is not None and len(customer_transactions_by_city) > 0:
        fig_cities = px.bar(
            customer_transactions_by_city.nlargest(10, 'order_count'),
            x='order_count',
            y='customer_city',
            orientation='h',
            title='Top 10 Kota Customer berdasarkan Order Count',
            labels={'order_count': 'Jumlah Order', 'customer_city': 'Kota'},
            color='order_count',
            color_continuous_scale='Blues'
        )
        fig_cities.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
        # Tambahkan label nilai pada setiap bar
        for i, (idx, row) in enumerate(customer_transactions_by_city.nlargest(10, 'order_count').iterrows()):
            fig_cities.add_annotation(
                x=row['order_count'],
                y=row['customer_city'],
                text=f" {row['order_count']:,.0f}",
                showarrow=False,
                xanchor='left',
                font=dict(size=10, color='black', family='Arial Black')
            )
        st.plotly_chart(fig_cities, use_container_width=True)
    else:
        st.info("Data customer tidak tersedia")

with col2:
    # Bar chart Top 10 Seller Cities (jika data tersedia)
    if seller_transactions_by_city is not None and len(seller_transactions_by_city) > 0:
        fig_sellers_side = px.bar(
            seller_transactions_by_city.nlargest(10, 'seller_count'),
            x='seller_count',
            y='seller_city',
            orientation='h',
            title='Top 10 Kota Seller berdasarkan Jumlah Seller',
            labels={'seller_count': 'Jumlah Seller', 'seller_city': 'Kota'},
            color='seller_count',
            color_continuous_scale='Greens'
        )
        fig_sellers_side.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
        # Tambahkan label nilai pada setiap bar
        for i, (idx, row) in enumerate(seller_transactions_by_city.nlargest(10, 'seller_count').iterrows()):
            fig_sellers_side.add_annotation(
                x=row['seller_count'],
                y=row['seller_city'],
                text=f" {row['seller_count']:,.0f}",
                showarrow=False,
                xanchor='left',
                font=dict(size=10, color='black', family='Arial Black')
            )
        st.plotly_chart(fig_sellers_side, use_container_width=True)
    else:
        st.info("Data seller tidak tersedia")

# Peta Interaktif
if customer_transactions_geo is not None and len(customer_transactions_geo) > 0:
    # Heatmap dengan Folium (alternatif)
    st.subheader("🗺️ Heatmap Customer Transactions")

    # Sample data untuk performa (max 5000 points)
    sample_data = customer_transactions_geo.sample(min(5000, len(customer_transactions_geo)))

    # Buat peta Folium
    brazil_map = folium.Map(
        location=[-14.2350, -51.9253],
        zoom_start=4,
        tiles='OpenStreetMap'
    )

    # Siapkan data untuk heatmap
    heat_data = [[row['geolocation_lat'], row['geolocation_lng'], row['order_count']]
                 for idx, row in sample_data.iterrows()]

    # Tambahkan heatmap
    HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(brazil_map)

    # Tambahkan marker untuk top 10 kota (gunakan data yang sudah diagregasi per kota)
    if customer_transactions_by_city is not None:
        top_cities_map = customer_transactions_by_city.nlargest(10, 'order_count')
        for idx, row in top_cities_map.iterrows():
            folium.CircleMarker(
                location=[row['geolocation_lat'], row['geolocation_lng']],
                radius=10,
                popup=f"{row['customer_city']}, {row['customer_state']}<br>Orders: {row['order_count']:,}<br>GMV: R$ {row['order_gmv']:,.0f}",
                color='blue',
                fill=True,
                fillColor='blue'
            ).add_to(brazil_map)

    # Tampilkan peta dengan HTML rendering untuk menghindari re-run terus menerus
    # Menggunakan HTML rendering langsung untuk mencegah interaksi yang memicu re-run
    map_html = brazil_map._repr_html_()
    # Modifikasi HTML untuk membuat width 100%
    map_html = map_html.replace('width:100%;', 'width:100% !important;')
    map_html = map_html.replace('width="100%"', 'width="100%" style="width:100% !important;"')
    st.components.v1.html(map_html, width=None, height=500, scrolling=False)

    # Peta Seller Locations (jika data tersedia)
    if seller_transactions_by_city is not None and len(seller_transactions_by_city) > 0:
        st.subheader("🗺️ Heatmap Seller Locations")

        # Sample data untuk performa (gunakan data yang sudah diagregasi per kota)
        sample_seller = seller_transactions_by_city.sample(min(2000, len(seller_transactions_by_city)))

        # Buat peta Folium untuk seller
        seller_map = folium.Map(
            location=[-14.2350, -51.9253],
            zoom_start=4,
            tiles='OpenStreetMap'
        )

        # Siapkan data untuk heatmap seller
        seller_heat_data = [[row['geolocation_lat'], row['geolocation_lng'], row['seller_count']]
                           for idx, row in sample_seller.iterrows()]

        # Tambahkan heatmap
        HeatMap(seller_heat_data, radius=15, blur=10, max_zoom=1,
                gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'orange', 1: 'red'}).add_to(seller_map)

        # Tambahkan marker untuk top 10 kota seller (gunakan data yang sudah diagregasi per kota)
        top_seller_cities_map = seller_transactions_by_city.nlargest(10, 'seller_count')
        for idx, row in top_seller_cities_map.iterrows():
            folium.CircleMarker(
                location=[row['geolocation_lat'], row['geolocation_lng']],
                radius=10,
                popup=f"{row['seller_city']}, {row['seller_state']}<br>Sellers: {row['seller_count']:,}",
                color='green',
                fill=True,
                fillColor='green'
            ).add_to(seller_map)

        # Tampilkan peta seller dengan HTML rendering
        seller_map_html = seller_map._repr_html_()
        # Modifikasi HTML untuk membuat width 100%
        seller_map_html = seller_map_html.replace('width:100%;', 'width:100% !important;')
        seller_map_html = seller_map_html.replace('width="100%"', 'width="100%" style="width:100% !important;"')
        st.components.v1.html(seller_map_html, width=None, height=500, scrolling=False)
else:
    st.info("ℹ️ Untuk menampilkan peta interaktif, diperlukan data koordinat geografis (latitude/longitude) dari tabel geolocation. Fitur ini akan ditampilkan jika data tersedia.")

st.markdown("---")

# ==================== FOOTER ====================
st.markdown("""
    <div style='text-align: center; padding: 2rem; color: #666;'>
        <p>📊 E-Commerce Dashboard - Olist | Dibuat dengan Streamlit</p>
        <p>Data periode: {} - {}</p>
    </div>
""".format(
    df['order_date'].min().strftime('%Y-%m-%d'),
    df['order_date'].max().strftime('%Y-%m-%d')
), unsafe_allow_html=True)


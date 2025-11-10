import streamlit as st
from streamlit_folium import st_folium

from utils import load_orders_data, load_order_items_data, load_geolocation_data, load_sellers_data
from analysis import analyze_monthly_trends, analyze_category_performance, analyze_rfm, prepare_geospatial_data
from visualizations import (
    plot_monthly_trends, plot_aov_trend, plot_top_categories_bar, plot_freight_ratio,
    plot_rfm_top_customers, plot_segment_distribution, plot_segment_pie,
    create_customer_heatmap, create_seller_heatmap,
    plot_gap_top_cities, plot_gap_no_seller_cities, plot_gap_comparison, plot_gap_categories_distribution
)
from insights import generate_trend_insights, generate_category_insights, generate_rfm_insights, generate_geospatial_insights

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Analisis E-Commerce",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data dengan caching
@st.cache_data
def load_data():
    """Load semua data yang diperlukan"""
    orders_df = load_orders_data()
    order_items_df = load_order_items_data()
    return orders_df, order_items_df

@st.cache_data
def load_geolocation_cached():
    """Load geolocation data dengan caching"""
    return load_geolocation_data()

@st.cache_data
def load_sellers_cached():
    """Load sellers data dengan caching"""
    return load_sellers_data()

# Load data
orders_df, order_items_df = load_data()

# ============================================
# SIDEBAR - Filter & Metrics
# ============================================
def render_sidebar(orders_df):
    """Render sidebar dengan filter dan metrics"""
    with st.sidebar:
        # Biodata
        st.subheader("👤 Biodata Pembuat")
        st.markdown("**Nama:**<br>Muhammad Ikhlas Naufalsyah Ranau", unsafe_allow_html=True)
        st.markdown("**Email:**<br>naufalsyah.ranau@gmail.com", unsafe_allow_html=True)
        st.markdown("**ID Dicoding:**<br><a href='https://www.dicoding.com/users/mikhlasnr/academies' target='_blank'>mikhlasnr</a>", unsafe_allow_html=True)
        st.markdown("---")

        min_date = orders_df['order_date'].min().date()
        max_date = orders_df['order_date'].max().date()

        st.subheader("🔍 Filter Data")
        st.caption(f"Data tersedia dari {min_date.strftime('%d %b %Y')} hingga {max_date.strftime('%d %b %Y')}")

        date_range = st.date_input(
            "Pilih Rentang Tanggal",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            help="Pilih rentang tanggal untuk memfilter data. Klik dua kali untuk memilih range."
        )

        if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
            start_date, end_date = date_range[0], date_range[1]
            if start_date > end_date:
                start_date, end_date = end_date, start_date
        else:
            start_date = min_date
            end_date = max_date

        filtered_orders = orders_df[
            (orders_df['order_date'].dt.date >= start_date) &
            (orders_df['order_date'].dt.date <= end_date)
        ].copy()

        return filtered_orders, start_date, end_date

# ============================================
# PERTANYAAN 1: TREN ORDERS, GMV, DAN AOV
# ============================================
def render_question_1(filtered_orders):
    """Render visualisasi dan insight untuk Pertanyaan 1"""
    st.header("📊 Pertanyaan 1: Tren Pertumbuhan & Pendapatan (Bulanan)")

    monthly_df = analyze_monthly_trends(filtered_orders)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Orders", f"{monthly_df['orders'].sum():,}")
    with col2:
        st.metric("Total GMV", f"R$ {monthly_df['gmv'].sum():,.2f}")
    with col3:
        st.metric("Rata-rata AOV", f"R$ {monthly_df['aov'].mean():.2f}")
    with col4:
        growth_rate = ((monthly_df['orders'].iloc[-1] / monthly_df['orders'].iloc[0]) ** (1/(len(monthly_df)-1)) - 1) * 100 if len(monthly_df) > 1 else 0
        st.metric("Pertumbuhan Bulanan", f"{growth_rate:.2f}%")

    st.plotly_chart(plot_monthly_trends(monthly_df), use_container_width=True)
    st.plotly_chart(plot_aov_trend(monthly_df), use_container_width=True)

    with st.expander("📝 Insight Analisis"):
        st.markdown(generate_trend_insights(monthly_df))

# ============================================
# PERTANYAAN 2: TOP KATEGORI & FREIGHT RATIO
# ============================================
def render_question_2(filtered_orders, order_items_df):
    """Render visualisasi dan insight untuk Pertanyaan 2"""
    st.header("📦 Pertanyaan 2: Analisis Kategori Produk")

    filtered_order_items = order_items_df[
        order_items_df['order_id'].isin(filtered_orders['order_id'])
    ].copy()

    category_agg, top_gmv, top_volume, top_freight = analyze_category_performance(filtered_order_items)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            plot_top_categories_bar(top_gmv, 'gmv', 'product_category_en',
                                   "Top 10 Kategori berdasarkan GMV", "GMV (R$)", '#72BCD4'),
            use_container_width=True
        )
    with col2:
        st.plotly_chart(
            plot_top_categories_bar(top_volume, 'orders', 'product_category_en',
                                   "Top 10 Kategori berdasarkan Volume Order", "Jumlah Order", '#4C9A2A'),
            use_container_width=True
        )

    st.subheader("📊 Analisis Freight Ratio")
    col1, col2 = st.columns(2)

    with col1:
        top_gmv_fr = top_gmv.copy()
        top_gmv_fr['freight_ratio_pct'] = top_gmv_fr['freight_ratio'] * 100
        st.plotly_chart(
            plot_freight_ratio(top_gmv_fr, "Freight Ratio untuk Top 10 Kategori GMV"),
            use_container_width=True
        )

    with col2:
        top_freight_fr = top_freight.copy()
        top_freight_fr['freight_ratio_pct'] = top_freight_fr['freight_ratio'] * 100
        st.plotly_chart(
            plot_top_categories_bar(top_freight_fr, 'freight_ratio_pct', 'product_category_en',
                                   "Top 10 Kategori dengan Freight Ratio Tertinggi", "Freight Ratio (%)", '#FF6B6B'),
            use_container_width=True
        )

    with st.expander("📝 Insight Analisis"):
        st.markdown(generate_category_insights(top_gmv, top_volume, top_freight))

# ============================================
# PERTANYAAN 3: RFM ANALYSIS
# ============================================
def render_question_3(filtered_orders):
    """Render visualisasi dan insight untuk Pertanyaan 3"""
    st.header("👥 Pertanyaan 3: RFM Analysis - Segmentasi Pelanggan")

    rfm_df, segment_df = analyze_rfm(filtered_orders)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rata-rata Recency", f"{rfm_df['recency'].mean():.1f} hari")
    with col2:
        st.metric("Rata-rata Frequency", f"{rfm_df['frequency'].mean():.2f}x")
    with col3:
        st.metric("Rata-rata Monetary", f"R$ {rfm_df['monetary'].mean():,.2f}")

    col1, col2, col3 = st.columns(3)
    with col1:
        top_recency = rfm_df.nsmallest(5, 'recency')
        st.plotly_chart(
            plot_rfm_top_customers(top_recency, 'recency', "Top 5 Customers by Recency",
                                  "Recency (days)", '#72BCD4'),
            use_container_width=True
        )
    with col2:
        top_frequency = rfm_df.nlargest(5, 'frequency')
        st.plotly_chart(
            plot_rfm_top_customers(top_frequency, 'frequency', "Top 5 Customers by Frequency",
                                  "Frequency", '#4C9A2A'),
            use_container_width=True
        )
    with col3:
        top_monetary = rfm_df.nlargest(5, 'monetary')
        st.plotly_chart(
            plot_rfm_top_customers(top_monetary, 'monetary', "Top 5 Customers by Monetary",
                                  "Monetary (R$)", '#D36C6C'),
            use_container_width=True
        )

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_segment_distribution(segment_df), use_container_width=True)
    with col2:
        st.plotly_chart(plot_segment_pie(segment_df), use_container_width=True)

    with st.expander("📝 Insight Analisis"):
        st.markdown(generate_rfm_insights(segment_df))

# ============================================
# PERTANYAAN 4: GEOSPATIAL ANALYSIS
# ============================================
def render_question_4(filtered_orders):
    """Render visualisasi dan insight untuk Pertanyaan 4"""
    st.header("🗺️ Pertanyaan 4: Geospatial Analysis")

    try:
        geolocation_df = load_geolocation_cached()
        sellers_df = load_sellers_cached()

        customer_by_city, seller_by_city, customer_geo, gap_df, gap_with_sellers, gap_without_sellers, gap_plot = prepare_geospatial_data(
            filtered_orders, geolocation_df, sellers_df
        )

        top_cities = customer_by_city.nlargest(10, 'order_count')
        top_sellers = seller_by_city.nlargest(10, 'seller_count')

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                plot_top_categories_bar(top_cities, 'order_count', 'customer_city',
                                       "Top 10 Kota Customer berdasarkan Order Count", "Jumlah Order", '#72BCD4'),
                use_container_width=True
            )
        with col2:
            st.plotly_chart(
                plot_top_categories_bar(top_sellers, 'seller_count', 'seller_city',
                                       "Top 10 Kota Seller berdasarkan Jumlah Seller", "Jumlah Seller", '#4C9A2A'),
                use_container_width=True
            )

        st.subheader("🗺️ Peta Kepadatan Customer Transactions")
        brazil_map = create_customer_heatmap(customer_geo, customer_by_city)
        st_folium(brazil_map, width=1200, height=500)

        st.subheader("🗺️ Peta Kepadatan Seller Locations")
        seller_map = create_seller_heatmap(seller_by_city)
        st_folium(seller_map, width=1200, height=500)

        st.subheader("📊 Analisis Gap Supply-Demand")

        # Metrics summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Kota dengan Seller", f"{len(gap_with_sellers):,}")
        with col2:
            st.metric("Kota Tanpa Seller", f"{len(gap_without_sellers):,}")
        with col3:
            avg_gap = gap_with_sellers['orders_per_seller'].mean() if len(gap_with_sellers) > 0 else 0
            st.metric("Rata-rata Gap", f"{avg_gap:.2f} orders/seller")
        with col4:
            high_gap_count = len(gap_with_sellers[gap_with_sellers['orders_per_seller'] > 50]) if len(gap_with_sellers) > 0 else 0
            st.metric("Kota Gap Tinggi (>50)", f"{high_gap_count:,}")

        # Top 20 Kota dengan Gap Tertinggi
        st.plotly_chart(
            plot_gap_top_cities(gap_with_sellers, top_n=20),
            use_container_width=True
        )

        # Top 10 Kota Tanpa Seller
        if len(gap_without_sellers) > 0:
            st.plotly_chart(
                plot_gap_no_seller_cities(gap_without_sellers, top_n=10),
                use_container_width=True
            )

        # Comparison Chart dan Gap Categories Distribution
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                plot_gap_comparison(gap_with_sellers, top_n=10),
                use_container_width=True
            )
        with col2:
            st.plotly_chart(
                plot_gap_categories_distribution(gap_plot),
                use_container_width=True
            )

        # Ringkasan statistik
        with st.expander("📊 Ringkasan Statistik Gap Supply-Demand"):
            st.write(f"**Total {len(gap_with_sellers)} kota dengan seller dianalisis**")
            st.write(f"**{len(gap_without_sellers)} kota tanpa seller (peluang ekspansi)**")
            if len(gap_with_sellers) > 0:
                st.write(f"**Rata-rata gap: {gap_with_sellers['orders_per_seller'].mean():.2f} orders/seller**")
                st.write(f"**{len(gap_with_sellers[gap_with_sellers['orders_per_seller'] > 50])} kota dengan gap tinggi (>50)**")
                st.write(f"**{len(gap_with_sellers[gap_with_sellers['orders_per_seller'] > 100])} kota dengan gap sangat tinggi (>100)**")

        with st.expander("📝 Insight Analisis"):
            top_gap = gap_df.nlargest(10, 'gap_ratio')
            st.markdown(generate_geospatial_insights(top_cities, top_sellers, top_gap))

    except Exception as e:
        st.error(f"❌ Error memuat data geolocation: {str(e)}")
        st.info("Pastikan file geolocation_dataset.csv tersedia di folder data/")

# ============================================
# MAIN DASHBOARD
# ============================================
def main():
    """Main function untuk menjalankan dashboard"""
    filtered_orders, _, _ = render_sidebar(orders_df)

    st.title("📈 Dashboard Analisis E-Commerce Public Dataset (Brazilian E-Commerce Public Dataset by Olist)")
    st.markdown("Visualization & Explanatory Analysis untuk 4 Pertanyaan Bisnis")
    st.markdown("---")

    render_question_1(filtered_orders)
    st.markdown("---")

    render_question_2(filtered_orders, order_items_df)
    st.markdown("---")

    render_question_3(filtered_orders)
    st.markdown("---")

    render_question_4(filtered_orders)
    st.markdown("---")


# Jalankan dashboard
main()

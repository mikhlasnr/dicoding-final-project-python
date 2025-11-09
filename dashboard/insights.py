"""Functions untuk generate insights text"""
import pandas as pd


def generate_trend_insights(monthly_df):
    """Generate insight text untuk tren bulanan"""
    if len(monthly_df) <= 1:
        return "**Temuan Utama:**\n- Data tidak cukup untuk analisis tren (minimal 2 bulan diperlukan)"

    orders_growth = ((monthly_df['orders'].iloc[-1] / monthly_df['orders'].iloc[0]) ** (1/(len(monthly_df)-1)) - 1) * 100
    gmv_growth = ((monthly_df['gmv'].iloc[-1] / monthly_df['gmv'].iloc[0]) ** (1/(len(monthly_df)-1)) - 1) * 100
    peak_month = monthly_df.loc[monthly_df['gmv'].idxmax()]
    peak_month_name = peak_month['order_date'].strftime('%B %Y')
    first_aov = monthly_df['aov'].iloc[0]
    last_aov = monthly_df['aov'].iloc[-1]
    aov_change = ((last_aov - first_aov) / first_aov) * 100
    highest_volume_month = monthly_df.loc[monthly_df['orders'].idxmax()]

    return f"""
    **Temuan Utama:**
    - Platform menunjukkan pertumbuhan dengan pertumbuhan rata-rata bulanan **{orders_growth:.2f}% untuk Orders dan {gmv_growth:.2f}% untuk GMV**
    - AOV {'turun' if aov_change < 0 else 'naik'} {abs(aov_change):.1f}% (R$ {first_aov:.2f} → R$ {last_aov:.2f})
    - **{peak_month_name}** adalah bulan puncak dengan {peak_month['orders']:,.0f} orders dan GMV R$ {peak_month['gmv']:,.2f}
    - Terdapat trade-off antara volume orders dan AOV - bulan dengan volume tertinggi ({highest_volume_month['orders']:,.0f} orders) memiliki AOV R$ {highest_volume_month['aov']:.2f}
    """


def generate_category_insights(top_gmv, top_volume, top_freight):
    """Generate insight text untuk analisis kategori"""
    if len(top_gmv) == 0:
        return "**Temuan Utama:**\n- Tidak ada data kategori untuk rentang tanggal yang dipilih"

    top_gmv_cat = top_gmv.iloc[0]['product_category_en']
    top_gmv_value = top_gmv.iloc[0]['gmv']
    top_gmv_fr_sorted = top_gmv.sort_values('freight_ratio')
    lowest_fr_cat = top_gmv_fr_sorted.iloc[0]['product_category_en']
    lowest_fr_value = top_gmv_fr_sorted.iloc[0]['freight_ratio'] * 100
    top_vol_cat = top_volume.iloc[0]['product_category_en'] if len(top_volume) > 0 else "N/A"
    high_fr_cats = top_freight[top_freight['freight_ratio'] > 0.3]
    high_fr_list = ""
    if len(high_fr_cats) > 0:
        high_fr_list = ", ".join([f"{row['product_category_en']} ({row['freight_ratio']*100:.2f}%)"
                                 for idx, row in high_fr_cats.head(3).iterrows()])
    top_5_vol = set(top_volume.head(5)['product_category_en'])
    top_5_gmv = set(top_gmv.head(5)['product_category_en'])
    overlap_count = len(top_5_vol.intersection(top_5_gmv))

    return f"""
    **Temuan Utama:**
    - **Pilar bisnis**: {top_gmv_cat} (GMV tertinggi: R$ {top_gmv_value:,.2f}), {lowest_fr_cat} (FR terendah: {lowest_fr_value:.2f}%), {top_vol_cat} (volume tertinggi)
    - Kategori dengan FR > 30%: {high_fr_list if high_fr_list else "Tidak ada kategori dengan FR > 30%"} - berpotensi menurunkan konversi
    - Korelasi positif: {overlap_count} dari 5 kategori top volume juga masuk top 5 GMV
    - Kategori dengan freight ratio tinggi perlu evaluasi strategi pricing/logistik
    """


def generate_rfm_insights(segment_df):
    """Generate insight text untuk RFM analysis"""
    if len(segment_df) == 0:
        return "**Temuan Utama:**\n- Tidak ada data customer untuk rentang tanggal yang dipilih"

    total_customers = segment_df['customer_count'].sum()
    segment_df['percentage'] = (segment_df['customer_count'] / total_customers) * 100

    low_value_seg = segment_df[segment_df['customer_segment'] == 'Low value customers']
    low_value_pct = low_value_seg['percentage'].values[0] if len(low_value_seg) > 0 else 0
    lost_seg = segment_df[segment_df['customer_segment'] == 'lost customers']
    lost_pct = lost_seg['percentage'].values[0] if len(lost_seg) > 0 else 0
    low_lost_total = low_value_pct + lost_pct

    top_seg = segment_df[segment_df['customer_segment'] == 'Top customers']
    top_pct = top_seg['percentage'].values[0] if len(top_seg) > 0 else 0
    high_seg = segment_df[segment_df['customer_segment'] == 'High value customer']
    high_pct = high_seg['percentage'].values[0] if len(high_seg) > 0 else 0
    premium_total = top_pct + high_pct

    medium_seg = segment_df[segment_df['customer_segment'] == 'Medium value customer']
    medium_pct = medium_seg['percentage'].values[0] if len(medium_seg) > 0 else 0

    return f"""
    **Temuan Utama:**
    - **{low_lost_total:.1f}% pelanggan** di segment Low value ({low_value_pct:.1f}%) dan Lost customers ({lost_pct:.1f}%)
    - Hanya **{premium_total:.1f}% pelanggan** di segment premium (Top: {top_pct:.1f}%, High: {high_pct:.1f}%) namun sangat berharga
    - Medium value customers ({medium_pct:.1f}%) memiliki potensi untuk ditingkatkan ke premium
    - Perlu strategi reaktivasi untuk Lost customers dan peningkatan nilai untuk Low value customers
    """


def generate_geospatial_insights(top_cities, top_sellers, top_gap):
    """Generate insight text untuk geospatial analysis"""
    if len(top_cities) == 0 or len(top_sellers) == 0 or len(top_gap) == 0:
        return "**Temuan Utama:**\n- Tidak ada data geospatial yang cukup untuk rentang tanggal yang dipilih"

    top_customer_city = top_cities.iloc[0]
    top_customer_name = f"{top_customer_city['customer_city']} ({top_customer_city['customer_state']})"
    top_customer_orders = top_customer_city['order_count']
    top_seller_city = top_sellers.iloc[0]
    top_seller_name = f"{top_seller_city['seller_city']} ({top_seller_city['seller_state']})"
    top_seller_count = top_seller_city['seller_count']
    top_gap_city = top_gap.iloc[0]
    top_gap_name = f"{top_gap_city['customer_city']} ({top_gap_city['customer_state']})"
    top_gap_ratio = top_gap_city['gap_ratio']
    top_gap_orders = top_gap_city['order_count']
    top_gap_sellers = top_gap_city['seller_count']
    top_customer_in_sellers = top_cities.iloc[0]['customer_city'] in top_sellers['seller_city'].values

    return f"""
    **Temuan Utama:**
    - **{top_customer_name}**: Pasar terbesar ({top_customer_orders:,.0f} orders) dan {'juga' if top_customer_in_sellers else 'bukan'} pusat supply utama
    - **{top_seller_name}**: Pusat supply utama dengan {top_seller_count:,.0f} sellers
    - **{top_gap_name}**: Gap supply-demand tertinggi - **{top_gap_ratio:.1f} orders/seller** ({top_gap_orders:,.0f} orders / {top_gap_sellers:.0f} sellers)
    - Area dengan gap sangat tinggi menunjukkan peluang ekspansi seller yang besar
    """


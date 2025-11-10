"""Analysis functions untuk setiap pertanyaan bisnis"""
import pandas as pd
import numpy as np


def analyze_monthly_trends(filtered_orders):
    """Analisis tren bulanan untuk Pertanyaan 1"""
    monthly_df = filtered_orders.groupby('order_date', as_index=False).agg({
        'order_id': 'nunique',
        'order_gmv': 'sum'
    }).rename(columns={'order_id': 'orders', 'order_gmv': 'gmv'})

    monthly_df['aov'] = monthly_df['gmv'] / monthly_df['orders']
    monthly_df = monthly_df.sort_values('order_date')

    return monthly_df


def analyze_category_performance(filtered_order_items):
    """Analisis kategori produk untuk Pertanyaan 2"""
    category_agg = filtered_order_items.groupby('product_category_en', as_index=False).agg({
        'item_gmv': 'sum',
        'order_id': 'nunique',
        'freight_value': 'sum',
        'price': 'sum'
    }).rename(columns={'order_id': 'orders', 'item_gmv': 'gmv'})

    category_agg['freight_ratio'] = category_agg['freight_value'] / category_agg['price'].replace(0, np.nan)
    category_agg = category_agg.fillna(0)

    top_gmv = category_agg.nlargest(10, 'gmv')
    top_volume = category_agg.nlargest(10, 'orders')
    top_freight = category_agg[category_agg['freight_ratio'] > 0].nlargest(10, 'freight_ratio')

    return category_agg, top_gmv, top_volume, top_freight


def analyze_rfm(filtered_orders):
    """Analisis RFM untuk Pertanyaan 3"""
    rfm_df = filtered_orders.groupby('customer_unique_id', as_index=False).agg({
        'order_purchase_timestamp': 'max',
        'order_id': 'nunique',
        'order_gmv': 'sum'
    })
    rfm_df.columns = ['customer_unique_id', 'max_order_timestamp', 'frequency', 'monetary']

    recent_date = filtered_orders['order_purchase_timestamp'].max()
    rfm_df['max_order_timestamp'] = pd.to_datetime(rfm_df['max_order_timestamp'])
    rfm_df['recency'] = (recent_date - rfm_df['max_order_timestamp']).dt.days
    rfm_df = rfm_df.drop('max_order_timestamp', axis=1)

    rfm_df['r_rank'] = rfm_df['recency'].rank(ascending=False)
    rfm_df['f_rank'] = rfm_df['frequency'].rank(ascending=True)
    rfm_df['m_rank'] = rfm_df['monetary'].rank(ascending=True)

    rfm_df['r_rank_norm'] = (rfm_df['r_rank'] / rfm_df['r_rank'].max()) * 100
    rfm_df['f_rank_norm'] = (rfm_df['f_rank'] / rfm_df['f_rank'].max()) * 100
    rfm_df['m_rank_norm'] = (rfm_df['m_rank'] / rfm_df['m_rank'].max()) * 100

    rfm_df['RFM_score'] = (0.15 * rfm_df['r_rank_norm'] +
                           0.28 * rfm_df['f_rank_norm'] +
                           0.57 * rfm_df['m_rank_norm'])
    rfm_df['RFM_score'] = rfm_df['RFM_score'] * 0.05

    rfm_df['customer_segment'] = np.where(
        rfm_df['RFM_score'] > 4.5, "Top customers",
        np.where(rfm_df['RFM_score'] > 4, "High value customer",
        np.where(rfm_df['RFM_score'] > 3, "Medium value customer",
        np.where(rfm_df['RFM_score'] > 1.6, 'Low value customers', 'lost customers'))))

    segment_df = rfm_df.groupby('customer_segment', as_index=False).agg({
        'customer_unique_id': 'nunique',
        'monetary': 'mean',
        'frequency': 'mean',
        'recency': 'mean'
    }).rename(columns={'customer_unique_id': 'customer_count'})

    segment_order = ["lost customers", "Low value customers", "Medium value customer",
                     "High value customer", "Top customers"]
    segment_df['customer_segment'] = pd.Categorical(
        segment_df['customer_segment'],
        categories=segment_order,
        ordered=True
    )
    segment_df = segment_df.sort_values('customer_segment')

    return rfm_df, segment_df


def prepare_geospatial_data(filtered_orders, geolocation_df, sellers_df):
    """Persiapkan data geospatial untuk Pertanyaan 4"""
    geolocation_df['geolocation_zip_code_prefix'] = geolocation_df['geolocation_zip_code_prefix'].astype(str)

    customer_by_city = filtered_orders.groupby(['customer_city', 'customer_state'], as_index=False).agg({
        'order_id': 'nunique',
        'order_gmv': 'sum'
    }).rename(columns={'order_id': 'order_count', 'order_gmv': 'order_gmv'})

    filtered_orders['customer_zip_code_prefix'] = filtered_orders['customer_zip_code_prefix'].astype(str)

    geo_agg = geolocation_df.groupby('geolocation_zip_code_prefix', as_index=False).agg({
        'geolocation_lat': 'first',
        'geolocation_lng': 'first'
    })

    customer_geo = filtered_orders.merge(
        geo_agg,
        left_on='customer_zip_code_prefix',
        right_on='geolocation_zip_code_prefix',
        how='left'
    )

    customer_geo = customer_geo[
        (customer_geo['geolocation_lat'].between(-35, 5)) &
        (customer_geo['geolocation_lng'].between(-75, -30))
    ]

    sellers_df['seller_zip_code_prefix'] = sellers_df['seller_zip_code_prefix'].astype(str)
    sellers_geo = sellers_df.merge(
        geo_agg,
        left_on='seller_zip_code_prefix',
        right_on='geolocation_zip_code_prefix',
        how='left'
    )

    seller_transactions = sellers_geo.groupby(['seller_zip_code_prefix', 'seller_city', 'seller_state'], as_index=False).agg({
        'seller_id': 'nunique'
    }).rename(columns={'seller_id': 'seller_count'})

    seller_transactions_geo = seller_transactions.merge(
        geo_agg,
        left_on='seller_zip_code_prefix',
        right_on='geolocation_zip_code_prefix',
        how='left'
    )

    seller_transactions_geo = seller_transactions_geo[
        (seller_transactions_geo['geolocation_lat'].notna()) &
        (seller_transactions_geo['geolocation_lng'].notna())
    ]

    seller_by_city = seller_transactions_geo.groupby(['seller_city', 'seller_state'], as_index=False).agg({
        'seller_count': 'sum',
        'geolocation_lat': 'mean',
        'geolocation_lng': 'mean'
    })

    seller_by_city = seller_by_city[
        (seller_by_city['geolocation_lat'].between(-35, 5)) &
        (seller_by_city['geolocation_lng'].between(-75, -30))
    ]

    gap_df = customer_by_city.merge(
        seller_by_city,
        left_on=['customer_city', 'customer_state'],
        right_on=['seller_city', 'seller_state'],
        how='left',
        suffixes=('_customer', '_seller')
    )
    gap_df['seller_count'] = gap_df['seller_count'].fillna(0)
    gap_df['gap_ratio'] = gap_df['order_count'] / gap_df['seller_count'].replace(0, np.nan)
    gap_df = gap_df[gap_df['gap_ratio'].notna()].sort_values('gap_ratio', ascending=False)

    # Buat gap_with_sellers dan gap_without_sellers untuk visualisasi lengkap
    gap_df_full = customer_by_city.merge(
        seller_by_city,
        left_on=['customer_city', 'customer_state'],
        right_on=['seller_city', 'seller_state'],
        how='left',
        suffixes=('_customer', '_seller')
    )
    gap_df_full['seller_count'] = gap_df_full['seller_count'].fillna(0)
    gap_df_full['orders_per_seller'] = gap_df_full['order_count'] / gap_df_full['seller_count'].replace(0, np.nan)

    # Pisahkan kota dengan seller dan tanpa seller
    gap_with_sellers = gap_df_full[gap_df_full['seller_count'] > 0].copy()
    gap_with_sellers = gap_with_sellers.sort_values('orders_per_seller', ascending=False)

    gap_without_sellers = gap_df_full[gap_df_full['seller_count'] == 0].copy()
    gap_without_sellers = gap_without_sellers.sort_values('order_count', ascending=False)

    # Buat gap_plot untuk kategori gap
    gap_plot = gap_with_sellers.copy()
    if len(gap_plot) > 0:
        gap_plot['gap_category'] = pd.cut(
            gap_plot['orders_per_seller'],
            bins=[0, 20, 50, 100, float('inf')],
            labels=['Low (<20)', 'Medium (20-50)', 'High (50-100)', 'Very High (>100)']
        )
    else:
        gap_plot['gap_category'] = pd.Series(dtype='category')

    return customer_by_city, seller_by_city, customer_geo, gap_df, gap_with_sellers, gap_without_sellers, gap_plot


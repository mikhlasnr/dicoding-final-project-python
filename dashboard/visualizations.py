"""Visualization functions untuk dashboard"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from folium.plugins import HeatMap
import pandas as pd


def plot_monthly_trends(monthly_df):
    """Plot tren bulanan Orders & GMV"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=monthly_df['order_date'],
            y=monthly_df['orders'],
            name="Orders",
            line=dict(color='#72BCD4', width=3),
            mode='lines+markers'
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=monthly_df['order_date'],
            y=monthly_df['gmv'],
            name="GMV (R$)",
            line=dict(color='#4C9A2A', width=3),
            mode='lines+markers'
        ),
        secondary_y=True,
    )
    fig.update_xaxes(title_text="Bulan")
    fig.update_yaxes(title_text="Jumlah Orders", secondary_y=False)
    fig.update_yaxes(title_text="GMV (R$)", secondary_y=True)
    fig.update_layout(
        title="Tren Bulanan: Orders & GMV",
        height=400,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def plot_aov_trend(monthly_df):
    """Plot tren AOV bulanan"""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=monthly_df['order_date'],
            y=monthly_df['aov'],
            name="AOV",
            line=dict(color='#D36C6C', width=3),
            mode='lines+markers',
            fill='tonexty',
            fillcolor='rgba(211, 108, 108, 0.1)'
        )
    )
    avg_aov = monthly_df['aov'].mean()
    fig.add_hline(
        y=avg_aov,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Rata-rata: R$ {avg_aov:.2f}"
    )
    fig.update_layout(
        title="Tren Bulanan: Average Order Value (AOV)",
        xaxis_title="Bulan",
        yaxis_title="AOV (R$)",
        height=400,
        hovermode='x unified'
    )
    return fig


def plot_top_categories_bar(data, x_col, y_col, title, x_title, color='#72BCD4'):
    """Plot horizontal bar chart untuk top categories"""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=data[x_col],
        y=data[y_col],
        orientation='h',
        marker=dict(color=color),
        text=[f"{x:,.0f}" if isinstance(x, (int, float)) and x >= 1 else f"{x:.2f}" for x in data[x_col]],
        textposition='outside'
    ))
    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title="Kategori",
        height=500,
        yaxis={'categoryorder': 'total ascending'}
    )
    return fig


def plot_freight_ratio(data, title, threshold=20):
    """Plot freight ratio dengan threshold"""
    fig = go.Figure()
    colors = ['#FF6B6B' if x > threshold else '#95E1D3' for x in data['freight_ratio_pct']]
    fig.add_trace(go.Bar(
        x=data['freight_ratio_pct'],
        y=data['product_category_en'],
        orientation='h',
        marker=dict(color=colors),
        text=[f"{x:.2f}%" for x in data['freight_ratio_pct']],
        textposition='outside'
    ))
    fig.add_vline(x=threshold, line_dash="dash", line_color="orange", annotation_text=f"Threshold {threshold}%")
    fig.update_layout(
        title=title,
        xaxis_title="Freight Ratio (%)",
        yaxis_title="Kategori",
        height=500,
        yaxis={'categoryorder': 'total ascending'}
    )
    return fig


def plot_rfm_top_customers(data, metric_col, title, x_title, color):
    """Plot top 5 customers untuk RFM metrics"""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=data[metric_col],
        y=data['customer_unique_id'].str[:8],
        orientation='h',
        marker=dict(color=color),
        text=[f"{x:.0f}" if metric_col == 'recency' else f"{x:.0f}x" if metric_col == 'frequency' else f"R$ {x:,.0f}" for x in data[metric_col]],
        textposition='outside'
    ))
    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title="Customer ID",
        height=300,
        yaxis={'categoryorder': 'total ascending'}
    )
    return fig


def plot_segment_distribution(segment_df):
    """Plot distribusi customer segment"""
    fig = go.Figure()
    colors = ['#72BCD4' if x in ['Top customers', 'High value customer'] else '#D3D3D3'
              for x in segment_df['customer_segment']]
    fig.add_trace(go.Bar(
        x=segment_df['customer_count'],
        y=segment_df['customer_segment'],
        orientation='h',
        marker=dict(color=colors),
        text=[f"{x:,}" for x in segment_df['customer_count']],
        textposition='outside'
    ))
    fig.update_layout(
        title="Distribusi Customer Segment",
        xaxis_title="Jumlah Customer",
        yaxis_title="Customer Segment",
        height=400,
        yaxis={'categoryorder': 'total ascending'}
    )
    return fig


def plot_segment_pie(segment_df):
    """Plot pie chart untuk proporsi customer segment"""
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=segment_df['customer_segment'],
        values=segment_df['customer_count'],
        hole=0.4,
        marker=dict(colors=['#FF6B6B', '#FFA07A', '#FFD700', '#90EE90', '#72BCD4'])
    ))
    fig.update_layout(
        title="Proporsi Customer Segment",
        height=400
    )
    return fig


def create_customer_heatmap(customer_geo, customer_by_city):
    """Buat peta heatmap untuk customer transactions"""
    sample_size = min(5000, len(customer_geo))
    customer_sample = customer_geo.sample(n=sample_size, random_state=42)

    brazil_map = folium.Map(
        location=[-14.2350, -51.9253],
        zoom_start=4,
        tiles='OpenStreetMap'
    )

    heat_data = [[row['geolocation_lat'], row['geolocation_lng'], 1]
                 for idx, row in customer_sample.iterrows()
                 if pd.notna(row['geolocation_lat']) and pd.notna(row['geolocation_lng'])]

    if heat_data:
        HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(brazil_map)

        top_5_cities = customer_by_city.nlargest(5, 'order_count')
        for idx, row in top_5_cities.iterrows():
            city_geo = customer_geo[
                (customer_geo['customer_city'] == row['customer_city']) &
                (customer_geo['customer_state'] == row['customer_state'])
            ]
            if not city_geo.empty:
                lat = city_geo['geolocation_lat'].iloc[0]
                lng = city_geo['geolocation_lng'].iloc[0]
                if pd.notna(lat) and pd.notna(lng):
                    folium.CircleMarker(
                        location=[lat, lng],
                        radius=10,
                        popup=f"{row['customer_city']}, {row['customer_state']}<br>Orders: {row['order_count']:,}<br>GMV: R$ {row['order_gmv']:,.0f}",
                        color='blue',
                        fill=True,
                        fillColor='blue'
                    ).add_to(brazil_map)

    return brazil_map


def create_seller_heatmap(seller_by_city):
    """Buat peta heatmap untuk seller locations"""
    sample_size_seller = min(2000, len(seller_by_city))
    seller_sample = seller_by_city.sample(n=sample_size_seller, random_state=42)

    seller_map = folium.Map(
        location=[-14.2350, -51.9253],
        zoom_start=4,
        tiles='OpenStreetMap'
    )

    seller_heat_data = [[row['geolocation_lat'], row['geolocation_lng'], row['seller_count']]
                        for idx, row in seller_sample.iterrows()
                        if pd.notna(row['geolocation_lat']) and pd.notna(row['geolocation_lng'])]

    if seller_heat_data:
        HeatMap(seller_heat_data, radius=15, blur=10, max_zoom=1,
                gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'orange', 1: 'red'}).add_to(seller_map)

        top_10_sellers = seller_by_city.nlargest(10, 'seller_count')
        for idx, row in top_10_sellers.iterrows():
            if pd.notna(row['geolocation_lat']) and pd.notna(row['geolocation_lng']):
                folium.CircleMarker(
                    location=[row['geolocation_lat'], row['geolocation_lng']],
                    radius=10,
                    popup=f"{row['seller_city']}, {row['seller_state']}<br>Sellers: {row['seller_count']:,}",
                    color='green',
                    fill=True,
                    fillColor='green'
                ).add_to(seller_map)

    return seller_map


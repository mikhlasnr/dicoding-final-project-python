"""Utility functions untuk dashboard"""
import pandas as pd
import os


def get_project_root():
    """Mendapatkan path root project"""
    try:
        dashboard_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(dashboard_dir)
        return project_root
    except:
        cwd = os.getcwd()
        if os.path.basename(cwd) == 'dashboard':
            return os.path.dirname(cwd)
        elif os.path.exists(os.path.join(cwd, 'data')):
            return cwd
        else:
            return os.path.dirname(cwd)


def load_orders_data():
    """Load orders enriched data"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    orders_df = pd.read_csv(os.path.join(base_path, 'orders_enriched.csv'))
    orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
    return orders_df


def load_order_items_data():
    """Load order items products data"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    order_items_df = pd.read_csv(os.path.join(base_path, 'order_items_products.csv'))
    return order_items_df


def load_geolocation_data():
    """Load geolocation data"""
    project_root = get_project_root()
    geolocation_path = os.path.join(project_root, 'data', 'geolocation_dataset.csv')
    geolocation_path = os.path.abspath(geolocation_path)

    if not os.path.exists(geolocation_path):
        raise FileNotFoundError(
            f"File geolocation tidak ditemukan di: {geolocation_path}\n"
            f"Pastikan file geolocation_dataset.csv ada di folder data/"
        )

    try:
        try:
            geolocation_df = pd.read_csv(
                geolocation_path,
                low_memory=False,
                encoding='utf-8'
            )
        except UnicodeDecodeError:
            geolocation_df = pd.read_csv(
                geolocation_path,
                low_memory=False,
                encoding='latin-1'
            )

        geolocation_df.columns = geolocation_df.columns.str.replace('"', '', regex=False).str.replace("'", '', regex=False).str.strip()

        if 'geolocation_zip_code_prefix' in geolocation_df.columns:
            geolocation_df['geolocation_zip_code_prefix'] = geolocation_df['geolocation_zip_code_prefix'].astype(str)
        else:
            zip_cols = [col for col in geolocation_df.columns if 'zip' in col.lower() or 'prefix' in col.lower()]
            if zip_cols:
                geolocation_df = geolocation_df.rename(columns={zip_cols[0]: 'geolocation_zip_code_prefix'})
                geolocation_df['geolocation_zip_code_prefix'] = geolocation_df['geolocation_zip_code_prefix'].astype(str)
            else:
                raise Exception(f"Kolom 'geolocation_zip_code_prefix' tidak ditemukan. Kolom yang tersedia: {list(geolocation_df.columns)}")

        return geolocation_df
    except Exception as e:
        raise Exception(f"Error membaca file geolocation: {str(e)}")


def load_sellers_data():
    """Load sellers data"""
    project_root = get_project_root()
    sellers_path = os.path.join(project_root, 'data', 'sellers_dataset.csv')
    sellers_path = os.path.abspath(sellers_path)

    if not os.path.exists(sellers_path):
        raise FileNotFoundError(
            f"File sellers tidak ditemukan di: {sellers_path}\n"
            f"Pastikan file sellers_dataset.csv ada di folder data/"
        )

    sellers_df = pd.read_csv(sellers_path)
    return sellers_df


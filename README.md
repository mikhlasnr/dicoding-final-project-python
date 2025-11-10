# Proyek Analisis Data: E-Commerce Public Dataset (Brazilian E-Commerce Public Dataset by Olist)

Proyek ini merupakan analisis data komprehensif untuk dataset e-commerce Olist yang mencakup analisis tren bisnis, segmentasi pelanggan (RFM), analisis produk, dan analisis geospatial.

**Pembuat:** Muhammad Ikhlas Naufalsyah Ranau
**Email:** naufalsyah.ranau@gmail.com
**ID Dicoding:** [mikhlasnr](https://www.dicoding.com/users/mikhlasnr/academies)

---

## 📋 Daftar Isi

- [Overview](#overview)
- [Struktur Project](#struktur-project)
- [Pertanyaan Bisnis](#pertanyaan-bisnis)
- [Setup Environment](#setup-environment)
- [Menjalankan Notebook](#menjalankan-notebook)
- [Menjalankan Dashboard](#menjalankan-dashboard)
- [Struktur Dashboard](#struktur-dashboard)
- [Data Requirements](#data-requirements)
- [Dependencies](#dependencies)

---

## 📊 Overview

Proyek ini terdiri dari dua komponen utama:

1. **Jupyter Notebook** (`notebook.ipynb`): Analisis data lengkap dengan EDA, data wrangling, dan visualisasi menggunakan Matplotlib dan Seaborn
2. **Streamlit Dashboard** (`dashboard/dashboard.py`): Dashboard interaktif untuk visualisasi dan explanatory analysis dengan filter tanggal dinamis

---

## 📁 Struktur Project

```
dicoding-final-project-python/
│
├── data/                          # Dataset CSV files
│   ├── customers_dataset.csv
│   ├── geolocation_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── orders_dataset.csv
│   ├── product_category_name_translation.csv
│   ├── products_dataset.csv
│   └── sellers_dataset.csv
│
├── dashboard/                     # Dashboard Streamlit
│   ├── dashboard.py              # Main dashboard file
│   ├── utils.py                  # Utility functions (data loading)
│   ├── analysis.py               # Analysis functions
│   ├── visualizations.py         # Visualization functions
│   ├── insights.py               # Insight generation functions
│   ├── orders_enriched.csv       # Pre-processed data (dari notebook)
│   └── order_items_products.csv  # Pre-processed data (dari notebook)
│
├── notebook.ipynb                # Jupyter notebook untuk analisis
├── requirements.txt              # Python dependencies
└── README.md                     # Dokumentasi project
```

---

## 🎯 Pertanyaan Bisnis

Proyek ini menjawab 4 pertanyaan bisnis utama:

### 1. Pertumbuhan & Pendapatan
- Bagaimana tren jumlah pesanan, GMV (price + freight), dan AOV per bulan selama 2016–2018?
- Bulan/musim apa dengan performa tertinggi dan terendah?

### 2. Produk & Kategori
- Kategori produk mana yang menyumbang GMV dan volume terbesar?
- Kategori mana yang memiliki rasio ongkir (freight/GMV) relatif tinggi?

### 3. Pelanggan & Retensi (RFM Analysis)
- Siapa pelanggan bernilai tinggi (Top/High Value) berdasarkan RFM?
- Bagaimana distribusi segmentasi pelanggan berdasarkan RFM score?

### 4. Geospatial Analysis
- Di wilayah mana konsentrasi pelanggan dan penjual tertinggi?
- Bagaimana peta kepadatan (heatmap) transaksi berdasarkan lokasi?
- Di kota mana terdapat kesenjangan supply-demand (gap) tertinggi?

**Keterangan Metrik:**
- **GMV (Gross Merchandise Value)**: Total nilai transaksi (harga produk + ongkir)
- **AOV (Average Order Value)**: Nilai rata-rata per transaksi = GMV / Jumlah Order
- **RFM**: Recency (kapan terakhir beli), Frequency (seberapa sering), Monetary (berapa banyak uang yang dikeluarkan)

---

## 🚀 Setup Environment

### Opsi 1: Menggunakan Anaconda (Recommended)

```bash
# Buat environment baru
conda create --name main-ds python=3.9
conda activate main-ds

# Install dependencies
pip install -r requirements.txt

# Install Jupyter (jika belum terinstall)
conda install jupyter
# atau
pip install jupyter
```

### Opsi 2: Menggunakan Virtual Environment (venv)

```bash
# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Jupyter (jika belum terinstall)
pip install jupyter
```

### Opsi 3: Menggunakan pipenv

```bash
# Install pipenv (jika belum terinstall)
pip install pipenv

# Install dependencies
pipenv install

# Aktifkan shell
pipenv shell

# Install dependencies tambahan jika diperlukan
pip install -r requirements.txt
```

---

## 📓 Menjalankan Notebook

### Prerequisites
- Python 3.9 atau lebih tinggi
- Jupyter Notebook atau JupyterLab terinstall
- Semua dependencies dari `requirements.txt` terinstall

### Langkah-langkah

1. **Pastikan environment sudah aktif**
   ```bash
   conda activate main-ds  # untuk Anaconda
   # atau
   source venv/bin/activate  # untuk venv
   ```

2. **Jalankan Jupyter Notebook**
   ```bash
   jupyter notebook
   ```
   Atau jika menggunakan JupyterLab:
   ```bash
   jupyter lab
   ```

3. **Buka file `notebook.ipynb`**
   - File akan terbuka di browser
   - Jalankan semua cells secara berurutan (Cell → Run All)

4. **Export Data untuk Dashboard**
   - Notebook akan secara otomatis mengexport file berikut ke folder `dashboard/`:
     - `orders_enriched.csv`
     - `order_items_products.csv`
   - File-file ini diperlukan untuk menjalankan dashboard

### Catatan Penting
- Pastikan semua dataset CSV ada di folder `data/`
- Notebook akan melakukan data wrangling dan preprocessing
- Proses export data ke folder `dashboard/` dilakukan di akhir notebook

---

## 🎨 Menjalankan Dashboard

### Prerequisites
- Python 3.9 atau lebih tinggi
- Streamlit terinstall
- File pre-processed data sudah ada di folder `dashboard/`:
  - `orders_enriched.csv`
  - `order_items_products.csv`
- Dataset `geolocation_dataset.csv` dan `sellers_dataset.csv` ada di folder `data/`

### Langkah-langkah

1. **Pastikan environment sudah aktif**
   ```bash
   conda activate main-ds  # untuk Anaconda
   # atau
   source venv/bin/activate  # untuk venv
   ```

2. **Pastikan file data sudah tersedia**
   - File `orders_enriched.csv` dan `order_items_products.csv` harus ada di folder `dashboard/`
   - File `geolocation_dataset.csv` dan `sellers_dataset.csv` harus ada di folder `data/`
   - Jika belum ada, jalankan notebook terlebih dahulu untuk generate file-file tersebut

3. **Jalankan Dashboard**
   ```bash
   cd dashboard
   streamlit run dashboard.py
   ```

   Atau dari root directory:
   ```bash
   streamlit run dashboard/dashboard.py
   ```

4. **Akses Dashboard**
   - Dashboard akan otomatis terbuka di browser
   - Default URL: `http://localhost:8501`
   - Jika tidak terbuka otomatis, buka URL tersebut secara manual

### Fitur Dashboard

- **Date Range Filter**: Filter data berdasarkan rentang tanggal
- **4 Analisis Utama**:
  1. Tren Bulanan (Orders, GMV, AOV)
  2. Analisis Kategori Produk (Top GMV, Volume, Freight Ratio)
  3. RFM Analysis (Segmentasi Pelanggan)
  4. Geospatial Analysis (Peta Heatmap, Gap Supply-Demand)
- **Dynamic Insights**: Insight yang menyesuaikan dengan filter tanggal
- **Interactive Visualizations**: Menggunakan Plotly dan Folium

---

## 🏗️ Struktur Dashboard

Dashboard menggunakan arsitektur modular untuk kemudahan maintenance:

### `dashboard.py`
File utama yang mengatur alur dashboard dan rendering UI.

### `utils.py`
Fungsi-fungsi utility untuk:
- `get_project_root()`: Mendapatkan path root project
- `load_orders_data()`: Load data orders enriched
- `load_order_items_data()`: Load data order items products
- `load_geolocation_data()`: Load data geolocation
- `load_sellers_data()`: Load data sellers

### `analysis.py`
Fungsi-fungsi analisis untuk setiap pertanyaan bisnis:
- `analyze_monthly_trends()`: Analisis tren bulanan (Q1)
- `analyze_category_performance()`: Analisis kategori produk (Q2)
- `analyze_rfm()`: Analisis RFM (Q3)
- `prepare_geospatial_data()`: Persiapan data geospatial (Q4)

### `visualizations.py`
Fungsi-fungsi untuk membuat visualisasi:
- Plot tren bulanan (Orders & GMV, AOV)
- Plot kategori produk (bar charts)
- Plot RFM (top customers, segment distribution)
- Peta heatmap (customer dan seller locations)

### `insights.py`
Fungsi-fungsi untuk generate insight text:
- `generate_trend_insights()`: Insight untuk tren bulanan
- `generate_category_insights()`: Insight untuk kategori produk
- `generate_rfm_insights()`: Insight untuk RFM analysis
- `generate_geospatial_insights()`: Insight untuk geospatial analysis

---

## 📦 Data Requirements

### Data untuk Notebook
Semua file CSV harus ada di folder `data/`:
- `customers_dataset.csv`
- `geolocation_dataset.csv`
- `order_items_dataset.csv`
- `order_payments_dataset.csv`
- `order_reviews_dataset.csv`
- `orders_dataset.csv`
- `product_category_name_translation.csv`
- `products_dataset.csv`
- `sellers_dataset.csv`

### Data untuk Dashboard
File yang diperlukan di folder `dashboard/`:
- `orders_enriched.csv` (dihasilkan dari notebook)
- `order_items_products.csv` (dihasilkan dari notebook)

File yang diperlukan di folder `data/`:
- `geolocation_dataset.csv` (untuk analisis geospatial)
- `sellers_dataset.csv` (untuk analisis geospatial)

**Catatan**: File `orders_enriched.csv` dan `order_items_products.csv` harus di-generate terlebih dahulu dengan menjalankan notebook.

---

## 📚 Dependencies

Semua dependencies tercantum di `requirements.txt`:

### Core Data Processing
- `pandas==2.1.4` - Manipulasi dan analisis data
- `numpy==1.25.2` - Operasi numerik

### Visualization (Notebook)
- `matplotlib==3.8.0` - Visualisasi statis
- `seaborn==0.13.0` - Visualisasi statis yang lebih menarik

### Visualization (Dashboard)
- `plotly==5.18.0` - Visualisasi interaktif

### Geospatial Visualization
- `folium==0.15.1` - Peta interaktif

### Dashboard Framework
- `streamlit==1.30.0` - Framework untuk dashboard web
- `streamlit-folium==0.15.1` - Integrasi Folium dengan Streamlit

### Jupyter Notebook Support
- `ipython==8.18.1` - Enhanced Python shell untuk Jupyter

### Install Semua Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔧 Troubleshooting

### Error: File tidak ditemukan
- Pastikan semua file CSV ada di folder yang benar
- Pastikan path relatif sudah benar
- Untuk dashboard, pastikan file `orders_enriched.csv` dan `order_items_products.csv` sudah di-generate dari notebook

### Error: Module tidak ditemukan
- Pastikan semua dependencies sudah terinstall: `pip install -r requirements.txt`
- Pastikan virtual environment sudah aktif

### Error: Streamlit tidak bisa dijalankan
- Pastikan Streamlit sudah terinstall: `pip install streamlit`
- Pastikan menjalankan dari directory yang benar atau gunakan path lengkap

### Error: Geolocation data tidak bisa dimuat
- Pastikan file `geolocation_dataset.csv` ada di folder `data/`
- Pastikan kolom `geolocation_zip_code_prefix` ada di file tersebut
- Cek encoding file (mungkin perlu encoding='latin-1')

---

## 📝 Catatan

- Dashboard menggunakan data yang sudah di-preprocess dari notebook
- Pastikan menjalankan notebook terlebih dahulu sebelum menjalankan dashboard
- Dashboard mendukung filter tanggal dinamis untuk semua analisis
- Semua insight di dashboard bersifat dinamis dan menyesuaikan dengan filter

---

## 📄 License

Proyek ini dibuat untuk keperluan menyelesaikan tugas proyek akhir di Dicoding Academy dengan judul modul
**Belajar Analisis Data dengan Python**.

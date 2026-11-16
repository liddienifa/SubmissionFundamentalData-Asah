# Brazilian E-Commerce Public Dataset Analytics Dashboard ✨

Proyek Analisis Data ini disusun untuk memenuhi tugas akhir kelas **Belajar Analisis Data dengan Python / Belajar Fundamental Analisis Data** di **Dicoding Indonesia**.

## 👤 Identitas Penyusun
- **Nama:** Liddieni Hanifa
- **Email:** hi.liddienihanifa@gmail.com
- **ID Dicoding:** Liddieni Hanifa

## 📂 Struktur Direktori Proyek
```text
submission
├── dashboard
│   ├── main_data.csv
│   └── dashboard.py
├── data
│   ├── customers_dataset.csv
│   ├── geolocation_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── orders_dataset.csv
│   ├── product_category_name_translation.csv
│   ├── products_dataset.csv
│   └── sellers_dataset.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## 🚀 Cara Menjalankan Dashboard Streamlit di Lokal

### 1. Persiapan Environment (Pilih salah satu: Anaconda/Miniconda atau Pip/Virtualenv)

**Opsi A — Menggunakan Conda:**
```bash
conda create --name main-ds python=3.11
conda activate main-ds
pip install -r requirements.txt
```

**Opsi B — Menggunakan Shell / Pipenv / Virtualenv:**
```bash
python -m venv env
# Untuk Windows:
env\Scripts\activate
# Untuk macOS/Linux:
source env/bin/activate

pip install -r requirements.txt
```

### 2. Menjalankan Aplikasi Dashboard Streamlit
Jalankan perintah berikut dari direktori utama (`submission/`):
```bash
streamlit run dashboard/dashboard.py
```
Atau masuk ke dalam folder `dashboard/` terlebih dahulu:
```bash
cd dashboard
streamlit run dashboard.py
```
Dashboard akan terbuka secara otomatis di peramban pada alamat `http://localhost:8501`.

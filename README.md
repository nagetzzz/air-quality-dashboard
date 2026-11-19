# Proyek Analisis Data: Air Quality Dataset (Beijing) ✨

Analisis kualitas udara (fokus PM2.5) dari 12 stasiun pemantauan di Beijing periode Maret 2013 – Februari 2017,
dilengkapi dashboard interaktif menggunakan Streamlit.

## Struktur Proyek
```
submission
├───dashboard
│   ├───main_data.csv      # data hasil cleaning (dibuat oleh notebook)
│   └───dashboard.py       # dashboard Streamlit
├───data                   # dataset mentah (12 berkas CSV, satu per stasiun)
├───notebook.ipynb         # proses analisis data lengkap
├───README.md
├───requirements.txt
└───url.txt                # tautan dashboard di Streamlit Cloud
```

## Setup Environment - Anaconda
```
conda create --name main-ds python=3.12
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
mkdir proyek_analisis_data
cd proyek_analisis_data
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

## Run Streamlit App
Jalankan dari folder utama proyek (`submission`):
```
streamlit run dashboard/dashboard.py
```
Dashboard akan terbuka di browser pada `http://localhost:8501`.

## Fitur Dashboard
- Filter rentang tanggal, stasiun, dan jenis polutan (PM2.5, PM10, SO2, NO2, CO, O3).
- Perbandingan rata-rata polutan per stasiun.
- Pola musiman (per bulan) dan harian (per jam), serta heatmap bulan × jam.
- Tren bulanan dan tahunan, serta perubahan per stasiun dari 2013/14 ke 2016/17.
- Kategori kualitas udara harian (binning PM2.5) dan peta stasiun.

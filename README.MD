# Dashboard Analisis Data Penjualan 🛒

## Deskripsi
Aplikasi ini adalah dashboard interaktif yang dibuat menggunakan Streamlit untuk menganalisis data penjualan. Dashboard ini membantu pengguna memahami pola penjualan, segmentasi pelanggan, dan distribusi geografis data. Anda dapat menjalankan aplikasi ini secara **online** melalui Streamlit Cloud atau **lokal** di komputer Anda.

---

## Buka Dashboard di Streamlit Cloud 🌐
Aplikasi ini sudah tersedia secara online dan dapat diakses melalui link berikut:

👉 **[Buka Dashboard di Streamlit Cloud](https://analysisdatapython-c3jwepjamodazdpptrydob.streamlit.app/)**

---

## Clone Repository dari GitHub 🛠️
Sebelum memulai, pastikan Anda sudah meng-clone repository ini ke komputer Anda. Gunakan perintah berikut:
```bash
git https://github.com/mfaiqrofifi/analysis_data_python.git
cd analysis_data_python
```

## Setup Environment - Python 🐍
Langkah-langkah untuk membuat environment menggunakan Anaconda:
```bash
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r .\dashboard\requirements.txt
```

## Setup Environment - Shell/Terminal
```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r .\dashboard\requirements.txt
```

## Run steamlit app
```
streamlit run .\dashboard\dashboard.py
```
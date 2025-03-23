# Tambahkan import ini di bagian atas file, bersama import-import lainnya
import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog
import matplotlib.pyplot as plt
import io
import base64
import time
from datetime import datetime  # Tambahkan baris ini
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import matplotlib.pyplot as plt

# Set page config
st.set_page_config(page_title="Ransum Sapi Perah", page_icon="🐄", layout="wide")

# Custom CSS untuk tampilan yang lebih baik
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #3498db;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .ingredient-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        border-left: 4px solid #3498db;
    }
    .info-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .result-box {
        background-color: #e8f8f5;
        padding: 1.5rem;
        border-radius: 5px;
        margin: 1.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Database bahan pakan
bahan_pakan_data = {
    'Nama Bahan': [
        'Biji barley (Hordeum vulgare L.)', 'Biji jagung (Zea mays L.)', 
        'Bungkil jagung—proses ekstrusi', 'Bungkil jagung—proses pengepresan', 
        'Bungkil jagung berkadar air tinggi', 'Biji millet Mutiara', 
        'Biji millet proso', 'Gandum', 'Biji gandum', 
        'Bungkil biji gandum—proses pengepresan', 'Bekatul', 'Dedak', 
        'Menir beras', 'Biji gandum hitam', 'Biji sorgum', 
        'Biji triticale', 'Biji gandum durum', 'Biji gandum lunak', 
        'Corn gluten feed', 'Corn gluten meal', 'Bungkil kelapa', 
        'Bungkil inti sawit', 'Bungkil kedelai', 'Kleci, kulit biji kedelai', 
        'Rumput Gajah', 'Rumput Odot', 'Rumput Raja', 
        'Tebon Jagung', 'Tebon Jagung dengan Bijinya', 'Alfalfa Hay', 
        'Jerami Kacang Tanah'
    ],
    'BK (%)': [
        87.2, 86.3, 86.3, 86.3, 67, 89.6, 90.6, 85.7, 87.6, 87.6, 88, 88, 
        87.6, 86.7, 87.8, 86.8, 87.8, 86.9, 87.8, 90.9, 90.5, 90.6, 93.2, 
        88.9, 20, 25, 18, 30, 35, 88, 86
    ],
    'PK (%BK)': [
        11.3, 8.8, 8.8, 8.8, 9.2, 12.5, 14.2, 12.8, 10.8, 10.8, 10.5, 8.5, 
        9.2, 9.8, 10.6, 11.5, 16.4, 12.6, 21.6, 67.8, 23.4, 18.3, 47, 12.8, 
        8.05, 11, 9, 6, 9, 18, 12
    ],
    'SK (%BK)': [
        5.4, 2.6, 2.6, 2.6, 2.6, 3.2, 7.4, 4.5, 13.1, 13.1, 2.4, 11, 0.6, 
        2.3, 2.8, 2.9, 3, 2.7, 9, 1.5, 13.6, 20.7, 6.4, 39.1, 30, 28, 32, 
        35, 25, 30, 35
    ],
    'NDF (%BK)': [
        21.5, 12.4, 12.4, 12.4, 12.4, 17.2, 23.2, 12.8, 35.7, 35.7, 7.5, 
        26.4, 5.7, 14.8, 11.1, 15, 15.9, 14.7, 39.9, 4, 53.6, 72.9, 13.6, 
        65.3, 65, 60, 68, 70, 55, 42, 60
    ],
    'ADF (%BK)': [
        6.5, 3.1, 3.1, 3.1, 3.1, 4.5, 12, 5.3, 16.3, 16.3, 2.9, 13.5, 1.8, 
        3.3, 4.3, 3.8, 4.2, 3.8, 10.6, 1.4, 27.5, 44, 8, 46.5, 35, 32, 38, 
        40, 30, 32, 38
    ],
    'Ca (g)': [
        0.8, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 1, 1.1, 1.1, 0.5, 0.7, 0.4, 0.7, 
        0.3, 0.7, 0.8, 0.7, 1.6, 0.3, 1, 3, 3.7, 5.6, 4.5, 5.0, 4.2, 3.8, 
        4.0, 15.0, 7.0
    ],
    'P (g)': [
        3.9, 2.9, 2.9, 2.9, 3.1, 3.3, 3, 3.4, 3.6, 3.6, 3.6, 2.8, 2.4, 3.5, 
        3.5, 3.8, 3.9, 3.6, 9.8, 4.1, 5.8, 6.1, 6.9, 1.7, 2.8, 3.0, 2.5, 2.2, 
        2.5, 2.8, 3.5
    ],
    'PDIA (g)': [
        30, 42, 52, 52, 24, 56, 26, 25, 20, 24, 28, 20, 25, 20, 47, 24, 36, 
        28, 53, 424, 99, 79, 154, 38, 20, 22, 19, 15, 25, 40, 30
    ],
    'PDI (g)': [
        87, 95, 108, 111, 80, 108, 86, 83, 73, 77, 80, 66, 81, 81, 98, 85, 
        96, 89, 109, 471, 152, 129, 208, 95, 60, 65, 58, 50, 70, 95, 80
    ],
    'ME (kkal)': [
        2960, 3340, 3340, 3340, 3320, 3400, 3440, 3080, 2740, 2740, 3160, 
        2400, 3200, 3120, 3180, 3100, 3160, 3130, 2980, 4450, 2750, 2390, 
        3580, 2830, 2000, 2200, 1900, 1800, 2500, 2700, 2300
    ],
    'NEl (kkal)': [
        1950, 2270, 2270, 2270, 2260, 2310, 2330, 2040, 1750, 1750, 2120, 
        1520, 2170, 2100, 2130, 2080, 2120, 2110, 1960, 3050, 1770, 1500, 
        2400, 1860, 1200, 1300, 1100, 1000, 1400, 1500, 1300
    ],
    'TDN (%)': [
        82.2, 89.3, 89.3, 89.3, 88.9, 86.1, 82.9, 85.6, 79.6, 79.6, 88.6, 
        72.5, 89.4, 84.4, 87.3, 84.1, 84.3, 84.5, 75.3, 94.1, 67, 48.1, 89, 
        67, 55, 58, 52, 50, 65, 70, 60
    ],
    'NEl (Mkal)': [
        1.84, 2.02, 2.1, 2.1, 2.01, 1.98, 1.91, 1.95, 1.78, 1.78, 2.01, 1.55, 
        2.02, 1.89, 1.97, 1.9, 1.95, 1.92, 1.74, 2.7, 1.53, 0.97, 2.41, 1.44, 
        1.02, 1.03, 1.01, 1.00, 1.04, 1.05, 1.03
    ],
    'RUP (%)': [
        27, 53, 49, 85, 25, 57, 18, 18, 18, 20, 28, 28, 28, 21, 57, 20, 22, 
        22, 25, 70, 47, 54, 34, 43, 20, 22, 18, 15, 25, 30, 25
    ],
    'RDP (%)': [
        73, 47, 51, 15, 75, 43, 82, 82, 82, 80, 72, 72, 72, 79, 43, 80, 78, 
        78, 75, 30, 53, 46, 66, 57, 80, 78, 82, 85, 75, 70, 75
    ],
    'Harga (Rp/kg)': [
        4500, 5000, 5200, 5200, 4800, 4600, 4500, 4500, 4200, 4300, 3800, 
        3000, 4000, 4500, 4600, 4500, 4700, 4600, 5500, 9000, 5000, 4000, 
        7500, 3500, 1500, 1800, 1400, 1300, 2000, 4500, 2000
    ]
}

# Konversi ke DataFrame
bahan_pakan_df = pd.DataFrame(bahan_pakan_data)

# Data acuan kebutuhan nutrisi sapi perah
data = {
    'Berat Badan (kg)': [350, 350, 350, 350, 450, 450, 450, 450, 600, 600, 600, 600],
    'Produksi Susu (L/hari)': [15, 20, 25, 30, 15, 20, 25, 30, 15, 20, 25, 30],
    'PK (%BK)': [16.0, 16.7, 17.0, 17.7, 15.0, 15.6, 16.0, 16.7, 14.6, 15.0, 15.6, 16.0],
    'SK (%BK)': [18.0, 18.0, 17.0, 16.0, 19.0, 18.0, 17.0, 16.0, 19.0, 18.0, 17.0, 16.0],
    'NDF (%BK)': [32.0, 31.0, 30.0, 29.0, 33.0, 32.0, 31.0, 30.0, 34.0, 33.0, 32.0, 31.0],
    'ADF (%BK)': [21.0, 20.0, 19.0, 18.0, 22.0, 21.0, 20.0, 19.0, 23.0, 22.0, 21.0, 20.0],
    'Ca (g)': [80.0, 90.0, 100.0, 110.0, 85.0, 95.0, 105.0, 115.0, 90.0, 100.0, 110.0, 120.0],
    'P (g)': [50.0, 55.0, 60.0, 65.0, 55.0, 60.0, 65.0, 70.0, 60.0, 65.0, 70.0, 75.0],
    'PDIA (g)': [250.0, 280.0, 310.0, 340.0, 270.0, 300.0, 330.0, 360.0, 290.0, 320.0, 350.0, 380.0],
    'PDI (g)': [1000.0, 1200.0, 1400.0, 1600.0, 1100.0, 1300.0, 1500.0, 1700.0, 1200.0, 1400.0, 1600.0, 1800.0],
    'ME (kkal)': [23000.0, 25000.0, 27000.0, 29000.0, 24000.0, 26000.0, 28000.0, 30000.0, 25000.0, 27000.0, 29000.0, 31000.0],
    'NEl (kkal)': [15000.0, 16000.0, 17000.0, 18000.0, 15500.0, 16500.0, 17500.0, 18500.0, 16000.0, 17000.0, 18000.0, 19000.0],
    'TDN (%)': [65.0, 66.0, 67.0, 68.0, 65.0, 66.0, 67.0, 68.0, 65.0, 66.0, 67.0, 68.0],
    'NEl (Mkal)': [15.0, 16.0, 17.0, 18.0, 15.6, 16.5, 17.5, 18.5, 16.0, 17.0, 18.0, 19.0],
    'RUP (%)': [35.0, 37.0, 38.0, 40.0, 34.0, 36.0, 37.0, 39.0, 33.0, 35.0, 36.0, 38.0],
    'RDP (%)': [65.0, 63.0, 62.0, 60.0, 66.0, 64.0, 63.0, 61.0, 67.0, 65.0, 64.0, 62.0]
}

df = pd.DataFrame(data)

# Function untuk download hasil
def get_download_link(df, filename, text):
    """Generate download link for dataframe"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Main title
st.markdown('<h1 class="main-header">Prediksi dan Optimalisasi Ransum Pakan Sapi Perah</h1>', unsafe_allow_html=True)

# About section
with st.expander("ℹ️ Tentang Aplikasi"):
    st.markdown("""
    Aplikasi ini membantu para peternak dan nutrisionis untuk menyusun ransum pakan sapi perah yang optimal 
    berdasarkan kebutuhan nutrisi dan bahan pakan yang tersedia. Aplikasi akan menghitung komposisi ransum yang 
    memenuhi kebutuhan nutrisi dengan biaya terendah.
    
    **Cara Penggunaan:**
    1. Masukkan berat badan sapi dan produksi susu harian
    2. Tambahkan bahan pakan yang akan digunakan (pilih dari database atau masukkan manual)
    3. Klik tombol "Optimalkan Ransum" untuk mendapatkan hasil
    
    **Fitur:**
    - Database bahan pakan dengan nilai nutrisi lengkap
    - Prediksi kebutuhan nutrisi berdasarkan berat badan dan produksi susu
    - Optimalisasi ransum dengan biaya minimal
    - Visualisasi hasil dalam bentuk grafik
    - Unduh hasil dalam format CSV
    
    **Keterangan Parameter Nutrisi:**
    - **BK (%)**: Bahan Kering - persentase bahan setelah air dihilangkan
    - **PK (%BK)**: Protein Kasar - kandungan protein total dalam persen bahan kering
    - **SK (%BK)**: Serat Kasar - kandungan serat total dalam persen bahan kering
    - **NDF (%BK)**: Neutral Detergent Fiber - mengukur dinding sel tanaman (selulosa, hemiselulosa, lignin)
    - **ADF (%BK)**: Acid Detergent Fiber - mengukur bagian serat yang kurang tersedia (selulosa, lignin)
    - **Ca (g)**: Kalsium - mineral penting untuk produksi susu dan kesehatan tulang
    - **P (g)**: Fosfor - mineral penting untuk metabolisme energi dan kesehatan tulang
    - **PDIA (g)**: Protein yang dicerna di usus kecil dari protein tidak terdegradasi di rumen
    - **PDI (g)**: Protein yang tersedia untuk produksi susu atau pertumbuhan
    - **ME (kkal)**: Metabolizable Energy - energi yang tersedia untuk metabolisme
    - **NEl (kkal)**: Net Energy for Lactation - energi yang tersedia khusus untuk produksi susu (dalam kkal)
    - **TDN (%)**: Total Digestible Nutrients - ukuran nilai energi pakan
    - **NEl (Mkal)**: Net Energy for Lactation - energi yang tersedia khusus untuk produksi susu (dalam Mkal)
    - **RUP (%)**: Rumen Undegraded Protein - protein yang tidak terdegradasi dalam rumen
    - **RDP (%)**: Rumen Degraded Protein - protein yang terdegradasi dalam rumen
    
    _Catatan: Nilai nutrisi pada database merupakan perkiraan berdasarkan berbagai sumber literatur dan dapat bervariasi tergantung pada kondisi pertumbuhan dan pengolahan bahan pakan._
    """)

# Main content in tabs
tab1, tab2, tab3 = st.tabs(["Input Sapi", "Bahan Pakan", "Hasil Optimasi"])

with tab1:
    st.markdown('<h2 class="section-header">Data Sapi dan Kebutuhan Nutrisi</h2>', unsafe_allow_html=True)
    
    # Input dari user
    col1, col2 = st.columns(2)
    with col1:
        berat_badan = st.number_input("Berat Badan Sapi (kg)", min_value=300, max_value=700, value=450)
    with col2:
        produksi_susu = st.number_input("Produksi Susu (L/hari)", min_value=10, max_value=35, value=20)
    
    # Filter data berdasarkan input user
    df_filtered = df[(df['Berat Badan (kg)'] == berat_badan) & (df['Produksi Susu (L/hari)'] == produksi_susu)]
    
    if len(df_filtered) > 0:
        # Prediksi kebutuhan nutrisi (rata-rata dari data yang difilter)
        kebutuhan_nutrisi = df_filtered.mean()
        
        st.markdown('<h3 class="section-header">Prediksi Kebutuhan Nutrisi</h3>', unsafe_allow_html=True)
        
        # Create a more readable format for the nutritional requirements
        nutrisi_display = pd.DataFrame({
            'Nutrisi': ['PK (%BK)', 'SK (%BK)', 'NDF (%BK)', 'ADF (%BK)', 'Ca (g)', 'P (g)', 
                        'PDIA (g)', 'PDI (g)', 'ME (kkal)', 'NEl (kkal)', 'TDN (%)', 
                        'NEl (Mkal)', 'RUP (%)', 'RDP (%)'],
            'Nilai': [
                f"{kebutuhan_nutrisi['PK (%BK)']:.2f}",
                f"{kebutuhan_nutrisi['SK (%BK)']:.2f}",
                f"{kebutuhan_nutrisi['NDF (%BK)']:.2f}",
                f"{kebutuhan_nutrisi['ADF (%BK)']:.2f}",
                f"{kebutuhan_nutrisi['Ca (g)']:.2f}",
                f"{kebutuhan_nutrisi['P (g)']:.2f}",
                f"{kebutuhan_nutrisi['PDIA (g)']:.2f}",
                f"{kebutuhan_nutrisi['PDI (g)']:.2f}",
                f"{kebutuhan_nutrisi['ME (kkal)']:.2f}",
                f"{kebutuhan_nutrisi['NEl (kkal)']:.2f}",
                f"{kebutuhan_nutrisi['TDN (%)']:.2f}",
                f"{kebutuhan_nutrisi['NEl (Mkal)']:.2f}",
                f"{kebutuhan_nutrisi['RUP (%)']:.2f}",
                f"{kebutuhan_nutrisi['RDP (%)']:.2f}"
            ],
            'Keterangan': [
                'Protein Kasar', 'Serat Kasar', 'Neutral Detergent Fiber', 'Acid Detergent Fiber',
                'Kalsium', 'Fosfor', 'Protein Digestible dalam Usus - Asal Pakan',
                'Protein Digestible dalam Usus - Total', 'Metabolizable Energy',
                'Net Energy Laktasi (kkal)', 'Total Digestible Nutrients',
                'Net Energy Laktasi (Mkal)', 'Rumen Undegraded Protein', 'Rumen Degraded Protein'
            ]
        })
        
        # Display in a nice table
        st.dataframe(nutrisi_display, use_container_width=True)
        
        # Store in session state for later use
        st.session_state['kebutuhan_nutrisi'] = kebutuhan_nutrisi
        
    else:
        st.warning("Tidak ada data yang sesuai dengan kriteria Berat Badan dan Produksi Susu yang diberikan.")

with tab2:
    st.markdown('<h2 class="section-header">Pemilihan Bahan Pakan</h2>', unsafe_allow_html=True)
    
    # Initialize session state for feed ingredients
    if 'bahan_pakan_terpilih' not in st.session_state:
        st.session_state['bahan_pakan_terpilih'] = {}
    
    # Method for adding feed ingredients
    method = st.radio(
        "Metode pemilihan bahan pakan:",
        ["Pilih dari database", "Input manual"],
        horizontal=True
    )
    
    if method == "Pilih dari database":
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Show database in searchable dataframe
            st.write("Database Bahan Pakan:")
            st.dataframe(bahan_pakan_df, use_container_width=True)
            
        with col2:
            # Widget to select feed ingredient
            selected_bahan = st.selectbox(
                "Pilih bahan pakan:",
                bahan_pakan_df['Nama Bahan'].tolist()
            )
            
            # Options for proportion constraints
            min_prop = st.number_input("Proporsi Minimum (%)", min_value=0.0, max_value=100.0, value=0.0)
            max_prop = st.number_input("Proporsi Maksimum (%)", min_value=0.0, max_value=100.0, value=100.0, 
                                       help="Batasan maksimum proporsi bahan dalam ransum")
            
            # Button to add to selected ingredients
            if st.button("Tambahkan Bahan"):
                selected_row = bahan_pakan_df[bahan_pakan_df['Nama Bahan'] == selected_bahan].iloc[0]
                
                # Add to session state with proportion constraints
                st.session_state['bahan_pakan_terpilih'][selected_bahan] = {
                    'PK (%BK)': selected_row['PK (%BK)'],
                    'SK (%BK)': selected_row['SK (%BK)'],
                    'NDF (%BK)': selected_row['NDF (%BK)'],
                    'ADF (%BK)': selected_row['ADF (%BK)'],
                    'Ca (g)': selected_row['Ca (g)'],
                    'P (g)': selected_row['P (g)'],
                    'PDIA (g)': selected_row['PDIA (g)'],
                    'PDI (g)': selected_row['PDI (g)'],
                    'ME (kkal)': selected_row['ME (kkal)'],
                    'NEl (kkal)': selected_row['NEl (kkal)'],
                    'TDN (%)': selected_row['TDN (%)'],
                    'NEl (Mkal)': selected_row['NEl (Mkal)'],
                    'RUP (%)': selected_row['RUP (%)'],
                    'RDP (%)': selected_row['RDP (%)'],
                    'Harga (Rp/kg)': selected_row['Harga (Rp/kg)'],
                    'Min Proporsi (%)': min_prop,
                    'Max Proporsi (%)': max_prop
                }
                st.success(f"Bahan {selected_bahan} berhasil ditambahkan!")
    
    else:  # Input manual
        st.subheader("Input Bahan Pakan Manual")
        
        # Create columns for input form
        col1, col2, col3 = st.columns(3)
        
        with col1:
            nama_bahan = st.text_input("Nama Bahan Pakan")
            pk = st.number_input("PK (%BK)", min_value=0.0, max_value=100.0, value=10.0, 
                                help="Protein Kasar - kandungan protein total dalam persen bahan kering")
            sk = st.number_input("SK (%BK)", min_value=0.0, max_value=100.0, value=10.0,
                                help="Serat Kasar - kandungan serat total dalam persen bahan kering")
            ndf = st.number_input("NDF (%BK)", min_value=0.0, max_value=100.0, value=30.0,
                                 help="Neutral Detergent Fiber - mengukur dinding sel tanaman (selulosa, hemiselulosa, lignin)")
            adf = st.number_input("ADF (%BK)", min_value=0.0, max_value=100.0, value=20.0,
                                 help="Acid Detergent Fiber - mengukur bagian serat yang kurang tersedia (selulosa, lignin)")
        
        with col2:
            ca = st.number_input("Ca (g)", min_value=0.0, max_value=200.0, value=5.0,
                               help="Kalsium - mineral penting untuk produksi susu dan kesehatan tulang")
            p = st.number_input("P (g)", min_value=0.0, max_value=200.0, value=3.0,
                              help="Fosfor - mineral penting untuk metabolisme energi dan kesehatan tulang")
            pdia = st.number_input("PDIA (g)", min_value=0.0, max_value=500.0, value=100.0,
                                 help="Protein yang dicerna di usus kecil dari protein tidak terdegradasi di rumen")
            pdi = st.number_input("PDI (g)", min_value=0.0, max_value=2000.0, value=500.0,
                                help="Protein yang tersedia untuk produksi susu atau pertumbuhan")
            me = st.number_input("ME (kkal)", min_value=0.0, max_value=50000.0, value=10000.0,
                               help="Metabolizable Energy - energi yang tersedia untuk metabolisme")
        
        with col3:
            nel_kkal = st.number_input("NEl (kkal)", min_value=0.0, max_value=30000.0, value=6000.0,
                                     help="Net Energy for Lactation - energi yang tersedia khusus untuk produksi susu (dalam kkal)")
            tdn = st.number_input("TDN (%)", min_value=0.0, max_value=100.0, value=60.0,
                                 help="Total Digestible Nutrients - ukuran nilai energi pakan")
            nel_mkal = st.number_input("NEl (Mkal)", min_value=0.0, max_value=30.0, value=6.0,
                                     help="Net Energy for Lactation - energi yang tersedia khusus untuk produksi susu (dalam Mkal)")
            rup = st.number_input("RUP (%)", min_value=0.0, max_value=100.0, value=30.0,
                                 help="Rumen Undegraded Protein - protein yang tidak terdegradasi dalam rumen")
            rdp = st.number_input("RDP (%)", min_value=0.0, max_value=100.0, value=70.0,
                                 help="Rumen Degraded Protein - protein yang terdegradasi dalam rumen")
        
        # Row for additional inputs
        col1, col2, col3 = st.columns(3)
        with col1:
            harga = st.number_input("Harga (Rp/kg)", min_value=0.0, value=5000.0)
        with col2:
            min_prop = st.number_input("Proporsi Minimum (%)", key="man_min_prop", min_value=0.0, max_value=100.0, value=0.0)
        with col3:
            max_prop = st.number_input("Proporsi Maksimum (%)", key="man_max_prop", min_value=0.0, max_value=100.0, value=100.0)
        
        # Button to add manual feed
        if st.button("Tambahkan Bahan Manual"):
            if nama_bahan:
                # Add unique suffix if name already exists
                if nama_bahan in st.session_state['bahan_pakan_terpilih']:
                    i = 1
                    while f"{nama_bahan} ({i})" in st.session_state['bahan_pakan_terpilih']:
                        i += 1
                    nama_bahan = f"{nama_bahan} ({i})"
                
                # Add to session state
                st.session_state['bahan_pakan_terpilih'][nama_bahan] = {
                    'PK (%BK)': pk,
                    'SK (%BK)': sk,
                    'NDF (%BK)': ndf,
                    'ADF (%BK)': adf,
                    'Ca (g)': ca,
                    'P (g)': p,
                    'PDIA (g)': pdia,
                    'PDI (g)': pdi,
                    'ME (kkal)': me,
                    'NEl (kkal)': nel_kkal,
                    'TDN (%)': tdn,
                    'NEl (Mkal)': nel_mkal,
                    'RUP (%)': rup,
                    'RDP (%)': rdp,
                    'Harga (Rp/kg)': harga,
                    'Min Proporsi (%)': min_prop,
                    'Max Proporsi (%)': max_prop
                }
                st.success(f"Bahan {nama_bahan} berhasil ditambahkan!")
            else:
                st.error("Nama bahan tidak boleh kosong!")
    
    # Display selected feed ingredients
    st.markdown('<h3 class="section-header">Bahan Pakan Terpilih</h3>', unsafe_allow_html=True)
    
    if st.session_state['bahan_pakan_terpilih']:
        # Create DataFrame for display
        selected_df = pd.DataFrame([
            {
                'Nama Bahan': nama,
                'PK (%BK)': info['PK (%BK)'],
                'NDF (%BK)': info['NDF (%BK)'],
                'TDN (%)': info['TDN (%)'],
                'NEl (Mkal)': info['NEl (Mkal)'],
                'Harga (Rp/kg)': info['Harga (Rp/kg)'],
                'Min Proporsi (%)': info['Min Proporsi (%)'],
                'Max Proporsi (%)': info['Max Proporsi (%)']
            }
            for nama, info in st.session_state['bahan_pakan_terpilih'].items()
        ])
        
        # Display selected ingredients
        st.dataframe(selected_df, use_container_width=True)
        
        # Button to clear selected ingredients
        if st.button("Hapus Semua Bahan"):
            st.session_state['bahan_pakan_terpilih'] = {}
            st.experimental_rerun()
    else:
        st.info("Belum ada bahan pakan yang dipilih.")
    
    # Tambahkan kode ini di bagian tab "Bahan Pakan", setelah menampilkan tabel bahan terpilih

    if st.session_state['bahan_pakan_terpilih']:
        # Setelah kode yang menampilkan tabel bahan terpilih
        
        # Visualisasi nutrisi bahan terpilih
        st.subheader("Visualisasi Nutrisi Bahan Terpilih")
        
        # Pilihan parameter untuk visualisasi
        nutrisi_pilihan = st.radio(
            "Pilih Parameter Nutrisi:",
            ["Protein dan Energi", "Serat", "Mineral", "RUP dan RDP"],
            horizontal=True
        )
        
        # Filtering berdasarkan pilihan
        if nutrisi_pilihan == "Protein dan Energi":
            params = ['PK (%BK)', 'PDIA (g)', 'PDI (g)', 'TDN (%)', 'NEl (Mkal)']
            colors = ['#3498db', '#2980b9', '#1abc9c', '#f39c12', '#e67e22']
            title = "Perbandingan Protein dan Energi"
        elif nutrisi_pilihan == "Serat":
            params = ['SK (%BK)', 'NDF (%BK)', 'ADF (%BK)']
            colors = ['#2ecc71', '#27ae60', '#16a085']
            title = "Perbandingan Kandungan Serat"
        elif nutrisi_pilihan == "Mineral":
            params = ['Ca (g)', 'P (g)']
            colors = ['#9b59b6', '#8e44ad']
            title = "Perbandingan Mineral"
        else:  # RUP dan RDP
            params = ['RUP (%)', 'RDP (%)']
            colors = ['#e74c3c', '#c0392b']
            title = "Perbandingan RUP dan RDP"
        
        # Create DataFrame for plotting
        viz_data = []
        for nama, info in st.session_state['bahan_pakan_terpilih'].items():
            row = {'Nama Bahan': nama}
            for param in params:
                row[param] = info[param]
            viz_data.append(row)
        
        viz_df = pd.DataFrame(viz_data)
        
        # Plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(viz_df['Nama Bahan']))
        width = 0.8 / len(params)
        
        for i, param in enumerate(params):
            ax.bar(x + i*width - (len(params)-1)*width/2, viz_df[param], width, label=param, color=colors[i])
        
        ax.set_xticks(x)
        ax.set_xticklabels(viz_df['Nama Bahan'], rotation=45, ha='right')
        ax.set_title(title)
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        st.pyplot(fig)

with tab3:
    st.markdown('<h2 class="section-header">Optimasi Ransum</h2>', unsafe_allow_html=True)
    
    # Parameter optimasi
    st.subheader("Parameter Optimasi")
    
    col1, col2 = st.columns(2)
    with col1:
        konsumsi_bk = st.number_input("Konsumsi Bahan Kering (kg/hari)", min_value=1.0, max_value=30.0, value=15.0,
                                    help="Jumlah konsumsi bahan kering per hari")
    with col2:
        ratio_hijauan = st.slider("Rasio Minimum Hijauan : Konsentrat", min_value=0, max_value=100, value=40,
                               help="Persentase minimum hijauan dalam ransum")
    
    # Pengaturan relaksasi batasan
    st.subheader("Pengaturan Relaksasi Batasan")
    with st.expander("Relaksasi Batasan (untuk mengatasi infeasible)"):
        relaxation_factor = st.slider(
            "Faktor Relaksasi Nutrisi (%)", 
            min_value=0, 
            max_value=30, 
            value=10,
            help="Persentase relaksasi batasan nutrisi. Semakin tinggi, semakin besar kemungkinan menemukan solusi."
        )
        
        relax_roughage = st.checkbox(
            "Relaksasi Batasan Rasio Hijauan", 
            value=True,
            help="Izinkan proporsi hijauan lebih rendah jika diperlukan"
        )
        
        st.info("Jika optimasi gagal, coba tingkatkan nilai relaksasi atau hilangkan beberapa batasan.")
    
    # Tambahkan kode ini setelah expander relaksasi batasan yang sudah ada

    # Tambahkan opsi untuk melihat detail mode optimasi
    with st.expander("Pengaturan Optimasi Lanjutan"):
        optimize_mode = st.radio(
            "Mode Optimasi:",
            ["Standar (Optimasi Biaya)", "Fokus pada Feasibility (Cari Solusi Apapun)", "Relaksasi Otomatis"],
            index=2,  # Default ke relaksasi otomatis
            help="Mode 'Relaksasi Otomatis' akan secara bertahap melonggarkan batasan hingga menemukan solusi optimal"
        )
        
        progressive_relax = st.checkbox(
            "Relaksasi Progresif", 
            value=True,
            help="Jika diaktifkan, sistem akan mencoba meningkatkan relaksasi secara otomatis sampai solusi ditemukan"
        )
        
        max_relax = st.slider(
            "Batas Maksimum Relaksasi (%)", 
            min_value=10, 
            max_value=50, 
            value=40,  # Tingkatkan nilai default
            help="Batas maksimum relaksasi yang akan dicoba dalam mode progresif"
        )
        
        adapt_strategy = st.radio(
            "Strategi Adaptasi:",
            ["Relaksasi Nutrisi", "Relaksasi Proporsi", "Relaksasi Keduanya"],
            index=2,
            help="Pilih batasan mana yang akan dilonggarkan secara otomatis"
        )
    
    # Define hijauan/roughage list
    hijauan_list = [
        'Rumput Gajah', 'Rumput Odot', 'Rumput Raja', 'Tebon Jagung', 
        'Tebon Jagung dengan Bijinya', 'Alfalfa Hay', 'Jerami Kacang Tanah'
    ]
    
    # Button to run optimization
    if st.button("Optimalkan Ransum"):
        if 'kebutuhan_nutrisi' not in st.session_state:
            st.error("Silakan tentukan kebutuhan nutrisi terlebih dahulu di tab 'Input Sapi'.")
        
        elif len(st.session_state['bahan_pakan_terpilih']) < 2:
            st.error("Diperlukan minimal 2 bahan pakan untuk melakukan optimasi.")
        
        else:
            try:
                import time
                from datetime import datetime

                # Ganti baris ini:
                # st.write("Memulai optimasi...")

                # Dengan kode ini:
                with st.spinner('Mempersiapkan data untuk optimasi...'):
                    # Create placeholder for optimization progress
                    progress_info = st.empty()
                    progress_bar = st.progress(0)
                    time_info = st.empty()
                    
                    # Initialize timer
                    start_time = datetime.now()
                    progress_info.info("Memulai optimasi ransum...")
                    
                    # Show initial progress
                    progress_bar.progress(5)
                    time_info.text(f"Waktu berjalan: 0 detik")
                    time.sleep(0.5)  # Give UI time to render
                    
                    # Update progress
                    progress_info.info("Menganalisis batasan nutrisi...")
                    progress_bar.progress(15)
                    
                    # Calculate remaining steps based on optimization mode
                    if optimize_mode == "Relaksasi Otomatis":
                        progress_info.warning("Mode relaksasi otomatis dipilih - proses mungkin membutuhkan waktu lebih lama")
                        estimated_time = "1-3 menit"
                    else:
                        estimated_time = "30-60 detik"
                    
                    time_info.text(f"Waktu berjalan: {(datetime.now() - start_time).seconds} detik | Estimasi: {estimated_time}")
                    time.sleep(0.5)
                    
                    # Show more progress
                    progress_info.info("Membuat matriks batasan...")
                    progress_bar.progress(30)
                    time_info.text(f"Waktu berjalan: {(datetime.now() - start_time).seconds} detik | Estimasi: {estimated_time}")

                # Kemudian, pada bagian setelah optimasi berhasil atau gagal, tambahkan:
                # (Tambahkan tepat sebelum menampilkan hasil)

                # Update final progress
                progress_bar.progress(100)
                time_info.text(f"Total waktu: {(datetime.now() - start_time).seconds} detik")
                progress_info.success("Optimasi selesai!")
                
                # Get the nutritional requirements
                kebutuhan_nutrisi = st.session_state['kebutuhan_nutrisi']
            except Exception as e:
                st.error(f"Terjadi kesalahan selama optimasi: {e}")
                
                # Get feed ingredients
                bahan_pakan = st.session_state['bahan_pakan_terpilih']
                
                # List nama bahan pakan untuk konsistensi urutan
                nama_bahan_list = list(bahan_pakan.keys())
                
                # Create the cost vector (objective function)
                c = np.array([bahan_pakan[nama]['Harga (Rp/kg)'] for nama in nama_bahan_list])
                
                # Create the constraint matrices
                A_ub = []  # For <= constraints
                b_ub = []  # RHS for <= constraints
                A_eq = []  # For == constraints
                b_eq = []  # RHS for == constraints
                
                # Constraint: sum of all proportions = 1
                A_eq.append(np.ones(len(bahan_pakan)))
                b_eq.append(1.0)  # Total proportion must be 1 (100%)
                
                # Get which items are roughage (hijauan)
                hijauan_indices = [i for i, nama in enumerate(nama_bahan_list) 
                                if any(h in nama for h in hijauan_list)]
                
                # Nutritional constraints using inequality (>=) constraints with relaxation
                for nutrisi in ['PK (%BK)', 'Ca (g)', 'P (g)', 'PDIA (g)', 'PDI (g)', 
                                'ME (kkal)', 'NEl (kkal)', 'TDN (%)', 'NEl (Mkal)', 'RUP (%)', 'RDP (%)']:
                    if nutrisi in kebutuhan_nutrisi:
                        # Get nutrient values for each feed
                        nutrient_values = np.array([bahan_pakan[nama][nutrisi] for nama in nama_bahan_list])
                        
                        # Apply relaxation factor to reduce the minimum requirement
                        relaxed_req = kebutuhan_nutrisi[nutrisi] * (1 - relaxation_factor/100)
                        
                        # Create constraint: sum(proportion * nutrient_value) >= relaxed_requirement
                        A_ub.append(-1 * nutrient_values)  # Negative for >= constraint
                        b_ub.append(-1 * relaxed_req)  # Negative for >= constraint

                # Add maximum constraints for fiber (<=) with relaxation
                for nutrisi in ['SK (%BK)', 'NDF (%BK)', 'ADF (%BK)']:
                    if nutrisi in kebutuhan_nutrisi:
                        # Get nutrient values for each feed
                        nutrient_values = np.array([bahan_pakan[nama][nutrisi] for nama in nama_bahan_list])
                        
                        # Apply relaxation factor to increase the maximum limit
                        relaxed_max = kebutuhan_nutrisi[nutrisi] * (1 + relaxation_factor/100)
                        
                        # Create constraint: sum(proportion * nutrient_value) <= relaxed_max
                        A_ub.append(nutrient_values)  # Positive for <= constraint
                        b_ub.append(relaxed_max)  # Positive for <= constraint

                # Relax or skip the roughage constraint if selected
                if hijauan_indices and not relax_roughage:
                    roughage_constraint = np.zeros(len(bahan_pakan))
                    for idx in hijauan_indices:
                        roughage_constraint[idx] = 1
                    A_ub.append(-1 * roughage_constraint)  # We want sum >= min_ratio
                    b_ub.append(-1 * ratio_hijauan / 100)  # Convert percentage to proportion
                
                # Add min/max proportion constraints for each feed
                for i, nama in enumerate(nama_bahan_list):
                    min_prop = bahan_pakan[nama]['Min Proporsi (%)'] / 100  # Convert % to proportion
                    max_prop = bahan_pakan[nama]['Max Proporsi (%)'] / 100  # Convert % to proportion
                    
                    # Min constraint: proportion[i] >= min_prop
                    if min_prop > 0:
                        min_constraint = np.zeros(len(bahan_pakan))
                        min_constraint[i] = -1  # Negative for >= constraint
                        A_ub.append(min_constraint)
                        b_ub.append(-1 * min_prop)  # Negative for >= constraint
                    
                    # Max constraint: proportion[i] <= max_prop
                    if max_prop < 1:
                        max_constraint = np.zeros(len(bahan_pakan))
                        max_constraint[i] = 1  # Positive for <= constraint
                        A_ub.append(max_constraint)
                        b_ub.append(max_prop)  # Positive for <= constraint
                
                # Convert lists to numpy arrays
                A_ub = np.array(A_ub)
                b_ub = np.array(b_ub)
                A_eq = np.array(A_eq)
                b_eq = np.array(b_eq)
                
                # Solve the linear programming problem
                st.write("Menjalankan optimasi...")

                if optimize_mode == "Relaksasi Otomatis":
                    # Initialize progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Prepare containers for storing attempts
                    relax_attempts = {}
                    
                    # Auto-adaptive solver
                    status_text.text("Mencoba tanpa relaksasi...")
                    result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, method='highs')
                    progress_bar.progress(10)
                    
                    if result.success:
                        status_text.text("Solusi optimal ditemukan tanpa relaksasi!")
                    else:
                        # Systematically try different relaxation strategies
                        found_solution = False
                        critical_nutrients = []
                        
                        # Step 1: Identify critical constraints
                        status_text.text("Menganalisis batasan kritis...")
                        progress_bar.progress(20)
                        
                        # For each nutrient, try relaxing only that one to see if it helps
                        for i, nutrisi in enumerate(['PK (%BK)', 'Ca (g)', 'P (g)', 'PDIA (g)', 'PDI (g)', 
                                                  'ME (kkal)', 'NEl (kkal)', 'TDN (%)', 'NEl (Mkal)', 'RUP (%)', 'RDP (%)',
                                                  'SK (%BK)', 'NDF (%BK)', 'ADF (%BK)']):
                            if nutrisi in kebutuhan_nutrisi:
                                # Create modified constraints matrices just for this nutrient
                                A_ub_test = A_ub.copy()
                                b_ub_test = b_ub.copy()
                                
                                # Find this nutrient's constraint and relax by 50%
                                for j, row in enumerate(A_ub_test):
                                    nutrient_values = np.array([bahan_pakan[nama][nutrisi] for nama in nama_bahan_list])
                                    
                                    # Check if this is a min constraint (negative coefficients)
                                    if nutrisi in ['PK (%BK)', 'Ca (g)', 'P (g)', 'PDIA (g)', 'PDI (g)', 
                                                'ME (kkal)', 'NEl (kkal)', 'TDN (%)', 'NEl (Mkal)', 'RUP (%)', 'RDP (%)']:
                                        if np.array_equal(-1 * nutrient_values, row):
                                            # Relax by 50%
                                            relaxed_req = kebutuhan_nutrisi[nutrisi] * 0.5
                                            b_ub_test[j] = -1 * relaxed_req
                                            break
                                    # Check if this is a max constraint (positive coefficients)
                                    elif nutrisi in ['SK (%BK)', 'NDF (%BK)', 'ADF (%BK)']:
                                        if np.array_equal(nutrient_values, row):
                                            # Relax by 50%
                                            relaxed_max = kebutuhan_nutrisi[nutrisi] * 1.5
                                            b_ub_test[j] = relaxed_max
                                            break
                                
                                # Try optimization with just this nutrient relaxed
                                test_result = linprog(dummy_c, A_ub=A_ub_test, b_ub=b_ub_test, A_eq=A_eq, b_eq=b_eq, method='highs')
                                
                                # If it succeeds, this nutrient was a critical constraint
                                if test_result.success:
                                    critical_nutrients.append(nutrisi)
                        
                        progress_bar.progress(40)
                        
                        if critical_nutrients:
                            status_text.text(f"Batasan kritis teridentifikasi: {', '.join(critical_nutrients)}")
                        else:
                            status_text.text("Tidak ada batasan tunggal yang kritis - mencoba relaksasi bertahap...")
                            critical_nutrients = ['PK (%BK)', 'NDF (%BK)', 'ADF (%BK)', 'PDI (g)', 'ME (kkal)']  # Fokus pada nutrisi utama
                        
                        # Step 2: Try progressive relaxation on critical nutrients
                        for relax_level in range(10, max_relax+1, 5):
                            progress_value = 40 + (relax_level/max_relax) * 40
                            progress_bar.progress(int(progress_value))
                            status_text.text(f"Mencoba relaksasi {relax_level}% pada nutrisi kritis...")
                            
                            # Update relaxed constraints focusing on critical nutrients
                            A_ub_copy = A_ub.copy()
                            b_ub_copy = b_ub.copy()
                            
                            # Relax minimum requirements for critical nutrients (relaxing downward)
                            for nutrisi in critical_nutrients:
                                if nutrisi in ['PK (%BK)', 'Ca (g)', 'P (g)', 'PDIA (g)', 'PDI (g)', 
                                             'ME (kkal)', 'NEl (kkal)', 'TDN (%)', 'NEl (Mkal)', 'RUP (%)', 'RDP (%)']:
                                    # Find constraints for this nutrient
                                    for j, row in enumerate(A_ub_copy):
                                        nutrient_values = np.array([bahan_pakan[nama][nutrisi] for nama in nama_bahan_list])
                                        if np.array_equal(-1 * nutrient_values, row):
                                            # Update the constraint
                                            relaxed_req = kebutuhan_nutrisi[nutrisi] * (1 - relax_level/100)
                                            b_ub_copy[j] = -1 * relaxed_req
                                
                                # Relax maximum requirements for critical nutrients (relaxing upward)
                                elif nutrisi in ['SK (%BK)', 'NDF (%BK)', 'ADF (%BK)']:
                                    for j, row in enumerate(A_ub_copy):
                                        nutrient_values = np.array([bahan_pakan[nama][nutrisi] for nama in nama_bahan_list])
                                        if np.array_equal(nutrient_values, row):
                                            # Update the constraint
                                            relaxed_max = kebutuhan_nutrisi[nutrisi] * (1 + relax_level/100)
                                            b_ub_copy[j] = relaxed_max
                            
                            # Relax proportion constraints if needed
                            if adapt_strategy in ["Relaksasi Proporsi", "Relaksasi Keduanya"] and relax_level > 20:
                                status_text.text(f"Mencoba relaksasi {relax_level}% pada nutrisi dan proporsi...")
                                
                                # Relax min/max proportion constraints
                                constraints_to_remove = []
                                for j, row in enumerate(A_ub_copy):
                                    # Identify proportion constraints (rows with a single 1 or -1)
                                    if sum(abs(row)) == 1:
                                        idx = np.where(row != 0)[0][0]
                                        if row[idx] == 1:  # Max constraint
                                            constraints_to_remove.append(j)
                                        elif relax_level > 30 and row[idx] == -1:  # Min constraint, only relax at higher levels
                                            constraints_to_remove.append(j)
                                
                                # Remove identified constraints
                                if constraints_to_remove:
                                    A_ub_copy = np.delete(A_ub_copy, constraints_to_remove, axis=0)
                                    b_ub_copy = np.delete(b_ub_copy, constraints_to_remove)
                            
                            # Try optimization with relaxed constraints
                            result = linprog(c, A_ub=A_ub_copy, b_ub=b_ub_copy, A_eq=A_eq, b_eq=b_eq, method='highs')
                            relax_attempts[relax_level] = result.success
                            
                            if result.success:
                                status_text.text(f"✅ Solusi ditemukan dengan relaksasi {relax_level}%!")
                                found_solution = True
                                break
                        
                        # Step 3: If still no solution, try more extreme measures
                        if not found_solution:
                            progress_bar.progress(80)
                            status_text.text("Mencoba pendekatan terakhir dengan relaksasi maksimum...")
                            
                            # Extreme approach: keep only the sum to 1 constraint
                            A_eq_final = A_eq.copy()
                            b_eq_final = b_eq.copy()
                            
                            # Only constrain total sum = 1 and any absolutely necessary bounds
                            dummy_c = np.ones(len(bahan_pakan))
                            result = linprog(dummy_c, A_eq=A_eq_final, b_eq=b_eq_final, bounds=[(0, 1) for _ in range(len(bahan_pakan))], method='highs')
                            
                            if result.success:
                                status_text.text("Solusi dasar ditemukan dengan relaksasi maksimum (hanya batasan jumlah = 100%)")
                                
                                # Use this feasible point to guide optimization
                                initial_point = result.x
                                
                                # Try cost optimization with this point as a starting point
                                result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=[(0, 1) for _ in range(len(bahan_pakan))], 
                                               x0=initial_point, method='highs')
                                
                                if result.success:
                                    status_text.text("✅ Solusi akhir ditemukan dengan pendekatan relaksasi bertahap!")
                                    found_solution = True
                                else:
                                    status_text.text("❌ Optimasi biaya gagal meskipun dengan relaksasi maksimum.")
                            else:
                                status_text.text("❌ Tidak dapat menemukan solusi bahkan dengan relaksasi maksimum.")
                    
                    progress_bar.progress(100)

                elif optimize_mode == "Standar (Optimasi Biaya)":
                    # Existing code for standard optimization
                    result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, method='highs')
                    
                    # If infeasible and progressive relaxation is enabled, try with increasing relaxation
                    if not result.success and progressive_relax and "infeasible" in result.message.lower():
                        st.warning("Optimasi standar gagal. Mencoba dengan relaksasi progresif...")
                        
                        for relax_level in range(relaxation_factor+5, max_relax+1, 5):
                            st.info(f"Mencoba dengan relaksasi {relax_level}%...")
                            
                            # Update relaxed constraints
                            A_ub_copy = A_ub.copy()
                            b_ub_copy = b_ub.copy()
                            
                            # Update minimum requirements (relaxing downward)
                            for i, nutrisi in enumerate(['PK (%BK)', 'Ca (g)', 'P (g)', 'PDIA (g)', 'PDI (g)', 
                                                       'ME (kkal)', 'NEl (kkal)', 'TDN (%)', 'NEl (Mkal)', 'RUP (%)', 'RDP (%)']):
                                if nutrisi in kebutuhan_nutrisi:
                                    # Find constraints for this nutrient (they have negative coefficients for >= constraints)
                                    for j, row in enumerate(A_ub_copy):
                                        nutrient_values = np.array([bahan_pakan[nama][nutrisi] for nama in nama_bahan_list])
                                        if np.array_equal(-1 * nutrient_values, row):
                                            # Update the constraint
                                            relaxed_req = kebutuhan_nutrisi[nutrisi] * (1 - relax_level/100)
                                            b_ub_copy[j] = -1 * relaxed_req
                            
                            # Update maximum limits (relaxing upward)
                            for i, nutrisi in enumerate(['SK (%BK)', 'NDF (%BK)', 'ADF (%BK)']):
                                if nutrisi in kebutuhan_nutrisi:
                                    for j, row in enumerate(A_ub_copy):
                                        nutrient_values = np.array([bahan_pakan[nama][nutrisi] for nama in nama_bahan_list])
                                        if np.array_equal(nutrient_values, row):
                                            # Update the constraint
                                            relaxed_max = kebutuhan_nutrisi[nutrisi] * (1 + relax_level/100)
                                            b_ub_copy[j] = relaxed_max
                            
                            # Try optimization with increased relaxation
                            result = linprog(c, A_ub=A_ub_copy, b_ub=b_ub_copy, A_eq=A_eq, b_eq=b_eq, method='highs')
                            
                            if result.success:
                                st.success(f"Solusi ditemukan dengan relaksasi {relax_level}%!")
                                break

                else:  # Fokus pada Feasibility
                    # Existing code for feasibility focus
                    dummy_c = np.ones(len(bahan_pakan))
                    result = linprog(dummy_c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, method='highs')
                    
                    # If successful with dummy objective, re-optimize with real costs
                    if result.success:
                        st.success("Solusi layak ditemukan! Mengoptimalkan biaya...")
                        
                        # Add constraints to ensure we keep a feasible solution
                        # Extract the feasible point's minimum values for each nutrient
                        feasible_point = result.x
                        nutrisi_optimal = {}
                        
                        for nutrisi in ['PK (%BK)', 'Ca (g)', 'P (g)', 'PDIA (g)', 'PDI (g)', 
                                      'ME (kkal)', 'NEl (kkal)', 'TDN (%)', 'NEl (Mkal)', 'RUP (%)', 'RDP (%)']:
                            nutrient_values = np.array([bahan_pakan[nama][nutrisi] for nama in nama_bahan_list])
                            nutrisi_optimal[nutrisi] = np.sum(feasible_point * nutrient_values)
                            
                            # Add a new constraint to ensure we don't go below this feasible value
                            nutrient_constraint = -1 * nutrient_values
                            A_ub = np.vstack([A_ub, nutrient_constraint])
                            b_ub = np.append(b_ub, -0.95 * nutrisi_optimal[nutrisi])  # Allow 5% degradation
                        
                        # Now optimize with the real cost function
                        result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, method='highs')
                
                # Add these lines inside the "Relaksasi Otomatis" block, after initializing critical_nutrients
                # and relax_attempts but before the if/else block

                # Store these variables in session state
                st.session_state['optimize_mode'] = optimize_mode
                st.session_state['optimization_performed'] = True
                st.session_state['relax_attempts'] = relax_attempts
                st.session_state['critical_nutrients'] = critical_nutrients

                # Display the results
                if result.success:
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.markdown('<h3 style="color:#27ae60; text-align:center;">Optimasi Berhasil!</h3>', unsafe_allow_html=True)
                    
                    # Create result dataframe with more details
                    proporsi_optimal = result.x
                    
                    # Filter out very small proportions for clarity
                    threshold = 0.001  # 0.1%
                    proporsi_filtered = np.where(proporsi_optimal < threshold, 0, proporsi_optimal)
                    
                    # Renormalize if needed
                    if np.sum(proporsi_filtered) > 0:
                        proporsi_normalized = proporsi_filtered / np.sum(proporsi_filtered)
                    else:
                        proporsi_normalized = proporsi_filtered
                    
                    # Calculate amounts in kg based on total dry matter intake
                    kg_per_hari = proporsi_normalized * konsumsi_bk
                    biaya_per_hari = kg_per_hari * np.array([bahan_pakan[nama]['Harga (Rp/kg)'] for nama in nama_bahan_list])
                    
                    # Create the final results DataFrame
                    hasil_df = pd.DataFrame({
                        "Nama Bahan": nama_bahan_list,
                        "Proporsi (%)": [f"{p*100:.2f}" for p in proporsi_normalized],
                        "Jumlah (kg/hari)": [f"{kg:.2f}" for kg in kg_per_hari],
                        "Harga (Rp/kg)": [f"{bahan_pakan[nama]['Harga (Rp/kg)']:,.0f}" for nama in nama_bahan_list],
                        "Biaya (Rp/hari)": [f"{cost:,.0f}" for cost in biaya_per_hari]
                    })
                    
                    # Include only non-zero proportions
                    hasil_df = hasil_df[np.array([float(p.replace('%', '')) for p in hasil_df["Proporsi (%)"]]) > 0]
                    
                    # Sort by proportion (descending)
                    hasil_df = hasil_df.sort_values(by="Proporsi (%)", ascending=False)
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.subheader("Komposisi Ransum Optimal")
                        st.dataframe(hasil_df)
                        
                        # Download link
                        st.markdown(get_download_link(hasil_df, "hasil_ransum_optimal.csv", 
                                                 "💾 Download hasil optimasi (CSV)"), unsafe_allow_html=True)
                    
                    with col2:
                        st.subheader("Biaya Ransum")
                        st.metric("Total Biaya per Hari", f"Rp {total_cost:,.0f}")  # type: ignore
                        st.metric("Biaya per kg Ransum", f"Rp {total_cost/konsumsi_bk:,.0f}")  # type: ignore
                        
                        # Calculate ratios
                        hijauan_idx = [i for i, nama in enumerate(nama_bahan_list) 
                                      if any(h in nama for h in hijauan_list)]
                        konsentrat_idx = [i for i in range(len(nama_bahan_list)) if i not in hijauan_idx]
                        
                        hijauan_pct = sum(proporsi_normalized[i] for i in hijauan_idx) * 100
                        konsentrat_pct = sum(proporsi_normalized[i] for i in konsentrat_idx) * 100
                        
                        st.metric("Rasio Hijauan : Konsentrat", 
                              f"{hijauan_pct:.1f}% : {konsentrat_pct:.1f}%")
                    
                    # Visualize the results
                    st.subheader("Visualisasi Komposisi Ransum")
                    
                    # Convert percentage strings back to float for plotting
                    plot_df = hasil_df.copy()
                    plot_df["Proporsi (%)"] = [float(p.replace("%", "")) for p in plot_df["Proporsi (%)"]]
                    
                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
                    
                    # Pie chart for composition
                    ax1.pie(
                        plot_df["Proporsi (%)"], 
                        labels=plot_df["Nama Bahan"],
                        autopct='%1.1f%%',
                        startangle=90,
                        wedgeprops={'edgecolor': 'white'}
                    )
                    ax1.set_title('Proporsi Bahan Pakan (%)', fontsize=14)
                    
                    # Bar chart for cost
                    costs = [float(cost.replace(",", "")) for cost in plot_df["Biaya (Rp/hari)"]]
                    ax2.barh(plot_df["Nama Bahan"], costs)
                    ax2.set_title('Biaya per Bahan (Rp/hari)', fontsize=14)
                    ax2.set_xlabel('Rupiah (Rp)')
                    ax2.grid(axis='x', linestyle='--', alpha=0.7)
                    
                    # Show costs on bars
                    for i, v in enumerate(costs):
                        ax2.text(v + 0.5, i, f"Rp {v:,.0f}", va='center')
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Calculate nutritional composition of the optimal ration
                    st.subheader("Analisis Nutrisi Ransum Optimal")
                    
                    # Calculate the nutrition provided by the optimal ration
                    nutrisi_optimal = {}
                    for nutrisi in ['PK (%BK)', 'SK (%BK)', 'NDF (%BK)', 'ADF (%BK)', 'Ca (g)', 'P (g)', 
                                  'PDIA (g)', 'PDI (g)', 'ME (kkal)', 'NEl (kkal)', 'TDN (%)', 
                                  'NEl (Mkal)', 'RUP (%)', 'RDP (%)']:
                        nutrient_values = np.array([bahan_pakan[nama][nutrisi] for nama in nama_bahan_list])
                        nutrisi_optimal[nutrisi] = np.sum(proporsi_normalized * nutrient_values)
                    
                    # Create DataFrame to compare target vs achieved
                    nutrisi_compare = pd.DataFrame({
                        'Nutrisi': list(nutrisi_optimal.keys()),
                        'Target': [kebutuhan_nutrisi.get(nutrisi, "N/A") for nutrisi in nutrisi_optimal.keys()],
                        'Hasil Ransum': [nutrisi_optimal[nutrisi] for nutrisi in nutrisi_optimal.keys()],
                        'Status': [
                            "✅ Terpenuhi" if nutrisi in ['PK (%BK)', 'Ca (g)', 'P (g)', 'PDIA (g)', 'PDI (g)', 
                                                        'ME (kkal)', 'NEl (kkal)', 'TDN (%)', 'NEl (Mkal)', 
                                                        'RUP (%)', 'RDP (%)'] and 
                                         nutrisi_optimal[nutrisi] >= kebutuhan_nutrisi.get(nutrisi, 0)
                            else "✅ Terpenuhi" if nutrisi in ['SK (%BK)', 'NDF (%BK)', 'ADF (%BK)'] and
                                                 nutrisi_optimal[nutrisi] <= kebutuhan_nutrisi.get(nutrisi, 100)
                            else "❌ Tidak Terpenuhi"
                            for nutrisi in nutrisi_optimal.keys()
                        ]
                    })

                    # Format for display
                    nutrisi_compare['Target'] = nutrisi_compare['Target'].apply(
                        lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)
                    nutrisi_compare['Hasil Ransum'] = nutrisi_compare['Hasil Ransum'].apply(
                        lambda x: f"{x:.2f}")

                    # Display in a nice table
                    st.dataframe(nutrisi_compare, use_container_width=True)
                    
                    # Tambahkan kode ini setelah menampilkan tabel hasil optimasi dan sebelum st.markdown('</div>...')

                    # Calculate total cost
                    total_cost = np.sum(biaya_per_hari)

                    # Add PDF download option
                    pdf_buffer = create_pdf_report(
                        hasil_df, 
                        nutrisi_compare, 
                        fig, 
                        total_cost, 
                        konsumsi_bk, 
                        hijauan_pct, 
                        konsentrat_pct
                    )

                    # Display download links
                    download_col1, download_col2 = st.columns(2)
                    with download_col1:
                        st.markdown(get_download_link(hasil_df, "hasil_ransum_optimal.csv", 
                                                   "💾 Download hasil optimasi (CSV)"), unsafe_allow_html=True)
                    with download_col2:
                        st.markdown(get_pdf_download_link(pdf_buffer, "laporan_ransum_optimal.pdf", 
                                                      "📄 Download laporan lengkap (PDF)"), unsafe_allow_html=True)

                    st.markdown('</div>', unsafe_allow_html=True)

                    # Tambahkan fungsi baru untuk membuat PDF

                    def create_pdf_report(hasil_df, nutrisi_compare, fig, total_cost, konsumsi_bk, hijauan_pct, konsentrat_pct):
                        """Generate a PDF report of the feed optimization results"""
                        buffer = io.BytesIO()
                        
                        # Create the PDF document
                        doc = SimpleDocTemplate(
                            buffer,
                            pagesize=A4,
                            rightMargin=72,
                            leftMargin=72,
                            topMargin=72,
                            bottomMargin=72
                        )
                        
                        # Container for the 'Flowable' objects
                        elements = []
                        
                        # Styles
                        styles = getSampleStyleSheet()
                        title_style = styles['Heading1']
                        subtitle_style = styles['Heading2']
                        normal_style = styles['Normal']
                        
                        # Title
                        elements.append(Paragraph("Laporan Hasil Optimasi Ransum Sapi Perah", title_style))
                        elements.append(Spacer(1, 0.25*inch))
                        
                        # Date
                        from datetime import datetime
                        elements.append(Paragraph(f"Tanggal: {datetime.now().strftime('%d-%m-%Y %H:%M')}", normal_style))
                        elements.append(Spacer(1, 0.5*inch))
                        
                        # Biaya section
                        elements.append(Paragraph("Ringkasan Biaya:", subtitle_style))
                        elements.append(Spacer(1, 0.1*inch))
                        cost_data = [
                            ["Parameter", "Nilai"],
                            ["Total Biaya per Hari", f"Rp {total_cost:,.0f}"],
                            ["Biaya per kg Ransum", f"Rp {total_cost/konsumsi_bk:,.0f}"],
                            ["Rasio Hijauan : Konsentrat", f"{hijauan_pct:.1f}% : {konsentrat_pct:.1f}%"]
                        ]
                        cost_table = Table(cost_data, colWidths=[2.5*inch, 2.5*inch])
                        cost_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (1, 0), colors.lightblue),
                            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        elements.append(cost_table)
                        elements.append(Spacer(1, 0.5*inch))
                        
                        # Komposisi Ransum Section
                        elements.append(Paragraph("Komposisi Ransum Optimal:", subtitle_style))
                        elements.append(Spacer(1, 0.1*inch))
                        
                        # Convert dataframe to table data
                        table_data = [hasil_df.columns.tolist()]
                        for _, row in hasil_df.iterrows():
                            table_data.append(row.tolist())
                        
                        # Create table
                        table = Table(table_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1.5*inch])
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        elements.append(table)
                        elements.append(Spacer(1, 0.5*inch))
                        
                        # Save the figure to a temporary file
                        img_buf = io.BytesIO()
                        fig.savefig(img_buf, format='png', dpi=300, bbox_inches='tight')
                        img_buf.seek(0)
                        
                        # Add the figure to the PDF
                        img = Image(img_buf, width=7*inch, height=3.5*inch)
                        elements.append(img)
                        elements.append(Spacer(1, 0.5*inch))
                        
                        # Analisis Nutrisi Section
                        elements.append(Paragraph("Analisis Nutrisi Ransum:", subtitle_style))
                        elements.append(Spacer(1, 0.1*inch))
                        
                        # Convert nutrisi_compare dataframe to table data
                        nutrisi_data = [nutrisi_compare.columns.tolist()]
                        for _, row in nutrisi_compare.iterrows():
                            nutrisi_data.append(row.tolist())
                        
                        # Create table
                        nutrisi_table = Table(nutrisi_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                        nutrisi_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        elements.append(nutrisi_table)
                        
                        # Disclaimer
                        elements.append(Spacer(1, 0.5*inch))
                        disclaimer_style = ParagraphStyle(
                            'Disclaimer',
                            parent=normal_style,
                            fontSize=8,
                            textColor=colors.gray
                        )
                        elements.append(Paragraph("Disclaimer: Hasil optimasi ini merupakan panduan dan dapat berbeda tergantung pada kondisi aktual. Konsultasikan dengan ahli nutrisi ternak untuk implementasi praktis.", disclaimer_style))
                        
                        # Build the PDF
                        doc.build(elements)
                        
                        # Get the PDF from the buffer
                        buffer.seek(0)
                        return buffer

                    def get_pdf_download_link(pdf_bytes, filename, text):
                        """Generate download link for PDF file"""
                        b64 = base64.b64encode(pdf_bytes.read()).decode()
                        href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">{text}</a>'
                        return href

# Tambahkan setelah bagian "Analisis Nutrisi Ransum Optimal"
if st.session_state.get('optimize_mode') == "Relaksasi Otomatis" and st.session_state.get('optimization_performed', False):
    st.subheader("Informasi Proses Relaksasi Otomatis")
    
    critical_nutrients = st.session_state.get('critical_nutrients', [])
    relax_attempts = st.session_state.get('relax_attempts', {})
    
    if critical_nutrients:
        st.write("#### Nutrisi Yang Diberi Relaksasi:")
        for nutrisi in critical_nutrients:
            st.write(f"- {nutrisi}")
    
    if relax_attempts:
        # Create visualization of relaxation attempts
        relax_levels = list(relax_attempts.keys())
        success_status = list(relax_attempts.values())
        
        fig, ax = plt.subplots(figsize=(10, 3))
        colors = ['#e74c3c' if not success else '#2ecc71' for success in success_status]
        
        ax.bar(relax_levels, [1] * len(relax_levels), color=colors)
        ax.set_xlabel('Tingkat Relaksasi (%)')
        ax.set_yticks([])
        ax.set_title('Riwayat Percobaan Relaksasi')

        # Add labels for success/failure
        for i, level in enumerate(relax_levels):
            label = "✓" if success_status[i] else "✗"
            ax.text(level, 0.5, label, ha='center', va='center', fontsize=14,
                     color='white', fontweight='bold')

        st.pyplot(fig)

        # Show final relaxation level used
        successful_levels = [level for level, success in relax_attempts.items() if success]
        if successful_levels:
            final_level = successful_levels[0]
            st.success(
                f"Solusi berhasil ditemukan pada tingkat relaksasi {final_level}%")
````

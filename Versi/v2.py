import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Set page config first (must be the first Streamlit command)
st.set_page_config(
    page_title="Software Ransum Sapi Perah",
    page_icon="🐄",
    layout="wide"
)

# Data kebutuhan nutrisi sapi perah
data = {
    'Berat Badan (kg)': [350, 350, 350, 350, 450, 450, 450, 450, 600, 600, 600, 600],
    'Produksi Susu (L/hari)': [15, 20, 25, 30, 15, 20, 25, 30, 15, 20, 25, 30],
    'PK (%BK)': [16.0, 0.7, 17.0, 0.7, 15.0, 0.6, 16.0, 0.7, 0.6, 15.0, 0.6, 16.0],
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
    'NEl (Mkal)': [15.0, 16.0, 17.0, 18.0, 0.6, 0.7, 0.7, 0.8, 16.0, 17.0, 18.0, 19.0],
    'RUP (%)': [35.0, 37.0, 38.0, 40.0, 34.0, 36.0, 37.0, 39.0, 33.0, 35.0, 36.0, 38.0],
    'RDP (%)': [65.0, 63.0, 62.0, 60.0, 66.0, 64.0, 63.0, 61.0, 67.0, 65.0, 64.0, 62.0]
}

df = pd.DataFrame(data)

# Bahan pakan data definition
bahan_pakan_data = {
    'Nama Bahan': [
        'Biji barley (Hordeum vulgare L.)',
        'Biji jagung (Zea mays L.)',
        'Bungkil jagung—proses ekstrusi',
        'Bungkil jagung—proses pengepresan',
        'Bungkil jagung berkadar air tinggi',
        'Biji millet Mutiara',
        'Biji millet proso',
        'Gandum',
        'Biji gandum',
        'Bungkil biji gandum—proses pengepresan',
        'Bekatul',
        'Dedak',
        'Menir beras',
        'Biji gandum hitam',
        'Biji sorgum',
        'Biji triticale',
        'Biji gandum durum',
        'Biji gandum lunak',
        'Corn gluten feed',
        'Corn gluten meal',
        'Bungkil kelapa',
        'Bungkil inti sawit',
        'Bungkil kedelai',
        'Kleci, kulit biji kedelai',
        'Rumput Gajah',
        'Rumput Odot',
        'Rumput Raja', 
        'Tebon Jagung',
        'Tebon Jagung dengan Bijinya',
        'Alfalfa Hay',
        'Jerami Kacang Tanah'
    ],
    'BK (%)': [87.2, 86.3, 86.3, 86.3, 67, 89.6, 90.6, 85.7, 87.6, 87.6, 88, 88, 87.6, 86.7, 87.8, 86.8, 87.8, 86.9, 87.8, 90.9, 90.5, 90.6, 93.2, 88.9, 20, 25, 18, 30, 35, 88, 86],
    'PK (%BK)': [11.3, 8.8, 8.8, 8.8, 9.2, 12.5, 14.2, 12.8, 10.8, 10.8, 10.5, 8.5, 9.2, 9.8, 10.6, 11.5, 16.4, 12.6, 21.6, 67.8, 23.4, 18.3, 47, 12.8, 8.05, 11, 9, 6, 9, 18, 12],
    'SK (%BK)': [5.4, 2.6, 2.6, 2.6, 2.6, 3.2, 7.4, 4.5, 13.1, 13.1, 2.4, 11, 0.6, 2.3, 2.8, 2.9, 3, 2.7, 9, 1.5, 13.6, 20.7, 6.4, 39.1, 30, 28, 32, 35, 25, 30, 35],
    'NDF (%BK)': [21.5, 12.4, 12.4, 12.4, 12.4, 17.2, 23.2, 12.8, 35.7, 35.7, 7.5, 26.4, 5.7, 14.8, 11.1, 15, 15.9, 14.7, 39.9, 4, 53.6, 72.9, 13.6, 65.3, 65, 60, 68, 70, 55, 42, 60],
    'ADF (%BK)': [6.5, 3.1, 3.1, 3.1, 3.1, 4.5, 12, 5.3, 16.3, 16.3, 2.9, 13.5, 1.8, 3.3, 4.3, 3.8, 4.2, 3.8, 10.6, 1.4, 27.5, 44, 8, 46.5, 35, 32, 38, 40, 30, 32, 38],
    'Ca (g)': [0.8, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 1, 1.1, 1.1, 0.5, 0.7, 0.4, 0.7, 0.3, 0.7, 0.8, 0.7, 1.6, 0.3, 1, 3, 3.7, 5.6, 4.5, 5.0, 4.2, 3.8, 4.0, 15.0, 7.0],
    'P (g)': [3.9, 2.9, 2.9, 2.9, 3.1, 3.3, 3, 3.4, 3.6, 3.6, 3.6, 2.8, 2.4, 3.5, 3.5, 3.8, 3.9, 3.6, 9.8, 4.1, 5.8, 6.1, 6.9, 1.7, 2.8, 3.0, 2.5, 2.2, 2.5, 2.8, 3.5],
    'PDIA (g)': [30, 42, 52, 52, 24, 56, 26, 25, 20, 24, 28, 20, 25, 20, 47, 24, 36, 28, 53, 424, 99, 79, 154, 38, 20, 22, 19, 15, 25, 40, 30],
    'PDI (g)': [87, 95, 108, 111, 80, 108, 86, 83, 73, 77, 80, 66, 81, 81, 98, 85, 96, 89, 109, 471, 152, 129, 208, 95, 60, 65, 58, 50, 70, 95, 80],
    'ME (kkal)': [2960, 3340, 3340, 3340, 3320, 3400, 3440, 3080, 2740, 2740, 3160, 2400, 3200, 3120, 3180, 3100, 3160, 3130, 2980, 4450, 2750, 2390, 3580, 2830, 2000, 2200, 1900, 1800, 2500, 2700, 2300],
    'NEl (kkal)': [1950, 2270, 2270, 2270, 2260, 2310, 2330, 2040, 1750, 1750, 2120, 1520, 2170, 2100, 2130, 2080, 2120, 2110, 1960, 3050, 1770, 1500, 2400, 1860, 1200, 1300, 1100, 1000, 1400, 1500, 1300],
    'TDN (%)': [82.2, 89.3, 89.3, 89.3, 88.9, 86.1, 82.9, 85.6, 79.6, 79.6, 88.6, 72.5, 89.4, 84.4, 87.3, 84.1, 84.3, 84.5, 75.3, 94.1, 67, 48.1, 89, 67, 55, 58, 52, 50, 65, 70, 60],
    'NEl (Mkal)': [1.84, 2.02, 2.1, 2.1, 2.01, 1.98, 1.91, 1.95, 1.78, 1.78, 2.01, 1.55, 2.02, 1.89, 1.97, 1.9, 1.95, 1.92, 1.74, 2.7, 1.53, 0.97, 2.41, 1.44, 1.02, 1.03, 1.01, 1.00, 1.04, 1.05, 1.03],
    'RUP (%)': [27, 53, 49, 85, 25, 57, 18, 18, 18, 20, 28, 28, 28, 21, 57, 20, 22, 22, 25, 70, 47, 54, 34, 43, 20, 22, 18, 15, 25, 30, 25],
    'RDP (%)': [73, 47, 51, 15, 75, 43, 82, 82, 82, 80, 72, 72, 72, 79, 43, 80, 78, 78, 75, 30, 53, 46, 66, 57, 80, 78, 82, 85, 75, 70, 75],
    'Harga (Rp/kg)': [4500, 4000, 4200, 4100, 3800, 4300, 4200, 4500, 4300, 4200, 3000, 2500, 3000, 4400, 4000, 4500, 4600, 4400, 5000, 7000, 3500, 3000, 8000, 2500, 1000, 1200, 1000, 800, 1000, 5000, 1500]
}

# Create DataFrame
bahan_pakan_df = pd.DataFrame(bahan_pakan_data)

# Define helper functions
def hitung_kebutuhan(berat_badan, produksi_susu):
    kebutuhan = df[(df['Berat Badan (kg)'] == berat_badan) & (df['Produksi Susu (L/hari)'] == produksi_susu)]
    if not kebutuhan.empty:
        return kebutuhan.iloc[0].to_dict()
    else:
        return None

# Dict of nutrient descriptions
nutrient_descriptions = {
    'PK (%BK)': 'Protein Kasar berdasarkan Bahan Kering',
    'SK (%BK)': 'Serat Kasar berdasarkan Bahan Kering',
    'NDF (%BK)': 'Neutral Detergent Fiber',
    'ADF (%BK)': 'Acid Detergent Fiber',
    'Ca (g)': 'Kebutuhan Kalsium',
    'P (g)': 'Kebutuhan Fosfor',
    'PDIA (g)': 'Protein yang dicerna di usus kecil dari protein tidak terdegradasi di rumen (PDIA). Nilai ini menunjukkan jumlah protein yang dapat langsung dimanfaatkan oleh sapi.',
    'PDI (g)': 'Protein yang tersedia untuk produksi susu atau pertumbuhan (PDI). Merupakan total protein yang dapat dimanfaatkan oleh sapi setelah proses pencernaan.',
    'ME (kkal)': 'Metabolizable Energy (ME). Energi yang tersedia untuk metabolisme setelah dikurangi energi yang hilang melalui feses, urin, dan gas.',
    'NEl (kkal)': 'Net Energy for Lactation (NEl). Energi bersih yang tersedia khusus untuk produksi susu.',
    'TDN (%)': 'Total Digestible Nutrients (TDN). Ukuran nilai energi pakan yang menunjukkan total nutrisi yang dapat dicerna.',
    'NEl (Mkal)': 'Net Energy for Lactation dalam MegaKalori. Satuan alternatif untuk energi bersih laktasi.',
    'RUP (%)': 'Rumen Undegraded Protein - protein yang tidak terdegradasi di rumen dan langsung masuk ke usus halus. Nilai dapat bervariasi berdasarkan tingkat kecernaan (25% atau 50%).',
    'RDP (%)': 'Rumen Degraded Protein - protein yang mengalami degradasi di rumen dan digunakan oleh mikroba untuk sintesis protein mikroba.'
}

# Now add custom CSS
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
    }
    .stProgress .st-bo {
        background-color: #f9f9f9;
    }
    .metric-card {
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .chart-container {
        background-color: f9f9f9;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .st-emotion-cache-16idsys p {
        font-size: 18px;
        font-weight: 600;
        color: #212121;
    }
</style>
""", unsafe_allow_html=True)

# Main title with emoji and description
# Replace your current page header with this version
st.markdown("""
<div style="text-align: center; padding: 1.5rem 0; margin-bottom: 2rem; background-color: #e8f5e9; border-radius: 10px; border: 1px solid #81c784;">
    <h1 style="color: #1b5e20; margin-bottom: 0.5rem;">🐄 Software Ransum Sapi Perah</h1>
    <p style="font-size: 1.2rem; color: #2e7d32; font-weight: 600;">Aplikasi Formulasi Ransum untuk Optimasi Nutrisi Sapi Perah</p>
</div>
<div style="background-color: #f9f9f9; border: 1px solid #e0e0e0; padding: 1.2rem; border-radius: 8px; margin-bottom: 2rem;">
    <p style="font-size: 1.1rem; color: #212121; margin-bottom: 0;">Membantu peternak menyusun ransum yang seimbang dan ekonomis berdasarkan kebutuhan nutrisi sapi perah. Aplikasi ini menggunakan data nutrisi standar dan dapat disesuaikan dengan kondisi lokal.</p>
</div>
""", unsafe_allow_html=True)

# Create tabs for better organization
tab1, tab2, tab3 = st.tabs(["📊 Input & Kebutuhan", "🌾 Formulasi Ransum", "📈 Analisis & Rekomendasi"])

with tab1:
    # Input section with improved layout
    st.markdown("### 📝 Data Sapi")
    
    col1, col2 = st.columns(2)
    with col1:
        berat_badan = st.number_input('Berat Badan Sapi (kg)', 
                                     min_value=300, max_value=800, 
                                     value=450, step=50)
    with col2:
        produksi_susu = st.number_input('Produksi Susu Harian (L)',
                                       min_value=0, max_value=40,
                                       value=20, step=5)

    # Calculate and display nutrition requirements
    kebutuhan = hitung_kebutuhan(berat_badan, produksi_susu)
    if kebutuhan:
        st.subheader('Kebutuhan Nutrisi Sapi Perah:')
        # Display nutrition requirements in two columns
        col1, col2 = st.columns(2)
        nutrients = list(kebutuhan.items())
        mid_point = len(nutrients) // 2
        with col1:
            for key, value in nutrients[:mid_point]:
                if key in nutrient_descriptions:
                    with st.expander(f"{key}: {value:.2f}"):
                        st.info(nutrient_descriptions[key])
        with col2:
            for key, value in nutrients[mid_point:]:
                if key in nutrient_descriptions:
                    with st.expander(f"{key}: {value:.2f}"):
                        st.info(nutrient_descriptions[key])
    else:
        st.write("Data kebutuhan nutrisi tidak ditemukan untuk kombinasi berat badan dan produksi susu yang diberikan.")

with tab2:
    st.markdown("### 🌾 Pemilihan Bahan Pakan")
    
    # Add better feed category display with improved styling and organization
    st.markdown("""
    <div style="display: flex; gap: 1.5rem; margin-bottom: 1.5rem; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 250px; background-color: #e8f5e9; padding: 1.2rem; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); border: 1px solid #81c784;">
            <h4 style="color: #2e7d32; margin-top: 0; border-bottom: 2px solid #81c784; padding-bottom: 8px;">🌿 Hijauan</h4>
            <p style="color: #1b5e20; margin-bottom: 10px; font-weight: 500;">Sumber serat dan nutrisi dasar</p>
            <ul style="list-style-type: none; padding-left: 0; color: #212121;">
                <li style="margin-bottom: 8px; display: flex; align-items: center;">
                    <span style="background-color: #c8e6c9; width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-right: 8px;">🌿</span>
                    <span>Rumput Gajah - tinggi serat</span>
                </li>
                <li style="margin-bottom: 8px; display: flex; align-items: center;">
                    <span style="background-color: #c8e6c9; width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-right: 8px;">🌿</span>
                    <span>Rumput Odot - lebih protein</span>
                </li>
                <li style="margin-bottom: 8px; display: flex; align-items: center;">
                    <span style="background-color: #c8e6c9; width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-right: 8px;">🌿</span>
                    <span>Rumput Raja - produksi tinggi</span>
                </li>
                <li style="margin-bottom: 0; display: flex; align-items: center;">
                    <span style="background-color: #c8e6c9; width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-right: 8px;">🌿</span>
                    <span>Alfalfa Hay - protein tinggi</span>
                </li>
            </ul>
        </div>
        <div style="flex: 1; min-width: 250px; background-color: #fff8e1; padding: 1.2rem; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); border: 1px solid #ffcc80;">
            <h4 style="color: #ef6c00; margin-top: 0; border-bottom: 2px solid #ffcc80; padding-bottom: 8px;">🌾 Konsentrat</h4>
            <p style="color: #e65100; margin-bottom: 10px; font-weight: 500;">Sumber energi dan protein</p>
            <ul style="list-style-type: none; padding-left: 0; color: #212121;">
                <li style="margin-bottom: 8px; display: flex; align-items: center;">
                    <span style="background-color: #ffecb3; width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-right: 8px;">🌾</span>
                    <span>Dedak - sumber energi ekonomis</span>
                </li>
                <li style="margin-bottom: 8px; display: flex; align-items: center;">
                    <span style="background-color: #ffecb3; width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-right: 8px;">🌾</span>
                    <span>Bungkil Kedelai - protein tinggi</span>
                </li>
                <li style="margin-bottom: 8px; display: flex; align-items: center;">
                    <span style="background-color: #ffecb3; width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-right: 8px;">🌾</span>
                    <span>Jagung - energi tinggi</span>
                </li>
                <li style="margin-bottom: 0; display: flex; align-items: center;">
                    <span style="background-color: #ffecb3; width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-right: 8px;">🌾</span>
                    <span>Bekatul - nutrisi seimbang</span>
                </li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add search and filter functionality
    col1, col2 = st.columns([2, 1])
    with col1:
        search_term = st.text_input("🔍 Cari Bahan Pakan:", placeholder="Ketik nama bahan...")
    with col2:
        category_filter = st.selectbox("Filter Kategori:", 
                                     ["Semua Bahan", "Hijauan", "Konsentrat", "Tinggi Protein", "Tinggi Energi"])
    
    # Filter bahan pakan based on search and category
    filtered_feeds = bahan_pakan_df['Nama Bahan'].tolist()
    
    if search_term:
        filtered_feeds = [feed for feed in filtered_feeds if search_term.lower() in feed.lower()]
    
    if category_filter == "Hijauan":
        hijauan_keywords = ["rumput", "tebon", "jerami", "hay", "alfalfa", "silase"]
        filtered_feeds = [feed for feed in filtered_feeds if any(keyword in feed.lower() for keyword in hijauan_keywords)]
    elif category_filter == "Konsentrat":
        filtered_feeds = [feed for feed in filtered_feeds if not any(keyword in feed.lower() 
                                                                for keyword in ["rumput", "tebon", "jerami", "hay", "alfalfa"])]
    elif category_filter == "Tinggi Protein":
        high_protein_feeds = bahan_pakan_df[bahan_pakan_df['PK (%BK)'] > 15]['Nama Bahan'].tolist()
        filtered_feeds = [feed for feed in filtered_feeds if feed in high_protein_feeds]
    elif category_filter == "Tinggi Energi":
        high_energy_feeds = bahan_pakan_df[bahan_pakan_df['TDN (%)'] > 75]['Nama Bahan'].tolist()
        filtered_feeds = [feed for feed in filtered_feeds if feed in high_energy_feeds]
    
    # Add quick pick buttons for common combinations
    st.markdown("#### Rekomendasi Kombinasi Cepat:")
    quick_pick_cols = st.columns(3)
    with quick_pick_cols[0]:
        if st.button("🐄 Kombinasi Dasar", use_container_width=True):
            selected_feeds = ['Rumput Gajah', 'Dedak', 'Bungkil kedelai']
    with quick_pick_cols[1]:
        if st.button("🥛 Laktasi Tinggi", use_container_width=True):
            selected_feeds = ['Rumput Odot', 'Bungkil kedelai', 'Biji jagung (Zea mays L.)', 'Bekatul']
    with quick_pick_cols[2]:
        if st.button("💰 Ekonomis", use_container_width=True):
            selected_feeds = ['Rumput Gajah', 'Dedak', 'Tebon Jagung']
    
    # Improved feed selection interface
    selected_feeds = st.multiselect(
        '📋 Pilih Bahan Pakan:',
        filtered_feeds,
        default=selected_feeds if 'selected_feeds' in locals() else [],
        help="Pilih minimal satu hijauan dan satu konsentrat"
    )
    
    # Initialize total_proportion
    total_proportion = 0
    
    # Show selected feeds and input proportions with improved UI
    if selected_feeds:
        # Create a container with styling
        st.markdown("""
        <div style="background-color: #f5f5f5; border-radius: 10px; padding: 1px 20px 10px 20px; margin: 15px 0;">
            <h4 style="color: #2e7d32; border-bottom: 1px solid #e0e0e0; padding-bottom: 8px;">✅ Bahan Pakan Terpilih</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Display key nutritional parameters for selected feeds
        selected_data = bahan_pakan_df[bahan_pakan_df['Nama Bahan'].isin(selected_feeds)]
        
        # Add visual indicators for key nutrients
        display_cols = ['Nama Bahan', 'PK (%BK)', 'TDN (%)', 'NDF (%BK)', 'Harga (Rp/kg)']
        st.dataframe(selected_data[display_cols], use_container_width=True)
        
        # Add input for proportions with better organization
        st.markdown("""
        <div style="background-color: #e8f5e9; border-radius: 10px; padding: 1px 20px 10px 20px; margin: 20px 0;">
            <h4 style="color: #2e7d32; border-bottom: 1px solid #c8e6c9; padding-bottom: 8px;">⚖️ Proporsi Bahan Pakan (%)</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Create columns for better organization of sliders
        proportions = {}
        
        # Create two columns for better layout
        for i, feed in enumerate(selected_feeds):
            col1, col2 = st.columns([3, 1])
            with col1:
                proportions[feed] = st.slider(f'{feed}', 0, 100, 
                                            int(100/len(selected_feeds)) if len(selected_feeds) <= 4 else 0,
                                            key=f"prop_{feed}")
            with col2:
                st.markdown(f"<div style='padding-top:25px; text-align:center; font-weight:bold; font-size:18px;'>{proportions[feed]}%</div>", unsafe_allow_html=True)
        
        # Validate proportions with progress bar
        total_proportion = sum(proportions.values())
        progress_color = "#4CAF50" if total_proportion == 100 else "#FF9800" if total_proportion < 100 else "#F44336"
        
        st.markdown(f"""
        <div style="margin-top: 20px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="font-weight: 600; color: #212121;">Total Proporsi:</span>
                <span style="font-weight: 700; color: {progress_color};">{total_proportion}%</span>
            </div>
            <div style="background-color: #e0e0e0; border-radius: 10px; height: 10px; width: 100%;">
                <div style="background-color: {progress_color}; width: {min(total_proportion, 100)}%; height: 10px; border-radius: 10px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if total_proportion != 100:
            if total_proportion < 100:
                st.warning(f'⚠️ Total proporsi kurang dari 100% (saat ini: {total_proportion}%). Perlu ditambah: {100-total_proportion}%')
            else:
                st.error(f'❌ Total proporsi melebihi 100% (saat ini: {total_proportion}%). Perlu dikurangi: {total_proportion-100}%')
        else:
            st.success('✅ Total proporsi: 100% - Formulasi lengkap')
            
            # Add button to distribute proportions evenly
            if st.button("↔️ Distribusi Proporsi Merata", use_container_width=True):
                even_value = 100 // len(selected_feeds)
                remainder = 100 % len(selected_feeds)
                for i, feed in enumerate(selected_feeds):
                    proportions[feed] = even_value + (1 if i < remainder else 0)
                st.rerun()
                
            # Calculate mixed feed composition
            mixed_feed_composition = {
                'PK (%BK)': 0,
                'SK (%BK)': 0,
                'NDF (%BK)': 0,
                'ADF (%BK)': 0,
                'Ca (g)': 0,
                'P (g)': 0,
                'PDIA (g)': 0,
                'PDI (g)': 0,
                'ME (kkal)': 0,
                'NEl (kkal)': 0,
                'TDN (%)': 0,
                'NEl (Mkal)': 0,
                'RUP (%)': 0,
                'RDP (%)': 0
            }
            
            # Calculate weighted average for each nutrient
            for feed, proportion in proportions.items():
                feed_data = bahan_pakan_df[bahan_pakan_df['Nama Bahan'] == feed].iloc[0]
                for nutrient in mixed_feed_composition.keys():
                    mixed_feed_composition[nutrient] += (feed_data[nutrient] * proportion / 100)
            
            # Calculate total cost
            total_cost = sum(bahan_pakan_df[bahan_pakan_df['Nama Bahan'] == feed].iloc[0]['Harga (Rp/kg)'] * proportion / 100 
                         for feed, proportion in proportions.items())
                
            # Show cost calculation
            st.markdown("""
            <div style="background-color: #f5f5f5; border-radius: 10px; padding: 15px; margin-top: 20px; color: black;">
                <h4 style="color: #1b5e20; margin-top: 0; margin-bottom: 10px;">💰 Estimasi Biaya Ransum</h4>
                <p style="margin-bottom: 0; color: black;">Harga rata-rata per kg bahan kering:</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="background-color: #e8f5e9; border-radius: 10px; padding: 15px; margin-top: 10px; text-align: center;">
                <span style="font-size: 24px; font-weight: 700; color: #2e7d32;">Rp {total_cost:,.0f}</span>
                <span style="font-size: 16px; color: #757575;"> / kg</span>
            </div>
            """, unsafe_allow_html=True)

with tab3:
    st.markdown("### 📈 Analisis & Rekomendasi")
    
    # First check if kebutuhan is defined and not None
    if 'kebutuhan' not in locals() or kebutuhan is None:
        st.warning("⚠️ Kembali ke tab pertama untuk mengatur data sapi dan mendapatkan kebutuhan nutrisi.")
    # Then check if proportions add up to 100%
    elif 'total_proportion' not in locals() or total_proportion != 100:
        st.info("Complete the feed selection in the 'Formulasi Ransum' tab first, ensuring total proportion equals 100%.")
    else:
        st.subheader('Analisis Nutrisi Ransum')
    
        # Create three columns for organized display
        comp_col, req_col, status_col = st.columns(3)
        
        # Setup analysis data structure
        analysis_data = {
            'Nutrisi': [],
            'Kandungan': [],
            'Kebutuhan': [],
            'Status': [],
            'Perbedaan (%)': []
        }
        
        # Calculate and organize analysis data
        for nutrient, value in mixed_feed_composition.items():
            if nutrient in kebutuhan:
                req = kebutuhan[nutrient]
                diff_percent = ((value - req) / req) * 100
                
                analysis_data['Nutrisi'].append(nutrient)
                analysis_data['Kandungan'].append(f"{value:.2f}")
                analysis_data['Kebutuhan'].append(f"{req:.2f}")
                
                # Determine status with tolerance level
                if abs(diff_percent) <= 10:
                    status = "✅ Sesuai"
                elif diff_percent > 0:
                    status = "⚠️ Berlebih"
                else:
                    status = "❌ Kurang"
                
                analysis_data['Status'].append(status)
                analysis_data['Perbedaan (%)'].append(f"{diff_percent:+.1f}")
        
        # Only continue if we have analysis data
        if analysis_data['Nutrisi']:
            # Convert to DataFrame
            analysis_df = pd.DataFrame(analysis_data)
            
            # Apply styling for better visualization
            def style_status(val):
                if '✅' in val:
                    return 'background-color: #90EE90'
                elif '⚠️' in val:
                    return 'background-color: #FFD700'
                elif '❌' in val:
                    return 'background-color: #FFB6C1'
                return ''
            
            # Display styled analysis table
            styled_df = analysis_df.style.apply(lambda x: [''] * len(x) if x.name != 'Status' 
                                              else [style_status(v) for v in x], axis=0)
            st.dataframe(styled_df, use_container_width=True)
            
            # Calculate summary statistics
            total_nutrients = len(analysis_df)
            balanced = sum(analysis_df['Status'].str.contains('✅'))
            excess = sum(analysis_df['Status'].str.contains('⚠️'))
            deficient = sum(analysis_df['Status'].str.contains('❌'))
            
            # Display summary metrics
            st.markdown("### Ringkasan Keseimbangan Nutrisi")
            metric_cols = st.columns(4)
            
            with metric_cols[0]:
                st.metric("Total Nutrisi", total_nutrients)
            with metric_cols[1]:
                st.metric("Seimbang", f"{balanced} ({balanced/total_nutrients*100:.1f}%)")
            with metric_cols[2]:
                st.metric("Berlebih", f"{excess} ({excess/total_nutrients*100:.1f}%)")
            with metric_cols[3]:
                st.metric("Kurang", f"{deficient} ({deficient/total_nutrients*100:.1f}%)")
            
            # Create visualization of nutrient status
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Prepare data for visualization
            nutrients = analysis_df['Nutrisi']
            differences = analysis_df['Perbedaan (%)'].astype(float)
            
            # Create bar chart
            bars = ax.bar(range(len(nutrients)), differences)
            
            # Color code bars
            for i, diff in enumerate(differences):
                if abs(diff) <= 10:
                    bars[i].set_color('green')
                elif diff > 0:
                    bars[i].set_color('gold')
                else:
                    bars[i].set_color('red')
            
            # Customize chart
            ax.set_xticks(range(len(nutrients)))
            ax.set_xticklabels(nutrients, rotation=45, ha='right')
            ax.set_ylabel('Perbedaan dari Kebutuhan (%)')
            ax.set_title('Analisis Keseimbangan Nutrisi')
            ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            ax.axhspan(-10, 10, color='green', alpha=0.1)
            
            # Add grid for better readability
            ax.grid(True, axis='y', linestyle='--', alpha=0.3)
            
            # Adjust layout and display
            plt.tight_layout()
            st.pyplot(fig)
    

# Replace the "Saran Optimasi" section with this improved version
if total_proportion == 100:
    # Get kebutuhan from session state if available, otherwise use local variable
    current_kebutuhan = st.session_state.get('kebutuhan', kebutuhan) if 'kebutuhan' in locals() else None
    
    # Only proceed with analysis if kebutuhan is available
    if current_kebutuhan is None:
        st.warning("⚠️ Kembali ke tab 'Input & Kebutuhan' terlebih dahulu untuk mengatur data sapi dan mendapatkan kebutuhan nutrisi.")
    else:
        # Add a section divider with styling
        st.markdown('<div style="height: 3px; background: linear-gradient(90deg, #1b5e20, #4caf50, #1b5e20); margin: 30px 0 20px 0; border-radius: 3px;"></div>', unsafe_allow_html=True)
        
        # Better styled header with icon
        st.markdown('<h3 style="color: #1b5e20; border-left: 5px solid #1b5e20; padding-left: 15px; margin-bottom: 20px;">🔄 Saran Optimasi Ransum</h3>', unsafe_allow_html=True)
        
        # Improved container for recommendations
        st.markdown("""
        <div style="background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 10px; padding: 20px; margin-bottom: 25px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <p style="font-size: 16px; font-weight: 600; color: #2e7d32; margin-bottom: 15px;">Rekomendasi ini membantu Anda menyempurnakan formula ransum berdasarkan hasil analisis nutrisi.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Set up columns for deficient and excess nutrients
        deficient_nutrients = []
        excess_nutrients = []
        
        for nutrient, value in mixed_feed_composition.items():
            if nutrient in current_kebutuhan:  # Use current_kebutuhan instead of kebutuhan
                req = current_kebutuhan[nutrient]
                diff_percent = ((value - req) / req) * 100
                if diff_percent < -10:
                    deficient_nutrients.append((nutrient, abs(diff_percent)))
                elif diff_percent > 10:
                    excess_nutrients.append((nutrient, diff_percent))
        
        # Create two columns for deficient and excess nutrients
        col1, col2 = st.columns(2)
        
        # Deficient nutrients in left column with better styling
        with col1:
            if deficient_nutrients:
                st.markdown("""
                <div style="background-color: #ffebee; border-left: 5px solid #c62828; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                    <h4 style="color: #c62828; margin-top: 0; margin-bottom: 10px;">❌ Nutrisi yang Perlu Ditingkatkan</h4>
                </div>
                """, unsafe_allow_html=True)
                
                for nutrient, diff in deficient_nutrients:
                    st.markdown(f"""
                    <div style="background-color: white; padding: 12px; border-radius: 5px; margin-bottom: 10px; border: 1px solid #ffcdd2;">
                        <p style="font-weight: 600; margin-bottom: 5px; color: #d32f2f;">{nutrient}: kurang {diff:.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Suggest ingredients high in this nutrient
                    st.markdown("<p style='font-weight: 600; font-size: 14px; margin: 8px 0;'>Bahan pakan kaya nutrient ini:</p>", unsafe_allow_html=True)
                    high_in_nutrient = bahan_pakan_df.nlargest(3, nutrient)[['Nama Bahan', nutrient]]
                    st.dataframe(high_in_nutrient, use_container_width=True)
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color: #e8f5e9; border-left: 5px solid #2e7d32; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                    <h4 style="color: #2e7d32; margin-top: 0; margin-bottom: 0;">✅ Semua nutrisi mencukupi</h4>
                </div>
                """, unsafe_allow_html=True)
        
        # Excess nutrients in right column with better styling
        with col2:
            if excess_nutrients:
                st.markdown("""
                <div style="background-color: #fff8e1; border-left: 5px solid #ff8f00; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                    <h4 style="color: #ff8f00; margin-top: 0; margin-bottom: 10px;">⚠️ Nutrisi yang Perlu Dikurangi</h4>
                </div>
                """, unsafe_allow_html=True)
                
                for nutrient, diff in excess_nutrients:
                    st.markdown(f"""
                    <div style="background-color: white; padding: 12px; border-radius: 5px; margin-bottom: 10px; border: 1px solid #ffe082;">
                        <p style="font-weight: 600; margin-bottom: 5px; color: #ff8f00;">{nutrient}: berlebih {diff:.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Suggest ingredients low in this nutrient
                    st.markdown("<p style='font-weight: 600; font-size: 14px; margin: 8px 0;'>Bahan pakan rendah nutrient ini:</p>", unsafe_allow_html=True)
                    low_in_nutrient = bahan_pakan_df.nsmallest(3, nutrient)[['Nama Bahan', nutrient]]
                    st.dataframe(low_in_nutrient, use_container_width=True)
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color: #e8f5e9; border-left: 5px solid #2e7d32; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                    <h4 style="color: #2e7d32; margin-top: 0; margin-bottom: 0;">✅ Tidak ada nutrisi berlebihan</h4>
                </div>
                """, unsafe_allow_html=True)
        
        # Add another divider
        st.markdown('<div style="height: 2px; background-color: #e0e0e0; margin: 25px 0;"></div>', unsafe_allow_html=True)
        
        # General Recommendations section
        st.markdown('<h4 style="color: #1b5e20; margin-bottom: 15px;">Rekomendasi Umum</h4>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="background-color: #e8f5e9; padding: 15px; border-radius: 8px; height: 100%; color: black;">
                <h5 style="color: #2e7d32; border-bottom: 1px solid #81c784; padding-bottom: 8px; margin-top: 0;">Prinsip Dasar</h5>
                <ul style="padding-left: 20px; margin-bottom: 0;">
                <li style="margin-bottom: 8px;">Pastikan rasio hijauan:konsentrat sesuai
                   <ul style="padding-left: 15px;">
                       <li>Sapi laktasi awal: 40:60</li>
                       <li>Sapi laktasi tengah: 50:50</li>
                       <li>Sapi laktasi akhir: 60:40</li>
                   </ul>
                </li>
                <li style="margin-bottom: 8px;">Perhatikan keseimbangan protein dan energi</li>
                <li style="margin-bottom: 8px;">Jaga kandungan serat (NDF & ADF) dalam batas aman</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px; height: 100%; color: black;">
                <h5 style="color: #2e7d32; border-bottom: 1px solid #81c784; padding-bottom: 8px; margin-top: 0;">Batasan Nutrisi Penting</h5>
                <ul style="padding-left: 20px; margin-bottom: 0;">
                    <li style="margin-bottom: 8px;"><b>NDF:</b> 28-35% dari BK</li>
                    <li style="margin-bottom: 8px;"><b>ADF:</b> 19-23% dari BK</li>
                    <li style="margin-bottom: 8px;"><b>SK:</b> 15-21% dari BK</li>
                    <li style="margin-bottom: 8px;"><b>PK:</b> sesuai produksi susu</li>
                    <li style="margin-bottom: 8px;"><b>TDN:</b> minimal 65%</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Add specific recommendations
        st.markdown('<h4 style="color: #1b5e20; margin-top: 25px; margin-bottom: 15px;">Rekomendasi Spesifik</h4>', unsafe_allow_html=True)
        
        # Calculate overall balance score
        balanced_nutrients = sum(1 for nutrient, value in mixed_feed_composition.items() 
                               if nutrient in current_kebutuhan and abs(((value - current_kebutuhan[nutrient]) / current_kebutuhan[nutrient]) * 100) <= 10)
        total_nutrients = sum(1 for nutrient in mixed_feed_composition.keys() if nutrient in current_kebutuhan)
        balance_score = (balanced_nutrients / total_nutrients) * 100
        
        # Display balance score with nice styling
        st.markdown(f"""
        <div style="background-color: #white; border: 1px solid #e0e0e0; border-radius: 10px; padding: 15px; margin-bottom: 20px; text-align: center;">
            <h5 style="margin-top: 0; margin-bottom: 5px; color: #1b5e20;">Skor Keseimbangan Ransum</h5>
            <div style="font-size: 28px; font-weight: 700; color: {'#2e7d32' if balance_score >= 70 else '#ff8f00' if balance_score >= 50 else '#c62828'}; margin: 5px 0;">
                {balance_score:.1f}%
            </div>
            <div style="font-size: 14px; color: #555;">
                {'Sangat Baik (>70%)' if balance_score >= 70 else 'Sedang (50-70%)' if balance_score >= 50 else 'Perlu Perbaikan (<50%)'}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Check protein to energy ratio
        if 'PK (%BK)' in mixed_feed_composition and 'TDN (%)' in mixed_feed_composition:
            pk_tdn_ratio = mixed_feed_composition['PK (%BK)'] / mixed_feed_composition['TDN (%)']
            
            if pk_tdn_ratio < 0.18:
                st.markdown("""
                <div style="background-color: #fff8e1; border-left: 5px solid #ff8f00; padding: 15px; border-radius: 5px; margin-bottom: 20px; color: black;">
                <h5 style="color: #ff8f00; margin-top: 0; margin-bottom: 10px;">⚠️ Rasio protein:energi terlalu rendah</h5>
                <p style="margin-bottom: 5px;">Pertimbangkan untuk:</p>
                <ul style="margin-bottom: 0;">
                    <li>Menambah sumber protein (misalnya bungkil kedelai)</li>
                    <li>Mengurangi sumber energi tinggi (misalnya jagung)</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
            elif pk_tdn_ratio > 0.22:
                st.markdown("""
                <div style="background-color: #fff8e1; border-left: 5px solid #ff8f00; padding: 15px; border-radius: 5px; margin-bottom: 20px; color: black;">
                <h5 style="color: #ff8f00; margin-top: 0; margin-bottom: 10px;">⚠️ Rasio protein:energi terlalu tinggi</h5>
                <p style="margin-bottom: 5px;">Pertimbangkan untuk:</p>
                <ul style="margin-bottom: 0;">
                    <li>Mengurangi sumber protein</li>
                    <li>Menambah sumber energi</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color: #e8f5e9; border-left: 5px solid #2e7d32; padding: 15px; border-radius: 5px; margin-bottom: 20px; color: black;">
                <h5 style="color: #2e7d32; margin-top: 0; margin-bottom: 0;">✅ Rasio protein:energi seimbang</h5>
                </div>
                """, unsafe_allow_html=True)

                # Add notes and disclaimers with improved styling
                st.markdown("""
                <div style="margin-top: 30px; border-top: 2px solid #e0e0e0; padding-top: 20px;">
                    <h4 style="color: #757575; margin-bottom: 15px;">Catatan Penting:</h4>
                    <ul style="list-style-type: disc; padding-left: 20px; color: #555;">
                        <li>Nilai nutrisi pada tabel merupakan perkiraan berdasarkan berbagai sumber literatur dan dapat bervariasi tergantung pada:
                            <ul style="list-style-type: circle; padding-left: 20px;">
                                <li>Kondisi pertumbuhan bahan pakan</li>
                                <li>Metode pengolahan</li>
                                <li>Penyimpanan dan penanganan</li>
                            </ul>
                        </li>
                    </ul>
                    
                    <h4 style="color: #757575; margin-top: 20px; margin-bottom: 15px;">Keterangan Tambahan:</h4>
                    <ul style="list-style-type: disc; padding-left: 20px; color: #555;">
                        <li><b>PDIA</b> (Protein Digestible in Intestine from feed): Protein yang dicerna di usus kecil dari protein tidak terdegradasi di rumen</li>
                        <li><b>PDI</b>: Protein yang tersedia untuk produksi susu atau pertumbuhan</li>
                        <li><b>ME</b>: Metabolizable Energy (Energi yang dapat dimetabolisme)</li>
                        <li><b>NEl</b>: Net Energy for Lactation (Energi bersih untuk laktasi)</li>
                        <li><b>TDN</b>: Total Digestible Nutrients (Total nutrisi yang dapat dicerna)</li>
                        <li><b>RUP</b>: Rumen Undegraded Protein dengan variasi tingkat kecernaan:
                            <ul style="list-style-type: circle; padding-left: 20px;">
                                <li>RUP 25% C: Tingkat kecernaan 25%</li>
                                <li>RUP 50% C: Tingkat kecernaan 50%</li>
                            </ul>
                        </li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

# Add this function somewhere before it's used
def create_pdf(berat_badan, produksi_susu, selected_feeds, proportions, mixed_feed_composition, analysis_df, 
              deficient_nutrients, excess_nutrients, balance_score, total_cost):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=1,
        spaceAfter=12
    )
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=10,
        spaceAfter=6
    )
    normal_style = styles["Normal"]
    
    # Title
    elements.append(Paragraph("Laporan Formulasi Ransum Sapi Perah", title_style))
    elements.append(Paragraph(f"Tanggal: {datetime.datetime.now().strftime('%d-%m-%Y')}", normal_style))
    elements.append(Spacer(1, 12))
    
    # Cow information
    elements.append(Paragraph("Informasi Sapi", heading_style))
    cow_data = [
        ["Berat Badan", f"{berat_badan} kg"],
        ["Produksi Susu", f"{produksi_susu} L/hari"]
    ]
    cow_table = Table(cow_data, colWidths=[200, 200])
    cow_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgreen),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(cow_table)
    elements.append(Spacer(1, 12))
    
    # Feed composition
    elements.append(Paragraph("Formula Ransum", heading_style))
    feed_data = [["Bahan Pakan", "Proporsi (%)"]]
    for feed, proportion in proportions.items():
        feed_data.append([feed, f"{proportion}"])
    feed_table = Table(feed_data, colWidths=[300, 100])
    feed_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(feed_table)
    elements.append(Spacer(1, 12))
    
    # Nutrition analysis
    elements.append(Paragraph("Analisis Nutrisi", heading_style))
    nutrition_data = [["Nutrisi", "Kandungan", "Kebutuhan", "Status", "Perbedaan (%)"]]
    
    # Convert the analysis_df to a list for the PDF
    for _, row in analysis_df.iterrows():
        nutrition_data.append([
            row['Nutrisi'], 
            row['Kandungan'],
            row['Kebutuhan'],
            row['Status'],
            row['Perbedaan (%)']
        ])
    
    nutrition_table = Table(nutrition_data, colWidths=[100, 90, 90, 90, 90])
    nutrition_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(nutrition_table)
    elements.append(Spacer(1, 12))
    
    # Recommendations summary
    elements.append(Paragraph("Rekomendasi", heading_style))
    elements.append(Paragraph(f"Skor Keseimbangan Ransum: {balance_score:.1f}%", normal_style))
    elements.append(Spacer(1, 6))
    
    if deficient_nutrients:
        elements.append(Paragraph("Nutrisi yang Perlu Ditingkatkan:", normal_style))
        for nutrient, diff in deficient_nutrients:
            elements.append(Paragraph(f"• {nutrient}: kurang {diff:.1f}%", normal_style))
        elements.append(Spacer(1, 6))
    
    if excess_nutrients:
        elements.append(Paragraph("Nutrisi yang Perlu Dikurangi:", normal_style))
        for nutrient, diff in excess_nutrients:
            elements.append(Paragraph(f"• {nutrient}: berlebih {diff:.1f}%", normal_style))
        elements.append(Spacer(1, 6))
    
    # Cost information
    elements.append(Paragraph("Informasi Biaya", heading_style))
    elements.append(Paragraph(f"Biaya per kg bahan kering: Rp {total_cost:,.0f}", normal_style))
    
    # Build the PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Add this where you want to show the download button (at the end of tab3, after all the analysis)
if 'total_proportion' in locals() and total_proportion == 100 and 'kebutuhan' in locals() and kebutuhan is not None:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Unduh Laporan")
    
    # Generate PDF when button is clicked
    if st.button("📄 Download Rangkuman PDF", use_container_width=True):
        try:
            # Create PDF
            pdf_buffer = create_pdf(
                berat_badan=berat_badan,
                produksi_susu=produksi_susu,
                selected_feeds=selected_feeds,
                proportions=proportions,
                mixed_feed_composition=mixed_feed_composition,
                analysis_df=analysis_df,
                deficient_nutrients=deficient_nutrients,
                excess_nutrients=excess_nutrients,
                balance_score=balance_score,
                total_cost=total_cost
            )
            
            # Provide download link
            b64_pdf = base64.b64encode(pdf_buffer.read()).decode()
            current_date = datetime.datetime.now().strftime("%Y%m%d")
            file_name = f"Formulasi_Ransum_Sapi_{current_date}.pdf"
            
            # Display download link
            href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{file_name}" style="display: inline-block; padding: 0.5rem 1rem; color: white; background-color: #2e7d32; text-decoration: none; font-weight: bold; border-radius: 4px; text-align: center; margin-top: 0.5rem;">⬇️ Klik untuk Mengunduh PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
            
            st.success("PDF berhasil dibuat! Klik link di atas untuk mengunduh.")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat membuat PDF: {str(e)}")

            # Footer with LinkedIn profile link and improved styling
st.markdown("""
<hr style="height:1px;border:none;color:#333;background-color:#333;margin-top:30px;margin-bottom:20px">
""", unsafe_allow_html=True)

# Get current year for footer
current_year = datetime.datetime.now().year

st.markdown(f"""
<div style="text-align:center; padding:15px; margin-top:10px; margin-bottom:20px">
    <p style="font-size:16px; color:#555">
        © {current_year} Developed by: 
        <a href="https://www.linkedin.com/in/galuh-adi-insani-1aa0a5105/" target="_blank" 
           style="text-decoration:none; color:#0077B5; font-weight:bold">
            <img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg" 
                 width="16" height="16" style="vertical-align:middle; margin-right:5px">
            Galuh Adi Insani
        </a> 
        with <span style="color:#e25555">❤️</span>
    </p>
    <p style="font-size:12px; color:#777">All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
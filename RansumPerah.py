import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog
import openpyxl
import matplotlib.pyplot as plt
import io
import base64

# Set page configuration
st.set_page_config(
    page_title="Formulasi Ransum Sapi Perah",
    page_icon="🐄",
    layout="wide"
)

# Define helper function at the top of the file
def clean_df_for_display(df):
    """Clean DataFrame for display in Streamlit by converting object columns to strings 
    and removing unnamed columns."""
    # Create a copy to avoid modifying the original
    df_display = df.copy()
    
    # Convert object columns with mixed types to string
    for col in df_display.select_dtypes(include=['object']).columns:
        df_display[col] = df_display[col].astype(str)
    
    # Remove any unnamed columns
    unnamed_cols = [col for col in df_display.columns if 'Unnamed:' in str(col)]
    if unnamed_cols:
        df_display = df_display.drop(columns=unnamed_cols)
    
    return df_display

def get_download_link(df, filename, text):
    """Generate a download link for a DataFrame as Excel file."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Hasil Optimasi')
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Custom CSS to improve appearance
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
    .success-message {
        color: #27ae60;
        font-weight: bold;
        font-size: 1.2rem;
        padding: 1rem;
        border-radius: 5px;
        background-color: #e8f8f5;
    }
    .warning-message {
        color: #e67e22;
        font-weight: bold;
    }
    .info-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Main title with styled header
st.markdown('<h1 class="main-header">Formulasi Ransum Sapi Perah</h1>', unsafe_allow_html=True)

# Show app description
with st.expander("ℹ️ Tentang Aplikasi", expanded=False):
    st.markdown("""
    Aplikasi ini membantu peternak dan ahli nutrisi ternak untuk membuat formulasi ransum sapi perah 
    dengan optimasi biaya. Aplikasi akan mencari kombinasi bahan pakan yang paling ekonomis sambil 
    memenuhi semua kebutuhan nutrisi yang ditetapkan.
    
    **Cara Penggunaan:**
    1. Masukkan kebutuhan nutrisi sapi perah
    2. Pilih sumber data bahan pakan (file Excel atau CSV)
    3. Tentukan parameter optimasi seperti proporsi minimum/maksimum
    4. Klik tombol "Optimasi Ransum" untuk mendapatkan hasil
    
    **Hasil Optimasi:**
    - Proporsi optimal setiap bahan pakan
    - Komposisi nutrisi dari ransum optimal
    - Biaya total ransum per hari
    - Perbandingan target nutrisi dengan hasil formulasi
    """)

# Input kebutuhan nutrisi dalam dua kolom
st.markdown('<h2 class="section-header">Kebutuhan Nutrisi Sapi</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    PK_target = st.number_input("PK (%BK) Target (Protein Kasar)", min_value=0.0, max_value=100.0, value=16.0, 
                              help="Kebutuhan minimum protein kasar dalam persen bahan kering")
    SK_max = st.number_input("SK (%BK) Maksimum (Serat Kasar)", min_value=0.0, max_value=100.0, value=20.0,
                          help="Batas maksimum serat kasar dalam persen bahan kering")
    NDF_max = st.number_input("NDF (%BK) Maksimum (Neutral Detergent Fiber)", min_value=0.0, max_value=100.0, value=40.0,
                           help="Batas maksimum NDF dalam persen bahan kering")
    ADF_max = st.number_input("ADF (%BK) Maksimum (Acid Detergent Fiber)", min_value=0.0, max_value=100.0, value=21.0,
                           help="Batas maksimum ADF dalam persen bahan kering")
    Ca_target = st.number_input("Ca (g) Target (Kalsium)", min_value=0.0, value=60.0,
                             help="Kebutuhan minimum kalsium dalam gram")
    P_target = st.number_input("P (g) Target (Fosfor)", min_value=0.0, value=40.0,
                            help="Kebutuhan minimum fosfor dalam gram")
    PDIA_min = st.number_input("PDIA (g) Minimum (Protein Digestible dalam Usus - Asal Pakan)", min_value=0.0, value=0.0,
                            help="Kebutuhan minimum PDIA dalam gram")

with col2:
    PDI_min = st.number_input("PDI (g) Minimum (Protein Digestible dalam Usus - Total)", min_value=0.0, value=0.0,
                           help="Kebutuhan minimum PDI dalam gram")
    ME_target = st.number_input("ME (kkal) Target (Metabolisable Energy)", min_value=0.0, value=6000.0,
                             help="Kebutuhan minimum energi metabolis dalam kkal")
    NEl_target = st.number_input("NEl (Mkal) Target (Net Energy Laktasi - Mkal)", min_value=0.0, value=1.5,
                              help="Kebutuhan minimum energi bersih laktasi dalam Mkal")
    TDN_target = st.number_input("TDN (%) Target (Total Digestible Nutrients)", min_value=0.0, max_value=100.0, value=65.0,
                               help="Kebutuhan minimum TDN dalam persen")
    RUP_min = st.number_input("RUP (%) Minimum (Rumen Undegraded Protein)", min_value=0.0, max_value=100.0, value=35.0,
                           help="Kebutuhan minimum RUP dalam persen dari protein total")
    RDP_min = st.number_input("RDP (%) Minimum (Rumen Degraded Protein)", min_value=0.0, max_value=100.0, value=65.0,
                           help="Kebutuhan minimum RDP dalam persen dari protein total")

# Input bahan pakan
st.markdown('<h2 class="section-header">Bahan Pakan yang Tersedia</h2>', unsafe_allow_html=True)

# File selection options
file_option = st.radio(
    "Pilih sumber data bahan pakan:",
    ("Gunakan DataRansumSapiPerah.xlsx", "Unggah file CSV"),
    help="Pilih sumber data bahan pakan dari file Excel yang disediakan atau unggah file CSV Anda sendiri"
)

df = None

if file_option == "Gunakan DataRansumSapiPerah.xlsx":
    try:
        # Membaca data dari file Excel
        excel_file = "DataRansumSapiPerah.xlsx"
        
        # Cek nama-nama sheet yang tersedia
        xls = pd.ExcelFile(excel_file)
        available_sheets = xls.sheet_names
        
        st.info(f"Sheet yang tersedia dalam file: {', '.join(available_sheets)}")
        
        # Coba baca sheet 'BahanPakan' atau alternatif
        sheet_bahan = None
        if 'BahanPakan' in available_sheets:
            sheet_bahan = 'BahanPakan'
        else:
            # Coba temukan sheet dengan nama serupa
            potential_sheets = [s for s in available_sheets if ('bahan' in s.lower() or 'pakan' in s.lower()) and not 'harga' in s.lower()]
            if potential_sheets:
                sheet_bahan = potential_sheets[0]
            else:
                # Gunakan sheet pertama sebagai fallback
                sheet_bahan = available_sheets[0]
                
        st.info(f"Menggunakan sheet '{sheet_bahan}' untuk data bahan pakan")
        
        # Read Excel with index_col=False to avoid unnamed columns
        df_bahan = pd.read_excel(excel_file, sheet_name=sheet_bahan, index_col=False)
        
        # Tampilkan kolom untuk debugging
        with st.expander("Detail kolom dari sheet bahan pakan", expanded=False):
            st.write(f"Kolom dalam sheet '{sheet_bahan}': {df_bahan.columns.tolist()}")
        
        # Remove any unnamed columns that might be present
        unnamed_cols = [col for col in df_bahan.columns if 'Unnamed:' in str(col)]
        if unnamed_cols:
            df_bahan = df_bahan.drop(columns=unnamed_cols)
        
        # Cek sheet untuk harga
        sheet_harga = None
        if 'HargaBahan' in available_sheets:
            sheet_harga = 'HargaBahan'
        elif 'HARGA BAHAN PAKAN' in available_sheets:
            sheet_harga = 'HARGA BAHAN PAKAN'
        else:
            # Coba temukan sheet dengan nama serupa (lebih fleksibel untuk berbagai format)
            potential_sheets = [s for s in available_sheets if 'harga' in s.lower() or 'price' in s.lower()]
            if potential_sheets:
                sheet_harga = potential_sheets[0]
        
        # Jika ada sheet harga terpisah, gabungkan data
        if sheet_harga:
            st.info(f"Menggunakan sheet '{sheet_harga}' untuk data harga")
            df_harga = pd.read_excel(excel_file, sheet_name=sheet_harga, index_col=False)
            
            # Tampilkan kolom untuk debugging
            with st.expander("Detail kolom dari sheet harga", expanded=False):
                st.write(f"Kolom dalam sheet '{sheet_harga}': {df_harga.columns.tolist()}")
            
            # Remove any unnamed columns from harga df as well
            unnamed_cols = [col for col in df_harga.columns if 'Unnamed:' in str(col)]
            if unnamed_cols:
                df_harga = df_harga.drop(columns=unnamed_cols)
            
            # Periksa kolom yang mungkin digunakan untuk penggabungan (lebih fleksibel)
            bahan_columns = df_bahan.columns.tolist()

            # Tambahkan pengecekan apakah bahan_columns kosong
            if len(bahan_columns) == 0:
                st.error("Data bahan pakan tidak memiliki kolom. Pastikan file Excel berisi data yang valid.")
                id_column = "Nama Bahan Pakan"  # Berikan default untuk mencegah error
            else:
                id_column = next((col for col in bahan_columns if 'nama' in col.lower() and 'bahan' in col.lower()), 
                               next((col for col in bahan_columns if 'nama' in col.lower() or 'bahan' in col.lower() or 'pakan' in col.lower()),
                                   bahan_columns[0] if len(bahan_columns) > 0 else "Nama Bahan Pakan"))

            st.info(f"Menggunakan kolom '{id_column}' untuk menggabungkan data")
            
            # Cari kolom yang sama di sheet harga untuk penggabungan
            harga_id_column = None
            for col in df_harga.columns:
                if col == id_column:  # Jika nama kolom sama persis
                    harga_id_column = col
                    break
                elif col.lower() == id_column.lower():  # Jika hanya berbeda huruf besar/kecil
                    harga_id_column = col
                    break
                elif 'nama' in col.lower() and ('bahan' in col.lower() or 'pakan' in col.lower()):  # Jika mengandung kata-kata kunci
                    harga_id_column = col
                    break
            
            # Jika tidak ditemukan, gunakan kolom pertama
            if not harga_id_column and len(df_harga.columns) > 0:
                harga_id_column = df_harga.columns[0]
                
            st.info(f"Menggunakan kolom '{id_column}' dari sheet bahan dan '{harga_id_column}' dari sheet harga untuk penggabungan")
            
            # Ensure the price column from HargaBahan is properly identified (lebih fleksibel)
            price_column = None
            for col in df_harga.columns:
                if 'harga' in col.lower() or 'price' in col.lower() or 'biaya' in col.lower() or 'cost' in col.lower() or 'rp' in col.lower():
                    price_column = col
                    break
            
            if price_column:
                st.info(f"Menggunakan kolom '{price_column}' dari sheet harga")
                
                # Rename to standardized format before merge if needed
                if price_column != 'Harga (Rp/kg)':
                    df_harga = df_harga.rename(columns={price_column: 'Harga (Rp/kg)'})
            else:
                # Jika tidak ada kolom yang terdentifikasi sebagai harga, gunakan kolom kedua (asumsi)
                if len(df_harga.columns) > 1:
                    price_column = df_harga.columns[1]
                    df_harga = df_harga.rename(columns={price_column: 'Harga (Rp/kg)'})
                    st.warning(f"Kolom harga tidak teridentifikasi secara spesifik. Menggunakan kolom '{price_column}' sebagai harga.")
                else:
                    st.warning("Kolom harga tidak ditemukan di sheet harga")
            
            # Pastikan kedua DataFrame memiliki kolom untuk penggabungan
            if harga_id_column and harga_id_column in df_harga.columns and id_column in df_bahan.columns:
                # Rename harga_id_column jika berbeda dengan id_column untuk mempermudah penggabungan
                if harga_id_column != id_column:
                    df_harga = df_harga.rename(columns={harga_id_column: id_column})
                
                # Specify suffixes to avoid _x, _y column issues
                df = pd.merge(df_bahan, df_harga, on=id_column, how='left', suffixes=('', '_harga'))
                
                # Clean up duplicate columns created by merge
                duplicate_cols = [col for col in df.columns if col.endswith('_harga')]
                if duplicate_cols:
                    df = df.drop(columns=duplicate_cols)
            else:
                st.warning(f"Tidak dapat melakukan penggabungan data karena kolom kunci tidak ditemukan. Menggunakan hanya data bahan pakan.")
                df = df_bahan
        else:
            # Jika tidak ada sheet harga, gunakan data bahan saja
            df = df_bahan
            st.warning("Sheet harga tidak ditemukan. Menggunakan hanya data bahan tanpa informasi harga.")
            
        # Cari kolom harga
        harga_column = next((col for col in df.columns if 'harga' in col.lower() or 'price' in col.lower() or 'biaya' in col.lower() or 'cost' in col.lower() or 'rp' in col.lower()), None)
        
        # Jika kolom harga tidak ditemukan, tambahkan default
        if harga_column:
            # Pastikan nama kolom seragam
            df = df.rename(columns={harga_column: 'Harga (Rp/kg)'})
            # Isi nilai harga yang kosong
            if df['Harga (Rp/kg)'].isnull().any():
                df['Harga (Rp/kg)'] = df['Harga (Rp/kg)'].fillna(1.0)
        else:
            # Buat kolom harga default
            df['Harga (Rp/kg)'] = 1.0
            st.warning("Kolom harga tidak ditemukan. Menggunakan nilai default 1.0 untuk semua bahan.")
            
        # Pastikan ada kolom 'Nama Bahan Pakan'
        if id_column != 'Nama Bahan Pakan':
            df = df.rename(columns={id_column: 'Nama Bahan Pakan'})
            
        st.success(f"Berhasil memuat data bahan pakan dari file Excel")
        
        # Show final data
        with st.expander("Data yang dimuat", expanded=True):
            st.write("Kolom yang tersedia:", df.columns.tolist())
            st.dataframe(clean_df_for_display(df))
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file Excel: {e}")
        # Tambahkan informasi stack trace lengkap untuk debugging
        import traceback
        st.code(traceback.format_exc())
        st.info("Pastikan file 'DataRansumSapiPerah.xlsx' berada di direktori yang sama dengan script ini.")
        st.info("Jika masih mengalami masalah, coba unggah file CSV sebagai alternatif.")
else:
    uploaded_file = st.file_uploader("Unggah file CSV berisi data bahan pakan", type=["csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.dataframe(clean_df_for_display(df))
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
            st.error("Pastikan file CSV memiliki format yang benar dan kolom yang dibutuhkan.")

if df is not None:
    # Memastikan nama kolom yang dibutuhkan ada dan sesuai
    required_columns = ["Nama Bahan Pakan", "PK", "SK", "NDF", "ADF", "Ca", "P", 
                       "ME (kkal)", "NEl (Mkal)", "TDN", "RUP", "RDP", "Harga (Rp/kg)"]
    
    # Normalize column names - convert to standard format
    column_mapping = {}
    for col in df.columns:
        # Check for similar names regardless of case, spaces, or special characters
        col_clean = col.lower().replace(" ", "").replace("(", "").replace(")", "").replace("%", "")
        
        if "nama" in col_clean and ("bahan" in col_clean or "pakan" in col_clean):
            column_mapping[col] = "Nama Bahan Pakan"
        elif "pk" in col_clean or "proteinkasar" in col_clean:
            column_mapping[col] = "PK"
        elif "sk" in col_clean or "seratkasar" in col_clean:
            column_mapping[col] = "SK"
        elif "ndf" in col_clean:
            column_mapping[col] = "NDF"
        elif "adf" in col_clean:
            column_mapping[col] = "ADF"
        elif col_clean == "ca" or "kalsium" in col_clean:
            column_mapping[col] = "Ca"
        elif col_clean == "p" or "fosfor" in col_clean:
            column_mapping[col] = "P"
        elif "me" in col_clean and "kkal" in col_clean:
            column_mapping[col] = "ME (kkal)"
        elif "nel" in col_clean and "mkal" in col_clean:
            column_mapping[col] = "NEl (Mkal)"
        elif "tdn" in col_clean:
            column_mapping[col] = "TDN"
        elif "rup" in col_clean:
            column_mapping[col] = "RUP"
        elif "rdp" in col_clean:
            column_mapping[col] = "RDP"
        elif "harga" in col_clean:
            column_mapping[col] = "Harga (Rp/kg)"
    
    # Rename columns based on the mapping
    if column_mapping:
        df = df.rename(columns=column_mapping)
        with st.expander("Lihat normalisasi nama kolom", expanded=False):
            st.info("Beberapa nama kolom telah dinormalisasi untuk pemrosesan:")
            st.write(column_mapping)
    
    # Periksa dan beri peringatan jika ada kolom yang hilang
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.warning(f"Kolom berikut tidak ditemukan dalam data: {', '.join(missing_columns)}")
        st.info("Kolom minimal yang dibutuhkan: Nama Bahan Pakan, PK, SK, NDF, ADF, Ca, P, ME (kkal), NEl (Mkal), TDN, RUP, RDP, Harga (Rp/kg)")
        
        # Create missing columns with default values if they don't exist
        for col in missing_columns:
            if col == "Harga (Rp/kg)":
                df[col] = 1.0  # Default price
            else:
                df[col] = 0.0  # Default nutritional value
                
        st.info(f"Kolom yang hilang telah dibuat dengan nilai default.")
    
    # Proses optimasi
    st.markdown('<h2 class="section-header">Optimasi Ransum</h2>', unsafe_allow_html=True)
    
    # Input tambahan untuk optimasi dalam dua kolom
    col1, col2 = st.columns(2)
    
    with col1:
        total_ransum = st.number_input("Total ransum yang dibutuhkan (kg/hari)", 
                                       min_value=0.1, value=15.0, step=0.5,
                                       help="Total jumlah pakan yang dibutuhkan sapi per hari")
        min_proporsi = st.number_input("Proporsi minimum per bahan pakan (%)", 
                                       min_value=0.0, max_value=100.0, value=5.0, step=1.0,
                                       help="Batas bawah proporsi untuk setiap bahan pakan") / 100
    
    with col2:
        max_proporsi = st.number_input("Proporsi maksimum per bahan pakan (%)", 
                                       min_value=0.0, max_value=100.0, value=60.0, step=5.0,
                                       help="Batas atas proporsi untuk setiap bahan pakan") / 100
        threshold = st.number_input("Threshold proporsi minimum (%)", 
                                   min_value=0.0, max_value=10.0, value=1.0, step=0.5,
                                   help="Bahan dengan proporsi di bawah nilai ini akan dianggap 0") / 100
    
    # Opsi tambahan
    with st.expander("Opsi Tambahan", expanded=False):
        show_chart = st.checkbox("Tampilkan grafik proporsi", value=True)
        include_all_feeds = st.checkbox("Tampilkan semua bahan (termasuk yang proporsinya 0)", value=False)
    
    if st.button("Optimasi Ransum"):
        try:
            with st.spinner('Melakukan optimasi ransum...'):
                # Jumlah bahan pakan
                n_bahan = len(df)
                
                # Before optimization
                # Ensure all data columns are numeric
                numeric_columns = ["PK", "SK", "NDF", "ADF", "Ca", "P", "ME (kkal)", 
                                  "NEl (Mkal)", "TDN", "RUP", "RDP", "Harga (Rp/kg)"]
    
                # Make sure no column has mixed types
                for col in df.columns:
                    if col in numeric_columns:
                        # Convert to numeric
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    else:
                        # Convert non-numeric columns to string to avoid PyArrow issues
                        df[col] = df[col].astype(str)
    
                # Ensure there are no duplicate or problematic columns
                df = df.loc[:, ~df.columns.duplicated()]
                unnamed_cols = [col for col in df.columns if 'Unnamed:' in str(col)]
                if unnamed_cols:
                    df = df.drop(columns=unnamed_cols)
    
                # Show preprocessed data
                with st.expander("Lihat data yang digunakan untuk optimasi", expanded=False):
                    st.dataframe(clean_df_for_display(df))
                
                # Objective function: minimize cost
                if "Harga (Rp/kg)" in df.columns:
                    c = df["Harga (Rp/kg)"].values
                else:
                    c = np.ones(n_bahan)  # Jika tidak ada kolom harga, semua bahan dianggap sama harganya
                
                # Constraints matrices
                A_ub = []  # Matrix for <= constraints
                b_ub = []  # Vector for <= constraints
                A_eq = []  # Matrix for == constraints
                b_eq = []  # Vector for == constraints
                
                # Constraint 1: Sum of proportions = 1
                A_eq.append(np.ones(n_bahan))
                b_eq.append(1.0)
                
                # Constraint 2: PK >= PK_target
                A_ub.append(-1 * df["PK"].values)
                b_ub.append(-1 * PK_target)
                
                # Constraint 3: SK <= SK_max
                A_ub.append(df["SK"].values)
                b_ub.append(SK_max)
                
                # Constraint 4: NDF <= NDF_max
                A_ub.append(df["NDF"].values)
                b_ub.append(NDF_max)
                
                # Constraint 5: ADF <= ADF_max
                A_ub.append(df["ADF"].values)
                b_ub.append(ADF_max)
                
                # Constraint 6: TDN >= TDN_target
                A_ub.append(-1 * df["TDN"].values)
                b_ub.append(-1 * TDN_target)
                
                # Constraint 7: RUP >= RUP_min
                A_ub.append(-1 * df["RUP"].values)
                b_ub.append(-1 * RUP_min)
                
                # Constraint 8: RDP >= RDP_min
                A_ub.append(-1 * df["RDP"].values)
                b_ub.append(-1 * RDP_min)
                
                # Constraint 9: Ca >= Ca_target
                A_ub.append(-1 * df["Ca"].values)
                b_ub.append(-1 * Ca_target)
                
                # Constraint 10: P >= P_target
                A_ub.append(-1 * df["P"].values)
                b_ub.append(-1 * P_target)
                
                # Constraint 11: ME >= ME_target
                A_ub.append(-1 * df["ME (kkal)"].values)
                b_ub.append(-1 * ME_target)
                
                # Constraint 12: NEl >= NEl_target
                A_ub.append(-1 * df["NEl (Mkal)"].values)
                b_ub.append(-1 * NEl_target)
                
                # Convert to numpy arrays
                A_ub = np.array(A_ub)
                b_ub = np.array(b_ub)
                A_eq = np.array(A_eq)
                b_eq = np.array(b_eq)
                
                # Bounds for each variable (proportion of each feed)
                bounds = [(min_proporsi, max_proporsi) for _ in range(n_bahan)]
                
                # Solve the linear programming problem
                result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
                
                if result.success:
                    st.markdown('<div class="success-message">Optimasi berhasil! Kombinasi pakan optimal telah ditemukan.</div>', unsafe_allow_html=True)
                    
                    # Display the results
                    proporsi_optimal = result.x
                    
                    # Apply threshold to filter out very small proportions
                    proporsi_optimal_filtered = np.where(proporsi_optimal < threshold, 0, proporsi_optimal)
                    
                    # Renormalize proportions to ensure they sum to 1
                    if sum(proporsi_optimal_filtered) > 0:
                        proporsi_optimal_normalized = proporsi_optimal_filtered / sum(proporsi_optimal_filtered)
                    else:
                        proporsi_optimal_normalized = proporsi_optimal
                    
                    st.subheader("Proporsi Optimal Bahan Pakan")
                    
                    # Create DataFrame for results
                    hasil_df = pd.DataFrame({
                        "Bahan Pakan": df["Nama Bahan Pakan"],
                        "Proporsi (%)": [f"{p*100:.2f}%" for p in proporsi_optimal_normalized],
                        "Proporsi Asli (%)": [f"{p*100:.2f}%" for p in proporsi_optimal],
                        "Jumlah (kg/hari)": [p * total_ransum for p in proporsi_optimal_normalized],
                        "Harga per kg (Rp)": df["Harga (Rp/kg)"],
                        "Biaya (Rp/hari)": df["Harga (Rp/kg)"] * proporsi_optimal_normalized * total_ransum
                    })
                    
                    # Filter out feeds with 0 proportion if requested
                    if not include_all_feeds:
                        hasil_df = hasil_df[hasil_df["Jumlah (kg/hari)"] > 0]
                    
                    # Sort by proportion (descending)
                    hasil_df = hasil_df.sort_values(by="Jumlah (kg/hari)", ascending=False)
                    
                    # Format as currency
                    hasil_df["Harga per kg (Rp)"] = hasil_df["Harga per kg (Rp)"].apply(lambda x: f"Rp {x:,.0f}")
                    hasil_df["Biaya (Rp/hari)"] = hasil_df["Biaya (Rp/hari)"].apply(lambda x: f"Rp {x:,.0f}")
                    hasil_df["Jumlah (kg/hari)"] = hasil_df["Jumlah (kg/hari)"].apply(lambda x: f"{x:.2f}")
                    
                    st.dataframe(hasil_df)
                    
                    # Download link for hasil_df
                    st.markdown(get_download_link(hasil_df, "hasil_formulasi_ransum.xlsx", 
                                              "💾 Download hasil formulasi sebagai file Excel"), 
                            unsafe_allow_html=True)
                    
                    # Visualize feed composition if requested
                    if show_chart and len(hasil_df) > 0:
                        st.subheader("Visualisasi Komposisi Ransum")
                        
                        # Create subplots for two charts
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Pie chart for proportion
                            fig1, ax1 = plt.subplots(figsize=(10, 6))
                            ax1.pie(
                                [float(p.strip('%'))/100 for p in hasil_df["Proporsi (%)"]],
                                labels=hasil_df["Bahan Pakan"],
                                autopct='%1.1f%%',
                                startangle=90,
                                shadow=True
                            )
                            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
                            ax1.set_title('Proporsi Bahan Pakan (%)')
                            st.pyplot(fig1)
                        
                        with col2:
                            # Bar chart for costs
                            fig2, ax2 = plt.subplots(figsize=(10, 6))
                            y_pos = np.arange(len(hasil_df))
                            biaya = [float(b.replace('Rp ', '').replace(',', '')) 
                                     for b in hasil_df["Biaya (Rp/hari)"]]
                            ax2.barh(y_pos, biaya, align='center')
                            ax2.set_yticks(y_pos)
                            ax2.set_yticklabels(hasil_df["Bahan Pakan"])
                            ax2.invert_yaxis()  # Labels read top-to-bottom
                            ax2.set_xlabel('Biaya (Rp/hari)')
                            ax2.set_title('Kontribusi Biaya per Bahan Pakan')
                            
                            # Add value labels to the bars
                            for i, v in enumerate(biaya):
                                ax2.text(v + 0.1, i, f'Rp {v:,.0f}', va='center')
                                
                            st.pyplot(fig2)
                    
                    # Calculate and display nutritional composition
                    st.subheader("Komposisi Nutrisi Ransum Optimal")
                    
                    # Use normalized proportions for calculation
                    PK_optimal = sum(df["PK"] * proporsi_optimal_normalized)
                    SK_optimal = sum(df["SK"] * proporsi_optimal_normalized)
                    NDF_optimal = sum(df["NDF"] * proporsi_optimal_normalized)
                    ADF_optimal = sum(df["ADF"] * proporsi_optimal_normalized)
                    Ca_optimal = sum(df["Ca"] * proporsi_optimal_normalized)
                    P_optimal = sum(df["P"] * proporsi_optimal_normalized)
                    ME_optimal = sum(df["ME (kkal)"] * proporsi_optimal_normalized)
                    NEl_optimal = sum(df["NEl (Mkal)"] * proporsi_optimal_normalized)
                    TDN_optimal = sum(df["TDN"] * proporsi_optimal_normalized)
                    RUP_optimal = sum(df["RUP"] * proporsi_optimal_normalized)
                    RDP_optimal = sum(df["RDP"] * proporsi_optimal_normalized)
                    
                    # Total cost using normalized proportions
                    total_cost = sum(df["Harga (Rp/kg)"] * proporsi_optimal_normalized) * total_ransum
                    
                    # Create a table for nutrient comparison
                    nutrisi_df = pd.DataFrame({
                        "Nutrisi": ["PK (%BK)", "SK (%BK)", "NDF (%BK)", "ADF (%BK)", 
                                   "Ca (g)", "P (g)", "ME (kkal)", "NEl (Mkal)", 
                                   "TDN (%)", "RUP (%)", "RDP (%)"],
                        "Target": [f"≥ {PK_target:.2f}", f"≤ {SK_max:.2f}", f"≤ {NDF_max:.2f}", f"≤ {ADF_max:.2f}", 
                                  f"≥ {Ca_target:.2f}", f"≥ {P_target:.2f}", f"≥ {ME_target:.2f}", f"≥ {NEl_target:.2f}", 
                                  f"≥ {TDN_target:.2f}", f"≥ {RUP_min:.2f}", f"≥ {RDP_min:.2f}"],
                        "Hasil Formulasi": [
                            f"{PK_optimal:.2f}", f"{SK_optimal:.2f}", f"{NDF_optimal:.2f}", 
                            f"{ADF_optimal:.2f}", f"{Ca_optimal:.2f}", f"{P_optimal:.2f}", 
                            f"{ME_optimal:.2f}", f"{NEl_optimal:.2f}", f"{TDN_optimal:.2f}", 
                            f"{RUP_optimal:.2f}", f"{RDP_optimal:.2f}"
                        ],
                        "Status": [
                            "✅ Memenuhi" if PK_optimal >= PK_target else "❌ Tidak Memenuhi",
                            "✅ Memenuhi" if SK_optimal <= SK_max else "❌ Tidak Memenuhi",
                            "✅ Memenuhi" if NDF_optimal <= NDF_max else "❌ Tidak Memenuhi",
                            "✅ Memenuhi" if ADF_optimal <= ADF_max else "❌ Tidak Memenuhi",
                            "✅ Memenuhi" if Ca_optimal >= Ca_target else "❌ Tidak Memenuhi",
                            "✅ Memenuhi" if P_optimal >= P_target else "❌ Tidak Memenuhi",
                            "✅ Memenuhi" if ME_optimal >= ME_target else "❌ Tidak Memenuhi",
                            "✅ Memenuhi" if NEl_optimal >= NEl_target else "❌ Tidak Memenuhi",
                            "✅ Memenuhi" if TDN_optimal >= TDN_target else "❌ Tidak Memenuhi",
                            "✅ Memenuhi" if RUP_optimal >= RUP_min else "❌ Tidak Memenuhi",
                            "✅ Memenuhi" if RDP_optimal >= RDP_min else "❌ Tidak Memenuhi",
                        ]
                    })
                    
                    st.dataframe(nutrisi_df)
                    
                    # Download link for nutrisi_df
                    st.markdown(get_download_link(nutrisi_df, "nutrisi_formulasi_ransum.xlsx", 
                                               "💾 Download hasil analisis nutrisi sebagai file Excel"), 
                             unsafe_allow_html=True)
                    
                    # Display total cost
                    st.subheader("Biaya Total")
                    st.markdown(f"<h3 style='color:#27ae60'>Rp {total_cost:,.2f} per hari (untuk {total_ransum} kg ransum)</h3>", 
                             unsafe_allow_html=True)
                    st.write(f"Biaya per kg: Rp {total_cost/total_ransum:,.2f}")
                    
                else:
                    st.error("Optimasi gagal. Tidak ditemukan solusi yang memenuhi semua batasan.")
                    st.write(f"Pesan kesalahan: {result.message}")
                    st.info("Coba ubah batasan nutrisi atau batas proporsi minimum/maksimum.")
                    
                    # Suggestions for troubleshooting
                    st.subheader("Saran Perbaikan")
                    st.markdown("""
                    * Kurangi nilai nutrisi target atau tingkatkan nilai maksimum
                    * Kurangi nilai proporsi minimum atau tingkatkan nilai maksimum
                    * Pastikan bahan pakan yang tersedia memiliki nilai nutrisi yang memadai
                    * Tambahkan lebih banyak jenis bahan pakan untuk memberikan lebih banyak pilihan
                    """)
        
        except Exception as e:
            st.error(f"Terjadi kesalahan dalam proses optimasi: {e}")
            st.info("Pastikan data bahan pakan lengkap dan format sesuai.")
else:
    st.info("Silahkan pilih sumber data bahan pakan untuk memulai formulasi.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 20px;">
    <p>Aplikasi Formulasi Ransum Sapi Perah v1.0</p>
    <p>Dikembangkan untuk membantu peternak menemukan formulasi ransum yang optimal dan ekonomis</p>
</div>
""", unsafe_allow_html=True)
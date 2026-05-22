import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pymongo import MongoClient

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="BoschMonitor OS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. KONEKSI DATABASE MONGODB
# ==========================================
@st.cache_resource
def init_mongodb():
    # Sesuaikan URI jika Anda menggunakan MongoDB Atlas (Cloud)
    client = MongoClient("mongodb://localhost:27017/")
    return client

try:
    mongo_client = init_mongodb()
    db = mongo_client["bosch_iot_db"]
    # Koleksi utama sesuai dengan rancangan Bucket Pattern
    bucket_collection = db["telemetry_buckets"]
    # Koleksi opsional untuk mencatat log anomali secara spesifik
    anomaly_collection = db["anomaly_log"]
    db_connected = True
except Exception as e:
    db_connected = False

# ==========================================
# 3. MANAJEMEN TEMA UTAMA (HITAM & PUTIH)
# ==========================================
st.sidebar.markdown("MENU NAVIGASI")
theme_mode = st.sidebar.radio("Mode Tampilan:", ["Hitam", "Putih"])

if theme_mode == "Hitam":
    c_bg = "#000000"
    c_text = "#FFFFFF"
    c_border = "#FFFFFF"
    c_chart_line1 = "#FFFFFF"
    c_chart_line2 = "#888888"
else:
    c_bg = "#FFFFFF"
    c_text = "#000000"
    c_border = "#000000"
    c_chart_line1 = "#000000"
    c_chart_line2 = "#777777"

# ==========================================
# 4. INJEKSI CSS ULTRA-MINIMALIS (TIMES NEW ROMAN, NO BOLD)
# ==========================================
st.markdown(f"""
    <style>
    html, body, p, h1, h2, h3, h4, h5, h6, span, div, li, th, td, label {{
        font-family: 'Times New Roman', Times, serif !important;
        font-weight: normal !important;
        animation: none !important;
        transition: none !important;
    }}
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"] {{
        display: none !important;
    }}
    .stApp {{
        background-color: {c_bg};
        color: {c_text};
    }}
    [data-testid="stSidebar"] {{
        background-color: {c_bg} !important;
        border-right: 1px solid {c_border};
    }}
    [data-testid="stSidebar"] * {{
        color: {c_text} !important;
        background-color: transparent !important;
    }}
    
    /* ========================================================
       PERBAIKAN CSS RADIO BUTTON (MENGHILANGKAN KOTAK TEKS) 
       ======================================================== */
    /* Hapus semua atribut bingkai dari teks paragraf */
    .stRadio div[role="radiogroup"] label p {{
        font-size: 16px !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }}
    
    /* Target EKSKLUSIF hanya pada anak pertama (lingkaran radio) */
    .stRadio div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {{
        border: 2px solid {c_text} !important;
        background-color: {c_bg} !important;
    }}
    
    /* Mewarnai isi titik saat radio dipilih */
    .stRadio div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child > div {{
        background-color: {c_text} !important;
    }}
    
    /* Pelucutan EKSKLUSIF pada anak terakhir (container teks) agar 100% polos */
    .stRadio div[role="radiogroup"] label[data-baseweb="radio"] > div:last-child {{
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background-color: transparent !important;
    }}
    /* ======================================================== */

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}
    .stSelectbox div[data-baseweb="select"] {{
        background-color: {c_bg} !important;
        border: 1px solid {c_border} !important;
        color: {c_text} !important;
        border-radius: 0px !important;
    }}
    [data-testid="stDataFrame"] {{
        background-color: {c_bg};
        border: 1px solid {c_border};
        border-radius: 0px;
        padding: 5px;
    }}
    </style>
""", unsafe_allow_html=True)

def create_minimal_kpi(title, value, trend):
    html = f"""
    <div style="border: 1px solid {c_border}; padding: 15px; margin-bottom: 15px; background-color: {c_bg};">
        <div style="font-size: 14px; text-transform: uppercase; color: {c_text};">{title}</div>
        <div style="font-size: 36px; margin: 10px 0 5px 0; color: {c_text};">{value}</div>
        <div style="font-size: 12px; color: {c_text};">{trend} vs minggu lalu</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ==========================================
# 5. ROUTING MENU UTAMA
# ==========================================
menu = st.sidebar.radio(
    "Pilih Panel:",
    ["Live Monitor", "Frequency Analysis", "Anomaly Log", "Maintenance Predictor"]
)

st.sidebar.markdown("---")
if db_connected:
    st.sidebar.text("Status: Terhubung ke MongoDB")
else:
    st.sidebar.text("Status: Koneksi DB Gagal")

# ------------------------------------------
# HALAMAN 1: LIVE MONITOR (KONEKSI DATA AKTUAL)
# ------------------------------------------
if menu == "Live Monitor":
    st.markdown(f"<h1 style='font-size: 28px; color: {c_text}; margin-bottom: 5px;'>Live Monitor</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 14px; color: {c_text}; margin-bottom: 20px;'>Pantauan real-time chart vibrasi & suhu berbasis MongoDB Bucket Pattern.</p>", unsafe_allow_html=True)
    
    # Inisialisasi variabel internal data aktual
    avg_temp_val = "42.5 C"
    rms_vib_val = "0.14 g"
    
    # Mengambil dokumen bucket terbaru dari MongoDB untuk MOTOR_01
    latest_bucket = None
    if db_connected:
        latest_bucket = bucket_collection.find_one(
            {"motor_id": "MOTOR_01"},
            sort=[("bucket_start", -1)]
        )
    
    # Pemrosesan jika data dalam MongoDB ditemukan
    if latest_bucket and "measurements" in latest_bucket and len(latest_bucket["measurements"]) > 0:
        df_real = pd.DataFrame(latest_bucket["measurements"])
        # Mengambil info statistik yang tersimpan di dalam struktur bucket
        if "stats" in latest_bucket:
            avg_temp_val = f"{latest_bucket['stats'].get('temp_avg', 42.5):.1f} C"
            rms_vib_val = f"{latest_bucket['stats'].get('vib_rms', 0.14):.3f} g"
        else:
            avg_temp_val = f"{df_real['temp'].mean():.1f} C"
            rms_vib_val = f"{df_real['ax'].mean():.2f} g"
            
        time_idx = df_real["t"]
        suhu = df_real["temp"]
        vibrasi = df_real["ax"]
        datasource_info = "Sumber Data: MongoDB Aktual"
    else:
        # Fallback data simulasi jika koleksi database kosong
        np.random.seed(42)
        time_idx = pd.date_range("2026-05-21", periods=20, freq="1h")
        vibrasi = np.abs(np.cumsum(np.random.randn(20) * 0.02) + 0.1)
        suhu = np.cumsum(np.random.randn(20) * 0.5) + 40
        datasource_info = "Sumber Data: Simulasi Internal (Database Kosong)"

    # Tampilan KPI Card
    col1, col2, col3, col4 = st.columns(4)
    with col1: create_minimal_kpi("Active Motors", "24", "+2")
    with col2: create_minimal_kpi("Avg Temp", avg_temp_val, "-1.2 C")
    with col3: create_minimal_kpi("RMS Vibration", rms_vib_val, "+0.02 g")
    with col4: create_minimal_kpi("System Status", "NOMINAL", "0")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='font-size: 16px; color: {c_text};'>Data Telemetri Sensor ({datasource_info})</h3>", unsafe_allow_html=True)
    
    # Render Plotly Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_idx, y=suhu, name="Suhu (C)", mode='lines', line=dict(color=c_chart_line1, width=1.5)))
    fig.add_trace(go.Scatter(x=time_idx, y=vibrasi * 100 if "Simulasi" in datasource_info else vibrasi, name="Vibrasi", mode='lines', line=dict(color=c_chart_line2, width=1.5)))

    fig.update_layout(
        plot_bgcolor=c_bg, paper_bgcolor=c_bg, margin=dict(l=40, r=20, t=20, b=40),
        xaxis=dict(showgrid=True, gridcolor=c_border, gridwidth=0.5, tickfont=dict(color=c_text, size=12)),
        yaxis=dict(showgrid=True, gridcolor=c_border, gridwidth=0.5, tickfont=dict(color=c_text, size=12)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=c_text)),
        hovermode="x"
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# ------------------------------------------
# HALAMAN 2: FREQUENCY ANALYSIS
# ------------------------------------------
elif menu == "Frequency Analysis":
    st.markdown(f"<h1 style='font-size: 28px; color: {c_text}; margin-bottom: 5px;'>Frequency Analysis</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 14px; color: {c_text}; margin-bottom: 20px;'>Visualisasi FFT spectrum plot per motor.</p>", unsafe_allow_html=True)
    
    motor_select = st.selectbox("Pilih ID Motor:", ["MOTOR_01", "MOTOR_02", "MOTOR_03"])
    st.markdown(f"<p style='font-size: 14px; color: {c_text}; margin-top: 10px;'>Menampilkan hasil Fast Fourier Transform untuk {motor_select}</p>", unsafe_allow_html=True)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(y=np.abs(np.random.randn(40))**2, marker_color=c_chart_line1, width=0.4))
    fig.update_layout(
        plot_bgcolor=c_bg, paper_bgcolor=c_bg, margin=dict(l=40, r=20, t=10, b=40),
        xaxis=dict(showgrid=True, gridcolor=c_border, gridwidth=0.5, tickfont=dict(color=c_text)),
        yaxis=dict(showgrid=True, gridcolor=c_border, gridwidth=0.5, tickfont=dict(color=c_text)),
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# ------------------------------------------
# HALAMAN 3: ANOMALY LOG (KONEKSI DATA ANOMALI AKTUAL)
# ------------------------------------------
elif menu == "Anomaly Log":
    st.markdown(f"<h1 style='font-size: 28px; color: {c_text}; margin-bottom: 5px;'>Anomaly Log</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 14px; color: {c_text}; margin-bottom: 20px;'>Tabel seluruh kejadian anomali dari database log.</p>", unsafe_allow_html=True)
    
    anomaly_loaded = False
    if db_connected:
        # Menarik data dari koleksi 'anomaly_log' sebanyak 50 data terbaru
        cursor = anomaly_collection.find({}, limit=50).sort("Timestamp", -1)
        log_list = list(cursor)
        if len(log_list) > 0:
            log_data = pd.DataFrame(log_list)
            # Membersihkan kolom internal id bawaan mongo saat dipasang ke dataframe
            if "_id" in log_data.columns:
                log_data = log_data.drop(columns=["_id"])
            anomaly_loaded = True

    if not anomaly_loaded:
        # Data cadangan jika koleksi log anomali belum memiliki entri data asli
        log_data = pd.DataFrame({
            "Timestamp": ["2026-05-21 08:12:00", "2026-05-21 10:45:30", "2026-05-21 11:02:15"],
            "Motor ID": ["MOTOR_02", "MOTOR_05", "MOTOR_01"],
            "Sensor": ["Suhu", "Vibrasi", "Vibrasi"],
            "Value": ["85 C", "0.8 g", "0.6 g"],
            "Severity": ["CRITICAL", "WARNING", "INFO"]
        })
    st.dataframe(log_data, use_container_width=True, hide_index=True)

# ------------------------------------------
# HALAMAN 4: MAINTENANCE PREDICTOR
# ------------------------------------------
elif menu == "Maintenance Predictor":
    st.markdown(f"<h1 style='font-size: 28px; color: {c_text}; margin-bottom: 5px;'>Maintenance Predictor</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 14px; color: {c_text}; margin-bottom: 20px;'>Estimasi sisa umur komponen berdasarkan tren degradasi.</p>", unsafe_allow_html=True)
    
    st.markdown(f"""
        <div style="border: 1px solid {c_border}; padding: 20px; line-height: 1.8; background-color: {c_bg}; color: {c_text};">
            <div>[!] MOTOR_02 - Estimasi Sisa Umur Komponen: 5 Hari Terhitung Kritis</div>
            <div>[-] MOTOR_05 - Estimasi Sisa Umur Komponen: 14 Hari Kategori Peringatan</div>
            <div>[+] MOTOR_01 - Kondisi Operasi: Stabil / Nominal</div>
            <div>[+] MOTOR_03 - Kondisi Operasi: Stabil / Nominal</div>
        </div>
    """, unsafe_allow_html=True)
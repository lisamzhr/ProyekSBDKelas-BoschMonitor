import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import time

API_BASE_URL = "https://proyeksbdkelas-boschmonitor.onrender.com"

# KONFIGURASI HALAMAN
st.set_page_config(
    page_title="BoschMonitor OS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cek Koneksi ke Backend API
@st.cache_data(ttl=5)
def fetch_api_data(endpoint):
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

backend_status = fetch_api_data("/")
api_connected = backend_status is not None

# MANAJEMEN TEMA UTAMA (HITAM & PUTIH)
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

# INJEKSI CSS (TIMES NEW ROMAN, NO BOLD)
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
    
    /* Perbaikan Radio Button CSS */
    .stRadio div[role="radiogroup"] label p {{ font-size: 16px !important; border: none !important; }}
    .stRadio div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {{ border: 2px solid {c_text} !important; background-color: {c_bg} !important; }}
    .stRadio div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child > div {{ background-color: {c_text} !important; }}
    .stRadio div[role="radiogroup"] label[data-baseweb="radio"] > div:last-child {{ background-color: transparent !important; }}

    .block-container {{ padding-top: 2rem; padding-bottom: 2rem; }}
    .stSelectbox div[data-baseweb="select"] {{ background-color: {c_bg} !important; border: 1px solid {c_border} !important; color: {c_text} !important; border-radius: 0px !important; }}
    [data-testid="stDataFrame"] {{ background-color: {c_bg}; border: 1px solid {c_border}; border-radius: 0px; padding: 5px; }}
    </style>
""", unsafe_allow_html=True)

def create_minimal_kpi(title, value, trend):
    html = f"""
    <div style="border: 1px solid {c_border}; padding: 15px; margin-bottom: 15px; background-color: {c_bg};">
        <div style="font-size: 14px; text-transform: uppercase; color: {c_text};">{title}</div>
        <div style="font-size: 36px; margin: 10px 0 5px 0; color: {c_text};">{value}</div>
        <div style="font-size: 12px; color: {c_text};">{trend}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ROUTING MENU UTAMA
menu = st.sidebar.radio(
    "Pilih Panel:",
    ["Live Monitor", "Frequency Analysis", "Anomaly Log", "Maintenance Predictor"]
)

st.sidebar.markdown("---")
if api_connected:
    st.sidebar.text("Status: API Online (Render)")
else:
    st.sidebar.text("Status: Endpoint API Terputus")

# HALAMAN 1: LIVE MONITOR (FETECH API BUCKETS)
if menu == "Live Monitor":
    st.markdown(f"<h1 style='font-size: 28px; color: {c_text}; margin-bottom: 5px;'>Live Monitor</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 14px; color: {c_text}; margin-bottom: 20px;'>Pantauan agregasi bucket (5 menitan) ditarik dari endpoint Flask.</p>", unsafe_allow_html=True)
    
    avg_temp_val = "N/A"
    rms_vib_val = "N/A"
    health_score = "N/A"
    
    # Ambil health
    health_data = fetch_api_data("/health/MOTOR_01")
    if health_data and "stats" in health_data:
        avg_temp_val = f"{health_data['stats'].get('temp_avg', 0):.1f} C"
        rms_vib_val = f"{health_data['stats'].get('vib_rms', 0):.3f} g"
        health_score = f"{health_data.get('health_score', 100)} %"
    
    # Ambil history bucket untuk grafik
    buckets_data = fetch_api_data("/buckets/MOTOR_01")
    
    if buckets_data and len(buckets_data) > 0:
        df_buckets = pd.DataFrame(buckets_data)
        # Ekstrak kolom stats dictionary menjadi kolom dataframe
        df_buckets = pd.concat([df_buckets.drop(['stats'], axis=1), df_buckets['stats'].apply(pd.Series)], axis=1)
        df_buckets = df_buckets.sort_values(by="bucket_start") # Urutkan dari terlama ke terbaru
        
        time_idx = pd.to_datetime(df_buckets["bucket_start"]).dt.strftime('%H:%M:%S')
        suhu = df_buckets["temp_avg"]
        vibrasi = df_buckets["vib_rms"]
        datasource_info = "REST API: Aggregated Bucket Data"
    else:
        # Fallback jika kosong
        time_idx = ["00:00", "00:05", "00:10"]
        suhu = [40, 42, 41]
        vibrasi = [0.1, 0.12, 0.11]
        datasource_info = "Menunggu data bucket pertama ditutup..."

    col1, col2, col3, col4 = st.columns(4)
    with col1: create_minimal_kpi("Device", "MOTOR_01", "Active")
    with col2: create_minimal_kpi("Avg Temp", avg_temp_val, "Dari Bucket Terakhir")
    with col3: create_minimal_kpi("RMS Vibration", rms_vib_val, "Dari Bucket Terakhir")
    with col4: create_minimal_kpi("Health Score", health_score, "Index Kondisi")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='font-size: 16px; color: {c_text};'>{datasource_info}</h3>", unsafe_allow_html=True)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_idx, y=suhu, name="Rata-rata Suhu (C)", mode='lines+markers', line=dict(color=c_chart_line1, width=2)))
    fig.add_trace(go.Scatter(x=time_idx, y=vibrasi * 100, name="Vibrasi (x100 g)", mode='lines+markers', line=dict(color=c_chart_line2, width=2)))

    fig.update_layout(
        plot_bgcolor=c_bg, paper_bgcolor=c_bg, margin=dict(l=40, r=20, t=20, b=40),
        xaxis=dict(showgrid=True, gridcolor=c_border, gridwidth=0.5, tickfont=dict(color=c_text, size=12)),
        yaxis=dict(showgrid=True, gridcolor=c_border, gridwidth=0.5, tickfont=dict(color=c_text, size=12)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=c_text)),
        hovermode="x"
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# HALAMAN 2: FREQUENCY ANALYSIS
elif menu == "Frequency Analysis":
    st.markdown(f"<h1 style='font-size: 28px; color: {c_text}; margin-bottom: 5px;'>Frequency Analysis</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 14px; color: {c_text}; margin-bottom: 20px;'>Visualisasi Fast Fourier Transform ditarik dari Analytics Engine.</p>", unsafe_allow_html=True)
    
    motor_select = st.selectbox("Pilih ID Motor:", ["MOTOR_01"])
    
    analytics_data = fetch_api_data(f"/analytics/{motor_select}")
    
    if analytics_data and "fft" in analytics_data["analytics"]:
        freqs = analytics_data["analytics"]["fft"].get("frequencies", [])
        mags = analytics_data["analytics"]["fft"].get("magnitudes", [])
        fault = analytics_data["analytics"]["fft"].get("detected_fault", "Undetected")
        
        st.markdown(f"<h3 style='font-size: 16px; color: {c_text};'>Detected Component State: {fault}</h3>", unsafe_allow_html=True)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=freqs, y=mags, marker_color=c_chart_line1, name="Magnitude"))
        fig.update_layout(
            plot_bgcolor=c_bg, paper_bgcolor=c_bg, margin=dict(l=40, r=20, t=10, b=40),
            xaxis=dict(title="Frekuensi (Hz)", showgrid=True, gridcolor=c_border, gridwidth=0.5, tickfont=dict(color=c_text)),
            yaxis=dict(title="Amplitude", showgrid=True, gridcolor=c_border, gridwidth=0.5, tickfont=dict(color=c_text)),
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("Belum ada data array mentah di dalam bucket untuk ditarik FFT-nya.")

# HALAMAN 3: ANOMALY LOG
elif menu == "Anomaly Log":
    st.markdown(f"<h1 style='font-size: 28px; color: {c_text}; margin-bottom: 5px;'>Anomaly Log</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 14px; color: {c_text}; margin-bottom: 20px;'>Mendeteksi titik anomali Suhu secara Z-Score dari Bucket Data terbaru.</p>", unsafe_allow_html=True)
    
    analytics_data = fetch_api_data("/analytics/MOTOR_01")
    
    if analytics_data and "anomalies" in analytics_data["analytics"]:
        anomalies = analytics_data["analytics"].get("anomalies", [])
        if len(anomalies) > 0:
            df_anomalies = pd.DataFrame(anomalies)
            # Tampilkan data timestamp dan ukuran temperaturnya saja agar ringkas
            st.dataframe(df_anomalies[['t', 'temp']], use_container_width=True, hide_index=True)
        else:
            st.markdown(f"""<div style="border: 1px solid {c_border}; padding: 15px; color: {c_text}; text-align: center;">Tidak ada anomali terdeteksi (Z-Score &lt; 3.0) pada bucket saat ini.</div>""", unsafe_allow_html=True)
    else:
         st.warning("Belum ada data untuk dianalisis.")

# HALAMAN 4: MAINTENANCE PREDICTOR
elif menu == "Maintenance Predictor":
    st.markdown(f"<h1 style='font-size: 28px; color: {c_text}; margin-bottom: 5px;'>Maintenance Predictor</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 14px; color: {c_text}; margin-bottom: 20px;'>Estimasi status mesin dihitung dari agregat Poin Penalti Analitik AI.</p>", unsafe_allow_html=True)
    
    analytics_data = fetch_api_data("/analytics/MOTOR_01")
    predictive_health = "N/A"
    
    if analytics_data:
        predictive_health = analytics_data["analytics"].get("predictive_health", "100")
        
    st.markdown(f"""
        <div style="border: 1px solid {c_border}; padding: 20px; line-height: 1.8; background-color: {c_bg}; color: {c_text};">
            <h2 style='font-size: 24px; margin-bottom: 15px;'>Predictive Health Score: {predictive_health}/100</h2>
            <div>Jika nilai < 70 : Direkomendasikan melakukan Predictive Maintenance minggu depan.</div>
            <div>Jika nilai < 50 : <b>Kritis.</b> Ganti komponen segera.</div>
        </div>
    """, unsafe_allow_html=True)
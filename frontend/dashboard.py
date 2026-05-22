import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import time

API_BASE_URL = "https://proyeksbdkelas-boschmonitor.onrender.com"

st.set_page_config(
    page_title="BoschMonitor OS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── fetch ─────────────────────────────────────────────────────────────────────
def fetch(endpoint, fallback=None):
    try:
        r = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
        if r.status_code == 200:
            return r.json()
        return fallback
    except Exception:
        return fallback

def get_motors():
    data = fetch("/motors", [])
    if data and isinstance(data, list) and len(data) > 0:
        return [m["motor_id"] for m in data]
    return ["MOTOR_01", "MOTOR_02"]

# ── tema ──────────────────────────────────────────────────────────────────────
backend_status = fetch("/")
api_connected  = backend_status is not None

st.sidebar.markdown("MENU NAVIGASI")
theme_mode = st.sidebar.radio("Mode Tampilan:", ["Hitam", "Putih"])

if theme_mode == "Hitam":
    c_bg     = "#000000"
    c_text   = "#FFFFFF"
    c_border = "#333333"
    c_l1     = "#FFFFFF"
    c_l2     = "#888888"
    c_l3     = "#555555"
else:
    c_bg     = "#FFFFFF"
    c_text   = "#000000"
    c_border = "#CCCCCC"
    c_l1     = "#000000"
    c_l2     = "#555555"
    c_l3     = "#AAAAAA"

st.markdown(f"""
<style>
html, body, p, h1, h2, h3, h4, h5, h6, span, div, li, th, td, label {{
    font-family: 'Times New Roman', Times, serif !important;
    font-weight: normal !important;
    animation: none !important;
    transition: none !important;
}}
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"] {{ display: none !important; }}
.stApp {{ background-color: {c_bg}; color: {c_text}; }}
[data-testid="stSidebar"] {{
    background-color: {c_bg} !important;
    border-right: 1px solid {c_border};
}}
[data-testid="stSidebar"] * {{
    color: {c_text} !important;
    background-color: transparent !important;
}}
.stRadio div[role="radiogroup"] label p {{
    font-size: 16px !important; border: none !important;
}}
.stRadio div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {{
    border: 2px solid {c_text} !important;
    background-color: {c_bg} !important;
}}
.stRadio div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child > div {{
    background-color: {c_text} !important;
}}
.block-container {{ padding-top: 2rem; padding-bottom: 2rem; }}
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

# ── helpers ───────────────────────────────────────────────────────────────────
CHART_BASE = dict(
    plot_bgcolor=c_bg, paper_bgcolor=c_bg,
    margin=dict(l=40, r=20, t=20, b=40),
    font=dict(family="Times New Roman", color=c_text)
)

def kpi(title, value, sub):
    st.markdown(f"""
    <div style="border:1px solid {c_border};padding:15px;margin-bottom:15px;background:{c_bg}">
        <div style="font-size:12px;text-transform:uppercase;color:{c_text};letter-spacing:0.1em">{title}</div>
        <div style="font-size:34px;margin:8px 0 4px 0;color:{c_text}">{value}</div>
        <div style="font-size:11px;color:{c_l2}">{sub}</div>
    </div>""", unsafe_allow_html=True)

def section(title):
    st.markdown(f"<h3 style='font-size:14px;color:{c_text};text-transform:uppercase;"
                f"letter-spacing:0.12em;border-bottom:1px solid {c_border};"
                f"padding-bottom:6px;margin:20px 0 14px 0'>{title}</h3>",
                unsafe_allow_html=True)

def safe_df(anomalies):
    if not anomalies:
        return pd.DataFrame()
    df = pd.DataFrame(anomalies)
    cols = [c for c in ["t", "temp", "ax", "ay", "az"] if c in df.columns]
    return df[cols]

# ── sidebar ───────────────────────────────────────────────────────────────────
menu = st.sidebar.radio(
    "Pilih Panel:",
    ["Live Monitor", "Frequency Analysis", "Anomaly Log", "Maintenance Predictor"]
)

st.sidebar.markdown("---")
motors_list = get_motors()
st.sidebar.markdown(f"Motors aktif: **{len(motors_list)}**")
for m in motors_list:
    st.sidebar.markdown(f"- {m}")
st.sidebar.markdown("---")

if api_connected:
    st.sidebar.markdown(f"<span style='color:{c_text}'>Status: API Online</span>", unsafe_allow_html=True)
else:
    st.sidebar.markdown(f"<span style='color:{c_text}'>Status: API Terputus</span>", unsafe_allow_html=True)

# ── LIVE MONITOR ──────────────────────────────────────────────────────────────
if menu == "Live Monitor":
    st.markdown(f"<h1 style='font-size:28px;color:{c_text};margin-bottom:4px'>Live Monitor</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:13px;color:{c_l2};margin-bottom:20px'>Pantauan agregasi bucket per 5 menit dari semua motor.</p>", unsafe_allow_html=True)

    selected_motor = st.selectbox("Motor:", motors_list)

    health_data  = fetch(f"/health/{selected_motor}")
    buckets_data = fetch(f"/buckets/{selected_motor}", [])

    avg_temp_val  = "N/A"
    rms_vib_val   = "N/A"
    health_score  = "N/A"
    temp_max_val  = "N/A"

    if health_data and "stats" in health_data:
        s = health_data["stats"]
        avg_temp_val = f"{s.get('temp_avg', 0):.1f} C"
        rms_vib_val  = f"{s.get('vib_rms',  0):.3f} g"
        temp_max_val = f"{s.get('temp_max', 0):.1f} C"
        health_score = f"{health_data.get('health_score', 100)}"

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Device",        selected_motor, "Active")
    with c2: kpi("Avg Temp",      avg_temp_val,   "Bucket terakhir")
    with c3: kpi("RMS Vibration", rms_vib_val,    "Bucket terakhir")
    with c4: kpi("Health Score",  health_score,   "0-100 index")

    st.markdown("<br>", unsafe_allow_html=True)

    if buckets_data and len(buckets_data) > 0:
        df = pd.DataFrame(buckets_data)
        closed = df[df["is_closed"] == True].copy()

        if not closed.empty:
            stats_df = closed["stats"].apply(pd.Series)
            closed   = pd.concat([closed.drop(["stats"], axis=1), stats_df], axis=1)
            closed   = closed.sort_values("bucket_start")
            time_idx = pd.to_datetime(closed["bucket_start"]).dt.strftime("%H:%M")
            suhu     = pd.to_numeric(closed["temp_avg"], errors="coerce")
            vibrasi  = pd.to_numeric(closed["vib_rms"],  errors="coerce")
            temp_max = pd.to_numeric(closed["temp_max"], errors="coerce")

            section("Trend Suhu per Bucket")
            fig_t = go.Figure()
            fig_t.add_trace(go.Scatter(x=time_idx, y=suhu,     name="Avg Suhu",  mode="lines+markers", line=dict(color=c_l1, width=2)))
            fig_t.add_trace(go.Scatter(x=time_idx, y=temp_max, name="Max Suhu",  mode="lines+markers", line=dict(color=c_l2, width=1.5, dash="dot")))
            fig_t.update_layout(**CHART_BASE, height=220,
                xaxis=dict(showgrid=True, gridcolor=c_border, tickfont=dict(color=c_text)),
                yaxis=dict(showgrid=True, gridcolor=c_border, tickfont=dict(color=c_text), title="Celsius"),
                legend=dict(orientation="h", y=1.1, font=dict(color=c_text)))
            st.plotly_chart(fig_t, use_container_width=True, config={"displayModeBar": False})

            section("Trend Vibrasi RMS per Bucket")
            colors = ["#ff4444" if v > 2.0 else "#ffaa00" if v > 1.5 else c_l1
                      for v in vibrasi.fillna(0)]
            fig_v = go.Figure()
            fig_v.add_trace(go.Bar(x=time_idx, y=vibrasi, marker_color=colors,
                                   name="RMS Vibration", opacity=0.85))
            fig_v.add_hline(y=2.0, line=dict(color="#ff4444", width=1, dash="dash"))
            fig_v.update_layout(**CHART_BASE, height=200,
                xaxis=dict(showgrid=False, tickfont=dict(color=c_text)),
                yaxis=dict(showgrid=True, gridcolor=c_border, tickfont=dict(color=c_text), title="g RMS"),
                showlegend=False)
            st.plotly_chart(fig_v, use_container_width=True, config={"displayModeBar": False})

            section("Bucket Log")
            display_cols = [c for c in ["_id","bucket_start","count","is_closed",
                                         "vib_rms","temp_avg","temp_max"] if c in closed.columns]
            st.dataframe(closed[display_cols], use_container_width=True, hide_index=True)
        else:
            st.info("Menunggu bucket pertama selesai (butuh 300 data).")
    else:
        st.info("Belum ada data. Jalankan simulate.py untuk mulai kirim data.")

# ── FREQUENCY ANALYSIS ────────────────────────────────────────────────────────
elif menu == "Frequency Analysis":
    st.markdown(f"<h1 style='font-size:28px;color:{c_text};margin-bottom:4px'>Frequency Analysis</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:13px;color:{c_l2};margin-bottom:20px'>Visualisasi FFT dari bucket terbaru motor.</p>", unsafe_allow_html=True)

    selected_motor = st.selectbox("Motor:", motors_list)
    analytics_data = fetch(f"/analytics/{selected_motor}")

    if analytics_data and "analytics" in analytics_data:
        fft_d = analytics_data["analytics"].get("fft", {})
        freqs = fft_d.get("frequencies", [])
        mags  = fft_d.get("magnitudes",  [])
        fault = fft_d.get("detected_fault", "Normal")
        dom_f = fft_d.get("dominant_freq", 0)

        c1, c2 = st.columns(2)
        with c1:
            fault_color = "#ff4444" if fault != "Normal" else c_text
            st.markdown(f"""
            <div style="border:1px solid {c_border};padding:15px;background:{c_bg}">
                <div style="font-size:11px;text-transform:uppercase;color:{c_l2}">Detected Fault</div>
                <div style="font-size:26px;color:{fault_color};margin-top:6px">{fault}</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div style="border:1px solid {c_border};padding:15px;background:{c_bg}">
                <div style="font-size:11px;text-transform:uppercase;color:{c_l2}">Dominant Frequency</div>
                <div style="font-size:26px;color:{c_text};margin-top:6px">{round(dom_f, 2)} Hz</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if freqs and mags:
            section("FFT Spectrum")
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=freqs[:100], y=mags[:100],
                marker=dict(
                    color=mags[:100],
                    colorscale=[[0, c_bg], [0.5, c_l2], [1, c_l1]],
                    line=dict(width=0)
                ),
                name="Magnitude"
            ))
            fig.update_layout(**CHART_BASE, height=280,
                xaxis=dict(title="Frekuensi (Hz)", showgrid=True,
                           gridcolor=c_border, tickfont=dict(color=c_text)),
                yaxis=dict(title="Amplitude", showgrid=True,
                           gridcolor=c_border, tickfont=dict(color=c_text)),
                bargap=0.05)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            section("Panduan Diagnosis Frekuensi")
            st.markdown(f"""
            <div style="border:1px solid {c_border};padding:16px;background:{c_bg};line-height:2">
                <div style="color:{c_text}">20 - 30 Hz &nbsp;&nbsp; Rotor fault</div>
                <div style="color:{c_text}">45 - 55 Hz &nbsp;&nbsp; Mechanical clearance / Stator electricity</div>
                <div style="color:{c_text}">&gt; 100 Hz &nbsp;&nbsp;&nbsp; Bearing fault</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.info("Belum cukup data untuk FFT. Butuh minimal 2 measurement.")
    else:
        st.warning("Belum ada data analytics untuk motor ini.")

# ── ANOMALY LOG ───────────────────────────────────────────────────────────────
elif menu == "Anomaly Log":
    st.markdown(f"<h1 style='font-size:28px;color:{c_text};margin-bottom:4px'>Anomaly Log</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:13px;color:{c_l2};margin-bottom:20px'>Deteksi titik anomali suhu via Z-Score dari bucket terbaru.</p>", unsafe_allow_html=True)

    selected_motor = st.selectbox("Motor:", motors_list)
    analytics_data = fetch(f"/analytics/{selected_motor}")

    if analytics_data and "analytics" in analytics_data:
        anomalies = analytics_data["analytics"].get("anomalies", [])
        trend     = analytics_data["analytics"].get("trend", [])
        ph        = analytics_data["analytics"].get("predictive_health", 100)

        c1, c2 = st.columns(2)
        with c1:
            a_color = "#ff4444" if len(anomalies) > 0 else c_text
            st.markdown(f"""
            <div style="border:1px solid {c_border};padding:15px;background:{c_bg}">
                <div style="font-size:11px;text-transform:uppercase;color:{c_l2}">Anomali Terdeteksi</div>
                <div style="font-size:34px;color:{a_color};margin-top:6px">{len(anomalies)}</div>
                <div style="font-size:11px;color:{c_l2}">Z-Score threshold 3.0</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div style="border:1px solid {c_border};padding:15px;background:{c_bg}">
                <div style="font-size:11px;text-transform:uppercase;color:{c_l2}">Predictive Health</div>
                <div style="font-size:34px;color:{c_text};margin-top:6px">{ph} / 100</div>
                <div style="font-size:11px;color:{c_l2}">Dari bucket terbaru</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if trend:
            section("Temperature Trend (Smoothed Rolling Average)")
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=list(range(len(trend))), y=trend,
                mode="lines", line=dict(color=c_l1, width=1.8),
                fill="tozeroy", fillcolor="rgba(0,0,0,0.08)" if theme_mode == "Putih" else "rgba(255,255,255,0.08)",
                name="Smoothed Temp"
            ))
            if anomalies:
                an_df = pd.DataFrame(anomalies)
                if "temp" in an_df.columns:
                    fig_trend.add_trace(go.Scatter(
                        x=list(range(len(an_df))),
                        y=an_df["temp"].tolist(),
                        mode="markers",
                        marker=dict(color="#ff4444", size=8, symbol="x"),
                        name="Anomali"
                    ))
            fig_trend.update_layout(**CHART_BASE, height=220,
                xaxis=dict(showgrid=False, tickfont=dict(color=c_text), title="Index"),
                yaxis=dict(showgrid=True, gridcolor=c_border, tickfont=dict(color=c_text), title="Celsius"),
                legend=dict(font=dict(color=c_text)))
            st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})

        section("Detail Anomali")
        df_an = safe_df(anomalies)
        if not df_an.empty:
            st.dataframe(df_an, use_container_width=True, hide_index=True)
        else:
            st.markdown(f"""
            <div style="border:1px solid {c_border};padding:15px;color:{c_text};text-align:center">
                Tidak ada anomali terdeteksi (Z-Score &lt; 3.0) pada bucket saat ini.
            </div>""", unsafe_allow_html=True)
    else:
        st.warning("Belum ada data untuk dianalisis.")

# ── MAINTENANCE PREDICTOR ─────────────────────────────────────────────────────
elif menu == "Maintenance Predictor":
    st.markdown(f"<h1 style='font-size:28px;color:{c_text};margin-bottom:4px'>Maintenance Predictor</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:13px;color:{c_l2};margin-bottom:20px'>Estimasi kondisi motor dari agregat analitik semua motor.</p>", unsafe_allow_html=True)

    section("Status Semua Motor")
    for motor_id in motors_list:
        h = fetch(f"/health/{motor_id}")
        an = fetch(f"/analytics/{motor_id}")

        sc  = h.get("health_score") if h else None
        ph  = an["analytics"].get("predictive_health") if an and "analytics" in an else None
        rms = h.get("stats", {}).get("vib_rms", "N/A") if h else "N/A"
        tmp = h.get("stats", {}).get("temp_avg", "N/A") if h else "N/A"
        flt = an["analytics"]["fft"].get("detected_fault", "N/A") if an and "analytics" in an else "N/A"

        if sc is not None and sc < 40:
            status = "KRITIS — Ganti komponen segera"
            border_color = "#ff4444"
        elif sc is not None and sc < 70:
            status = "PERINGATAN — Jadwalkan maintenance minggu ini"
            border_color = "#ffaa00"
        else:
            status = "NORMAL — Tidak ada tindakan diperlukan"
            border_color = c_border

        st.markdown(f"""
        <div style="border:1px solid {border_color};padding:20px;margin-bottom:14px;background:{c_bg}">
            <div style="font-size:16px;color:{c_text};margin-bottom:12px">{motor_id}</div>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px">
                <div>
                    <div style="font-size:10px;text-transform:uppercase;color:{c_l2}">Health Score</div>
                    <div style="font-size:22px;color:{c_text}">{sc if sc is not None else 'N/A'}</div>
                </div>
                <div>
                    <div style="font-size:10px;text-transform:uppercase;color:{c_l2}">Predictive Health</div>
                    <div style="font-size:22px;color:{c_text}">{ph if ph is not None else 'N/A'}</div>
                </div>
                <div>
                    <div style="font-size:10px;text-transform:uppercase;color:{c_l2}">RMS Vibration</div>
                    <div style="font-size:22px;color:{c_text}">{rms} g</div>
                </div>
                <div>
                    <div style="font-size:10px;text-transform:uppercase;color:{c_l2}">Avg Temp</div>
                    <div style="font-size:22px;color:{c_text}">{tmp} C</div>
                </div>
            </div>
            <div style="margin-top:12px;font-size:12px;color:{c_l2}">Fault: {flt}</div>
            <div style="margin-top:6px;font-size:13px;color:{c_text}">{status}</div>
        </div>""", unsafe_allow_html=True)

    section("Panduan Rekomendasi")
    st.markdown(f"""
    <div style="border:1px solid {c_border};padding:16px;background:{c_bg};line-height:2">
        <div style="color:{c_text}">Health Score 70 - 100 &nbsp; Normal. Tidak ada tindakan.</div>
        <div style="color:{c_text}">Health Score 40 - 69  &nbsp; Peringatan. Jadwalkan maintenance minggu ini.</div>
        <div style="color:{c_text}">Health Score 0  - 39  &nbsp; Kritis. Hentikan operasi dan ganti komponen.</div>
        <div style="color:{c_l2};margin-top:8px;font-size:11px">
            Predictive Health dikurangi 5 poin per anomali suhu terdeteksi dan 20 poin bila ada fault komponen.
        </div>
    </div>""", unsafe_allow_html=True)

# ── auto refresh ──────────────────────────────────────────────────────────────
time.sleep(10)
st.rerun()
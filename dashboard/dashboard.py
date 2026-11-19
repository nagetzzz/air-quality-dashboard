import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------------ Konstanta
COLOR_BASE = "#B8C0CC"
COLOR_HIGH = "#C0392B"
COLOR_LOW = "#2E86AB"
COLOR_TEXT = "#2C3E50"
STANDARD_PM25 = 35  # standar tahunan PM2.5 China, GB 3095-2012 Grade II (µg/m³)
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
AQI_BINS = [0, 35, 75, 115, 150, 250, np.inf]
AQI_LABELS = ["Baik", "Sedang", "Tercemar Ringan", "Tercemar Sedang", "Tercemar Berat", "Sangat Berbahaya"]
AQI_COLORS = ["#2E8B57", "#F1C40F", "#E67E22", "#E74C3C", "#8E44AD", "#6E2C00"]
POLLUTANTS = {
    "PM2.5": "Partikel halus ≤ 2,5 µm",
    "PM10": "Partikel ≤ 10 µm",
    "SO2": "Sulfur dioksida",
    "NO2": "Nitrogen dioksida",
    "CO": "Karbon monoksida",
    "O3": "Ozon",
}
STATION_COORDS = {  # koordinat perkiraan stasiun pemantauan
    "Aotizhongxin": (39.982, 116.397), "Changping": (40.217, 116.230), "Dingling": (40.292, 116.220),
    "Dongsi": (39.929, 116.417), "Guanyuan": (39.929, 116.339), "Gucheng": (39.914, 116.184),
    "Huairou": (40.328, 116.628), "Nongzhanguan": (39.937, 116.461), "Shunyi": (40.127, 116.655),
    "Tiantan": (39.886, 116.407), "Wanliu": (39.987, 116.287), "Wanshouxigong": (39.878, 116.352),
}

st.set_page_config(page_title="Dashboard Kualitas Udara Beijing", page_icon="🌫️", layout="wide")

st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    .hero {background: linear-gradient(120deg, #2C3E50 0%, #4A6278 100%); color: white;
           padding: 1.6rem 2rem; border-radius: 14px; margin-bottom: 1.2rem;}
    .hero h1 {color: white; margin: 0; font-size: 2.1rem; padding: 0;}
    .hero p {color: #DCE3EA; margin: .35rem 0 0 0; font-size: 1rem;}
    .kpi {background: white; border: 1px solid #E6E9EE; border-left: 6px solid var(--accent);
          border-radius: 12px; padding: 1rem 1.2rem; height: 100%; box-shadow: 0 1px 3px rgba(0,0,0,.05);}
    .kpi .label {color: #6B7785; font-size: .85rem; margin-bottom: .25rem;}
    .kpi .value {color: #2C3E50; font-size: 1.75rem; font-weight: 700; line-height: 1.2;}
    .kpi .note {color: #8A95A3; font-size: .8rem; margin-top: .2rem;}
    .insight {background: #F4F7FA; border-left: 4px solid #2E86AB; border-radius: 8px;
              padding: .8rem 1rem; margin-top: .4rem; color: #2C3E50;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------ Data
@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main_data.csv")
    df = pd.read_csv(path, parse_dates=["datetime"])
    df["month"] = df["datetime"].dt.month
    df["hour"] = df["datetime"].dt.hour
    df["date"] = df["datetime"].dt.normalize()
    year = df["datetime"].dt.year
    start = pd.Series(np.where(df["month"] >= 3, year, year - 1), index=df.index)
    df["periode"] = start.astype(str) + "/" + (start + 1).astype(str).str[-2:]
    return df


def highlight(values):
    """Abu-abu untuk semua bar, merah untuk nilai tertinggi, biru untuk terendah."""
    values = np.asarray(values)
    colors = [COLOR_BASE] * len(values)
    if len(values) > 1:
        colors[int(np.nanargmin(values))] = COLOR_LOW
    colors[int(np.nanargmax(values))] = COLOR_HIGH
    return colors


def style(fig, height=420):
    fig.update_layout(
        height=height, margin=dict(l=10, r=10, t=50, b=10), template="plotly_white",
        font=dict(color=COLOR_TEXT), title_font_size=16, hoverlabel=dict(bgcolor="white"),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1),
    )
    return fig


def kpi(col, label, value, note, accent):
    col.markdown(
        f'<div class="kpi" style="--accent:{accent}"><div class="label">{label}</div>'
        f'<div class="value">{value}</div><div class="note">{note}</div></div>',
        unsafe_allow_html=True,
    )


def insight(text):
    st.markdown(f'<div class="insight">💡 {text}</div>', unsafe_allow_html=True)


all_df = load_data()
all_stations = sorted(all_df["station"].unique())

# ------------------------------------------------------------------ Sidebar
with st.sidebar:
    st.header("🌫️ Filter Data")
    min_date, max_date = all_df["date"].min().date(), all_df["date"].max().date()
    date_range = st.date_input("Rentang waktu", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    stations = st.multiselect("Stasiun", all_stations, default=all_stations,
                              help="Hapus beberapa stasiun untuk membandingkan stasiun tertentu saja")
    pollutant = st.radio("Polutan", list(POLLUTANTS), horizontal=True)
    st.caption(POLLUTANTS[pollutant])
    st.divider()
    with st.expander("ℹ️ Tentang dashboard"):
        st.markdown(
            "Data: **Beijing Multi-Site Air Quality**, data per jam dari 12 stasiun, "
            "1 Mar 2013 – 28 Feb 2017.\n\n"
            "Acuan: standar tahunan PM2.5 China **35 µg/m³**; kategori harian mengikuti indeks HJ 633-2012."
        )

if len(date_range) != 2 or not stations:
    st.warning("Pilih rentang tanggal (awal dan akhir) serta minimal satu stasiun.")
    st.stop()

start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
df = all_df[all_df["date"].between(start_date, end_date) & all_df["station"].isin(stations)].copy()
if df.empty:
    st.warning("Tidak ada data untuk filter yang dipilih.")
    st.stop()

# CO tersimpan dalam µg/m³, ditampilkan dalam mg/m³ agar mudah dibaca
unit_div, unit = (1000, "mg/m³") if pollutant == "CO" else (1, "µg/m³")
df["value"] = df[pollutant] / unit_div
is_pm25 = pollutant == "PM2.5"

# ------------------------------------------------------------------ Header & KPI
st.markdown(
    f"""<div class="hero"><h1>Dashboard Kualitas Udara Beijing</h1>
    <p>{start_date:%d %b %Y} – {end_date:%d %b %Y} &nbsp;·&nbsp; {len(stations)} stasiun &nbsp;·&nbsp;
    polutan <b>{pollutant}</b> ({POLLUTANTS[pollutant].lower()})</p></div>""",
    unsafe_allow_html=True,
)

daily_pm = df.groupby(["station", "date"])["PM2.5"].mean()
pm_mean = df["PM2.5"].mean()
station_mean = df.groupby("station")["value"].mean().sort_values()

c1, c2, c3, c4 = st.columns(4)
kpi(c1, f"Rata-rata {pollutant}", f"{df['value'].mean():.1f} <small>{unit}</small>",
    f"Median {df['value'].median():.1f} {unit}", COLOR_LOW)
kpi(c2, "PM2.5 vs standar China", f"{pm_mean / STANDARD_PM25:.2f}×",
    f"{pm_mean:.1f} vs {STANDARD_PM25} µg/m³", COLOR_HIGH if pm_mean > STANDARD_PM25 else "#2E8B57")
kpi(c3, "Hari tercemar", f"{(daily_pm > 75).mean() * 100:.1f}%",
    "Rata-rata PM2.5 harian > 75 µg/m³", "#E67E22")
kpi(c4, f"Stasiun {pollutant} tertinggi", station_mean.index[-1],
    f"{station_mean.iloc[-1]:.1f} {unit}", "#8E44AD")
st.write("")

tab1, tab2, tab3, tab4 = st.tabs(["📍 Per Stasiun", "🕒 Pola Waktu", "📉 Tren Tahunan", "🗺️ Kategori & Peta"])

# ------------------------------------------------------------------ Tab 1: per stasiun
with tab1:
    fig = go.Figure(go.Bar(
        x=station_mean.values, y=station_mean.index, orientation="h",
        marker_color=highlight(station_mean.values),
        text=[f"{v:.1f}" for v in station_mean.values], textposition="outside",
        hovertemplate="<b>%{y}</b><br>" + pollutant + ": %{x:.1f} " + unit + "<extra></extra>",
    ))
    if is_pm25:
        fig.add_vline(x=STANDARD_PM25, line_dash="dash", line_color="black",
                      annotation_text="Standar China 35 µg/m³", annotation_position="bottom right")
    fig.update_layout(title=f"Rata-rata {pollutant} per Stasiun", xaxis_title=f"{pollutant} ({unit})",
                      yaxis_title=None, xaxis_range=[0, station_mean.max() * 1.12])
    st.plotly_chart(style(fig, height=max(320, 38 * len(station_mean) + 90)), width="stretch")

    spread = station_mean.iloc[-1] / station_mean.iloc[0] if len(station_mean) > 1 else 1
    insight(f"<b>{station_mean.index[-1]}</b> memiliki rata-rata {pollutant} tertinggi "
            f"({station_mean.iloc[-1]:.1f} {unit}), <b>{station_mean.index[0]}</b> terendah "
            f"({station_mean.iloc[0]:.1f} {unit}), selisih {(spread - 1) * 100:.0f}%. "
            "Stasiun pusat kota cenderung lebih tercemar dibanding pinggiran utara.")

# ------------------------------------------------------------------ Tab 2: pola waktu
with tab2:
    monthly = df.groupby("month")["value"].mean().reindex(range(1, 13))
    hourly = df.groupby("hour")["value"].mean()
    left, right = st.columns(2)

    with left:
        fig = go.Figure(go.Bar(
            x=MONTH_NAMES, y=monthly.values, marker_color=highlight(monthly.fillna(0).values),
            hovertemplate="%{x}: %{y:.1f} " + unit + "<extra></extra>",
        ))
        if is_pm25:
            fig.add_hline(y=STANDARD_PM25, line_dash="dash", line_color="black",
                          annotation_text="Standar 35", annotation_position="top left")
        fig.update_layout(title="Rata-rata per Bulan", yaxis_title=f"{pollutant} ({unit})")
        st.plotly_chart(style(fig), width="stretch")

    with right:
        fig = go.Figure(go.Scatter(
            x=hourly.index, y=hourly.values, mode="lines+markers", line=dict(color=COLOR_BASE, width=3),
            hovertemplate="Pukul %{x}.00: %{y:.1f} " + unit + "<extra></extra>", showlegend=False,
        ))
        for idx, color, name in [(hourly.idxmax(), COLOR_HIGH, "Puncak"), (hourly.idxmin(), COLOR_LOW, "Terendah")]:
            fig.add_trace(go.Scatter(x=[idx], y=[hourly[idx]], mode="markers+text", marker=dict(size=13, color=color),
                                     text=[f"{name} {idx:02d}.00"], textposition="top center",
                                     hoverinfo="skip", showlegend=False))
        fig.update_layout(title="Rata-rata per Jam", xaxis_title="Jam", yaxis_title=f"{pollutant} ({unit})",
                          yaxis_range=[0, hourly.max() * 1.18], xaxis=dict(dtick=2))
        st.plotly_chart(style(fig), width="stretch")

    heat = df.pivot_table(index="month", columns="hour", values="value", aggfunc="mean")
    fig = px.imshow(heat.values, x=list(heat.columns), y=[MONTH_NAMES[m - 1] for m in heat.index],
                    color_continuous_scale="Reds", aspect="auto",
                    labels=dict(x="Jam", y="Bulan", color=f"{pollutant} ({unit})"))
    fig.update_layout(title="Kombinasi Bulan × Jam")
    st.plotly_chart(style(fig, height=380), width="stretch")

    insight(f"Puncak bulanan pada <b>{MONTH_NAMES[int(monthly.idxmax()) - 1]}</b> ({monthly.max():.1f} {unit}) "
            f"dan terendah pada <b>{MONTH_NAMES[int(monthly.idxmin()) - 1]}</b> ({monthly.min():.1f} {unit}). "
            f"Dalam sehari, tertinggi pukul <b>{hourly.idxmax():02d}.00</b> dan terendah pukul "
            f"<b>{hourly.idxmin():02d}.00</b>.")

# ------------------------------------------------------------------ Tab 3: tren
with tab3:
    ts = df.set_index("datetime")["value"].resample("MS").mean().dropna()
    fig = go.Figure(go.Scatter(x=ts.index, y=ts.values, mode="lines", line=dict(color=COLOR_HIGH, width=2.5),
                               fill="tozeroy", fillcolor="rgba(192,57,43,0.08)",
                               hovertemplate="%{x|%b %Y}: %{y:.1f} " + unit + "<extra></extra>"))
    if is_pm25:
        fig.add_hline(y=STANDARD_PM25, line_dash="dash", line_color="black",
                      annotation_text="Standar China 35 µg/m³", annotation_position="top left")
    fig.update_layout(title=f"Rata-rata Bulanan {pollutant}", yaxis_title=f"{pollutant} ({unit})",
                      yaxis_range=[0, ts.max() * 1.15])
    st.plotly_chart(style(fig, height=380), width="stretch")

    periode_all = df.groupby("periode")["value"].mean()
    periode_station = df.pivot_table(index="station", columns="periode", values="value", aggfunc="mean")
    left, right = st.columns(2)
    with left:
        fig = go.Figure(go.Scatter(
            x=periode_all.index, y=periode_all.values, mode="lines+markers+text",
            line=dict(color=COLOR_HIGH, width=3), marker=dict(size=10),
            text=[f"{v:.1f}" for v in periode_all.values], textposition="top center",
            hovertemplate="%{x}: %{y:.1f} " + unit + "<extra></extra>",
        ))
        fig.update_layout(title="Rata-rata per Periode (Maret–Februari)", xaxis_title="Periode",
                          yaxis_title=f"{pollutant} ({unit})", yaxis_range=[0, periode_all.max() * 1.2],
                          xaxis_type="category")
        st.plotly_chart(style(fig), width="stretch")

    has_change = {"2013/14", "2016/17"}.issubset(periode_station.columns)
    with right:
        if has_change:
            chg = ((periode_station["2016/17"] / periode_station["2013/14"] - 1) * 100).dropna().sort_values(
                ascending=False)
            fig = go.Figure(go.Bar(
                x=chg.values, y=chg.index, orientation="h", marker_color=highlight(-chg.values),
                text=[f"{v:+.1f}%" for v in chg.values], textposition="outside",
                hovertemplate="<b>%{y}</b><br>Perubahan: %{x:.1f}%<extra></extra>",
            ))
            fig.add_vline(x=0, line_color="black", line_width=1)
            fig.update_layout(title="Perubahan per Stasiun, 2013/14 → 2016/17", xaxis_title="Perubahan (%)",
                              xaxis_range=[min(chg.min(), 0) * 1.3 - 1, max(chg.max(), 0) * 1.3 + 1])
            st.plotly_chart(style(fig), width="stretch")
        else:
            st.info("Pilih rentang waktu yang mencakup periode 2013/14 dan 2016/17 untuk melihat perubahan per stasiun.")

    if has_change:
        total = (periode_all["2016/17"] / periode_all["2013/14"] - 1) * 100
        insight(f"Rata-rata {pollutant} berubah <b>{total:+.1f}%</b> dari 2013/14 ke 2016/17. "
                f"Perubahan paling besar di <b>{chg.idxmin()}</b> ({chg.min():+.1f}%) dan paling kecil di "
                f"<b>{chg.idxmax()}</b> ({chg.max():+.1f}%).")

# ------------------------------------------------------------------ Tab 4: kategori & peta
with tab4:
    st.caption("Kategori berdasarkan rata-rata PM2.5 harian (binning, indeks kualitas udara China HJ 633-2012).")
    cat_df = daily_pm.reset_index(name="pm25")
    cat_df["kategori"] = pd.cut(cat_df["pm25"], bins=AQI_BINS, labels=AQI_LABELS)
    pct_all = cat_df["kategori"].value_counts(normalize=True).reindex(AQI_LABELS).fillna(0) * 100

    left, right = st.columns([1, 1.4])
    with left:
        fig = go.Figure(go.Pie(labels=pct_all.index, values=pct_all.values, hole=0.55, sort=False,
                               marker=dict(colors=AQI_COLORS), textinfo="percent",
                               hovertemplate="%{label}: %{value:.1f}% hari<extra></extra>"))
        fig.update_layout(title="Proporsi Hari per Kategori",
                          annotations=[dict(text=f"<b>{pct_all['Baik']:.0f}%</b><br>hari Baik",
                                            showarrow=False, font_size=16)])
        fig = style(fig)
        fig.update_layout(legend=dict(orientation="v", y=0.5, yanchor="middle", x=1.02, xanchor="left"))
        st.plotly_chart(fig, width="stretch")

    with right:
        per_station = (cat_df.groupby("station", observed=True)["kategori"].value_counts(normalize=True)
                       .mul(100).rename("persen").reset_index())
        order = cat_df.assign(t=cat_df["pm25"] > 75).groupby("station")["t"].mean().sort_values().index.tolist()
        fig = px.bar(per_station, x="persen", y="station", color="kategori", orientation="h",
                     category_orders={"kategori": AQI_LABELS, "station": order[::-1]},
                     color_discrete_sequence=AQI_COLORS,
                     labels={"persen": "Persentase hari (%)", "station": "", "kategori": ""})
        fig.update_traces(hovertemplate="%{y}: %{x:.1f}%<extra></extra>")
        fig.update_layout(title="Komposisi Kategori per Stasiun (urut dari paling tercemar)", barmode="stack",
                          xaxis_range=[0, 100])
        fig = style(fig, height=max(420, 30 * len(order) + 120))
        fig.update_layout(legend=dict(y=-0.25, yanchor="top", x=0.5, xanchor="center"))
        st.plotly_chart(fig, width="stretch")

    geo = df.groupby("station")["PM2.5"].mean().reset_index(name="pm25")
    geo["lat"] = geo["station"].map(lambda s: STATION_COORDS[s][0])
    geo["lon"] = geo["station"].map(lambda s: STATION_COORDS[s][1])
    fig = px.scatter_map(geo, lat="lat", lon="lon", size="pm25", color="pm25", hover_name="station",
                         color_continuous_scale="YlOrRd", size_max=22, zoom=8.8,
                         center=dict(lat=40.08, lon=116.40), map_style="carto-positron",
                         labels={"pm25": "PM2.5 (µg/m³)"},
                         hover_data={"lat": False, "lon": False, "pm25": ":.1f"})
    fig.update_layout(title="Peta Rata-rata PM2.5 per Stasiun")
    st.plotly_chart(style(fig, height=520), width="stretch")

    insight(f"Hanya <b>{pct_all['Baik']:.1f}%</b> hari berkategori Baik, sementara "
            f"<b>{pct_all[AQI_LABELS[2:]].sum():.1f}%</b> hari tergolong tercemar. Di peta, lingkaran besar "
            "berwarna merah berkumpul di pusat kota, sedangkan pinggiran utara lebih bersih. "
            "Koordinat stasiun bersifat perkiraan.")

st.caption("Proyek Analisis Data · Dicoding · Beijing Multi-Site Air Quality Dataset (Mar 2013 – Feb 2017)")

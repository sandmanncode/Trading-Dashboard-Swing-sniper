import time
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
from plotly.subplots import make_subplots

st.set_page_config(page_title="882 Swing Sniper & Alarms", layout="wide")

CSS = """
<style>
.main { background-color: #0e1117; color: #ffffff; }
.card {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}
.metric-card {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 15px;
    text-align: center;
    margin-bottom: 10px;
}
.metric-card h4 { margin: 0 0 6px 0; color: #8b949e; font-size: 14px; }
.metric-card h2, .metric-card h3 { margin: 0; }
.metric-card p { margin: 6px 0 0 0; font-size: 13px; color: #8b949e; }
.alert-box {
    background-color: rgba(255, 165, 0, 0.1);
    border: 1px solid #ffa500;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 15px;
    color: #ffa500;
    font-weight: bold;
}
.status-bar { font-size: 13px; color: #8b949e; margin-bottom: 15px; }
.fg-card {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
    margin: 10px 0 20px 0;
}
.fg-emoji { font-size: 56px; line-height: 1.1; }
.fg-value { font-size: 26px; font-weight: 800; margin-top: 4px; }
.fg-text { font-size: 15px; color: #c9d1d9; margin-top: 4px; }
.entry-highlight {
    font-size: 24px;
    font-weight: 800;
    color: #ffffff;
    background: rgba(255, 255, 255, 0.06);
    padding: 6px 12px;
    border-radius: 6px;
    display: inline-block;
    margin: 6px 0 10px 0;
}
.row-line { font-size: 14px; margin: 3px 0; }
.progress-bg {
    background-color: #30363d;
    border-radius: 6px;
    height: 10px;
    width: 100%;
    margin-top: 6px;
}
.progress-fill { height: 10px; border-radius: 6px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

st.title("⚡ 882 Swing Sniper · Heatmap & Alarms Edition")
st.caption("Live Multi-Timeframe Analysis · Orderblocks · Volume Profile · Liquidity Heatmap · Alarm-System")
st.markdown(
    f"<div class='status-bar'>🕓 Zuletzt aktualisiert: {datetime.now().strftime('%H:%M:%S')} Uhr</div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- Sidebar
st.sidebar.header("Dashboard-Steuerung")
coin_choice = st.sidebar.selectbox("Wähle einen Coin", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"])

timeframe_options = {
    "15 Minuten": "15m",
    "30 Minuten": "30m",
    "1 Stunde": "1h",
    "2 Stunden": "2h",
    "4 Stunden": "4h",
    "12 Stunden": "12h",
    "1 Tag": "1d",
    "3 Tage": "3d",
}
timeframe_label = st.sidebar.selectbox("Zeitfenster", list(timeframe_options.keys()), index=4)
tf = timeframe_options[timeframe_label]

st.sidebar.markdown("---")
st.sidebar.header("🔔 Alarm-System")
selected_alarm = st.sidebar.selectbox(
    "Wähle Alarm-Typ",
    [
        "Kein Alarm aktiv",
        "1. 882 Long/Short Zonen-Alarm (Preis berührt Zone)",
        "2. RSI Extreme Alarm (RSI > 70 oder < 30)",
        "3. Liquidations-Spike Alarm (Hoher Heatmap-Druck)",
    ],
)
alarm_active = st.sidebar.checkbox("Alarm scharf schalten", value=True)


# ---------------------------------------------------------------- Daten
@st.cache_data(ttl=60)
def fetch_binance_data(symbol, interval, max_retries=3):
    clean_symbol = symbol.replace("/", "")
    url = f"https://api.binance.com/api/v3/klines?symbol={clean_symbol}&interval={interval}&limit=120"
    last_error = None

    for versuch in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=10)
            data = response.json()

            if isinstance(data, dict) and "code" in data:
                raise ValueError(f"Binance-Fehler: {data.get('msg', 'Unbekannt')} (Code: {data.get('code')})")
            if not data:
                raise ValueError("Keine Daten erhalten")

            df = pd.DataFrame(data, columns=[
                "timestamp", "open", "high", "low", "close", "volume",
                "close_time", "quote_asset_volume", "number_of_trades",
                "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore",
            ])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            for col in ["open", "high", "low", "close", "volume"]:
                df[col] = df[col].astype(float)
            return df
        except Exception as e:
            last_error = e
            if versuch < max_retries:
                time.sleep(1.5 * versuch)

    raise RuntimeError(f"Binance-Abfrage nach {max_retries} Versuchen fehlgeschlagen: {last_error}")


@st.cache_data(ttl=300)
def fetch_fear_greed(max_retries=3):
    url = "https://api.alternative.me/fng/?limit=1&format=json"
    for versuch in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=10)
            entry = response.json()["data"][0]
            return int(entry["value"]), entry["value_classification"]
        except Exception:
            if versuch < max_retries:
                time.sleep(1.5 * versuch)
    return None, None


def calculate_analytics(df):
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))
    df["liquidity_score"] = df["volume"] * (df["high"] - df["low"])
    return df


def proximity_percent(current_price, zone_low, zone_high):
    if zone_low <= current_price <= zone_high:
        return 100.0
    distance = min(abs(current_price - zone_low), abs(current_price - zone_high))
    return round(max(0.0, 100 - (distance / current_price * 1000)), 1)


# ---------------------------------------------------------------- HTML-Bausteine
def metric_card(title, value, sub, color="#ffffff", border="#30363d"):
    return (
        f"<div class='metric-card' style='border-color:{border};'>"
        f"<h4>{title}</h4>"
        f"<h2 style='color:{color};'>{value}</h2>"
        f"<p>{sub}</p>"
        f"</div>"
    )


def setup_card(title, status, color, zone_low, zone_high, entry, stop, tp1, tp2, proximity):
    return (
        f"<div class='card' style='border-left: 5px solid {color};'>"
        f"<h3 style='color:{color}; margin-top:0;'>{title}</h3>"
        f"<p style='background:rgba(255,255,255,0.05); padding:8px; border-radius:5px; font-size:13px;'>{status}</p>"
        f"<div class='row-line'><b>Entry</b></div>"
        f"<div class='entry-highlight' style='color:{color};'>${entry:,.2f}</div>"
        f"<div class='row-line'><b>Zone:</b> ${zone_low:,.2f} – ${zone_high:,.2f}</div>"
        f"<div class='row-line'><b>Stop-Loss:</b> ${stop:,.2f}</div>"
        f"<div class='row-line'><b>TP1:</b> ${tp1:,.2f}</div>"
        f"<div class='row-line'><b>TP2:</b> ${tp2:,.2f}</div>"
        f"<div class='row-line' style='margin-top:10px;'>Nähe zur Zone: {proximity:.0f}%</div>"
        f"<div class='progress-bg'><div class='progress-fill' style='width:{proximity}%; background:{color};'></div></div>"
        f"</div>"
    )


# ---------------------------------------------------------------- Fear & Greed
fg_value, fg_class = fetch_fear_greed()
fg_map = {
    "Extreme Fear": ("😱", "#ff4d4d", "Panik pur – viele verkaufen aus Angst."),
    "Fear": ("😨", "#ff8c42", "Vorsicht überwiegt am Markt."),
    "Neutral": ("😐", "#ffd93d", "Der Markt ist unentschlossen."),
    "Greed": ("😏", "#8ce99a", "Optimismus macht sich breit."),
    "Extreme Greed": ("🤑", "#00ffcc", "Exxxcellent! Es wird euphorisch – Vorsicht vor der Blase."),
}
fg_emoji, fg_color, fg_text = fg_map.get(fg_class, ("❓", "#8b949e", "Keine Daten verfügbar"))
fg_number = fg_value if fg_value is not None else "--"

st.markdown(
    f"<div class='fg-card' style='border-color:{fg_color};'>"
    f"<div style='color:#8b949e; font-size:14px;'>😎 Markt-Stimmung · Fear &amp; Greed Index</div>"
    f"<div class='fg-emoji'>{fg_emoji}</div>"
    f"<div class='fg-value' style='color:{fg_color};'>{fg_number} / 100 · {fg_class or 'n/a'}</div>"
    f"<div class='fg-text'>{fg_text}</div>"
    f"</div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- Hauptdaten (nur 1 Abfrage)
try:
    df = fetch_binance_data(coin_choice, tf)
except Exception as e:
    st.error(str(e))
    st.stop()

df = calculate_analytics(df)

current_price = df["close"].iloc[-1]
price_change = current_price - df["close"].iloc[0]
rsi_val = df["rsi"].iloc[-1]
if pd.isna(rsi_val):
    rsi_val = 50.0

long_zone_low = current_price * 0.84
long_zone_high = current_price * 0.87
short_zone_low = current_price * 0.99
short_zone_high = current_price * 1.02

# ---------------------------------------------------------------- Alarm-Logik
alarm_triggered = False
alarm_message = ""
if alarm_active:
    in_long = long_zone_low <= current_price <= long_zone_high
    in_short = short_zone_low <= current_price <= short_zone_high
    if "1." in selected_alarm and (in_long or in_short):
        alarm_triggered = True
        alarm_message = f"🚨 ALARM: Kurs (${current_price:,.2f}) hat die 882 Long/Short-Zone erreicht!"
    elif "2." in selected_alarm and (rsi_val > 70 or rsi_val < 30):
        alarm_triggered = True
        alarm_message = f"🚨 ALARM: RSI im Extrembereich ({rsi_val:.1f})!"
    elif "3." in selected_alarm and df["liquidity_score"].iloc[-1] > df["liquidity_score"].mean() * 1.5:
        alarm_triggered = True
        alarm_message = "🚨 ALARM: Hoher Liquidations-Spike in der Heatmap erkannt!"

# ---------------------------------------------------------------- KPI-Leiste
rsi_color = "#ff4d4d" if rsi_val > 70 else "#00ffcc" if rsi_val < 30 else "#8b949e"
rsi_text = "Überkauft" if rsi_val > 70 else "Überverkauft" if rsi_val < 30 else "Neutral"
change_color = "#00ffcc" if price_change >= 0 else "#ff4d4d"
alarm_state = "Alarm scharf" if (alarm_active and selected_alarm != "Kein Alarm aktiv") else "Alarm aus"

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(
        metric_card(f"{coin_choice} ({tf})", f"${current_price:,.2f}", f"{price_change:+,.2f} USD", color=change_color),
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(metric_card("Swing-Signal", "WAIT", "Kein Setup bestätigt", color="#ffa500"), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card("Markt-Bias", "NEUTRAL", "Trend unentschieden"), unsafe_allow_html=True)
with c4:
    st.markdown(
        metric_card("RSI (14)", f"{rsi_val:.1f}", rsi_text, color=rsi_color, border=rsi_color),
        unsafe_allow_html=True,
    )
with c5:
    st.markdown(metric_card("Status", "LIVE", alarm_state, color="#00ffcc"), unsafe_allow_html=True)

if alarm_triggered:
    st.markdown(f"<div class='alert-box'>{alarm_message}</div>", unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------------- Chart + Setup-Karten
chart_col, info_col = st.columns([3, 1])

with chart_col:
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03,
        row_heights=[0.60, 0.20, 0.20],
        subplot_titles=(f"{coin_choice} Preis & Volumenspitzen", "RSI (14)", "Liquidations-Heatmap (Cluster)"),
    )
    fig.add_trace(go.Candlestick(
        x=df["timestamp"], open=df["open"], high=df["high"],
        low=df["low"], close=df["close"], name=coin_choice,
    ), row=1, col=1)
    fig.add_trace(go.Bar(
        x=df["timestamp"], y=df["volume"], name="Volumen",
        marker_color="rgba(100, 150, 250, 0.3)",
    ), row=1, col=1)
    fig.add_hrect(y0=long_zone_low, y1=long_zone_high, fillcolor="green", opacity=0.12, line_width=0, row=1, col=1)
    fig.add_hrect(y0=short_zone_low, y1=short_zone_high, fillcolor="red", opacity=0.12, line_width=0, row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["rsi"], name="RSI", line=dict(color="#00ffcc", width=2),
    ), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["liquidity_score"], fill="tozeroy", name="Liquidations-Druck",
        line=dict(color="#ff9900", width=2), fillcolor="rgba(255, 153, 0, 0.2)",
    ), row=3, col=1)
    fig.update_layout(
        template="plotly_dark", height=750, xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=30, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

with info_col:
    long_prox = proximity_percent(current_price, long_zone_low, long_zone_high)
    short_prox = proximity_percent(current_price, short_zone_low, short_zone_high)

    st.markdown(
        setup_card(
            "🟢 882 LONG", "Warte auf Long-Zone (82-88% Retracement)", "#00ffcc",
            long_zone_low, long_zone_high,
            current_price * 0.855, current_price * 0.82,
            current_price * 0.90, current_price * 0.94, long_prox,
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        setup_card(
            "🔴 882 SHORT", "Kurs nahe der Short-Zone" if short_prox >= 100 else "Warte auf Short-Zone", "#ff4d4d",
            short_zone_low, short_zone_high,
            current_price * 1.005, current_price * 1.04,
            current_price * 0.96, current_price * 0.92, short_prox,
        ),
        unsafe_allow_html=True,
    )

import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Layout auf "Wide" für das Trader-Terminal
st.set_page_config(page_title="882 Swing Sniper · Cloud Edition", layout="wide")

# Custom Styling
st.markdown("""
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
    }
    </style>
""", unsafe_allow_html=True)

# Titelbereich
st.title("⚡ 882 Swing Sniper · UHLMA & Andean Oszillator")
st.caption("Cloud-Ready Edition (Powered by Yahoo Finance)")

# Sidebar
st.sidebar.header("Dashboard-Steuerung")
coin_choice = st.sidebar.selectbox("Wähle einen Coin", ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD"])
timeframe = st.sidebar.selectbox("Zeitrahmen", ["15m", "30m", "1h", "1d"], index=2)

# Intervall-Mapping für yfinance
tf_mapping = {"15m": "15m", "30m": "30m", "1h": "1h", "1d": "1d"}
period_mapping = {"15m": "5d", "30m": "5d", "1h": "30d", "1d": "1max"}

# Daten von Yahoo Finance laden (umgeht Binance Cloud-Sperre)
@st.cache_data(ttl=60)
def fetch_crypto_data(symbol, interval):
    period = "60d" if interval in ["15m", "30m", "1h"] else "max"
    df = yf.download(symbol, period=period, interval=interval, progress=False)
    
    # MultiIndex-Spalten von yfinance bereinigen falls vorhanden
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    df = df.reset_index()
    # Spaltennamen anpassen
    df.rename(columns={
        'Datetime': 'timestamp', 
        'Date': 'timestamp',
        'Open': 'open', 
        'High': 'high', 
        'Low': 'low', 
        'Close': 'close', 
        'Volume': 'volume'
    }, inplace=True)
    
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = df[col].astype(float)
    return df

# Indikatoren-Berechnung
def calculate_custom_indicators(df):
    df['uhlma'] = df['close'].rolling(window=20).mean()
    df['uhlma_trend'] = df['uhlma'].diff().apply(lambda x: 'Green' if x >= 0 else 'Red')
    
    df['signal'] = 'HOLD'
    df.loc[(df['uhlma_trend'] == 'Green') & (df['uhlma_trend'].shift(1) == 'Red'), 'signal'] = 'BUY'
    df.loc[(df['uhlma_trend'] == 'Red') & (df['uhlma_trend'].shift(1) == 'Green'), 'signal'] = 'SELL'

    spread = df['high'] - df['low']
    df['andean_bull'] = (spread * (df['close'] >= df['open'])).rolling(window=14).mean()
    df['andean_bear'] = (spread * (df['close'] < df['open'])).rolling(window=14).mean()
    
    return df

try:
    df = fetch_crypto_data(coin_choice, timeframe)
    df = calculate_custom_indicators(df)

    current_price = df['close'].iloc[-1]
    price_change = current_price - df['close'].iloc[0]
    last_signal = df['signal'].iloc[-1]

    # Top KPI-Leiste
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"<div class='metric-card'><h4>{coin_choice}</h4><h2>${current_price:,.2f}</h2><p style='color: {'#00ffcc' if price_change >= 0 else '#ff4d4d'};'>{price_change:+,.2f} USD</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card'><h4>UHLMA Signal</h4><h3 style='color: {'#00ffcc' if last_signal == 'BUY' else '#ff4d4d' if last_signal == 'SELL' else '#ffa500'};'>{last_signal}</h3><p>Trend-Bestätigung</p></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-card'><h4>Trend-Status</h4><h3>{'BULLISCH 🟢' if df['uhlma_trend'].iloc[-1] == 'Green' else 'BÄRISCH 🔴'}</h3><p>UHLMA Linie</p></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='metric-card'><h4>Zeitrahmen</h4><h3>{timeframe}</h3><p>Aktiver Intervall</p></div>", unsafe_allow_html=True)
    with c5:
        st.markdown(f"<div class='metric-card'><h4>Status</h4><h3 style='color: #00ffcc;'>LIVE</h3><p>Verbunden</p></div>", unsafe_allow_html=True)

    st.markdown("---")

    chart_col, info_col = st.columns([3, 1])

    with chart_col:
        fig = make_subplots(
            rows=2, cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.03, 
            row_heights=[0.70, 0.30],
            subplot_titles=(f"{coin_choice} Chart mit UHLMA & Signalen", "Andean Oscillator")
        )
        
        fig.add_trace(go.Candlestick(
            x=df['timestamp'], open=df['open'], high=df['high'],
            low=df['low'], close=df['close'], name=coin_choice
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['uhlma'], name="UHLMA", 
            line=dict(color="#00ffcc" if df['uhlma_trend'].iloc[-1] == 'Green' else "#ff4d4d", width=2.5)
        ), row=1, col=1)

        buy_signals = df[df['signal'] == 'BUY']
        sell_signals = df[df['signal'] == 'SELL']
        
        fig.add_trace(go.Scatter(
            x=buy_signals['timestamp'], y=buy_signals['low'] * 0.99, mode='text+markers',
            marker=dict(symbol='triangle-up', size=12, color='green'), text="BUY", textposition="bottom center", name="Buy Signal"
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=sell_signals['timestamp'], y=sell_signals['high'] * 1.01, mode='text+markers',
            marker=dict(symbol='triangle-down', size=12, color='red'), text="SELL", textposition="top center", name="Sell Signal"
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['andean_bull'], name="Bull Line", 
            line=dict(color="#00ffcc", width=2), fill='tozeroy', fillcolor='rgba(0, 255, 204, 0.1)'
        ), row=2, col=1)
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['andean_bear'], name="Bear Line", 
            line=dict(color="#ff4d4d", width=2), fill='tozeroy', fillcolor='rgba(255, 77, 77, 0.1)'
        ), row=2, col=1)

        fig.update_layout(template="plotly_dark", height=750, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with info_col:
        st.markdown("""
            <div class="card" style="border-left: 5px solid #00ffcc;">
                <h3 style="color: #00ffcc; margin-top: 0;">🎯 Setup Info</h3>
                <p style="font-size: 13px;">Datenquelle: Yahoo Finance (Cloud-kompatibel)</p>
            </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Fehler beim Laden der Daten: {e}")

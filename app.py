import json
import time
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
import streamlit.components.v1 as components
from plotly.subplots import make_subplots

st.set_page_config(page_title="Swing Sniper · Master-Terminal", page_icon="⚡", layout="wide")

CSS = """
<style>
.main { background-color: #0e1117; color: #ffffff; }
.card {
    background-color: #161b22; border: 1px solid #30363d; border-radius: 10px;
    padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}
.metric-card {
    background-color: #161b22; border: 1px solid #30363d; border-radius: 8px;
    padding: 15px; text-align: center; margin-bottom: 10px;
}
.metric-card h4 { margin: 0 0 6px 0; color: #8b949e; font-size: 14px; }
.metric-card h2, .metric-card h3 { margin: 0; }
.metric-card p { margin: 6px 0 0 0; font-size: 13px; color: #8b949e; }
.alert-box {
    background-color: rgba(255, 165, 0, 0.1); border: 1px solid #ffa500; border-radius: 8px;
    padding: 10px; margin-bottom: 15px; color: #ffa500; font-weight: bold;
}
.status-bar { font-size: 13px; color: #8b949e; margin-bottom: 15px; }
.fg-card {
    background-color: #161b22; border: 1px solid #30363d; border-radius: 12px;
    padding: 18px; text-align: center; margin: 10px 0 20px 0;
}
.fg-emoji { font-size: 56px; line-height: 1.1; }
.fg-value { font-size: 26px; font-weight: 800; margin-top: 4px; }
.fg-text { font-size: 15px; color: #c9d1d9; margin-top: 4px; }
.entry-highlight {
    font-size: 24px; font-weight: 800; background: rgba(255, 255, 255, 0.06);
    padding: 6px 12px; border-radius: 6px; display: inline-block; margin: 6px 0 10px 0;
}
.row-line { font-size: 14px; margin: 3px 0; }
.progress-bg { background-color: #30363d; border-radius: 6px; height: 10px; width: 100%; margin-top: 6px; }
.progress-fill { height: 10px; border-radius: 6px; }
.tip {
    background-color: #161b22; border: 1px solid #30363d; border-left: 4px solid #58a6ff;
    border-radius: 6px; padding: 10px 14px; margin: 6px 0; font-size: 14px; color: #e6edf3;
}
.tip-good { border-left-color: #00ffcc; }
.tip-warn { border-left-color: #ffa500; }
.tip-info { border-left-color: #58a6ff; }
.pattern-guide-box {
    background-color: #161b22; border: 1px solid #30363d; border-radius: 8px;
    padding: 12px 14px; margin-bottom: 10px;
}
.pattern-guide-box h5 { margin: 6px 0 4px 0; font-size: 16px; }
.pattern-guide-box p { margin: 0; font-size: 13px; color: #c9d1d9; }
.pattern-tag { font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 10px; display: inline-block; }
.tag-bullish { background: rgba(0, 255, 204, 0.15); color: #00ffcc; }
.tag-bearish { background: rgba(255, 77, 77, 0.15); color: #ff4d4d; }
.tag-avoid { background: rgba(255, 165, 0, 0.15); color: #ffa500; }
.sizing-table { width: 100%; border-collapse: collapse; margin-bottom: 18px; font-size: 13px; }
.sizing-table th {
    background-color: #161b22; color: #8b949e; text-align: left; padding: 8px 10px;
    border-bottom: 1px solid #30363d; font-size: 12px;
}
.sizing-table td {
    background-color: #0e1117; padding: 8px 10px; border-bottom: 1px solid #21262d; vertical-align: top;
}
.rules-box {
    background-color: rgba(255, 77, 77, 0.08); border: 1px solid #ff4d4d; border-radius: 8px;
    padding: 10px 14px; margin-bottom: 14px; font-size: 14px; color: #ffb3b3;
}

.stApp { background: radial-gradient(1200px 600px at 8% -10%, #12232d 0%, #0b0e14 55%) fixed; }
.block-container { padding-top: 1.4rem; max-width: 1600px; }
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] { background: #161b22; border-radius: 8px 8px 0 0; padding: 10px 18px; font-size: 16px; }
.stTabs [aria-selected="true"] { background: #1f2a36; }
.mtf-badge { display: inline-block; padding: 4px 12px; border-radius: 6px; font-weight: 700; font-size: 14px; margin: 2px 6px 2px 0; }
.mtf-green { background: rgba(0,255,204,0.15); color: #00ffcc; border: 1px solid #00ffcc; }
.mtf-red { background: rgba(255,77,77,0.15); color: #ff4d4d; border: 1px solid #ff4d4d; }
.mtf-grey { background: rgba(139,148,158,0.15); color: #c9d1d9; border: 1px solid #8b949e; }
.score-box { background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(22,27,34,0.95)); border: 2px solid #30363d;
    border-radius: 12px; padding: 14px 16px; margin-bottom: 12px; }
.score-title { color: #8b949e; font-size: 14px; }
.score-value { font-size: 40px; font-weight: 800; line-height: 1.1; margin: 4px 0; }
.score-of { font-size: 16px; color: #8b949e; font-weight: 400; }
.score-label { color: #c9d1d9; font-size: 13px; margin-bottom: 6px; }
.score-parts { margin-top: 8px; font-size: 12px; color: #8b949e; }
.score-row { display: flex; justify-content: space-between; padding: 1px 0; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------- Daten & Berechnungen
@st.cache_data(ttl=300)
def fetch_eur_usdt():
    """Wie viele USDT ist 1 € wert? Erst Binance, dann Ersatzquelle."""
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=EURUSDT", timeout=10).json()
        return float(r["price"])
    except Exception:
        pass
    try:
        r = requests.get("https://api.frankfurter.app/latest?from=EUR&to=USD", timeout=10).json()
        return float(r["rates"]["USD"])
    except Exception:
        return None


@st.cache_data(ttl=60)
def fetch_binance_data(symbol, interval, max_retries=3, limit=500):
    clean_symbol = symbol.replace("/", "")
    url = f"https://api.binance.com/api/v3/klines?symbol={clean_symbol}&interval={interval}&limit={limit}"
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
    prev_close = df["close"].shift(1)
    true_range = pd.concat(
        [df["high"] - df["low"], (df["high"] - prev_close).abs(), (df["low"] - prev_close).abs()], axis=1
    ).max(axis=1)
    df["atr"] = true_range.rolling(window=14).mean()
    for length in (21, 50, 200):
        df[f"ema{length}"] = df["close"].ewm(span=length, adjust=False).mean()
    return df


# ---------------------------------------------------------------- Swing-Struktur & Einstiege
def find_pivots(df, k=5):
    """Findet Swing-Hochs (H) und Swing-Tiefs (L); gleiche Typen hintereinander werden zusammengefasst."""
    highs, lows = df["high"].to_numpy(), df["low"].to_numpy()
    raw = []
    for i in range(k, len(df) - k):
        if highs[i] == highs[i - k:i + k + 1].max():
            raw.append((i, "H", float(highs[i])))
        if lows[i] == lows[i - k:i + k + 1].min():
            raw.append((i, "L", float(lows[i])))
    raw.sort(key=lambda p: p[0])
    cleaned = []
    for p in raw:
        if cleaned and cleaned[-1][1] == p[1]:
            last = cleaned[-1]
            if (p[1] == "H" and p[2] >= last[2]) or (p[1] == "L" and p[2] <= last[2]):
                cleaned[-1] = p
        else:
            cleaned.append(p)
    return cleaned


def latest_legs(pivots, min_size):
    """Letzter Aufwärts-Swing (Tief -> Hoch) und letzter Abwärts-Swing (Hoch -> Tief)."""
    up = down = None
    for a, b in zip(pivots, pivots[1:]):
        if a[1] == "L" and b[1] == "H" and b[2] - a[2] >= min_size:
            up = (a[2], b[2])
        if a[1] == "H" and b[1] == "L" and a[2] - b[2] >= min_size:
            down = (b[2], a[2])
    return up, down


def fib_setup(direction, low, high, atr, name, short, zone_r, entry_r, sl_r, tp_rs):
    leg = high - low

    def price(r):
        return high - r * leg if direction == "long" else low + r * leg

    zone = sorted([price(zone_r[0]), price(zone_r[1])])
    buf = 0.2 * atr
    sl = price(sl_r) - buf if direction == "long" else price(sl_r) + buf
    return {
        "name": name, "short": short, "direction": direction, "draw": True,
        "zone_lo": zone[0], "zone_hi": zone[1], "entry": price(entry_r), "sl": sl,
        "tps": [price(r) for r in tp_rs],
    }


def ema_setup(direction, ema_value, atr, length, current_price):
    if direction == "long" and ema_value >= current_price:
        return None
    if direction == "short" and ema_value <= current_price:
        return None
    risk = 1.5 * atr
    sign = 1 if direction == "long" else -1
    entry = ema_value
    return {
        "name": f"EMA {length} Pullback (TPs: 1,5R / 3R / 5R)", "short": f"EMA {length}",
        "direction": direction, "draw": False,
        "zone_lo": entry - 0.25 * atr, "zone_hi": entry + 0.25 * atr, "entry": entry,
        "sl": entry - sign * risk, "tps": [entry + sign * m * risk for m in (1.5, 3, 5)],
    }


def get_status(s, price):
    if s["direction"] == "long":
        if price < s["sl"]:
            return "⛔ Ungültig (SL unterschritten)"
        if s["zone_lo"] <= price <= s["zone_hi"]:
            return "🎯 IN ZONE"
        if price < s["zone_lo"]:
            return "⚠️ Kurs unter Zone"
    else:
        if price > s["sl"]:
            return "⛔ Ungültig (SL überschritten)"
        if s["zone_lo"] <= price <= s["zone_hi"]:
            return "🎯 IN ZONE"
        if price > s["zone_hi"]:
            return "⚠️ Kurs über Zone"
    return f"⏳ Wartet ({s['dist_pct']:+.1f} %)"


def enrich(s, price, risk_usdt, money_div, lev):
    risk_per_unit = abs(s["entry"] - s["sl"])
    s["dist_pct"] = (s["entry"] - price) / price * 100
    if risk_per_unit <= 0:
        s["qty"] = s["notional"] = s["margin"] = 0.0
        s["profits"] = [0.0, 0.0, 0.0]
        s["rr"] = [0.0, 0.0, 0.0]
    else:
        qty = risk_usdt / risk_per_unit
        s["qty"] = qty
        s["notional"] = qty * s["entry"] / money_div
        s["margin"] = s["notional"] / lev
        s["profits"] = [qty * abs(tp - s["entry"]) / money_div for tp in s["tps"]]
        s["rr"] = [abs(tp - s["entry"]) / risk_per_unit for tp in s["tps"]]
    s["status"] = get_status(s, price)
    return s


# ---------------------------------------------------------------- Kerzenmuster (Regeln aus dem Candlestick-Guide)
RANKS = {
    "Retracing Wicks": "Top-Setup #1", "Advancing Wicks": "Top-Setup #2",
    "Evening Star": "Top-Setup #3", "Morning Star": "Top-Setup #4",
    "Tweezer Top": "Top-Setup #5", "Tweezer Bottom": "Top-Setup #6",
    "Hammer": "Stärkste Einzelkerze", "Shooting Star": "Stärkste Einzelkerze",
    "Dragonfly Doji": "2. stärkste Einzelkerze", "Gravestone Doji": "2. stärkste Einzelkerze",
    "Hanging Man": "3. stärkste (nur ca. 70/30)", "Inverted Hammer": "3. stärkste Einzelkerze",
    "Bullish Engulfing": "Gutes Muster", "Bearish Engulfing": "Gutes Muster",
    "3 Line Strike (bullisch)": "Gutes Muster", "3 Line Strike (bärisch)": "Gutes Muster",
    "Marubozu": "Meiden", "Three White Soldiers": "Meiden", "Three Black Crows": "Meiden",
}


def detect_patterns(df, long_setups, short_setups, lookback=12):
    """Sucht Muster nur in GESCHLOSSENEN Kerzen (die letzte, noch laufende Kerze wird ausgelassen)."""
    n = len(df) - 1
    if n < 8:
        return []
    o, h, l, c = (df[k].to_numpy() for k in ("open", "high", "low", "close"))
    atr = df["atr"].to_numpy()
    ema50 = df["ema50"].to_numpy()
    ts = df["timestamp"].to_numpy()

    def st_(i):
        return {
            "rng": max(h[i] - l[i], 1e-12), "body": abs(c[i] - o[i]),
            "up": h[i] - max(o[i], c[i]), "lo": min(o[i], c[i]) - l[i],
            "bull": c[i] > o[i], "bear": c[i] < o[i],
        }

    def zone_hit(i, span, setups):
        lo_p, hi_p = l[i - span + 1:i + 1].min(), h[i - span + 1:i + 1].max()
        tol = 0.5 * (atr[i] if not np.isnan(atr[i]) else 0.0)
        for s in setups:
            if s["status"].startswith("⛔"):
                continue
            if lo_p <= s["zone_hi"] + tol and hi_p >= s["zone_lo"] - tol:
                return s["short"]
        return None

    found = []
    for i in range(max(6, n - lookback), n):
        a = st_(i)
        p = st_(i - 1)
        down_before = c[i - 1] < c[i - 6]
        up_before = c[i - 1] > c[i - 6]
        sideways = bool(i >= 20 and not np.isnan(atr[i]) and abs(ema50[i] - ema50[i - 20]) < atr[i])

        def add(name, direction, span, ok=True, note=""):
            setups = long_setups if direction == "bull" else short_setups if direction == "bear" else []
            if direction == "avoid":
                quality = "⛔ meiden"
            else:
                quality = "✅ Regeln erfüllt" if ok else "⚠️ schwach – nicht nehmen"
            found.append({
                "i": i, "time": pd.Timestamp(ts[i]).strftime("%d.%m. %H:%M"), "name": name,
                "direction": direction, "rank": RANKS.get(name, ""), "quality": quality, "ok": ok,
                "note": note, "sideways": sideways, "zone": zone_hit(i, span, setups) if setups else None,
            })

        # --- Einzelkerzen
        if a["body"] <= 0.1 * a["rng"] and a["lo"] >= 0.6 * a["rng"] and a["up"] <= 0.1 * a["rng"]:
            add("Dragonfly Doji", "bull", 1, note="Schließt dort, wo sie geöffnet hat")
        elif a["body"] <= 0.1 * a["rng"] and a["up"] >= 0.6 * a["rng"] and a["lo"] <= 0.1 * a["rng"]:
            add("Gravestone Doji", "bear", 1, note="Schließt dort, wo sie geöffnet hat")
        elif a["lo"] >= 0.5 * a["rng"] and a["up"] <= 0.15 * a["rng"]:
            if down_before:
                add("Hammer", "bull", 1, note="Käufer drückten den Preis in der Kerze nach oben")
            elif up_before:
                add("Hanging Man", "bear", 1, ok=False, note="Nur ca. 70 % bullisch / 30 % bärisch – am Top eher bärisch")
        elif a["up"] >= 0.5 * a["rng"] and a["lo"] <= 0.15 * a["rng"]:
            if up_before:
                add("Shooting Star", "bear", 1, note="Verkäufer drückten den Preis in der Kerze nach unten")
            elif down_before:
                add("Inverted Hammer", "bull", 1, note="Am Bottom bullisch")
        if a["body"] >= 0.92 * a["rng"] and not np.isnan(atr[i]) and a["rng"] >= 1.2 * atr[i]:
            add("Marubozu", "avoid", 1, note="Später Einstieg, schlechtes CRV, schwacher Momentum-Wechsel")

        # --- Zwei Kerzen
        if p["bear"] and a["bull"] and o[i] <= c[i - 1] and c[i] >= o[i - 1] and a["body"] > p["body"]:
            weak = a["lo"] < 0.05 * a["rng"]
            add("Bullish Engulfing", "bull", 2, ok=not weak,
                note="Kein Docht unten = schwächer" if weak else "Körper schluckt die Vorgängerkerze")
        if p["bull"] and a["bear"] and o[i] >= c[i - 1] and c[i] <= o[i - 1] and a["body"] > p["body"]:
            weak = a["up"] < 0.05 * a["rng"]
            add("Bearish Engulfing", "bear", 2, ok=not weak,
                note="Kein Docht oben = schwächer" if weak else "Körper schluckt die Vorgängerkerze")

        if p["bear"] and a["bull"] and p["lo"] >= 0.3 * p["body"] and a["lo"] >= 0.3 * a["body"]:
            diff = abs(p["lo"] - a["lo"]) / max(p["lo"], a["lo"], 1e-12)
            if diff < 0.10 and a["lo"] <= p["lo"] * 1.02:
                add("Tweezer Bottom", "bull", 2, note="Untere Dochte (fast) gleich lang")
            elif 0.10 <= diff <= 0.20:
                add("Advancing Wicks", "bull", 2, note="Untere Dochte unterscheiden sich um 10–20 %")
        if p["bull"] and a["bear"] and p["up"] >= 0.3 * p["body"] and a["up"] >= 0.3 * a["body"]:
            diff = abs(p["up"] - a["up"]) / max(p["up"], a["up"], 1e-12)
            if diff < 0.10 and a["up"] <= p["up"] * 1.02:
                add("Tweezer Top", "bear", 2, note="Obere Dochte (fast) gleich lang")
            elif 0.10 <= diff <= 0.20:
                add("Retracing Wicks", "bear", 2, note="Obere Dochte unterscheiden sich um 10–20 %")

        # --- Drei Kerzen
        if i >= 2:
            x, y = st_(i - 2), st_(i - 1)
            mid = (o[i - 2] + c[i - 2]) / 2
            if (x["bear"] and x["body"] >= 0.5 * x["rng"] and y["body"] <= 0.35 * x["body"] and a["bull"]
                    and c[i] > mid and a["lo"] >= 0.05 * a["rng"] and abs(c[i] - o[i - 2]) > 0.05 * x["body"]):
                add("Morning Star", "bull", 3, note="Trendumkehr am Ende eines Abwärtstrends")
            if (x["bull"] and x["body"] >= 0.5 * x["rng"] and y["body"] <= 0.35 * x["body"] and a["bear"]
                    and c[i] < mid and a["up"] >= 0.05 * a["rng"] and abs(c[i] - o[i - 2]) > 0.05 * x["body"]):
                add("Evening Star", "bear", 3, note="Trendumkehr am Ende eines Aufwärtstrends")
            if (x["bull"] and y["bull"] and a["bull"] and c[i - 1] > c[i - 2] and c[i] > c[i - 1]
                    and o[i - 1] >= o[i - 2] and o[i] >= o[i - 1]):
                add("Three White Soldiers", "avoid", 3, note="Später Einstieg, hohes Umkehrrisiko")
            if (x["bear"] and y["bear"] and a["bear"] and c[i - 1] < c[i - 2] and c[i] < c[i - 1]
                    and o[i - 1] <= o[i - 2] and o[i] <= o[i - 1]):
                add("Three Black Crows", "avoid", 3, note="Später Einstieg, hohes Umkehrrisiko")

        # --- Vier Kerzen: 3 Line Strike
        if i >= 3:
            k1, k2, k3 = st_(i - 3), st_(i - 2), st_(i - 1)
            if (k1["bear"] and k2["bear"] and k3["bear"] and c[i - 3] > c[i - 2] > c[i - 1]
                    and a["bull"] and c[i] >= o[i - 3]):
                shrinking = k1["body"] > k2["body"] > k3["body"]
                add("3 Line Strike (bullisch)", "bull", 4,
                    note="Besonders stark: bärische Kerzen werden kleiner" if shrinking else "Normal (bärische Kerzen werden nicht kleiner)")
            if (k1["bull"] and k2["bull"] and k3["bull"] and c[i - 3] < c[i - 2] < c[i - 1]
                    and a["bear"] and c[i] <= o[i - 3]):
                shrinking = k1["body"] > k2["body"] > k3["body"]
                add("3 Line Strike (bärisch)", "bear", 4,
                    note="Besonders stark: bullische Kerzen werden kleiner" if shrinking else "Normal (bullische Kerzen werden nicht kleiner)")

    found.sort(key=lambda r: r["i"], reverse=True)
    return found


# ---------------------------------------------------------------- Anzeige-Helfer
def price_decimals(p):
    return 2 if p >= 100 else 4 if p >= 1 else 6


def metric_card(title, value, sub, color="#ffffff", border="#30363d"):
    return (
        f"<div class='metric-card' style='border-color:{border};'>"
        f"<h4>{title}</h4><h2 style='color:{color};'>{value}</h2><p>{sub}</p></div>"
    )


def setup_card(title, color, setup, fp, proximity):
    if setup is None:
        return (
            f"<div class='card' style='border-left: 5px solid {color};'>"
            f"<h3 style='color:{color}; margin-top:0;'>{title}</h3>"
            f"<p style='font-size:13px;'>Kein gültiger Swing gefunden (zu wenig Kursdaten oder keine klare Struktur).</p></div>"
        )
    return (
        f"<div class='card' style='border-left: 5px solid {color};'>"
        f"<h3 style='color:{color}; margin-top:0;'>{title}</h3>"
        f"<p style='background:rgba(255,255,255,0.05); padding:8px; border-radius:5px; font-size:13px;'>{setup['status']}</p>"
        f"<div class='row-line'><b>Entry</b></div>"
        f"<div class='entry-highlight' style='color:{color};'>{fp(setup['entry'])}</div>"
        f"<div class='row-line'><b>Zone:</b> {fp(setup['zone_lo'])} – {fp(setup['zone_hi'])}</div>"
        f"<div class='row-line'><b>Stop-Loss:</b> {fp(setup['sl'])}</div>"
        f"<div class='row-line'><b>TP1:</b> {fp(setup['tps'][0])}</div>"
        f"<div class='row-line'><b>TP2:</b> {fp(setup['tps'][1])}</div>"
        f"<div class='row-line'><b>TP3:</b> {fp(setup['tps'][2])}</div>"
        f"<div class='row-line' style='margin-top:10px;'>Nähe zur Zone: {proximity:.0f}%</div>"
        f"<div class='progress-bg'><div class='progress-fill' style='width:{proximity}%; background:{color};'></div></div>"
        f"</div>"
    )


def proximity_percent(price, zone_low, zone_high):
    if zone_low <= price <= zone_high:
        return 100.0
    distance = min(abs(price - zone_low), abs(price - zone_high))
    return round(max(0.0, 100 - (distance / price * 1000)), 1)


def show_plotly(fig, config):
    try:
        st.plotly_chart(fig, use_container_width=True, config=config)
    except Exception:
        st.plotly_chart(fig, width="stretch", config=config)


def show_table(frame):
    try:
        st.dataframe(frame, hide_index=True, use_container_width=True)
    except Exception:
        st.dataframe(frame, hide_index=True, width="stretch")


def levels_frame(setups, fp):
    rows = []
    for s in setups:
        rows.append({
            "Setup": s["name"],
            "Entry-Zone": f"{fp(s['zone_lo'])} – {fp(s['zone_hi'])}",
            "Entry": fp(s["entry"]),
            "Stop-Loss": fp(s["sl"]),
            "TP1": fp(s["tps"][0]), "TP2": fp(s["tps"][1]), "TP3": fp(s["tps"][2]),
            "CRV (TP1 / TP2 / TP3)": " / ".join(f"{r:.1f}" for r in s["rr"]),
            "Abstand": f"{s['dist_pct']:+.1f} %",
            "Status": s["status"],
        })
    return pd.DataFrame(rows)


def money_cell(usdt_value, eur_usdt, sign=""):
    """Große USDT-Zahl, klein der Euro-Gegenwert darunter."""
    main = f"{sign}{usdt_value:,.2f} USDT"
    if eur_usdt:
        sub = f"<br><span style='font-size:11px; color:#8b949e;'>≈ {sign}{usdt_value / eur_usdt:,.2f} €</span>"
    else:
        sub = "<br><span style='font-size:11px; color:#8b949e;'>(€-Kurs nicht verfügbar)</span>"
    return main + sub


def sizing_table_html(setups, coin, qty_dec, lev, eur_usdt):
    header = (
        "<tr>"
        f"<th>Setup</th><th>Menge ({coin})</th><th>Positionswert</th><th>Margin bei {lev}x</th>"
        "<th>Verlust bei SL</th><th>Gewinn TP1</th><th>Gewinn TP2</th><th>Gewinn TP3</th></tr>"
    )
    body = ""
    for s in setups:
        risk_loss = s["qty"] * abs(s["entry"] - s["sl"])
        cells = "".join(
            f"<td>{c}</td>" for c in [
                s["name"],
                f"{s['qty']:,.{qty_dec}f}",
                money_cell(s["notional"], eur_usdt),
                money_cell(s["margin"], eur_usdt),
                money_cell(risk_loss, eur_usdt, sign="-"),
                money_cell(s["profits"][0], eur_usdt, sign="+"),
                money_cell(s["profits"][1], eur_usdt, sign="+"),
                money_cell(s["profits"][2], eur_usdt, sign="+"),
            ]
        )
        body += f"<tr>{cells}</tr>"
    return (
        "<table class='sizing-table'>" + header + body + "</table>"
    )


def patterns_frame(patterns):
    rows = []
    for p in patterns:
        if p["sideways"]:
            context = "⚠️ Seitwärtsphase – ignorieren"
        elif p["zone"]:
            context = f"✅ in Einstiegszone ({p['zone']})"
        else:
            context = "kein Einstiegsbereich in der Nähe"
        rows.append({
            "Kerze (Schluss)": p["time"], "Muster": p["name"],
            "Richtung": {"bull": "🟢 bullisch", "bear": "🔴 bärisch", "avoid": "🟠 meiden"}[p["direction"]],
            "Rang": p["rank"], "Qualität": p["quality"], "Kontext": context, "Hinweis": p["note"],
        })
    return pd.DataFrame(rows)


def build_tips(price, bias, rsi_val, fg_value, long_setups, short_setups, patterns, fp):
    tips = []
    if bias == "BULLISCH":
        tips.append(("good", "Trend ist bullisch (Kurs über EMA 50 und EMA 200): Long-Einstiege laufen mit dem Trend, Short-Einstiege sind Gegentrend und riskanter."))
    elif bias == "BÄRISCH":
        tips.append(("good", "Trend ist bärisch (Kurs unter EMA 50 und EMA 200): Short-Einstiege laufen mit dem Trend, Long-Einstiege sind Gegentrend und riskanter."))
    else:
        tips.append(("warn", "Kein klarer Trend (EMAs nicht sauber geordnet): kleiner handeln oder auf klare Bestätigung warten."))

    valid = [(s, "Long") for s in long_setups if not s["status"].startswith("⛔")]
    valid += [(s, "Short") for s in short_setups if not s["status"].startswith("⛔")]
    in_zone = [(s, d) for s, d in valid if s["status"].startswith("🎯")]
    for s, d in in_zone:
        tips.append(("warn", f"Kurs ist JETZT in der Zone von {d} – {s['name']}. Nicht blind einsteigen: Kerzen-Bestätigung abwarten (Muster aus der Liste unten, Kerzenschluss aus der Zone heraus)."))
    if valid:
        s, d = min(valid, key=lambda x: abs(x[0]["dist_pct"]))
        if not s["status"].startswith("🎯"):
            tips.append(("info", f"Nächste mögliche Einstiegsregion: {d} – {s['name']}: {fp(s['zone_lo'])} bis {fp(s['zone_hi'])} ({s['dist_pct']:+.1f} % vom Kurs). Limit-Order oder Alarm in diese Zone setzen."))
    else:
        tips.append(("info", "Aktuell gibt es kein gültiges Setup. Warten, bis sich ein neuer Swing gebildet hat."))

    best = [p for p in patterns if p["i"] >= max(x["i"] for x in patterns) - 2 and p["ok"] and p["direction"] != "avoid"
            and p["zone"] and not p["sideways"]] if patterns else []
    for p in best[:2]:
        tips.append(("good", f"⭐ Konfluenz: {p['name']} ({p['time']}) liegt in der Einstiegszone {p['zone']} – das ist die Kombination, auf die der Guide setzt."))
    avoid = [p for p in patterns[:3] if p["direction"] == "avoid"] if patterns else []
    if avoid:
        tips.append(("warn", f"Letztes Muster ({avoid[0]['name']}) gilt als spätes Signal mit schlechtem CRV – eher nicht traden."))

    if rsi_val > 70:
        tips.append(("warn", f"RSI ist überkauft ({rsi_val:.0f}): Longs nicht hinterherlaufen, Rücksetzer in die Zonen abwarten."))
    elif rsi_val < 30:
        tips.append(("warn", f"RSI ist überverkauft ({rsi_val:.0f}): Shorts nicht hinterherlaufen, Erholung in die Zonen abwarten."))
    if fg_value is not None and fg_value >= 75:
        tips.append(("warn", f"Fear & Greed steht bei {fg_value} (extreme Gier): Markt ist überhitzt, Rücksetzer sind wahrscheinlicher."))
    elif fg_value is not None and fg_value <= 25:
        tips.append(("warn", f"Fear & Greed steht bei {fg_value} (extreme Angst): Panikverkäufe und schnelle Erholungen sind möglich."))
    tips.append(("info", "Praxis: Stop-Loss immer mitsetzen und die Positionsgröße aus der Tabelle unten übernehmen."))
    return tips


GUIDE_RULES = (
    "<b>Muster NIE ohne Kontext traden!</b> Muster sind eher eine finale Unterschrift, einen Trade einzugehen. "
    "<b>Nie in einer Seitwärtsphase anwenden!</b> Bei Gebieten, wo vorher lange Dochte waren, geht der Preis meist dagegen. "
    "Alle guten Setups bauen auf diesen Mustern auf."
)

GUIDE_CARDS = [
    ("bullish", "BULLISCH · STÄRKSTER", "🔨 Hammer", "Langer Docht unten (min. 50 %). Käufer drückten den Kurs nach oben. Ideal an Fib 0.882 / 0.941 Konfluenz."),
    ("bearish", "BEARISH · STÄRKSTER", "🌠 Shooting Star", "Langer Docht oben. Verkäufer drückten den Preis nach starkem Anstieg massiv nach unten. Perfekt an Widerständen."),
    ("bullish", "BULLISCH · TOP SETUP", "🟢 Bullish Engulfing", "Grüne Kerze schluckt die rote Vorläuferkerze vollständig. Starkes Momentum-Signal. Ohne Docht unten ist sie schwächer – dann Trade nicht nehmen."),
    ("bearish", "BEARISH · TOP SETUP", "🔴 Bearish Engulfing", "Rote Kerze schluckt die grüne Vorläuferkerze vollständig. Starkes Umkehrsignal. Ohne Docht oben ist sie schwächer – dann Trade nicht nehmen."),
    ("bullish", "BULLISCH · TOP-SETUP #2", "📈 Advancing Wicks", "Zwei Kerzen mit langen unteren Dochten (min. 30 % vom Körper). Die Dochte unterscheiden sich nur minimal (10–20 %) und sind nicht gleich lang."),
    ("bearish", "BEARISH · TOP-SETUP #1", "📉 Retracing Wicks", "Zwei Kerzen mit langen oberen Dochten (min. 30 % vom Körper). Die Dochte unterscheiden sich nur minimal (10–20 %) und sind nicht gleich lang."),
    ("bullish", "BULLISCH · TOP-SETUP #4", "🌅 Morning Star", "Trendumkehr-Muster am Ende eines Abwärtstrends. Die bullische Kerze muss einen Docht haben und darf nicht gleich schließen wie die bärische Kerze."),
    ("bearish", "BEARISH · TOP-SETUP #3", "🌆 Evening Star", "Trendumkehr-Muster am Ende eines Aufwärtstrends. Die bärische Kerze muss einen Docht haben."),
    ("bullish", "BULLISCH · TOP-SETUP #6", "🔧 Tweezer Bottom", "Die unteren Dochte sollten min. 30 % vom Kerzenkörper ausmachen. Dochte gleich lang, der zweite darf minimal kürzer sein."),
    ("bearish", "BEARISH · TOP-SETUP #5", "🔧 Tweezer Top", "Die oberen Dochte sollten min. 30 % vom Kerzenkörper ausmachen. Dochte gleich lang, der zweite darf minimal kürzer sein."),
    ("bullish", "BULLISCH · 2. STÄRKSTER", "🐉 Dragonfly Doji", "Wie eine magere Hammerkerze. Schließt dort, wo die Kerze geöffnet hat."),
    ("bearish", "BEARISH · 2. STÄRKSTER", "🪦 Gravestone Doji", "Wie ein magerer Shooting Star. Schließt dort, wo die Kerze geöffnet hat."),
    ("bullish", "BULLISCH · GUTES MUSTER", "3️⃣ 3 Line Strike (bullisch)", "Drei bärische Kerzen, dann eine große bullische Kerze. Besonders stark, wenn die bärischen Kerzen kleiner werden."),
    ("bearish", "BEARISH · GUTES MUSTER", "3️⃣ 3 Line Strike (bärisch)", "Drei bullische Kerzen, dann eine große bärische Kerze. Besonders stark, wenn die bullischen Kerzen kleiner werden."),
    ("bearish", "BEARISH · TRENDWENDE", "📉 Kopf & Schulter (Bearish)", "Klassisches Chartmuster mit linker Schulter, Kopf und rechter Schulter. Der Bruch der Nackenlinie signalisiert einen starken Abverkauf. (Wird im Dashboard nicht automatisch erkannt.)"),
    ("avoid", "ACHTUNG · 70/30", "⚠️ Hanging Man / Inverted Hammer", "Hanging Man: ca. 70 % bullisch, 30 % bärisch, wie eine schwache Hammer-Kerze. Bei einem Top bärisch, am Bottom bullisch."),
    ("avoid", "MEIDEN · SPÄTER EINSTIEG", "🚫 Marubozu, Three White Soldiers, Three Black Crows", "Später Einstieg, schlechtes Risiko/Chance-Verhältnis, hohes Umkehrrisiko bzw. schwacher Momentum-Wechsel."),
    ("avoid", "FÜR KRYPTO IRRELEVANT", "➖ Piercing, Dark Cloud Cover, Harami, Kicker", "Laut Guide für Krypto nicht relevant – werden vom Dashboard nicht ausgewertet."),
]


def pattern_card(kind, tag, title, text):
    return (
        f"<div class='pattern-guide-box'><span class='pattern-tag tag-{kind}'>{tag}</span>"
        f"<h5>{title}</h5><p>{text}</p></div>"
    )



TV_INTERVALS = {"15m": "15", "30m": "30", "1h": "60", "2h": "120", "4h": "240", "12h": "720", "1d": "D", "3d": "3D"}
EMA_STYLE = {
    21: {"color": "#FFD60A", "width": 1.5},
    50: {"color": "#FF8C00", "width": 1.5},
    200: {"color": "#B71C1C", "width": 3.5},
}


def tradingview_widget(symbol, interval):
    ema_studies = [{"id": "MAExp@tv-basicstudies", "inputs": {"length": length}} for length in EMA_STYLE]
    config = {
        "autosize": True, "symbol": "BINANCE:" + symbol.replace("/", ""), "interval": TV_INTERVALS[interval],
        "timezone": "Europe/Berlin", "theme": "dark", "style": "1", "locale": "de_DE",
        "backgroundColor": "#0e1117", "allow_symbol_change": True, "hide_side_toolbar": False,
        "withdateranges": True, "save_image": True, "calendar": False,
        "studies": ema_studies + ["RSI@tv-basicstudies"], "support_host": "https://www.tradingview.com",
    }
    return (
        "<div class='tradingview-widget-container' style='height:100%;width:100%;'>"
        "<div class='tradingview-widget-container__widget' style='height:100%;width:100%;'></div>"
        "<script type='text/javascript' "
        "src='https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js' async>"
        + json.dumps(config) + "</script></div>"
    )


def draw_setups(fig, setups):
    for s in setups:
        if not s.get("draw") or s["status"].startswith("⛔"):
            continue
        color = "#00ffcc" if s["direction"] == "long" else "#ff4d4d"
        is_main = s["name"].startswith("882")
        fig.add_hrect(
            y0=s["zone_lo"], y1=s["zone_hi"], fillcolor=color, opacity=0.18 if is_main else 0.08,
            line_width=0, row=1, col=1,
            annotation_text=f"{'Long' if s['direction'] == 'long' else 'Short'} {s['short']}",
            annotation_position="top left",
        )
        if is_main:
            fig.add_hline(y=s["entry"], line_dash="dash", line_color=color, line_width=1, row=1, col=1)
            if show_levels:
                fig.add_hline(y=s["sl"], line_dash="dot", line_color="#ff6b6b", line_width=1, row=1, col=1,
                              annotation_text="SL")
                for n_tp, tp in enumerate(s["tps"], 1):
                    fig.add_hline(y=tp, line_dash="dot", line_color=color, line_width=1, row=1, col=1,
                                  annotation_text=f"TP{n_tp}")


# ---------------------------------------------------------------- Trend, Seitwärts, MTF
def trend_bias(price, ema50, ema200):
    if price > ema50 > ema200:
        return "BULLISCH"
    if price < ema50 < ema200:
        return "BÄRISCH"
    return "NEUTRAL"


def is_sideways(df):
    if len(df) < 22 or pd.isna(df["atr"].iloc[-1]):
        return False
    return bool(abs(df["ema50"].iloc[-1] - df["ema50"].iloc[-21]) < df["atr"].iloc[-1])


MTF_FRAMES = ["15m", "1h", "4h", "1d"]


@st.cache_data(ttl=120)
def fetch_mtf_bias(symbol, interval):
    """Trend eines höheren/niedrigeren Zeitfensters (echte, eigene Abfrage). None = nicht verfügbar."""
    try:
        d = calculate_analytics(fetch_binance_data(symbol, interval, max_retries=2, limit=250))
        return trend_bias(float(d["close"].iloc[-1]), float(d["ema50"].iloc[-1]), float(d["ema200"].iloc[-1]))
    except Exception:
        return None


def mtf_html(mtf):
    names = {"BULLISCH": ("mtf-green", "🟢"), "BÄRISCH": ("mtf-red", "🔴"), "NEUTRAL": ("mtf-grey", "⚪")}
    badges = ""
    for frame, bias in mtf.items():
        cls, icon = names.get(bias, ("mtf-grey", "❔"))
        badges += f"<span class='mtf-badge {cls}'>{frame}: {bias or 'n/a'} {icon}</span>"
    return (
        "<div class='card' style='padding:14px 18px;'>"
        "<b style='color:#00ffcc;'>🚦 Multi-Timeframe-Ampel</b>"
        "<span style='color:#8b949e; font-size:12px;'> · Trend je Zeitfenster (Kurs vs. EMA 50 / EMA 200)</span>"
        f"<div style='margin-top:8px;'>{badges}</div></div>"
    )


# ---------------------------------------------------------------- GUSS-Strategie (Projektdatei "GUSS Sniperentry Strategie")
GUSS_FIBS = (0.5, 0.559, 0.618, 0.667, 0.786)


def detect_guss(df, lookback=40):
    """GUSS (Long): neues Hoch weit über der 21 EMA -> Korrektur OHNE bullische Kerze zur 50 EMA -> Einstieg dort."""
    res = {"state": "none", "reason": "", "setup": None, "confluence": [], "info": ""}
    n = len(df)
    if n < 60:
        res["reason"] = "Zu wenig Kerzen für die Auswertung."
        return res
    o, h, l, c = (df[k].to_numpy() for k in ("open", "high", "low", "close"))
    atr, e21, e50 = df["atr"].to_numpy(), df["ema21"].to_numpy(), df["ema50"].to_numpy()
    start = max(21, n - lookback)
    ih = start + int(np.argmax(h[start:n]))
    if ih > n - 2:
        res["reason"] = "Das höchste Hoch ist die aktuelle Kerze – die Korrektur hat noch nicht begonnen."
        return res
    if not h[ih] > h[ih - 20:ih].max():
        res["reason"] = "Kein neues höheres Hoch gegenüber den Kerzen davor."
        return res
    atr_ih = atr[ih] if not np.isnan(atr[ih]) else float(np.nanmean(atr))
    if h[ih] - e21[ih] < 1.5 * atr_ih:
        res["reason"] = "Das Hoch liegt nicht weit genug über der 21 EMA (keine Überdehnung)."
        return res
    touch = next((j for j in range(ih + 1, n) if l[j] <= e50[j]), None)
    between = range(ih + 1, touch) if touch is not None else range(ih + 1, n)
    if any(c[j] > o[j] for j in between):
        res["state"] = "invalid"
        res["reason"] = "Bullische Kerze vor Erreichen der 50 EMA – Setup ungültig (Regel der Strategie)."
        return res
    if touch is not None and touch < n - 3:
        res["state"] = "expired"
        res["reason"] = "Die 50 EMA wurde schon vor mehreren Kerzen erreicht – der Einstieg ist vorbei."
        return res
    atr_now = atr[-1] if not np.isnan(atr[-1]) else atr_ih
    leg_low = float(l[max(0, ih - 30):ih].min())
    leg = float(h[ih]) - leg_low
    entry = float(e50[-1])
    sl = leg_low - 0.2 * atr_now
    if leg <= 0 or entry <= sl:
        res["reason"] = "Die Struktur passt nicht (50 EMA liegt unter dem letzten Tief)."
        return res
    if e21[-1] <= entry:
        res["reason"] = "Die 21 EMA liegt nicht über der 50 EMA – kein intakter Aufwärtstrend."
        return res
    res["confluence"] = [r for r in GUSS_FIBS if abs(float(h[ih]) - r * leg - entry) <= 0.3 * atr_now]
    res["state"] = "touch" if touch is not None else "armed"
    res["info"] = f"Hoch vom {pd.Timestamp(df['timestamp'].iloc[ih]).strftime('%d.%m. %H:%M')}"
    res["setup"] = {
        "name": "GUSS Sniper (50 EMA, TP1 = 21 EMA)", "short": "GUSS", "direction": "long", "draw": True,
        "zone_lo": entry - 0.25 * atr_now, "zone_hi": entry + 0.25 * atr_now, "entry": entry, "sl": sl,
        "tps": [float(e21[-1]), float(h[ih]), float(h[ih]) + 0.272 * leg],
    }
    return res


# ---------------------------------------------------------------- LSOB (Liquidity Sweep Orderblock)
def _lsob_setup(direction, zone_lo, zone_hi, sweep_extreme, atr_now):
    entry = (zone_lo + zone_hi) / 2
    if direction == "short":
        sl = max(sweep_extreme, zone_hi) + 0.2 * atr_now
        risk = sl - entry
        tps = [entry - m * risk for m in (1.5, 3, 5)]
    else:
        sl = min(sweep_extreme, zone_lo) - 0.2 * atr_now
        risk = entry - sl
        tps = [entry + m * risk for m in (1.5, 3, 5)]
    if risk <= 0:
        return None
    return {
        "name": f"LSOB {'Short' if direction == 'short' else 'Long'} (Sweep-Orderblock, TPs: 1,5R / 3R / 5R)",
        "short": "LSOB", "direction": direction, "draw": True,
        "zone_lo": zone_lo, "zone_hi": zone_hi, "entry": entry, "sl": sl, "tps": tps,
    }


def detect_lsob(df, lookback=45):
    """Liquidity Sweep -> 2 Gegenkerzen -> Orderblock -> Rücklauf. Auslegung der Projektdatei (nur Text, ohne Grafiken)."""
    out = {}
    n = len(df)
    o, h, l, c = (df[k].to_numpy() for k in ("open", "high", "low", "close"))
    atr = df["atr"].to_numpy()
    for direction in ("short", "long"):
        best_valid, best_invalid = None, None
        for s in range(max(21, n - lookback), n - 3):
            a = atr[s]
            if np.isnan(a) or a <= 0:
                continue
            if direction == "short":
                prior = h[s - 20:s].max()
                if not (h[s] > prior + 0.05 * a and c[s] < prior):
                    continue
                if not (c[s + 1] < o[s + 1] and c[s + 2] < o[s + 2]):
                    continue
                k = next((j for j in range(s, max(s - 6, 0), -1) if c[j] > o[j]), None)
            else:
                prior = l[s - 20:s].min()
                if not (l[s] < prior - 0.05 * a and c[s] > prior):
                    continue
                if not (c[s + 1] > o[s + 1] and c[s + 2] > o[s + 2]):
                    continue
                k = next((j for j in range(s, max(s - 6, 0), -1) if c[j] < o[j]), None)
            if k is None:
                continue
            zone_lo, zone_hi = float(l[k]), float(h[k])
            mid = (zone_lo + zone_hi) / 2
            sweep_extreme = float(h[s]) if direction == "short" else float(l[s])
            state, reason, hit = "armed", "Wartet auf den Rücklauf in die Zone.", None
            for m in range(s + 3, n):
                if direction == "short":
                    if h[m] > sweep_extreme:
                        state, reason = "invalid", "Neuer Liquidity Sweep (Hoch wurde erneut überschritten)."; break
                    if c[m] > zone_hi:
                        state, reason = "invalid", "Zone wird nicht respektiert (Schlusskurs über der Zone)."; break
                    if h[m] >= zone_lo:
                        if c[m] >= mid:
                            state, reason = "invalid", "Kerze schließt zu weit in der Zone."
                        else:
                            state, reason, hit = "rejected", "Zone wird abgelehnt (gültiges Signal).", m
                        break
                else:
                    if l[m] < sweep_extreme:
                        state, reason = "invalid", "Neuer Liquidity Sweep (Tief wurde erneut unterschritten)."; break
                    if c[m] < zone_lo:
                        state, reason = "invalid", "Zone wird nicht respektiert (Schlusskurs unter der Zone)."; break
                    if l[m] <= zone_hi:
                        if c[m] <= mid:
                            state, reason = "invalid", "Kerze schließt zu weit in der Zone."
                        else:
                            state, reason, hit = "rejected", "Zone wird abgelehnt (gültiges Signal).", m
                        break
            if state == "armed" and (n - 1 - (s + 2)) > 60:
                state, reason = "expired", "Der Rücklauf kam nicht rechtzeitig – Zone verfallen."
            atr_now = atr[-1] if not np.isnan(atr[-1]) else a
            rec = {
                "state": state, "reason": reason,
                "info": f"Sweep-Kerze {pd.Timestamp(df['timestamp'].iloc[s]).strftime('%d.%m. %H:%M')}",
                "setup": None if state in ("invalid", "expired") else _lsob_setup(direction, zone_lo, zone_hi, sweep_extreme, float(atr_now)),
                "hit": hit, "s": s,
            }
            if state in ("armed", "rejected") and rec["setup"]:
                best_valid = rec
            else:
                best_invalid = rec
        out[direction] = best_valid or best_invalid or {
            "state": "none", "reason": "Kein Liquidity Sweep mit 2 Gegenkerzen in den letzten Kerzen.",
            "info": "", "setup": None, "hit": None, "s": None,
        }
    return out


STATE_TEXT = {
    "armed": "🟡 Aufgebaut – wartet auf den Einstieg", "touch": "🎯 Einstiegszone erreicht",
    "rejected": "✅ Zone abgelehnt – gültiges Signal", "invalid": "⛔ Ungültig",
    "expired": "⌛ Abgelaufen", "none": "— Kein Setup",
}


def strategy_panel(title, color, rec, extra=""):
    setup = rec.get("setup")
    detail = rec.get("info", "")
    zone = ""
    if setup:
        zone = f"<div class='row-line'><b>Zone:</b> {fp(setup['zone_lo'])} – {fp(setup['zone_hi'])} · <b>Entry:</b> {fp(setup['entry'])}</div>"
    return (
        f"<div class='card' style='border-left:5px solid {color};'>"
        f"<h4 style='color:{color}; margin:0 0 6px 0;'>{title}</h4>"
        f"<div class='row-line'><b>{STATE_TEXT.get(rec['state'], '')}</b></div>"
        f"<div class='row-line' style='color:#8b949e;'>{rec.get('reason', '')} {detail}</div>{zone}{extra}</div>"
    )


# ---------------------------------------------------------------- Setup-Score (Checkliste, KEINE Gewinnwahrscheinlichkeit)
def setup_score(direction, price, atr_val, bias, mtf, setups, patterns, sideways, rsi_val, last_closed):
    want = "BULLISCH" if direction == "long" else "BÄRISCH"
    parts = []
    valid = [s for s in setups if not s["status"].startswith("⛔")]
    pts = 0
    if valid:
        dist = min(
            0.0 if s["zone_lo"] <= price <= s["zone_hi"] else min(abs(price - s["zone_lo"]), abs(price - s["zone_hi"])) / atr_val
            for s in valid
        )
        pts = 30 if dist == 0 else 20 if dist <= 1 else 10 if dist <= 2 else 0
    parts.append(("Nähe zur Einstiegszone", pts, 30))
    t_pts = 25 if bias == want else 10 if bias == "NEUTRAL" else 0
    parts.append(("Trend (EMA 50/200)", t_pts, 25))
    known = [v for v in mtf.values() if v]
    m_pts = round(20 * sum(1 for v in known if v == want) / len(known)) if known else 0
    parts.append(("Zeitfenster stimmen überein", m_pts, 20))
    recent = [p for p in patterns if p["direction"] == ("bull" if direction == "long" else "bear")
              and p["ok"] and p["i"] >= last_closed - 2]
    p_pts = 0
    if recent:
        p_pts = 25 if any(p["zone"] and not p["sideways"] for p in recent) else 10
    parts.append(("Kerzenmuster", p_pts, 25))
    total = pts + t_pts + m_pts + p_pts
    if sideways:
        total -= 15
        parts.append(("Abzug: Seitwärtsphase", -15, "–"))
    if (direction == "long" and rsi_val > 70) or (direction == "short" and rsi_val < 30):
        total -= 10
        parts.append(("Abzug: RSI-Extrem gegen die Richtung", -10, "–"))
    return max(0, min(100, int(total))), parts


def score_card(title, color, score, parts):
    label = "stark – viele Bausteine passen" if score >= 75 else "mittel – noch passt nicht alles" if score >= 50 else "schwach – besser warten"
    rows = "".join(f"<div class='score-row'><span>{name}</span><span>{got}/{mx}</span></div>" for name, got, mx in parts)
    return (
        f"<div class='score-box' style='border-color:{color};'>"
        f"<div class='score-title'>{title}</div>"
        f"<div class='score-value' style='color:{color};'>{score}<span class='score-of'> / 100</span></div>"
        f"<div class='score-label'>{label}</div>"
        f"<div class='progress-bg'><div class='progress-fill' style='width:{score}%; background:{color};'></div></div>"
        f"<div class='score-parts'>{rows}</div></div>"
    )


# ---------------------------------------------------------------- Backtest (ehrlich: ohne Blick in die Zukunft)
FIB_DEFS = [
    ("882-Retracement (82–88 %)", "882-Retracement", (0.82, 0.88), 0.85, 1.0, [0.5, 0.236, 0.0]),
    ("Golden Pocket (61,8–65 %)", "Golden Pocket", (0.618, 0.65), 0.64, 0.786, [0.382, 0.236, 0.0]),
]


def _sim_trade(order, fill_idx, hi, lo, cl, n, max_hold):
    """Spielt einen gefüllten Trade Kerze für Kerze durch. Bei SL und TP in derselben Kerze zählt der SL zuerst."""
    entry, sl, tps = order["entry"], order["sl"], order["tps"]
    risk = abs(entry - sl)
    is_long = order["direction"] == "long"
    sl_idx, tp_idx, last = None, [None, None, None], fill_idx
    for j in range(fill_idx, min(n - 1, fill_idx + max_hold) + 1):
        last = j
        if (is_long and lo[j] <= sl) or (not is_long and hi[j] >= sl):
            sl_idx = j
            break
        if j > fill_idx:
            for k in range(3):
                if tp_idx[k] is None and ((is_long and hi[j] >= tps[k]) or (not is_long and lo[j] <= tps[k])):
                    tp_idx[k] = j
            if tp_idx[2] is not None:
                break
    close_r = ((cl[last] - entry) if is_long else (entry - cl[last])) / risk
    out = []
    for k in range(3):
        rr = abs(tps[k] - entry) / risk
        if tp_idx[k] is not None and (sl_idx is None or tp_idx[k] < sl_idx):
            out.append({"r": rr, "exit": tp_idx[k], "res": "win"})
        elif sl_idx is not None:
            out.append({"r": -1.0, "exit": sl_idx, "res": "loss"})
        else:
            out.append({"r": close_r, "exit": last, "res": "timeout"})
    return out


def run_backtest(df, window=150, max_wait=60, max_hold=120, start=200):
    n = len(df)
    hi, lo, cl = df["high"].to_numpy(), df["low"].to_numpy(), df["close"].to_numpy()
    atr_all = df["atr"].to_numpy()
    seen, pending, trades = set(), [], []
    for t in range(start, n):
        still = []
        for od in pending:
            if t - od["created"] > max_wait:
                continue
            filled = lo[t] <= od["entry"] if od["direction"] == "long" else hi[t] >= od["entry"]
            if filled:
                trades.append({
                    "name": od["short"], "direction": od["direction"], "created": od["created"], "fill": t,
                    "entry": od["entry"], "sl": od["sl"], "res": _sim_trade(od, t, hi, lo, cl, n, max_hold),
                })
            else:
                still.append(od)
        pending = still
        a = atr_all[t]
        if np.isnan(a) or a <= 0:
            continue
        win = df.iloc[max(0, t - window + 1):t + 1].reset_index(drop=True)
        up, down = latest_legs(find_pivots(win), 4 * a)
        for direction, leg in (("long", up), ("short", down)):
            if not leg:
                continue
            for name, short, zr, er, slr, tpr in FIB_DEFS:
                key = (direction, name, round(leg[0], 8), round(leg[1], 8))
                if key in seen:
                    continue
                s = fib_setup(direction, leg[0], leg[1], a, name, short, zr, er, slr, tpr)
                placeable = cl[t] > s["entry"] if direction == "long" else cl[t] < s["entry"]
                broken = cl[t] < s["sl"] if direction == "long" else cl[t] > s["sl"]
                if not placeable or broken:
                    continue
                seen.add(key)
                s["created"] = t
                pending.append(s)
    return trades


def backtest_table(trades, k):
    """Auswertung je Setup und Richtung; k = 0/1/2 (Exit bei TP1/TP2/TP3)."""
    groups = {}
    for tr in trades:
        for key in ((tr["name"], tr["direction"]), ("Alle", "gesamt")):
            groups.setdefault(key, []).append(tr)
    rows = []
    for (name, direction), trs in sorted(groups.items(), key=lambda kv: (kv[0][0] == "Alle", kv[0])):
        res = [t["res"][k] for t in trs]
        wins = sum(1 for r in res if r["res"] == "win")
        losses = sum(1 for r in res if r["res"] == "loss")
        touts = sum(1 for r in res if r["res"] == "timeout")
        rs = [r["r"] for r in sorted(res, key=lambda r: r["exit"])]
        eq, peak, dd = 0.0, 0.0, 0.0
        for r in rs:
            eq += r
            peak = max(peak, eq)
            dd = max(dd, peak - eq)
        rows.append({
            "Setup": name, "Richtung": direction, "Trades": len(trs),
            "Treffer": f"{wins / (wins + losses) * 100:.0f} %" if wins + losses else "–",
            "Gewonnen / Verloren / offen": f"{wins} / {losses} / {touts}",
            "Ø Ergebnis (R)": f"{sum(rs) / len(rs):+.2f}", "Summe (R)": f"{sum(rs):+.1f}",
            "Max. Drawdown (R)": f"{dd:.1f}",
        })
    return pd.DataFrame(rows)


def equity_curve(trades, k):
    res = sorted((t["res"][k] for t in trades), key=lambda r: r["exit"])
    return list(np.cumsum([r["r"] for r in res])) if res else []


@st.cache_data(ttl=900)
def cached_backtest(symbol, interval):
    raw = fetch_binance_data(symbol, interval, limit=1000)
    d = calculate_analytics(raw).reset_index(drop=True)
    return run_backtest(d), len(d)


# ---------------------------------------------------------------- Alarm-Ton (ohne externe Sound-Dateien)
SOUNDS = {
    "Glocke (Standard)": ("sine", [880, 1320, 880], 0.30),
    "Warn-Signal": ("square", [440, 330, 440, 330], 0.18),
    "Erfolgs-Ping": ("triangle", [1320, 1760], 0.14),
}
SOUND_JS = """<script>
(function(){ try {
 var C = new (window.AudioContext || window.webkitAudioContext)();
 var t = C.currentTime; var freqs = __FREQS__; var dur = __DUR__;
 freqs.forEach(function(f, i){
   var o = C.createOscillator(), g = C.createGain(); o.type = '__WAVE__'; o.frequency.value = f;
   g.gain.setValueAtTime(0.0001, t + i * dur); g.gain.exponentialRampToValueAtTime(0.25, t + i * dur + 0.02);
   g.gain.exponentialRampToValueAtTime(0.0001, t + (i + 1) * dur);
   o.connect(g); g.connect(C.destination); o.start(t + i * dur); o.stop(t + (i + 1) * dur);
 });
} catch(e) {} })();
</script>"""


def alarm_sound_html(kind):
    wave, freqs, dur = SOUNDS.get(kind, SOUNDS["Glocke (Standard)"])
    return SOUND_JS.replace("__FREQS__", json.dumps(freqs)).replace("__DUR__", str(dur)).replace("__WAVE__", wave)


# ---------------------------------------------------------------- Hauptchart
def build_main_chart(df, coin, setups, patterns, height, current_price):
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.64, 0.18, 0.18],
        specs=[[{"secondary_y": True}], [{}], [{}]],
        subplot_titles=(f"{coin} · Preis, EMAs, Einstiegszonen", "RSI (14)", "Volumen-Druck (Schätzung: Volumen × Spanne)"),
    )
    fig.add_trace(go.Candlestick(
        x=df["timestamp"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], name=coin,
        increasing=dict(line=dict(color="#00ffcc"), fillcolor="rgba(0,255,204,0.55)"),
        decreasing=dict(line=dict(color="#ff4d4d"), fillcolor="rgba(255,77,77,0.55)"),
    ), row=1, col=1, secondary_y=False)
    for length, style in EMA_STYLE.items():
        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df[f"ema{length}"], name=f"EMA {length}",
            line=dict(color=style["color"], width=style["width"]),
        ), row=1, col=1, secondary_y=False)
    vol_colors = ["rgba(0,255,204,0.25)" if cc >= oo else "rgba(255,77,77,0.25)" for oo, cc in zip(df["open"], df["close"])]
    fig.add_trace(go.Bar(x=df["timestamp"], y=df["volume"], name="Volumen", marker_color=vol_colors),
                  row=1, col=1, secondary_y=True)
    fig.update_yaxes(range=[0, df["volume"].max() * 4], showgrid=False, visible=False, row=1, col=1, secondary_y=True)

    draw_setups(fig, setups)
    fig.add_hline(y=current_price, line_dash="dot", line_color="#ffffff", line_width=1, row=1, col=1,
                  annotation_text=fp(current_price), annotation_position="right")

    bull = [p for p in patterns if p["direction"] == "bull"]
    bear = [p for p in patterns if p["direction"] == "bear"]
    if bull:
        fig.add_trace(go.Scatter(
            x=[df["timestamp"].iloc[p["i"]] for p in bull], y=[df["low"].iloc[p["i"]] * 0.998 for p in bull],
            mode="markers", name="Bullische Muster", text=[p["name"] for p in bull],
            marker=dict(symbol="triangle-up", size=12, color="#00ffcc", line=dict(width=1, color="#0b0e14")),
        ), row=1, col=1, secondary_y=False)
    if bear:
        fig.add_trace(go.Scatter(
            x=[df["timestamp"].iloc[p["i"]] for p in bear], y=[df["high"].iloc[p["i"]] * 1.002 for p in bear],
            mode="markers", name="Bärische Muster", text=[p["name"] for p in bear],
            marker=dict(symbol="triangle-down", size=12, color="#ff4d4d", line=dict(width=1, color="#0b0e14")),
        ), row=1, col=1, secondary_y=False)

    y_min, y_max = float(df["low"].min()), float(df["high"].max())
    for s in setups:
        if s.get("draw") and not s["status"].startswith("⛔") and abs(s["entry"] - current_price) / current_price <= 0.15:
            y_min, y_max = min(y_min, s["zone_lo"]), max(y_max, s["zone_hi"])
            if show_levels and s["name"].startswith("882"):
                y_min, y_max = min(y_min, s["sl"], *s["tps"]), max(y_max, s["sl"], *s["tps"])
    fig.update_yaxes(range=[y_min * 0.995, y_max * 1.005], row=1, col=1, secondary_y=False)

    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["rsi"], name="RSI", line=dict(color="#58a6ff", width=2)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="rgba(255,77,77,0.6)", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="rgba(0,255,204,0.6)", row=2, col=1)
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["liquidity_score"], fill="tozeroy", name="Volumen-Druck",
        line=dict(color="#ff9900", width=2), fillcolor="rgba(255,153,0,0.2)",
    ), row=3, col=1)
    fig.update_layout(
        template="plotly_dark", height=height, xaxis_rangeslider_visible=False, hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,17,23,0.85)",
        margin=dict(l=10, r=70, t=40, b=10), dragmode="pan", legend=dict(orientation="h", y=1.04, x=0),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(48,54,61,0.5)")
    return fig


# ================================================================ SEITENLEISTE
st.sidebar.header("🎯 Dashboard-Steuerung")
coin_choice = st.sidebar.selectbox("Wähle einen Coin", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"])

timeframe_options = {
    "15 Minuten": "15m", "30 Minuten": "30m", "1 Stunde": "1h", "2 Stunden": "2h",
    "4 Stunden": "4h", "12 Stunden": "12h", "1 Tag": "1d", "3 Tage": "3d",
}
timeframe_label = st.sidebar.selectbox("Zeitfenster", list(timeframe_options.keys()), index=4)
tf = timeframe_options[timeframe_label]
chart_mode = st.sidebar.radio("Chart-Ansicht", ["Eigener Chart (EMAs, Zonen, Muster)", "TradingView (alle Zeichen-Tools)"])

st.sidebar.markdown("---")
st.sidebar.header("🪟 Layout-Studio")
chart_height = st.sidebar.slider("Chart-Höhe (Pixel)", 450, 1000, 700, 50)
chart_ratio = st.sidebar.slider("Chart-Breite (gegenüber Info-Spalte)", 2, 8, 5)
show_mtf = st.sidebar.checkbox("MTF-Ampel anzeigen", value=True)
show_score = st.sidebar.checkbox("Setup-Score anzeigen", value=True)
show_tips = st.sidebar.checkbox("Einstiegs-Tipps anzeigen", value=True)
show_levels = st.sidebar.checkbox("SL & TPs im Eigenen Chart zeigen", value=False)

st.sidebar.markdown("---")
st.sidebar.header("💶 Risiko-Rechner")
risk_eur = st.sidebar.number_input("Risiko pro Trade (€)", min_value=1.0, max_value=1000.0, value=10.0, step=1.0)
leverage = st.sidebar.number_input("Hebel (nur für die Margin-Anzeige)", min_value=1, max_value=125, value=5, step=1)
eur_usdt = fetch_eur_usdt()
money_unit, money_div = "USDT", 1.0
risk_usdt = risk_eur * eur_usdt if eur_usdt else risk_eur
if eur_usdt:
    st.sidebar.markdown(
        f"<div style='font-size:12px; color:#8b949e; margin-top:-10px; margin-bottom:10px;'>"
        f"💱 Live-Kurs: 1 € ≈ {eur_usdt:,.4f} USDT<br>"
        f"Dein Risiko: {risk_eur:g} € ≈ {risk_usdt:,.2f} USDT pro Trade</div>",
        unsafe_allow_html=True,
    )
else:
    st.sidebar.markdown(
        "<div style='font-size:12px; color:#ffa500; margin-top:-10px; margin-bottom:10px;'>"
        "⚠️ Euro-Kurs nicht abrufbar – Risiko wird direkt als USDT-Betrag verwendet.</div>",
        unsafe_allow_html=True,
    )

st.sidebar.markdown("---")
st.sidebar.header("🔔 Alarm-System")
selected_alarm = st.sidebar.selectbox(
    "Wähle Alarm-Typ",
    [
        "Kein Alarm aktiv",
        "1. 882 Long/Short Zonen-Alarm (Preis berührt Zone)",
        "2. RSI Extreme Alarm (RSI > 70 oder < 30)",
        "3. Volumen-Spike Alarm (hoher Volumen-Druck)",
        "4. Strategie-Alarm (GUSS-Einstieg / LSOB-Signal)",
    ],
)
alarm_active = st.sidebar.checkbox("Alarm scharf schalten", value=True)
sound_on = st.sidebar.checkbox("Alarm-Ton abspielen", value=True)
sound_type = st.sidebar.selectbox("Alarm-Sound", list(SOUNDS.keys()))
auto_refresh = st.sidebar.checkbox("Automatisch aktualisieren", value=False)
refresh_sec = st.sidebar.selectbox("Aktualisierung alle …", [30, 60, 120, 300], index=1)

# ================================================================ KOPF
st.title("⚡ Swing Sniper · Master-Terminal")
st.caption("882-Retracement · Golden Pocket · GUSS · LSOB · Kerzenmuster · Backtest – alles in einem Dashboard")

# ---- Fear & Greed
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

# ---- Hauptdaten (nur 1 Abfrage für das gewählte Zeitfenster)
try:
    df = fetch_binance_data(coin_choice, tf)
except Exception as e:
    st.error(str(e))
    st.stop()

df = calculate_analytics(df).tail(150).reset_index(drop=True)

current_price = float(df["close"].iloc[-1])
price_change = current_price - float(df["close"].iloc[0])
rsi_val = df["rsi"].iloc[-1]
if pd.isna(rsi_val):
    rsi_val = 50.0
atr = df["atr"].iloc[-1]
if pd.isna(atr) or atr <= 0:
    atr = float((df["high"] - df["low"]).mean())

dec = price_decimals(current_price)
qty_dec = 5 if current_price >= 10000 else 3 if current_price >= 100 else 1
coin_symbol = coin_choice.split("/")[0]


def fp(x):
    return f"{x:,.{dec}f} USDT"


# ---- Setups: Fibonacci-Swings, EMA-Pullbacks, GUSS, LSOB
pivots = find_pivots(df)
up_leg, down_leg = latest_legs(pivots, 4 * atr)
long_setups, short_setups = [], []
if up_leg:
    long_setups.append(fib_setup("long", up_leg[0], up_leg[1], atr, "882-Retracement (82–88 %)", "882-Retracement",
                                 (0.82, 0.88), 0.85, 1.0, [0.5, 0.236, 0.0]))
    long_setups.append(fib_setup("long", up_leg[0], up_leg[1], atr, "Golden Pocket (61,8–65 %)", "Golden Pocket",
                                 (0.618, 0.65), 0.64, 0.786, [0.382, 0.236, 0.0]))
if down_leg:
    short_setups.append(fib_setup("short", down_leg[0], down_leg[1], atr, "882-Retracement (82–88 %)", "882-Retracement",
                                  (0.82, 0.88), 0.85, 1.0, [0.5, 0.236, 0.0]))
    short_setups.append(fib_setup("short", down_leg[0], down_leg[1], atr, "Golden Pocket (61,8–65 %)", "Golden Pocket",
                                  (0.618, 0.65), 0.64, 0.786, [0.382, 0.236, 0.0]))
for length in (21, 50, 200):
    ema_value = float(df[f"ema{length}"].iloc[-1])
    for direction, bucket in (("long", long_setups), ("short", short_setups)):
        s = ema_setup(direction, ema_value, atr, length, current_price)
        if s:
            bucket.append(s)

guss = detect_guss(df)
lsob = detect_lsob(df)
if guss["setup"]:
    long_setups.append(guss["setup"])
if lsob["long"]["setup"]:
    long_setups.append(lsob["long"]["setup"])
if lsob["short"]["setup"]:
    short_setups.append(lsob["short"]["setup"])
for s in long_setups + short_setups:
    enrich(s, current_price, risk_usdt, money_div, leverage)

long_main = next((s for s in long_setups if s["name"].startswith("882")), None)
short_main = next((s for s in short_setups if s["name"].startswith("882")), None)
all_setups = long_setups + short_setups

# ---- Trend, Muster, MTF, Score
ema50_now, ema200_now = float(df["ema50"].iloc[-1]), float(df["ema200"].iloc[-1])
bias = trend_bias(current_price, ema50_now, ema200_now)
bias_color = {"BULLISCH": "#00ffcc", "BÄRISCH": "#ff4d4d"}.get(bias, "#ffffff")
patterns = detect_patterns(df, long_setups, short_setups)
sideways_now = is_sideways(df)
mtf = {frame: fetch_mtf_bias(coin_choice, frame) for frame in MTF_FRAMES} if show_mtf else {}
last_closed = len(df) - 2
long_score, long_parts = setup_score("long", current_price, atr, bias, mtf, long_setups, patterns, sideways_now, rsi_val, last_closed)
short_score, short_parts = setup_score("short", current_price, atr, bias, mtf, short_setups, patterns, sideways_now, rsi_val, last_closed)

# ---- Alarm-Logik
alarm_triggered = False
alarm_message = ""
if alarm_active:
    in_long = bool(long_main and long_main["status"].startswith("🎯"))
    in_short = bool(short_main and short_main["status"].startswith("🎯"))
    fresh_lsob = [d for d in ("long", "short") if lsob[d]["state"] == "rejected" and (lsob[d].get("hit") or 0) >= len(df) - 3]
    if "1." in selected_alarm and (in_long or in_short):
        alarm_triggered = True
        alarm_message = f"🚨 ALARM: Kurs ({fp(current_price)}) ist in der 882-{'Long' if in_long else 'Short'}-Zone!"
    elif "2." in selected_alarm and (rsi_val > 70 or rsi_val < 30):
        alarm_triggered = True
        alarm_message = f"🚨 ALARM: RSI im Extrembereich ({rsi_val:.1f})!"
    elif "3." in selected_alarm and df["liquidity_score"].iloc[-1] > df["liquidity_score"].mean() * 1.5:
        alarm_triggered = True
        alarm_message = "🚨 ALARM: Hoher Volumen-Druck (Volumen × Spanne) erkannt!"
    elif "4." in selected_alarm and (guss["state"] == "touch" or fresh_lsob):
        alarm_triggered = True
        alarm_message = "🚨 ALARM: " + ("GUSS – Kurs an der 50 EMA!" if guss["state"] == "touch" else f"LSOB {fresh_lsob[0].upper()} – Zone wurde abgelehnt!")

# ---- Kopfzeile: Status, Fear & Greed, KPIs
alarm_state = "Alarm scharf" if (alarm_active and selected_alarm != "Kein Alarm aktiv") else "Alarm aus"
refresh_state = f"Auto-Update alle {refresh_sec} s" if auto_refresh else "Auto-Update aus"
st.markdown(
    f"<div class='status-bar'>🕓 Zuletzt aktualisiert: {datetime.now().strftime('%H:%M:%S')} Uhr · {alarm_state} · {refresh_state}</div>",
    unsafe_allow_html=True,
)

rsi_color = "#ff4d4d" if rsi_val > 70 else "#00ffcc" if rsi_val < 30 else "#8b949e"
rsi_text = "Überkauft" if rsi_val > 70 else "Überverkauft" if rsi_val < 30 else "Neutral"
change_color = "#00ffcc" if price_change >= 0 else "#ff4d4d"
if long_main and long_main["status"].startswith("🎯"):
    signal, signal_color, signal_sub = "LONG-ZONE", "#00ffcc", "Kurs in der 882-Long-Zone"
elif short_main and short_main["status"].startswith("🎯"):
    signal, signal_color, signal_sub = "SHORT-ZONE", "#ff4d4d", "Kurs in der 882-Short-Zone"
else:
    signal, signal_color, signal_sub = "WAIT", "#ffa500", "Kein Kurs in einer 882-Zone"

k0, k1, k2, k3, k4 = st.columns([1.5, 1.2, 1, 1, 1])
with k0:
    st.markdown(
        f"<div class='fg-card' style='border-color:{fg_color};'>"
        f"<div style='color:#8b949e; font-size:13px;'>😎 Fear &amp; Greed Index</div>"
        f"<div class='fg-emoji'>{fg_emoji}</div>"
        f"<div class='fg-value' style='color:{fg_color};'>{fg_number} / 100 · {fg_class or 'n/a'}</div>"
        f"<div class='fg-text'>{fg_text}</div></div>",
        unsafe_allow_html=True,
    )
with k1:
    st.markdown(metric_card(f"{coin_choice} ({tf})", f"{current_price:,.{dec}f} USDT", f"{price_change:+,.{dec}f} USDT", color=change_color), unsafe_allow_html=True)
with k2:
    st.markdown(metric_card("Swing-Signal", signal, signal_sub, color=signal_color), unsafe_allow_html=True)
with k3:
    st.markdown(metric_card("Markt-Bias", bias, "Kurs vs. EMA 50 / EMA 200", color=bias_color), unsafe_allow_html=True)
with k4:
    st.markdown(metric_card("RSI (14)", f"{rsi_val:.1f}", rsi_text, color=rsi_color, border=rsi_color), unsafe_allow_html=True)

if alarm_triggered:
    st.markdown(f"<div class='alert-box'>{alarm_message}</div>", unsafe_allow_html=True)
    if sound_on:
        components.html(alarm_sound_html(sound_type), height=0)

# ================================================================ TABS
tab_dash, tab_entries, tab_patterns, tab_backtest, tab_library = st.tabs(
    ["📊 Dashboard", "🎯 Einstiege & Positionsgröße", "🕯️ Muster & Strategien", "🤖 Backtest", "📖 Nachschlagewerk"]
)

# ---------------------------------------------------------------- Tab 1: Dashboard
with tab_dash:
    if show_mtf:
        st.markdown(mtf_html(mtf), unsafe_allow_html=True)
    chart_col, side_col = st.columns([chart_ratio, 2])
    with chart_col:
        if chart_mode.startswith("TradingView"):
            components.html(tradingview_widget(coin_choice, tf), height=chart_height)
            st.caption(
                "TradingView-Widget: Zeichen-Tools links am Chart. Einstiegszonen und Kerzenmuster findest du in den "
                "Tabs; eingezeichnet werden sie in der Ansicht „Eigener Chart“."
            )
        else:
            fig = build_main_chart(df, coin_choice, all_setups, patterns, chart_height, current_price)
            show_plotly(fig, {
                "scrollZoom": True, "displaylogo": False,
                "modeBarButtonsToAdd": ["drawline", "drawopenpath", "drawrect", "eraseshape"],
            })
    with side_col:
        if show_score:
            st.markdown(score_card("🟢 Long-Score", "#00ffcc", long_score, long_parts), unsafe_allow_html=True)
            st.markdown(score_card("🔴 Short-Score", "#ff4d4d", short_score, short_parts), unsafe_allow_html=True)
            st.caption("Checkliste aus Zone, Trend, Zeitfenstern und Mustern – keine Gewinnwahrscheinlichkeit.")
        long_prox = proximity_percent(current_price, long_main["zone_lo"], long_main["zone_hi"]) if long_main else 0
        short_prox = proximity_percent(current_price, short_main["zone_lo"], short_main["zone_hi"]) if short_main else 0
        st.markdown(setup_card("🟢 882 LONG", "#00ffcc", long_main, fp, long_prox), unsafe_allow_html=True)
        st.markdown(setup_card("🔴 882 SHORT", "#ff4d4d", short_main, fp, short_prox), unsafe_allow_html=True)

    if show_tips:
        st.subheader("💡 Aktuelle Einstiegs-Tipps")
        tips = build_tips(current_price, bias, rsi_val, fg_value, long_setups, short_setups, patterns, fp)
        if guss["state"] == "armed":
            tips.insert(1, ("info", f"GUSS aufgebaut: Korrektur ohne bullische Kerze läuft. Einstieg an der 50 EMA bei {fp(guss['setup']['entry'])}."))
        elif guss["state"] == "touch":
            tips.insert(1, ("warn", f"GUSS: Kurs hat die 50 EMA erreicht ({fp(guss['setup']['entry'])}) – Einstiegsbereich der Strategie."))
        for d, label in (("short", "Short"), ("long", "Long")):
            if lsob[d]["state"] == "armed":
                tips.insert(1, ("info", f"LSOB {label}: Sweep + 2 Gegenkerzen erkannt, Orderblock-Zone bei {fp(lsob[d]['setup']['zone_lo'])} bis {fp(lsob[d]['setup']['zone_hi'])} – wartet auf den Rücklauf."))
            elif lsob[d]["state"] == "rejected":
                tips.insert(1, ("good", f"LSOB {label}: Orderblock-Zone wurde abgelehnt – das Signal der Strategie ist da."))
        for kind, text in tips:
            st.markdown(f"<div class='tip tip-{kind}'>{text}</div>", unsafe_allow_html=True)
        st.caption("Regelbasierte Hinweise – keine Anlageberatung und keine Gewinn-Garantie.")

# ---------------------------------------------------------------- Tab 2: Einstiege
with tab_entries:
    st.subheader("🟢 Long-Einstiege")
    if long_setups:
        show_table(levels_frame(long_setups, fp))
        st.markdown(f"**Positionsgröße bei {risk_eur:g} € Risiko pro Trade** (Hebel {leverage}x nur für die Margin-Anzeige)")
        st.markdown(sizing_table_html(long_setups, coin_symbol, qty_dec, leverage, eur_usdt), unsafe_allow_html=True)
    else:
        st.info("Kein gültiger Aufwärts-Swing gefunden – aktuell keine Long-Einstiege berechenbar.")

    st.subheader("🔴 Short-Einstiege")
    if short_setups:
        show_table(levels_frame(short_setups, fp))
        st.markdown(f"**Positionsgröße bei {risk_eur:g} € Risiko pro Trade** (Hebel {leverage}x nur für die Margin-Anzeige)")
        st.markdown(sizing_table_html(short_setups, coin_symbol, qty_dec, leverage, eur_usdt), unsafe_allow_html=True)
    else:
        st.info("Kein gültiger Abwärts-Swing gefunden – aktuell keine Short-Einstiege berechenbar.")
    st.caption(
        "Gebühren und Funding sind nicht eingerechnet. Mengen ggf. auf die Mindestschrittgröße der Börse runden. "
        "Fibonacci-Setups: Stop-Loss hinter dem Swing-Extrem (+0,2 ATR). GUSS: TP3 ist eine eigene Erweiterung (0,272 des Swings), "
        "TP1/TP2 = 21 EMA / Swing-Hoch."
    )

# ---------------------------------------------------------------- Tab 3: Muster & Strategien
with tab_patterns:
    st.subheader("🕯️ Erkannte Kerzenmuster (letzte 12 geschlossene Kerzen)")
    if patterns:
        show_table(patterns_frame(patterns))
    else:
        st.info("In den letzten 12 geschlossenen Kerzen wurde kein Muster aus dem Guide erkannt.")
    st.caption("Muster zählen nur mit Kontext: in einer Einstiegszone, mit dem Trend und nicht in einer Seitwärtsphase.")

    st.subheader("🎯 Strategie-Signale")
    g1, g2, g3 = st.columns(3)
    with g1:
        extra = ""
        if guss["confluence"]:
            extra = f"<div class='row-line'><b>Fibonacci-Konfluenz an der 50 EMA:</b> {', '.join(str(x) for x in guss['confluence'])}</div>"
        elif guss["setup"]:
            extra = "<div class='row-line' style='color:#8b949e;'>Keine Fibonacci-Konfluenz an der 50 EMA (optionale Zusatzbestätigung).</div>"
        st.markdown(strategy_panel("🟢 GUSS (Long)", "#00ffcc", guss, extra), unsafe_allow_html=True)
    with g2:
        st.markdown(strategy_panel("🔴 LSOB Short", "#ff4d4d", lsob["short"]), unsafe_allow_html=True)
    with g3:
        st.markdown(strategy_panel("🟢 LSOB Long", "#00ffcc", lsob["long"]), unsafe_allow_html=True)
    st.caption(
        "GUSS folgt der Strategie-PDF (Überdehnung zur 21 EMA, Korrektur ohne bullische Kerze zur 50 EMA). "
        "Zur LSOB-Datei liegt im Projekt nur Text ohne Grafiken vor: Die Orderblock-Zone (Kerze vor den 2 Gegenkerzen) "
        "und die Bewertung „zu tief / abgelehnt“ sind meine Auslegung – bitte mit den Original-Bildern abgleichen."
    )

# ---------------------------------------------------------------- Tab 4: Backtest
with tab_backtest:
    st.subheader("🤖 Backtest der Fibonacci-Setups")
    st.markdown(
        f"Getestet werden **882-Retracement** und **Golden Pocket** (Long und Short) auf den letzten ~1000 Kerzen von "
        f"**{coin_choice} ({tf})**. Die Zonen werden Kerze für Kerze so berechnet, wie das Dashboard sie live sehen würde – "
        "ohne Blick in die Zukunft."
    )
    bt_run = st.button("🚀 Backtest starten")
    if bt_run:
        st.session_state["bt_key"] = (coin_choice, tf)
    if st.session_state.get("bt_key") == (coin_choice, tf):
        try:
            with st.spinner("Backtest läuft …"):
                bt_trades, bt_candles = cached_backtest(coin_choice, tf)
        except Exception as e:
            bt_trades, bt_candles = None, 0
            st.error(f"Backtest nicht möglich: {e}")
        if bt_trades is not None:
            if not bt_trades:
                st.info(f"Keine gefüllten Trades in {bt_candles} Kerzen. Wähle ein anderes Zeitfenster oder einen anderen Coin.")
            else:
                exit_label = st.selectbox("Position schließen bei …", ["TP1", "TP2", "TP3"], index=1)
                kx = ["TP1", "TP2", "TP3"].index(exit_label)
                table = backtest_table(bt_trades, kx)
                total = table[table["Setup"] == "Alle"].iloc[0]
                m1, m2, m3, m4 = st.columns(4)
                sum_r = float(total["Summe (R)"])
                with m1:
                    st.markdown(metric_card("Trades", f"{total['Trades']}", f"{bt_candles} Kerzen getestet"), unsafe_allow_html=True)
                with m2:
                    st.markdown(metric_card("Trefferquote", total["Treffer"], f"Exit bei {exit_label}", color="#00ffcc"), unsafe_allow_html=True)
                with m3:
                    st.markdown(metric_card("Ø Ergebnis je Trade", f"{total['Ø Ergebnis (R)']} R", f"≈ {float(total['Ø Ergebnis (R)']) * risk_eur:+.2f} € bei {risk_eur:g} € Risiko", color="#ffd700"), unsafe_allow_html=True)
                with m4:
                    st.markdown(metric_card("Max. Drawdown", f"{total['Max. Drawdown (R)']} R", f"Summe {sum_r:+.1f} R ≈ {sum_r * risk_eur:+.0f} €", color="#ff4d4d"), unsafe_allow_html=True)
                show_table(table)
                curve = equity_curve(bt_trades, kx)
                fig_eq = go.Figure()
                fig_eq.add_trace(go.Scatter(x=list(range(1, len(curve) + 1)), y=curve, mode="lines", name="Kumuliert (R)", line=dict(color="#00ffcc", width=2)))
                fig_eq.update_layout(template="plotly_dark", height=320, margin=dict(l=10, r=10, t=30, b=10),
                                     title=f"Kumuliertes Ergebnis in R (Exit bei {exit_label})", paper_bgcolor="rgba(0,0,0,0)")
                show_plotly(fig_eq, {"displaylogo": False})
                st.caption(
                    "R = dein Risiko pro Trade (1 R = Verlust am Stop-Loss). Annahmen: Einstieg, sobald der Kurs die Entry-Linie berührt "
                    "(max. 60 Kerzen Wartezeit); Haltedauer max. 120 Kerzen (dann Schluss zum Kerzenschlusskurs); bei SL und TP in "
                    "derselben Kerze zählt der SL; keine Gebühren, kein Funding, keine Slippage. Vergangenheit ist keine Garantie – "
                    "bei wenigen Trades sind die Zahlen kaum aussagekräftig."
                )
    else:
        st.info("Drücke „Backtest starten“, um die Auswertung für den gewählten Coin und das Zeitfenster zu berechnen.")

# ---------------------------------------------------------------- Tab 5: Nachschlagewerk
with tab_library:
    st.markdown(f"<div class='rules-box'>{GUIDE_RULES}</div>", unsafe_allow_html=True)
    st.subheader("🕯️ Kerzenmuster-Guide")
    l1, l2 = st.columns(2)
    with l1:
        st.markdown("#### 🟢 Bullish")
        for kind, tag, title, text in GUIDE_CARDS:
            if kind == "bullish":
                st.markdown(pattern_card(kind, tag, title, text), unsafe_allow_html=True)
    with l2:
        st.markdown("#### 🔴 Bearish")
        for kind, tag, title, text in GUIDE_CARDS:
            if kind == "bearish":
                st.markdown(pattern_card(kind, tag, title, text), unsafe_allow_html=True)
    st.markdown("#### 🟠 Vorsicht / meiden")
    for kind, tag, title, text in GUIDE_CARDS:
        if kind == "avoid":
            st.markdown(pattern_card(kind, tag, title, text), unsafe_allow_html=True)
    st.subheader("🎯 Strategie-Regeln")
    st.markdown(pattern_card("bullish", "GUSS · LONG", "GUSS Sniper-Entry",
        "1) Neues höheres Hoch mit klarer Dynamik, weit über der 21 EMA (Überdehnung). 2) Korrektur direkt zur 50 EMA – "
        "ohne bullische Kerze dazwischen, sonst ungültig (alternativ höheren Zeitrahmen prüfen). 3) Einstieg an der 50 EMA, "
        "ideal mit Fib 0.5 / 0.559 / 0.618 / 0.667 / 0.786 an derselben Stelle. 4) TP1 an der 21 EMA (z. B. 25 % mitnehmen), "
        "dann SL auf Break-Even. Bevorzugt große Coins mit hohem Volumen."), unsafe_allow_html=True)
    st.markdown(pattern_card("bearish", "LSOB · SHORT / LONG", "Liquidity Sweep Orderblock",
        "1) Liquidity Sweep: Preis nimmt ein vorheriges Hoch (Short) bzw. Tief (Long) heraus – gleiche Hochs ohne Überschreiten sind kein Sweep. "
        "2) Zwei Kerzen in Gegenrichtung. 3) Orderblock einzeichnen. 4) Preis kommt zurück zur Zone. Gültig: Zone wird abgelehnt, "
        "die Kerze schneidet nicht zu tief hinein. Ungültig: schließt zu weit in der Zone, Zone wird nicht respektiert oder nicht getroffen, "
        "neuer Liquidity Sweep."), unsafe_allow_html=True)
    st.markdown(pattern_card("avoid", "SETUP-SCORE", "So entsteht der Score",
        "Nähe zur Einstiegszone (30) + Trend (25) + passende Zeitfenster (20) + Kerzenmuster (25); Abzüge für Seitwärtsphase (−15) "
        "und RSI-Extrem gegen die Richtung (−10). Das ist eine Checkliste, keine Gewinnwahrscheinlichkeit."), unsafe_allow_html=True)

# ================================================================ AUTO-AKTUALISIERUNG
if auto_refresh:
    time.sleep(refresh_sec)
    st.rerun()

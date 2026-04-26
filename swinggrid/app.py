"""
AutoSwing — Live Crypto Grid Trading Dashboard
Redesigned frontend: terminal-dark, DM Mono + Syne, no default Streamlit chrome.
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from binance_client import BinanceClientWrapper as BinanceTestnetClient
from grid_strategy import GridTrader
from utils import (
    format_currency,
    format_btc,
    format_percentage,
    create_candlestick_chart,
    create_price_line_chart,
    format_trade_for_display,
    get_trend_indicator,
)

st.set_page_config(
    page_title="AutoSwing",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── FONTS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
*, *::before, *::after { box-sizing: border-box; }

html, .stApp {
    background-color: #08090C !important;
    font-family: 'Syne', sans-serif !important;
    color: #CBD5E1 !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer,
header[data-testid="stHeader"],
[data-testid="collapsedControl"],
[data-testid="stSidebar"] { display: none !important; }

.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stMain"] > div:first-child { padding-top: 0 !important; }

/* ── TOP BAR ── */
.as-topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 2rem; height: 52px;
    background: #0C0D12; border-bottom: 1px solid #1C2030;
}
.as-logo {
    font-family: 'Syne', sans-serif; font-weight: 800;
    font-size: 1rem; letter-spacing: 0.12em; text-transform: uppercase; color: #E2E8F0;
}
.as-logo em { font-style: normal; color: #00FFB0; }
.as-topbar-right { display: flex; align-items: center; gap: 0.75rem; }

/* ── PILLS ── */
.pill {
    display: inline-flex; align-items: center; gap: 0.35rem;
    padding: 0.2rem 0.65rem; border-radius: 999px;
    font-family: 'DM Mono', monospace; font-size: 0.65rem;
    font-weight: 500; letter-spacing: 0.06em; text-transform: uppercase; white-space: nowrap;
}
.pill-live    { background: rgba(0,255,176,0.08); border: 1px solid rgba(0,255,176,0.22); color: #00FFB0; }
.pill-sandbox { background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.22); color: #F59E0B; }
.pill-error   { background: rgba(255,69,96,0.08); border: 1px solid rgba(255,69,96,0.22); color: #FF4560; }
.pill-run     { background: rgba(0,255,176,0.06); border: 1px solid rgba(0,255,176,0.18); color: #00D4A0; }
.pill-stop    { background: rgba(100,116,139,0.08); border: 1px solid rgba(100,116,139,0.2); color: #64748B; }
.dot { width: 5px; height: 5px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
.dot-g { background: #00FFB0; animation: blink 1.8s ease-in-out infinite; }
.dot-y { background: #F59E0B; }
.dot-r { background: #FF4560; }
.dot-g2 { background: #00D4A0; animation: blink 2s ease-in-out infinite; }
.dot-s { background: #64748B; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.25} }

/* ── SECTION LABEL ── */
.as-section-label {
    display: block; font-family: 'DM Mono', monospace; font-size: 0.6rem;
    letter-spacing: 0.14em; text-transform: uppercase;
    color: #334155; margin-bottom: 0.6rem;
}

/* ── PRICE HERO ── */
.as-price-hero {
    background: #0C0D12; border: 1px solid #1C2030; border-radius: 8px;
    padding: 1rem 1.4rem; display: flex; align-items: flex-end;
    justify-content: space-between; margin-bottom: 1rem;
}
.as-price-symbol {
    font-family: 'DM Mono', monospace; font-size: 0.62rem;
    letter-spacing: 0.12em; text-transform: uppercase; color: #334155; margin-bottom: 0.2rem;
}
.as-price-val {
    font-family: 'DM Mono', monospace; font-size: 2.1rem; font-weight: 400;
    letter-spacing: -0.02em; line-height: 1; color: #E2E8F0;
}
.as-price-val.up   { color: #00FFB0; }
.as-price-val.down { color: #FF4560; }
.as-price-rhs {
    text-align: right; font-family: 'DM Mono', monospace;
    font-size: 0.7rem; color: #475569; line-height: 1.7;
}

/* ── METRIC CARDS ── */
.as-metrics { display: grid; grid-template-columns: repeat(4,1fr); gap: 0.75rem; margin-bottom: 1rem; }
.as-card {
    background: #0C0D12; border: 1px solid #1C2030; border-radius: 8px;
    padding: 0.9rem 1.1rem; position: relative; overflow: hidden;
}
.as-card::after { content:''; position:absolute; top:0;left:0;right:0; height:2px; background:#1C2030; }
.as-card.pos::after { background: linear-gradient(90deg,#00FFB0,#00CC8A); }
.as-card.neg::after { background: linear-gradient(90deg,#FF4560,#CC1133); }
.as-card-label {
    font-family: 'DM Mono', monospace; font-size: 0.6rem;
    letter-spacing: 0.1em; text-transform: uppercase; color: #334155; margin-bottom: 0.45rem;
}
.as-card-value {
    font-family: 'DM Mono', monospace; font-size: 1.25rem;
    font-weight: 400; color: #CBD5E1; line-height: 1.1;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.as-card-value.green { color: #00FFB0; }
.as-card-value.red   { color: #FF4560; }
.as-card-sub { font-family: 'DM Mono', monospace; font-size: 0.65rem; margin-top: 0.3rem; color: #334155; }
.as-card-sub.green { color: rgba(0,255,176,0.6); }
.as-card-sub.red   { color: rgba(255,69,96,0.6); }

/* ── TRADE TABLE ── */
.as-trade-table { background:#0C0D12; border:1px solid #1C2030; border-radius:8px; overflow:hidden; }
.as-trade-header {
    display: grid; grid-template-columns: 1fr 1fr 1.4fr 1.4fr 1.2fr 1.2fr;
    padding: 0.55rem 1rem; background: #0A0B10; border-bottom: 1px solid #1C2030;
    font-family: 'DM Mono', monospace; font-size: 0.6rem;
    letter-spacing: 0.1em; text-transform: uppercase; color: #334155;
}
.as-trade-row {
    display: grid; grid-template-columns: 1fr 1fr 1.4fr 1.4fr 1.2fr 1.2fr;
    padding: 0.55rem 1rem; border-bottom: 1px solid #141720;
    font-family: 'DM Mono', monospace; font-size: 0.78rem; color: #64748B; align-items: center;
}
.as-trade-row:last-child { border-bottom: none; }
.as-trade-row:hover { background: #10121A; }
.badge-buy  { display:inline-block; padding:0.12rem 0.45rem; background:rgba(0,255,176,0.1); color:#00FFB0; border-radius:3px; font-size:0.68rem; }
.badge-sell { display:inline-block; padding:0.12rem 0.45rem; background:rgba(255,69,96,0.1); color:#FF4560; border-radius:3px; font-size:0.68rem; }
.pnl-pos { color: #00D4A0; }
.pnl-neg { color: #FF4560; }

/* ── STATS BLOCK ── */
.as-stat-block { background:#0C0D12; border:1px solid #1C2030; border-radius:8px; padding:1rem 1.1rem; }
.as-stat-row {
    display:flex; justify-content:space-between; align-items:baseline;
    padding:0.45rem 0; border-bottom:1px solid #141720;
    font-family:'DM Mono',monospace; font-size:0.75rem;
}
.as-stat-row:last-child { border-bottom:none; }
.as-stat-key { color:#334155; font-size:0.68rem; text-transform:uppercase; letter-spacing:0.07em; }
.as-stat-val { color:#94A3B8; }

/* ── HOW IT WORKS ── */
.hiw-flow { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; margin: 0.75rem 0; }
.hiw-node {
    background: #0C0D12;
    border: 1px solid #1C2030;
    border-radius: 6px;
    padding: 9px 14px;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #94A3B8;
    line-height: 1.4;
}
.hiw-node-accent {
    background: rgba(0,255,176,0.06);
    border: 1px solid rgba(0,255,176,0.22);
    border-radius: 6px;
    padding: 9px 14px;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #00FFB0;
    line-height: 1.4;
}
.hiw-arrow { font-family: 'DM Mono', monospace; font-size: 0.85rem; color: #334155; }
.hiw-section {
    background: #0C0D12;
    border: 1px solid #1C2030;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
}
.hiw-section h4 {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.62rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #334155 !important;
    margin-bottom: 0.6rem !important;
    font-weight: 400 !important;
}
.hiw-section p, .hiw-section li {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: #64748B;
    line-height: 1.7;
    margin: 0 0 0.35rem 0;
}
.hiw-section li { margin-left: 1rem; }
.hiw-val { color: #94A3B8; }
.hiw-green { color: #00FFB0; }
.hiw-yellow { color: #F59E0B; }
.hiw-param-row {
    display: flex; justify-content: space-between; align-items: baseline;
    padding: 0.4rem 0; border-bottom: 1px solid #141720;
    font-family: 'DM Mono', monospace; font-size: 0.75rem;
}
.hiw-param-row:last-child { border-bottom: none; }
.hiw-param-key { color: #475569; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.06em; }
.hiw-param-desc { color: #64748B; font-size: 0.72rem; max-width: 60%; text-align: right; }

/* ── WIDGET OVERRIDES ── */
div[data-testid="stSlider"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stRadio"] > label {
    font-family: 'DM Mono', monospace !important; font-size: 0.68rem !important;
    letter-spacing: 0.08em !important; text-transform: uppercase !important; color: #334155 !important;
}
div[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background: #00FFB0 !important; border-color: #00FFB0 !important;
}
div[data-testid="stSelectbox"] [data-baseweb="select"] {
    background: #10121A !important; border-color: #1C2030 !important;
}
div[data-testid="stSelectbox"] [data-baseweb="select"] * {
    font-family: 'DM Mono', monospace !important; font-size: 0.8rem !important;
    color: #94A3B8 !important; background: #10121A !important;
}
div[data-testid="stRadio"] p { font-family:'DM Mono',monospace !important; font-size:0.75rem !important; color:#94A3B8 !important; }
div[data-testid="stRadio"] [data-baseweb="radio"] span { border-color: #1C2030 !important; }
div[data-testid="stRadio"] [data-baseweb="radio"][aria-checked="true"] span { background: #00FFB0 !important; border-color: #00FFB0 !important; }

.stButton > button {
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important;
    font-size: 0.72rem !important; letter-spacing: 0.08em !important;
    text-transform: uppercase !important; border-radius: 5px !important;
    padding: 0.45rem 1.1rem !important; transition: all 0.12s ease !important; border: none !important;
}
.stButton > button[kind="primary"]  { background: #00FFB0 !important; color: #08090C !important; }
.stButton > button[kind="primary"]:hover { background: #00E8A0 !important; box-shadow: 0 0 18px rgba(0,255,176,0.2) !important; }
.stButton > button[kind="secondary"] { background: #10121A !important; color: #64748B !important; border: 1px solid #1C2030 !important; }
.stButton > button[kind="secondary"]:hover { border-color: #334155 !important; color: #94A3B8 !important; }

div[data-testid="stExpander"] details > summary {
    font-family: 'DM Mono', monospace !important; font-size: 0.68rem !important;
    letter-spacing: 0.1em !important; text-transform: uppercase !important;
    color: #475569 !important; background: #0C0D12 !important; border-color: #1C2030 !important; border-radius: 6px !important;
}
div[data-testid="stExpander"] .streamlit-expanderContent {
    background: #0C0D12 !important; border: 1px solid #1C2030 !important;
    border-top: none !important; border-radius: 0 0 6px 6px !important;
}
.stPlotlyChart > div { border: 1px solid #1C2030 !important; border-radius: 8px !important; overflow: hidden !important; }
.stDataFrame * { font-family: 'DM Mono', monospace !important; font-size: 0.78rem !important; }
div[data-testid="stAlert"] {
    background: #0C0D12 !important; border: 1px solid #1C2030 !important;
    border-radius: 6px !important; font-family: 'DM Mono', monospace !important; font-size: 0.78rem !important;
}
.stMarkdown p { font-size: 0.85rem !important; color: #64748B !important; }
h1,h2,h3 { font-family: 'Syne', sans-serif !important; color: #E2E8F0 !important; }
hr { border-color: #1C2030 !important; }
div[data-testid="stToast"] {
    background: #141720 !important; border: 1px solid #1C2030 !important;
    border-radius: 6px !important; font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important; color: #94A3B8 !important;
}
.stCaption { font-family: 'DM Mono', monospace !important; color: #475569 !important; font-size: 0.68rem !important; }
</style>
""", unsafe_allow_html=True)


# ── SESSION STATE ─────────────────────────────────────────────────────────────
def init_session_state():
    if "bot_running" not in st.session_state:
        st.session_state.bot_running = False
    if "trader" not in st.session_state:
        st.session_state.trader = GridTrader()
    if "binance_client" not in st.session_state:
        api_key = api_secret = None
        use_mainnet = use_binance_us = False
        try:
            secrets = st.secrets.get("binance", {})
            api_key = secrets.get("api_key")
            api_secret = secrets.get("api_secret")
            use_mainnet = secrets.get("product_mode", False)
            use_binance_us = secrets.get("use_binance_us", False)
        except Exception:
            pass
        if not api_key:
            api_key = os.environ.get("BINANCE_TESTNET_API_KEY")
            api_secret = os.environ.get("BINANCE_TESTNET_API_SECRET")
            use_mainnet = os.environ.get("USE_MAINNET_DATA", "False").lower() == "true"
            use_binance_us = os.environ.get("USE_BINANCE_US", "False").lower() == "true"
        st.session_state.binance_client = BinanceTestnetClient(
            api_key, api_secret, use_mainnet, use_binance_us
        )
    if "last_price" not in st.session_state:
        st.session_state.last_price = None
    if "chart_type" not in st.session_state:
        st.session_state.chart_type = "Candlestick"


# ── TOP BAR ───────────────────────────────────────────────────────────────────
def render_topbar():
    client = st.session_state.binance_client
    is_live = getattr(client, "use_mainnet", False)
    conn_status = getattr(client, "connection_status", "UNKNOWN")
    error = getattr(client, "last_error", None)

    if is_live:
        if conn_status == "CONNECTED":
            conn_pill = '<span class="pill pill-live"><span class="dot dot-g"></span>Live</span>'
        elif conn_status == "RESTRICTED":
            conn_pill = '<span class="pill pill-sandbox"><span class="dot dot-y"></span>Restricted</span>'
            if error:
                st.toast(f"Connection: {error}")
        else:
            conn_pill = '<span class="pill pill-error"><span class="dot dot-r"></span>Error</span>'
            if error:
                st.toast(f"Error: {error}")
    else:
        conn_pill = '<span class="pill pill-sandbox"><span class="dot dot-y"></span>Sandbox</span>'

    bot_pill = (
        '<span class="pill pill-run"><span class="dot dot-g2"></span>Running</span>'
        if st.session_state.bot_running
        else '<span class="pill pill-stop"><span class="dot dot-s"></span>Idle</span>'
    )

    st.markdown(f"""
    <div class="as-topbar">
      <div class="as-logo">AUTO<em>SWING</em></div>
      <div class="as-topbar-right">
        {conn_pill}
        {bot_pill}
        <span style="font-family:'DM Mono',monospace;font-size:0.62rem;color:#334155;letter-spacing:0.08em;">
          BTC/USDT · GRID
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── PRICE HERO ────────────────────────────────────────────────────────────────
def render_price_hero(current_price: float, last_price: float, stats: dict):
    if last_price and current_price > last_price:
        cls, arrow = "up", "↑"
        change = f"+{format_percentage(((current_price - last_price) / last_price) * 100)}"
    elif last_price and current_price < last_price:
        cls, arrow = "down", "↓"
        change = format_percentage(((current_price - last_price) / last_price) * 100)
    else:
        cls, arrow, change = "", "→", "0.00%"

    ref = stats.get("reference_price")
    ref_str = format_currency(ref) if ref else "—"
    pnl = stats.get("total_pnl", 0)
    pnl_color = "#00FFB0" if pnl >= 0 else "#FF4560"

    st.markdown(f"""
    <div class="as-price-hero">
      <div>
        <div class="as-price-symbol">BTC / USDT · Live</div>
        <div class="as-price-val {cls}">{arrow} {format_currency(current_price)}</div>
      </div>
      <div class="as-price-rhs">
        <div>Session Δ &nbsp;<span style="color:#94A3B8">{change}</span></div>
        <div>Reference &nbsp;<span style="color:#94A3B8">{ref_str}</span></div>
        <div>P&amp;L &nbsp;<span style="color:{pnl_color}">{format_currency(pnl)}</span></div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── METRIC CARDS ─────────────────────────────────────────────────────────────
def render_metrics(current_price: float, stats: dict):
    pnl = stats["total_pnl"]
    pnl_cls = "green" if pnl > 0 else ("red" if pnl < 0 else "")
    card_cls = "pos" if pnl > 0 else ("neg" if pnl < 0 else "")
    pnl_pct = (
        format_percentage((pnl / config.STARTING_USDT_BALANCE) * 100)
        if config.STARTING_USDT_BALANCE > 0 else "0.00%"
    )

    st.markdown(f"""
    <div class="as-metrics">
      <div class="as-card">
        <div class="as-card-label">USDT Balance</div>
        <div class="as-card-value">{format_currency(stats['usdt_balance'])}</div>
        <div class="as-card-sub">Available cash</div>
      </div>
      <div class="as-card">
        <div class="as-card-label">BTC Holdings</div>
        <div class="as-card-value" style="font-size:1rem">{format_btc(stats['btc_balance'])}</div>
        <div class="as-card-sub">≈ {format_currency(stats['btc_balance'] * current_price)}</div>
      </div>
      <div class="as-card">
        <div class="as-card-label">Portfolio Value</div>
        <div class="as-card-value">{format_currency(stats['portfolio_value'])}</div>
        <div class="as-card-sub">Cash + BTC</div>
      </div>
      <div class="as-card {card_cls}">
        <div class="as-card-label">Total P&amp;L</div>
        <div class="as-card-value {pnl_cls}">{format_currency(pnl)}</div>
        <div class="as-card-sub {pnl_cls}">{pnl_pct} since start</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── CHART ─────────────────────────────────────────────────────────────────────
def render_chart(client: BinanceTestnetClient, chart_type: str):
    df = client.get_klines(config.SYMBOL, config.KLINE_INTERVAL, config.KLINE_LIMIT)
    if chart_type == "Candlestick":
        fig = create_candlestick_chart(df, "BTC/USDT")
    else:
        fig = create_price_line_chart(df, "BTC/USDT")

    fig.update_layout(
        paper_bgcolor="#0C0D12",
        plot_bgcolor="#0C0D12",
        title=dict(text="BTC / USDT  ·  1m", font=dict(family="DM Mono", size=11, color="#334155")),
        xaxis=dict(
            gridcolor="#141720", linecolor="#1C2030",
            tickfont=dict(family="DM Mono", size=10, color="#334155"),
            rangeslider=dict(visible=False),
        ),
        yaxis=dict(
            gridcolor="#141720", linecolor="#1C2030",
            tickfont=dict(family="DM Mono", size=10, color="#334155"),
            side="right",
        ),
        margin=dict(l=0, r=64, t=36, b=28),
        height=360,
    )
    st.plotly_chart(fig, use_container_width=True)


# ── TRADE LOG ─────────────────────────────────────────────────────────────────
def render_trade_log(trades: list):
    st.markdown('<span class="as-section-label">Recent Trades</span>', unsafe_allow_html=True)

    if not trades:
        st.markdown("""
        <div style="padding:1.5rem;text-align:center;background:#0C0D12;border:1px solid #1C2030;
             border-radius:8px;font-family:'DM Mono',monospace;font-size:0.75rem;
             color:#334155;letter-spacing:0.06em;">
          NO TRADES YET — START THE BOT TO BEGIN
        </div>""", unsafe_allow_html=True)
        return

    formatted = [format_trade_for_display(t) for t in reversed(trades[-20:])]
    df = pd.DataFrame(formatted)

    def _color_type(val):
        if val == "BUY":
            return "color: #00FFB0; font-weight: 600"
        if val == "SELL":
            return "color: #FF4560; font-weight: 600"
        return ""

    def _color_pnl(val):
        if val == "—":
            return "color: #334155"
        try:
            num = float(str(val).replace("$", "").replace(",", "").replace("-", ""))
            return "color: #00D4A0" if "-" not in str(val) and num >= 0 else "color: #FF4560"
        except Exception:
            return ""

    styled = (
        df.style
        .map(_color_type, subset=["Type"])
        .map(_color_pnl, subset=["P&L"])
        .set_properties(**{
            "font-family": "'DM Mono', monospace",
            "font-size": "13px",
            "background-color": "#0C0D12",
            "color": "#64748B",
            "border-color": "#1C2030",
        })
        .set_table_styles([
            {"selector": "thead th", "props": [
                ("background-color", "#0A0B10"),
                ("color", "#334155"),
                ("font-family", "'DM Mono', monospace"),
                ("font-size", "11px"),
                ("text-transform", "uppercase"),
                ("letter-spacing", "0.1em"),
                ("border-bottom", "1px solid #1C2030"),
            ]},
            {"selector": "tbody tr:hover td", "props": [("background-color", "#10121A")]},
            {"selector": "td, th", "props": [("border-color", "#1C2030")]},
        ])
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)


# ── BOT STATS ─────────────────────────────────────────────────────────────────
def render_bot_stats(stats: dict):
    ref = stats.get("reference_price")
    ref_str = format_currency(ref) if ref else "—"

    rows = [
        ("Total Trades",     str(stats["total_trades"])),
        ("Realized P&L",     format_currency(stats["realized_pnl"])),
        ("Unrealized P&L",   format_currency(stats["unrealized_pnl"])),
        ("Reference Price",  ref_str),
        ("Buy Threshold",    f"{st.session_state.trader.buy_threshold:.2f}%"),
        ("Sell Threshold",   f"+{st.session_state.trader.sell_threshold:.2f}%"),
        ("Trade Size",       format_currency(config.TRADE_AMOUNT_USDT)),
        ("Symbol",           config.SYMBOL),
    ]
    rows_html = "".join(
        f'<div class="as-stat-row">'
        f'<span class="as-stat-key">{k}</span>'
        f'<span class="as-stat-val">{v}</span>'
        f'</div>'
        for k, v in rows
    )
    st.markdown(f"""
    <span class="as-section-label">Bot Statistics</span>
    <div class="as-stat-block">{rows_html}</div>
    """, unsafe_allow_html=True)


# ── SETTINGS PANEL (replaces sidebar) ────────────────────────────────────────
def render_settings_panel() -> int:
    with st.expander("Grid Settings & Controls", expanded=False):
        col_a, col_b, col_c = st.columns([1, 1, 1])

        with col_a:
            buy_threshold = st.slider(
                "Buy Threshold (%)",
                min_value=-5.0, max_value=-0.01,
                value=max(st.session_state.trader.buy_threshold, -5.0),
                step=0.01, format="%.2f",
                help="Buy when price drops this % below reference",
            )
            sell_threshold = st.slider(
                "Sell Threshold (%)",
                min_value=0.01, max_value=5.0,
                value=min(st.session_state.trader.sell_threshold, 5.0),
                step=0.01, format="%.2f",
                help="Sell when price rises this % above reference",
            )
            if (
                buy_threshold != st.session_state.trader.buy_threshold
                or sell_threshold != st.session_state.trader.sell_threshold
            ):
                st.session_state.trader.update_thresholds(buy_threshold, sell_threshold)

        with col_b:
            refresh_interval = st.selectbox(
                "Update Interval",
                options=[10, 15, 20, 30],
                index=1,
                format_func=lambda x: f"{x}s",
            )
            st.session_state.chart_type = st.radio(
                "Chart Type",
                options=["Candlestick", "Line"],
                horizontal=True,
            )

        with col_c:
            st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
            if st.button("Reset Portfolio", use_container_width=True, type="secondary"):
                st.session_state.trader.reset()
                st.session_state.bot_running = False
                st.rerun()
            st.caption(
                "Runs on Binance Testnet — no real money. "
                "Grid buys dips and sells rallies within a defined range."
            )

    return refresh_interval


# ── HOW IT WORKS ──────────────────────────────────────────────────────────────
def render_how_it_works():
    """Render the How It Works reference page."""

    st.markdown('<span class="as-section-label">AutoSwing — How It Works</span>', unsafe_allow_html=True)

    # ── Overview ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="hiw-section">
      <h4>What this dashboard does</h4>
      <p>AutoSwing is a simulated grid trading dashboard for BTC/USDT on Binance. It polls the Binance
      API for live price data, applies a threshold-based buy/sell strategy, and displays real-time
      portfolio metrics — without placing real orders or touching real money.</p>
      <p>All trades are virtual. Starting capital is $10,000 USDT. Use it to study grid trading
      mechanics, tune parameters, and observe how the strategy behaves across different market conditions.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Data flow diagram ─────────────────────────────────────────────────────
    st.markdown('<span class="as-section-label" style="margin-top:1rem;">Data &amp; execution flow</span>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#0C0D12;border:1px solid #1C2030;border-radius:8px;padding:1.2rem 1.4rem;margin-bottom:0.75rem;">

      <p style="font-family:'DM Mono',monospace;font-size:0.6rem;letter-spacing:0.12em;text-transform:uppercase;color:#334155;margin-bottom:0.75rem;">Price ingestion</p>
      <div class="hiw-flow">
        <div class="hiw-node-accent">Binance REST API<br><span style="color:#475569;font-size:0.66rem;">/api/v3/ticker/price</span></div>
        <span class="hiw-arrow">→</span>
        <div class="hiw-node">BinanceClientWrapper<br><span style="color:#475569;font-size:0.66rem;">get_current_price()</span></div>
        <span class="hiw-arrow">→</span>
        <div class="hiw-node">current_price: float</div>
        <span class="hiw-arrow">→</span>
        <div class="hiw-node">get_klines() for chart<br><span style="color:#475569;font-size:0.66rem;">60 × 1-min candles</span></div>
      </div>

      <p style="font-family:'DM Mono',monospace;font-size:0.6rem;letter-spacing:0.12em;text-transform:uppercase;color:#334155;margin-bottom:0.75rem;margin-top:1rem;">Strategy execution</p>
      <div class="hiw-flow">
        <div class="hiw-node">current_price</div>
        <span class="hiw-arrow">→</span>
        <div class="hiw-node">GridTrader.check_and_execute()<br><span style="color:#475569;font-size:0.66rem;">computes price_change_pct</span></div>
        <span class="hiw-arrow">→</span>
        <div class="hiw-node" style="border-color:rgba(0,255,176,0.25);color:#00FFB0;">BUY signal<br><span style="color:#475569;font-size:0.66rem;">pct ≤ buy_threshold</span></div>
        <span class="hiw-arrow" style="color:#334155;">or</span>
        <div class="hiw-node" style="border-color:rgba(255,69,96,0.25);color:#FF4560;">SELL signal<br><span style="color:#475569;font-size:0.66rem;">pct ≥ sell_threshold</span></div>
        <span class="hiw-arrow">→</span>
        <div class="hiw-node-accent">reference_price update<br><span style="color:#475569;font-size:0.66rem;">grid shifts to trade price</span></div>
      </div>

      <p style="font-family:'DM Mono',monospace;font-size:0.6rem;letter-spacing:0.12em;text-transform:uppercase;color:#334155;margin-bottom:0.75rem;margin-top:1rem;">Dashboard refresh</p>
      <div class="hiw-flow">
        <div class="hiw-node">get_stats(current_price)</div>
        <span class="hiw-arrow">→</span>
        <div class="hiw-node">Metric cards + trade log</div>
        <span class="hiw-arrow">→</span>
        <div class="hiw-node">time.sleep(interval)</div>
        <span class="hiw-arrow">→</span>
        <div class="hiw-node-accent">st.rerun()</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Grid strategy ─────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="hiw-section">
          <h4>Grid trading strategy</h4>
          <p>A grid strategy places orders at fixed intervals above and below a reference price,
          capturing profit from oscillation rather than directional movement.</p>
          <p>When the bot starts, the current price becomes the <span class="hiw-green">reference_price</span>.
          Every polling cycle:</p>
          <ul>
            <li>Compute <span class="hiw-val">price_change_pct = (current − reference) / reference × 100</span></li>
            <li>If <span class="hiw-val">pct ≤ buy_threshold</span> (e.g., −2%): spend $100 USDT to buy BTC</li>
            <li>If <span class="hiw-val">pct ≥ sell_threshold</span> (e.g., +2.5%): sell BTC, receive USDT</li>
            <li>After each trade, <span class="hiw-green">reference_price</span> moves to the current price</li>
          </ul>
          <p>The grid "shifts" after each trade, so the strategy keeps tracking the market wherever it goes —
          not anchored to a fixed price forever.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="hiw-section">
          <h4>What each metric means</h4>
          <p><span class="hiw-green">USDT Balance</span> — Cash available. Depletes on buys, increases on sells.</p>
          <p><span class="hiw-green">BTC Holdings</span> — BTC currently held. Increases on buys, decreases on sells.</p>
          <p><span class="hiw-green">Portfolio Value</span> — USDT balance + (BTC balance × current price). Total worth if you liquidated now.</p>
          <p><span class="hiw-green">Total P&amp;L</span> — Current portfolio value minus the initial $10,000. Your net gain or loss since the bot started.</p>
          <p><span class="hiw-val">Realized P&amp;L</span> — Profit locked in from completed BUY→SELL cycles. This is your actual earned profit.</p>
          <p><span class="hiw-val">Unrealized P&amp;L</span> — Paper gain/loss on BTC you currently hold, based on average buy price vs current price.</p>
          <p><span class="hiw-val">Trade count</span> — Total BUY + SELL events executed this session.</p>
          <p><span class="hiw-val">Reference price</span> — The anchor price used to measure threshold crossings.</p>
        </div>
        """, unsafe_allow_html=True)

    # ── Parameter guide ───────────────────────────────────────────────────────
    st.markdown('<span class="as-section-label" style="margin-top:1rem;">Parameter guide</span>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#0C0D12;border:1px solid #1C2030;border-radius:8px;padding:1rem 1.2rem;margin-bottom:0.75rem;">
      <div class="hiw-param-row">
        <span class="hiw-param-key">Buy threshold</span>
        <span class="hiw-param-desc">Default <span class="hiw-green">−2.0%</span>. Tighter (−0.5%) = more trades, more noise. Wider (−5%) = fewer but larger moves required. Typical range: −0.5% to −5%.</span>
      </div>
      <div class="hiw-param-row">
        <span class="hiw-param-key">Sell threshold</span>
        <span class="hiw-param-desc">Default <span class="hiw-green">+2.5%</span>. Higher = larger profit per trade but longer waits. Lower = frequent small gains. Typical range: +0.5% to +5%.</span>
      </div>
      <div class="hiw-param-row">
        <span class="hiw-param-key">Trade size</span>
        <span class="hiw-param-desc">Fixed at <span class="hiw-green">$100 USDT</span> per trade (set in config.py). Smaller = less risk per trade. Must be below your USDT balance or the order is skipped.</span>
      </div>
      <div class="hiw-param-row">
        <span class="hiw-param-key">Update interval</span>
        <span class="hiw-param-desc">10–30 seconds. Shorter = faster price reaction but more API calls. 15s is a reasonable default for testnet price granularity.</span>
      </div>
      <div class="hiw-param-row">
        <span class="hiw-param-key">Chart type</span>
        <span class="hiw-param-desc">Candlestick shows open/high/low/close per 1-min candle. Line shows close-price trend. Both pull the last 60 candles from Binance.</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Advanced metrics & sandbox ────────────────────────────────────────────
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("""
        <div class="hiw-section">
          <h4>Advanced strategy metrics</h4>
          <p>These metrics are not currently displayed in the dashboard but are relevant
          to evaluating any grid strategy:</p>
          <p><span class="hiw-val">Sharpe ratio</span> — Return per unit of volatility.
          Computed as <span class="hiw-val">(mean return − risk-free rate) / std(returns)</span>.
          A grid strategy typically targets Sharpe &gt; 1.0. High Sharpe means consistent,
          low-risk gains relative to volatility.</p>
          <p><span class="hiw-val">Max drawdown</span> — Worst peak-to-trough decline in
          portfolio value during a session. A grid in a strongly trending market can accumulate
          a large drawdown as it keeps buying a falling asset. Watch this to gauge strategy risk.</p>
          <p>Both can be computed from the trade history returned by
          <span class="hiw-val">GridTrader.get_trade_history()</span>.</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="hiw-section">
          <h4>Sandbox mode</h4>
          <p><span class="hiw-green">ENABLE_REAL_TRADING = False</span> in config.py at all times.
          No orders are ever sent to Binance. The bot only reads prices; it never writes.</p>
          <p>By default, <span class="hiw-val">USE_MAINNET_DATA = False</span> connects to Binance
          Testnet (<span class="hiw-val">testnet.binance.vision</span>). Testnet prices can diverge from
          real market prices — they are useful for testing connectivity and logic but not for realistic
          P&amp;L simulation.</p>
          <p>Set <span class="hiw-val">USE_MAINNET_DATA = True</span> (or via environment variable
          <span class="hiw-val">USE_MAINNET_DATA=true</span>) to pull real BTC/USDT prices from
          <span class="hiw-val">api.binance.com</span> while keeping all trades simulated.</p>
          <p>Starting balances: <span class="hiw-green">$10,000 USDT</span>, <span class="hiw-green">0 BTC</span>.
          Click "Reset Portfolio" to restart the simulation at any time.</p>
        </div>
        """, unsafe_allow_html=True)


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    init_session_state()
    render_topbar()

    # Body: narrow padding via columns
    _, col_main, _ = st.columns([0.035, 0.93, 0.035])

    with col_main:
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        # Page navigation
        page = st.radio(
            "View",
            options=["Dashboard", "How It Works"],
            horizontal=True,
            label_visibility="collapsed",
            key="page_nav",
        )

        st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

        if page == "How It Works":
            render_how_it_works()
            return

        # ── DASHBOARD ────────────────────────────────────────────────────────

        # Controls row: start/stop + settings expander
        col_btn, col_settings = st.columns([0.16, 0.84])
        with col_btn:
            if st.session_state.bot_running:
                if st.button("Stop", type="secondary", use_container_width=True):
                    st.session_state.bot_running = False
                    st.rerun()
            else:
                if st.button("Start Bot", type="primary", use_container_width=True):
                    st.session_state.bot_running = True
                    price = st.session_state.binance_client.get_current_price()
                    st.session_state.trader.initialize(price)
                    st.rerun()
        with col_settings:
            refresh_interval = render_settings_panel()

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        # Fetch live data
        client = st.session_state.binance_client
        current_price = client.get_current_price()
        last_price = st.session_state.last_price

        # Execute bot logic
        if st.session_state.bot_running:
            trade = st.session_state.trader.check_and_execute(current_price)
            if trade:
                if trade.type == "BUY":
                    st.toast(f"BUY  {format_currency(trade.price)}")
                else:
                    st.toast(
                        f"SELL  {format_currency(trade.price)}  ·  "
                        f"P&L {format_currency(trade.pnl or 0)}"
                    )

        stats = st.session_state.trader.get_stats(current_price)

        render_price_hero(current_price, last_price, stats)
        render_metrics(current_price, stats)
        render_chart(client, st.session_state.chart_type)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        col_log, col_stats = st.columns([0.64, 0.36])
        with col_log:
            render_trade_log(st.session_state.trader.get_trade_history())
        with col_stats:
            render_bot_stats(stats)

        st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

        st.session_state.last_price = current_price

        if st.session_state.bot_running:
            time.sleep(refresh_interval)
            st.rerun()


if __name__ == "__main__":
    main()

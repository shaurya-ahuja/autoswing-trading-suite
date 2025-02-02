"""
AutoSwing - Live Crypto Grid Trading Dashboard
A Streamlit-based dashboard for simulated BTC/USDT grid trading on Binance testnet.

⚠️ SANDBOX/TESTNET MODE ONLY - No real money involved
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime
import os
import sys

# Add current directory to path for imports
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

# Page configuration
st.set_page_config(
    page_title="AutoSwing - Grid Trading Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for dark fintech theme
st.markdown("""
<style>
    /* Main theme */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Header styling */
    .main-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
        border-bottom: 1px solid #333;
        margin-bottom: 1rem;
    }
    
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        color: #FAFAFA;
        margin: 0;
    }
    
    .sandbox-badge {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #333;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
    }
    
    .metric-label {
        color: #888;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #FAFAFA;
    }
    
    .metric-value.profit {
        color: #00D26A;
    }
    
    .metric-value.loss {
        color: #FF4B4B;
    }
    
    /* Status indicator */
    .status-running {
        color: #00D26A;
        font-weight: 600;
    }
    
    .status-paused {
        color: #FF4B4B;
        font-weight: 600;
    }
    
    /* Trade table styling */
    .trade-buy {
        color: #00D26A !important;
        font-weight: 600;
    }
    
    .trade-sell {
        color: #FF4B4B !important;
        font-weight: 600;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1a1a2e;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Price display */
    .price-display {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if 'bot_running' not in st.session_state:
        st.session_state.bot_running = False
    
    if 'trader' not in st.session_state:
        st.session_state.trader = GridTrader()
    
    if 'binance_client' not in st.session_state:
        # Try to get API keys from secrets or environment
        api_key = None
        api_secret = None
        use_mainnet = False
        use_binance_us = False
        
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
            # Default to false from env if not set
            use_mainnet = os.environ.get("USE_MAINNET_DATA", "False").lower() == "true"
            use_binance_us = os.environ.get("USE_BINANCE_US", "False").lower() == "true"
        
        st.session_state.binance_client = BinanceTestnetClient(api_key, api_secret, use_mainnet, use_binance_us)
    
    if 'last_price' not in st.session_state:
        st.session_state.last_price = None
    
    if 'price_history' not in st.session_state:
        st.session_state.price_history = []
    
    if 'chart_type' not in st.session_state:
        st.session_state.chart_type = "Candlestick"


def render_header():
    """Render the main header."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("# 🤖 AutoSwing")
        st.caption("Live Grid Trading Dashboard")
    
    with col2:
        client = st.session_state.binance_client
        is_live = getattr(client, 'use_mainnet', False)
        status = getattr(client, 'connection_status', 'UNKNOWN')
        error = getattr(client, 'last_error', None)

        if is_live:
            if status == "CONNECTED":
                badge_html = '<span class="sandbox-badge" style="background: linear-gradient(135deg, #00C851 0%, #007E33 100%);">🟢 LIVE DATA</span>'
            elif status == "RESTRICTED":
                badge_html = f'<span class="sandbox-badge" style="background: #FF8800;">⚠️ RESTRICTED</span>'
                st.toast(f"Connection Issue: {error}", icon="⚠️")
            else:
                badge_html = f'<span class="sandbox-badge" style="background: #CC0000;">🔴 ERROR</span>'
                if error:
                    st.toast(f"Connection Error: {error}", icon="❌")
        else:
            badge_html = '<span class="sandbox-badge">🔒 SANDBOX MODE</span>'

        st.markdown(
            f'<div style="text-align: right; padding-top: 0.5rem;">{badge_html}</div>',
            unsafe_allow_html=True
        )


def render_sidebar():
    """Render the sidebar controls."""
    with st.sidebar:
        st.markdown("## ⚙️ Bot Controls")
        st.markdown("---")
        
        # Start/Stop button
        if st.session_state.bot_running:
            if st.button("⏹️ Stop Bot", type="primary", use_container_width=True):
                st.session_state.bot_running = False
                st.rerun()
        else:
            if st.button("▶️ Start Bot", type="primary", use_container_width=True):
                st.session_state.bot_running = True
                # Initialize trader with current price
                current_price = st.session_state.binance_client.get_current_price()
                st.session_state.trader.initialize(current_price)
                st.rerun()
        
        # Status indicator
        if st.session_state.bot_running:
            st.markdown(f"<p class='status-running'>{config.STATUS_RUNNING}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p class='status-paused'>{config.STATUS_PAUSED}</p>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("## 📊 Grid Settings")
        
        # Buy threshold slider
        buy_threshold = st.slider(
            "Buy Threshold (%)",
            min_value=-5.0,
            max_value=-0.01,
            value=max(st.session_state.trader.buy_threshold, -5.0), # Ensure value is within range
            step=0.01,
            format="%.2f",
            help="Price must drop this % below reference to trigger a buy"
        )
        
        # Sell threshold slider
        sell_threshold = st.slider(
            "Sell Threshold (%)",
            min_value=0.01,
            max_value=5.0,
            value=min(st.session_state.trader.sell_threshold, 5.0), # Ensure value is within range
            step=0.01,
            format="%.2f",
            help="Price must rise this % above reference to trigger a sell"
        )
        
        # Update thresholds if changed
        if buy_threshold != st.session_state.trader.buy_threshold or \
           sell_threshold != st.session_state.trader.sell_threshold:
            st.session_state.trader.update_thresholds(buy_threshold, sell_threshold)
        
        st.markdown("---")
        st.markdown("## 🔄 Refresh Settings")
        
        # Refresh interval
        refresh_interval = st.selectbox(
            "Update Interval",
            options=[10, 15, 20, 30],
            index=1,
            format_func=lambda x: f"{x} seconds"
        )
        
        # Chart type selection
        st.session_state.chart_type = st.radio(
            "Chart Type",
            options=["Candlestick", "Line"],
            horizontal=True
        )
        
        st.markdown("---")
        
        # Reset button
        if st.button("🔄 Reset Portfolio", use_container_width=True):
            st.session_state.trader.reset()
            st.session_state.bot_running = False
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📖 About")
        st.caption(
            "AutoSwing is a simulated grid trading bot for educational purposes. "
            "It connects to Binance Testnet and does NOT execute real trades."
        )
        
        return refresh_interval


def render_metrics(current_price: float, stats: dict):
    """Render the portfolio metrics cards."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💵 USDT Balance",
            value=format_currency(stats['usdt_balance']),
        )
    
    with col2:
        st.metric(
            label="₿ BTC Holdings",
            value=format_btc(stats['btc_balance']),
        )
    
    with col3:
        st.metric(
            label="💼 Portfolio Value",
            value=format_currency(stats['portfolio_value']),
        )
    
    with col4:
        pnl = stats['total_pnl']
        pnl_color = "normal" if pnl == 0 else ("inverse" if pnl < 0 else "off")
        st.metric(
            label="📈 Total P&L",
            value=format_currency(pnl),
            delta=format_percentage((pnl / config.STARTING_USDT_BALANCE) * 100) if config.STARTING_USDT_BALANCE > 0 else "0%",
            delta_color=pnl_color
        )


def render_price_chart(client: BinanceTestnetClient, chart_type: str):
    """Render the price chart."""
    # Fetch kline data
    df = client.get_klines(config.SYMBOL, config.KLINE_INTERVAL, config.KLINE_LIMIT)
    
    if chart_type == "Candlestick":
        fig = create_candlestick_chart(df, "BTC/USDT")
    else:
        fig = create_price_line_chart(df, "BTC/USDT")
    
    st.plotly_chart(fig, use_container_width=True)


def render_current_price(current_price: float, last_price: float):
    """Render the current price display."""
    trend = get_trend_indicator(current_price, last_price) if last_price else "📊"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        price_color = (
            config.COLORS['profit'] if last_price and current_price > last_price
            else config.COLORS['loss'] if last_price and current_price < last_price
            else config.COLORS['primary']
        )
        
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1rem; background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%); 
                        border-radius: 12px; border: 1px solid #333;">
                <p style="color: #888; margin-bottom: 0.5rem; font-size: 0.9rem;">BTC/USDT LIVE PRICE</p>
                <p style="font-size: 2.5rem; font-weight: 700; color: {price_color}; margin: 0;">
                    {trend} {format_currency(current_price)}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_trade_log(trades: list):
    """Render the trade log table."""
    st.markdown("### 📋 Recent Trades")
    
    if not trades:
        st.info("No trades yet. Start the bot to begin trading!")
        return
    
    # Format trades for display
    formatted_trades = [format_trade_for_display(t) for t in trades]
    df = pd.DataFrame(formatted_trades)
    
    # Apply styling
    def style_trade_type(val):
        if val == "BUY":
            return f'color: {config.COLORS["profit"]}; font-weight: 600'
        elif val == "SELL":
            return f'color: {config.COLORS["loss"]}; font-weight: 600'
        return ''
    
    def style_pnl(val):
        if val != "—":
            try:
                # Extract numeric value
                num = float(val.replace('$', '').replace(',', '').replace('-', ''))
                if '-' in val:
                    return f'color: {config.COLORS["loss"]}'
                elif num > 0:
                    return f'color: {config.COLORS["profit"]}'
            except:
                pass
        return ''
    
    styled_df = df.style.applymap(style_trade_type, subset=['Type'])
    styled_df = styled_df.applymap(style_pnl, subset=['P&L'])
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True)


def render_bot_stats(stats: dict, current_price: float):
    """Render additional bot statistics."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Trading Stats")
        st.markdown(f"**Total Trades:** {stats['total_trades']}")
        st.markdown(f"**Realized P&L:** {format_currency(stats['realized_pnl'])}")
        st.markdown(f"**Unrealized P&L:** {format_currency(stats['unrealized_pnl'])}")
        if stats['reference_price']:
            st.markdown(f"**Reference Price:** {format_currency(stats['reference_price'])}")
    
    with col2:
        st.markdown("### ⚙️ Current Settings")
        st.markdown(f"**Buy Threshold:** {st.session_state.trader.buy_threshold}%")
        st.markdown(f"**Sell Threshold:** +{st.session_state.trader.sell_threshold}%")
        st.markdown(f"**Trade Amount:** {format_currency(config.TRADE_AMOUNT_USDT)}")
        st.markdown(f"**Symbol:** {config.SYMBOL}")


def main():
    """Main application entry point."""
    # Initialize session state
    init_session_state()
    
    # Render header
    render_header()
    
    # Render sidebar and get refresh interval
    refresh_interval = render_sidebar()
    
    # Get current price
    client = st.session_state.binance_client
    current_price = client.get_current_price()
    last_price = st.session_state.last_price
    
    # Execute trading logic if bot is running
    if st.session_state.bot_running:
        trade = st.session_state.trader.check_and_execute(current_price)
        if trade:
            if trade.type == "BUY":
                st.toast(f"🟢 BUY executed at {format_currency(trade.price)}", icon="📈")
            else:
                st.toast(f"🔴 SELL executed at {format_currency(trade.price)} | P&L: {format_currency(trade.pnl or 0)}", icon="📉")
    
    # Get trading stats
    stats = st.session_state.trader.get_stats(current_price)
    
    # Main content area
    st.markdown("---")
    
    # Current price display
    render_current_price(current_price, last_price)
    
    st.markdown("")
    
    # Portfolio metrics
    render_metrics(current_price, stats)
    
    st.markdown("---")
    
    # Price chart
    render_price_chart(client, st.session_state.chart_type)
    
    st.markdown("---")
    
    # Two column layout for trades and stats
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_trade_log(st.session_state.trader.get_trade_history())
    
    with col2:
        render_bot_stats(stats, current_price)
    
    # Update last price
    st.session_state.last_price = current_price
    
    # Auto-refresh when bot is running
    if st.session_state.bot_running:
        time.sleep(refresh_interval)
        st.rerun()


if __name__ == "__main__":
    main()

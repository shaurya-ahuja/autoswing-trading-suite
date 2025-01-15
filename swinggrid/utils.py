"""
AutoSwing Utility Functions
"""

import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from config import COLORS


def format_currency(value: float, symbol: str = "$") -> str:
    """Format a number as currency with proper formatting."""
    if value >= 0:
        return f"{symbol}{value:,.2f}"
    else:
        return f"-{symbol}{abs(value):,.2f}"


def format_btc(value: float) -> str:
    """Format BTC amounts with 8 decimal places."""
    return f"{value:.8f} BTC"


def format_percentage(value: float) -> str:
    """Format a percentage with sign."""
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values."""
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100


def create_candlestick_chart(df: pd.DataFrame, title: str = "BTC/USDT") -> go.Figure:
    """
    Create a Plotly candlestick chart from OHLCV data.
    
    Args:
        df: DataFrame with columns: open, high, low, close, time
        title: Chart title
    
    Returns:
        Plotly Figure object
    """
    fig = go.Figure(data=[go.Candlestick(
        x=df['time'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        increasing_line_color=COLORS['profit'],
        decreasing_line_color=COLORS['loss'],
        increasing_fillcolor=COLORS['profit'],
        decreasing_fillcolor=COLORS['loss'],
    )])
    
    fig.update_layout(
        title=dict(
            text=f"📊 {title} Live Price",
            font=dict(size=20, color=COLORS['text']),
        ),
        xaxis_title="Time",
        yaxis_title="Price (USDT)",
        template="plotly_dark",
        paper_bgcolor=COLORS['background'],
        plot_bgcolor=COLORS['background'],
        xaxis=dict(
            gridcolor='#333333',
            showgrid=True,
            rangeslider=dict(visible=False),
        ),
        yaxis=dict(
            gridcolor='#333333',
            showgrid=True,
            side='right',
        ),
        margin=dict(l=10, r=60, t=50, b=40),
        height=400,
    )
    
    return fig


def create_price_line_chart(df: pd.DataFrame, title: str = "BTC/USDT") -> go.Figure:
    """
    Create a Plotly line chart from price data.
    
    Args:
        df: DataFrame with columns: time, close
        title: Chart title
    
    Returns:
        Plotly Figure object
    """
    # Determine color based on trend
    if len(df) > 1:
        color = COLORS['profit'] if df['close'].iloc[-1] >= df['close'].iloc[0] else COLORS['loss']
    else:
        color = COLORS['primary']
    
    fig = go.Figure(data=[go.Scatter(
        x=df['time'],
        y=df['close'],
        mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1)",
    )])
    
    fig.update_layout(
        title=dict(
            text=f"📈 {title} Price Trend",
            font=dict(size=20, color=COLORS['text']),
        ),
        xaxis_title="Time",
        yaxis_title="Price (USDT)",
        template="plotly_dark",
        paper_bgcolor=COLORS['background'],
        plot_bgcolor=COLORS['background'],
        xaxis=dict(gridcolor='#333333', showgrid=True),
        yaxis=dict(gridcolor='#333333', showgrid=True, side='right'),
        margin=dict(l=10, r=60, t=50, b=40),
        height=400,
    )
    
    return fig


def format_trade_for_display(trade: dict) -> dict:
    """Format a trade dictionary for display in the trade log."""
    return {
        "Time": trade.get("time", "").strftime("%H:%M:%S") if isinstance(trade.get("time"), datetime) else str(trade.get("time", "")),
        "Type": trade.get("type", "").upper(),
        "Price": format_currency(trade.get("price", 0)),
        "Amount": f"{trade.get('amount', 0):.6f} BTC",
        "Value": format_currency(trade.get("value", 0)),
        "P&L": format_currency(trade.get("pnl", 0)) if trade.get("pnl") is not None else "—",
    }


def get_trend_indicator(current: float, previous: float) -> str:
    """Get trend indicator emoji based on price movement."""
    if current > previous:
        return "📈"
    elif current < previous:
        return "📉"
    else:
        return "➡️"

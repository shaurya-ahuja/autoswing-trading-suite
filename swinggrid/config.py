"""
AutoSwing Configuration Constants
"""

# Trading pair
SYMBOL = "BTCUSDT"

# Default grid trading thresholds (in percentage)
DEFAULT_BUY_THRESHOLD = -2.0  # Buy when price drops 2% below reference
DEFAULT_SELL_THRESHOLD = 2.5  # Sell when price rises 2.5% above reference

# Simulated starting balances
STARTING_USDT_BALANCE = 10000.0
STARTING_BTC_BALANCE = 0.0

# Trade amount per grid level (in USDT)
TRADE_AMOUNT_USDT = 100.0

# Minimum trade amount in BTC
MIN_TRADE_BTC = 0.0001

# Refresh interval in seconds
DEFAULT_REFRESH_INTERVAL = 15

# Chart settings
KLINE_INTERVAL = "1m"  # 1-minute candles
KLINE_LIMIT = 60  # Last 60 candles

# Binance Testnet API endpoints
# Binance Testnet API endpoints (Default)
TESTNET_BASE_URL = "https://testnet.binance.vision"
TESTNET_WS_URL = "wss://testnet.binance.vision/ws"

# Mainnet API endpoints (Real Data)
MAINNET_BASE_URL = "https://api.binance.com"
MAINNET_WS_URL = "wss://stream.binance.com:9443/ws"

# Binance.US API endpoints (For US Users)
BINANCE_US_BASE_URL = "https://api.binance.us"
BINANCE_US_WS_URL = "wss://stream.binance.us:9443/ws"

# Operation Mode
# Set to 'True' to use Mainnet Data (Real Prices)
# Set to 'False' to use Testnet Data
USE_MAINNET_DATA = False 

# Set to 'True' if using Binance.US
USE_BINANCE_US = False 

# Trading Mode
# ALWAYS False for this dashboard version to prevent real money loss
ENABLE_REAL_TRADING = False

# UI Theme colors
COLORS = {
    "profit": "#00D26A",
    "loss": "#FF4B4B",
    "primary": "#00ADB5",
    "background": "#0E1117",
    "card": "#1E1E1E",
    "text": "#FAFAFA",
}

# Status messages
STATUS_RUNNING = "🟢 Bot Running"
STATUS_PAUSED = "🔴 Bot Paused"

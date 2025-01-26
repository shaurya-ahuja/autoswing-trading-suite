# 🚀 AutoSwing Trading Suite

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Binance](https://img.shields.io/badge/Binance-Data-F0B90B?style=for-the-badge&logo=binance&logoColor=white)](https://binance.com)

> **Professional Crypto Grid Trading Dashboard & Bot Suite**
>
> ⚠️ **Note**: This suite is designed for **simulated trading** (paper trading) using real-time market data. It helps you test strategies without risking real funds.

---

## 🌟 Overview

**AutoSwing** is a powerful, modular trading toolkit designed for crypto enthusiasts and developers. It provides two premium interfaces to interact with the market:

1.  **🖥️ Web Dashboard (SwingGrid)**: A beautiful, real-time Streamlit dashboard for visualizing grid trading strategies with live market data.
2.  **📱 Telegram Bot**: A robust command-line interface to manage strategies on the go.

---

## ✨ Features

### 🖥️ SwingGrid Dashboard
- **Real-Time Data**: Toggles between **Binance Testnet** (demo) and **Mainnet** (real price) data.
- **Visual Strategy**: Live interactive candlestick & line charts powered by Plotly.
- **Simulated Execution**: "Paper trade" algorithm that simulates buys/sells based on your logic, protecting your wallet.
- **Profit Tracking**: Real-time P&L (Profit & Loss) calculation and portfolio value tracking in USDT.
- **Customizable**: Adjust buy/sell thresholds on the fly via the sidebar.

### 📱 Telegram Command Center
- **Grid Trading**: Deploy multi-level buy orders with a single command.
- **DCA Mode**: Execute Dollar Cost Averaging strategies automatically.
- **Portfolio Checks**: Check balances and total asset value instantly.

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.9 or higher
- Git

### 1. Clone & Install
```bash
git clone https://github.com/yourusername/autoswing-trading-suite.git
cd autoswing-trading-suite

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Dashboard
```bash
cd swinggrid
streamlit run app.py
```
> The dashboard will open at `http://localhost:8501`. By default, it runs in **Testnet Mode** (no keys required).

---

## ☁️ Deployment (Free on Streamlit Cloud)

Host your dashboard for free to access it from anywhere.

1.  **Push to GitHub**: Ensure this code is in your GitHub repository.
2.  **Go to [Streamlit Cloud](https://share.streamlit.io/)** and sign in.
3.  **New App**:
    *   **Repository**: Select your repo.
    *   **Main file path**: `swinggrid/app.py`.
4.  **Configure Secrets** (Crucial for Real Data):
    *   Click "Advanced Settings" -> "Secrets".
    *   Add your Binance Configuration (see below).
5.  **Deploy!**

---

## ⚙️ Configuration

### 1. Secrets Management (Streamlit)
To use **Real Market Data** (Mainnet) or private Testnet limits, configure your secrets. 

**For Local Run**: Create `.streamlit/secrets.toml` inside `swinggrid/`.
**For Cloud**: Paste into the Secrets area.

```toml
[binance]
# Optional: Required only for private account data or higher rate limits
api_key = "YOUR_API_KEY"
api_secret = "YOUR_API_SECRET"

# Set to true to see REAL market prices (Mainnet)
# Set to false to use Testnet (Demo) data
product_mode = true
```

### 2. Environment Variables (.env)
For the **Telegram Bot**, you must use a `.env` file in the root directory:

```env
# autoswing-trading-suite/.env

TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
```

---

## 🤖 Running the Telegram Bot

The Telegram bot runs as a standalone process.

```bash
# From the root directory
python telegram_controller.py
```

### Bot Commands
| Command | Usage | Description |
|:---|:---|:---|
| `/start` | `/start` | Show interactive menu |
| `/grid` | `/grid BTC/USDT 5 30000 40000` | Setup grid: 5 levels between $30k-$40k |
| `/dca` | `/dca ETH/USDT 10 1000` | Invest $1000 in ETH over 10 intervals |
| `/balance` | `/balance USDT` | Check specific coin balance |

---

## 📂 Project Structure

```text
autoswing-trading-suite/
├── 🖥️ swinggrid/               # Web Dashboard (Streamlit)
│   ├── app.py                  # Main dashboard application
│   ├── binance_client.py       # Wrapper for Binance API (Testnet/Mainnet)
│   ├── grid_strategy.py        # Trading logic core
│   ├── config.py               # Dashboard settings
│   ├── utils.py                # Charts & formatting helpers
│   └── assets/                 # Images & resources
│
├── 📱 telegram_controller.py   # Telegram Bot Entry Point
├── exchange_client.py          # CCXT Exchange Wrapper (for Bot)
├── trading_bots.py             # Bot Trading Logic Engines
├── requirements.txt            # Project dependencies
└── README.md                   # Documentation
```

---

## 🛡️ Disclaimer

**Educational Purpose Only**: This software is for educational and testing purposes. The default configuration uses **simulated trading** logic.
*   **Do not** enable real trading (`ENABLE_REAL_TRADING = True` in config) unless you have thoroughly audited the code and understand the risks.
*   Cryptocurrency trading involves high risk. The authors are not responsible for any financial losses.

---

<p align="center">
  Made with ❤️ by the AutoSwing Team
</p>

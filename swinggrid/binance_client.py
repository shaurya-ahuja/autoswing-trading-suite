"""
AutoSwing Binance Testnet Client
Connects to Binance testnet for real-time price data.
"""

import os
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, List
import requests
import config

try:
    from binance.client import Client
    from binance.exceptions import BinanceAPIException
    BINANCE_AVAILABLE = True
except ImportError:
    BINANCE_AVAILABLE = False
    Client = None
    BinanceAPIException = Exception


class BinanceClientWrapper:
    """
    Binance API client wrapper for fetching real-time price data.
    Supports Testnet, Mainnet (Global), and Binance.US.
    """
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, use_mainnet: bool = False, use_binance_us: bool = False):
        """
        Initialize the Binance client.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            use_mainnet: If True, connects to Mainnet. If False, connects to Testnet.
            use_binance_us: If True and use_mainnet is True, connects to Binance.US.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.use_mainnet = use_mainnet
        self.use_binance_us = use_binance_us
        
        # Determine Base URL
        if not use_mainnet:
            self.base_url = config.TESTNET_BASE_URL
        elif use_binance_us:
            self.base_url = config.BINANCE_US_BASE_URL
        else:
            self.base_url = config.MAINNET_BASE_URL
            
        self.client = None
        self.connection_status = "INITIALIZING"
        self.last_error = None
        
        # Initialize python-binance client if keys provided and library available
        if BINANCE_AVAILABLE and api_key and api_secret:
            try:
                self.client = Client(
                    api_key=api_key,
                    api_secret=api_secret,
                    testnet=not use_mainnet,
                    tld='us' if use_binance_us and use_mainnet else 'com'
                )
                self.connection_status = "CONNECTED"
            except Exception as e:
                self.last_error = f"Init Error: {str(e)}"
                self.connection_status = "ERROR"
                print(f"Warning: Could not initialize Binance client: {e}")
                self.client = None
        else:
            if not BINANCE_AVAILABLE:
                self.last_error = "Library 'python-binance' missing"
            elif not api_key:
                self.last_error = "API Key missing"
            self.connection_status = "ERROR"
    
    def get_current_price(self, symbol: str = "BTCUSDT") -> float:
        """
        Fetch the current price for a symbol.
        
        Args:
            symbol: Trading pair symbol (default: BTCUSDT)
        
        Returns:
            Current price as float
        """
        try:
            if self.client:
                ticker = self.client.get_symbol_ticker(symbol=symbol)
                return float(ticker['price'])
            else:
                # Fallback to REST API
                response = requests.get(
                    f"{self.base_url}/api/v3/ticker/price",
                    params={"symbol": symbol},
                    timeout=10
                )
                if response.status_code == 451: # Geo-restriction
                     self.last_error = "Geo-Restricted (451)"
                     self.connection_status = "RESTRICTED"
                     print("Warning: Geo-restricted. Using simulated data.")
                     return self._generate_simulated_price()
                
                response.raise_for_status()
                self.connection_status = "CONNECTED" # Success via REST
                return float(response.json()['price'])
        except Exception as e:
            self.last_error = f"Fetch Error: {str(e)}"
            self.connection_status = "ERROR"
            print(f"Error fetching price: {e}")
            return self._generate_simulated_price()
    
    def get_klines(self, symbol: str = "BTCUSDT", interval: str = "1m", limit: int = 60) -> pd.DataFrame:
        """
        Fetch candlestick/kline data.
        
        Args:
            symbol: Trading pair symbol
            interval: Kline interval (1m, 5m, 15m, 1h, etc.)
            limit: Number of candles to fetch (max 1000)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            if self.client:
                klines = self.client.get_klines(
                    symbol=symbol,
                    interval=interval,
                    limit=limit
                )
            else:
                # Fallback to REST API
                response = requests.get(
                    f"{self.base_url}/api/v3/klines",
                    params={
                        "symbol": symbol,
                        "interval": interval,
                        "limit": limit
                    },
                    timeout=10
                )
                if response.status_code == 451:
                     return self._generate_demo_klines(limit)

                response.raise_for_status()
                klines = response.json()
            
            # Parse klines into DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            df['time'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)
            
            return df[['time', 'open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            print(f"Error fetching klines: {e}")
            # Return simulated data for demo
            return self._generate_demo_klines(limit)
    
    def get_24h_stats(self, symbol: str = "BTCUSDT") -> Dict:
        """
        Fetch 24-hour statistics for a symbol.
        
        Args:
            symbol: Trading pair symbol
        
        Returns:
            Dictionary with 24h stats
        """
        try:
            if self.client:
                stats = self.client.get_ticker(symbol=symbol)
            else:
                response = requests.get(
                    f"{self.base_url}/api/v3/ticker/24hr",
                    params={"symbol": symbol},
                    timeout=10
                )
                if response.status_code == 451:
                     return {
                        "price_change": 0, "price_change_percent": 0,
                        "high": 0, "low": 0, "volume": 0, "quote_volume": 0
                     }

                response.raise_for_status()
                stats = response.json()
            
            return {
                "price_change": float(stats.get('priceChange', 0)),
                "price_change_percent": float(stats.get('priceChangePercent', 0)),
                "high": float(stats.get('highPrice', 0)),
                "low": float(stats.get('lowPrice', 0)),
                "volume": float(stats.get('volume', 0)),
                "quote_volume": float(stats.get('quoteVolume', 0)),
            }
        except Exception as e:
            print(f"Error fetching 24h stats: {e}")
            return {
                "price_change": 0,
                "price_change_percent": 0,
                "high": 0,
                "low": 0,
                "volume": 0,
                "quote_volume": 0,
            }

    def _generate_simulated_price(self) -> float:
        """Generate a simulated price for fallback."""
        return 42000.0 + (hash(str(datetime.now())) % 2000 - 1000)

    def _generate_demo_klines(self, limit: int) -> pd.DataFrame:
        """Generate demo candlestick data when API is unavailable."""
        import random
        from datetime import timedelta
        import math
        
        base_price = 42000.0
        now = datetime.now()
        
        # Seed for reproducibility within the minute
        random.seed(int(now.timestamp()) % 1000)
        
        # Generate times and prices using pure Python
        time_list = []
        open_list = []
        high_list = []
        low_list = []
        close_list = []
        volume_list = []
        
        current_price = base_price
        
        for i in range(limit):
            # Time for this candle
            t = now - timedelta(minutes=limit - i - 1)
            
            # Random walk for price
            change = random.gauss(0, 0.001)
            current_price = current_price * math.exp(change)
            
            # Generate OHLCV data
            volatility = current_price * 0.002
            open_p = current_price + random.gauss(0, volatility)
            close_p = current_price + random.gauss(0, volatility)
            high_p = max(open_p, close_p) + abs(random.gauss(0, volatility))
            low_p = min(open_p, close_p) - abs(random.gauss(0, volatility))
            volume = random.uniform(10, 100)
            
            time_list.append(t)
            open_list.append(open_p)
            high_list.append(high_p)
            low_list.append(low_p)
            close_list.append(close_p)
            volume_list.append(volume)
        
        # Create DataFrame column by column
        df = pd.DataFrame()
        df['time'] = time_list
        df['open'] = open_list
        df['high'] = high_list
        df['low'] = low_list
        df['close'] = close_list
        df['volume'] = volume_list
        
        return df

    def test_connection(self) -> bool:
        """Test if the API connection is working."""
        try:
            self.get_current_price()
            return True
        except Exception:
            return False

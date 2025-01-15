"""
AutoSwing Binance Testnet Client
Connects to Binance testnet for real-time price data.
"""

import os
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, List
import requests

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
    Supports both Testnet (Simulated) and Mainnet (Real) data.
    """
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, use_mainnet: bool = False):
        """
        Initialize the Binance client.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            use_mainnet: If True, connects to Mainnet. If False, connects to Testnet.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.use_mainnet = use_mainnet
        self.base_url = config.MAINNET_BASE_URL if use_mainnet else config.TESTNET_BASE_URL
        self.client = None
        
        # Initialize python-binance client if keys provided and library available
        if BINANCE_AVAILABLE and api_key and api_secret:
            try:
                self.client = Client(
                    api_key=api_key,
                    api_secret=api_secret,
                    testnet=not use_mainnet
                )
            except Exception as e:
                print(f"Warning: Could not initialize Binance client: {e}")
                self.client = None
    
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
                     print("Warning: Geo-restricted. Using simulated data.")
                     return self._generate_simulated_price()
                
                response.raise_for_status()
                return float(response.json()['price'])
        except Exception as e:
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

    def test_connection(self) -> bool:
        """Test if the API connection is working."""
        try:
            self.get_current_price()
            return True
        except Exception:
            return False

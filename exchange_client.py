"""
AutoSwing Trading Suite - Exchange Client
Multi-exchange connector using CCXT library.

Author: AutoSwing Team
License: MIT
"""

import ccxt
from decouple import config
from typing import Dict, Optional


class CryptoExchange:
    """
    Universal cryptocurrency exchange connector.
    Supports any exchange available through CCXT.
    """
    
    def __init__(self, exchange_id: str):
        """
        Initialize connection to a cryptocurrency exchange.
        
        Args:
            exchange_id: Exchange identifier (e.g., 'binance', 'coinbase')
        """
        self.exchange_id = exchange_id
        self._api_key = config(f"{exchange_id.upper()}_API_KEY")
        self._api_secret = config(f"{exchange_id.upper()}_API_SECRET")
        
        # Initialize CCXT exchange instance
        exchange_class = getattr(ccxt, exchange_id)
        self.client = exchange_class({
            'apiKey': self._api_key,
            'secret': self._api_secret,
            'enableRateLimit': True,
        })
    
    def fetch_token_balance(self, token: str) -> Dict[str, float]:
        """
        Get balance information for a specific token.
        
        Args:
            token: Token symbol (e.g., 'BTC', 'USDT')
            
        Returns:
            Dictionary with 'available', 'locked', and 'total' balances
        """
        try:
            all_balances = self.client.fetch_balance()
            
            if token not in all_balances or 'free' not in all_balances[token]:
                raise KeyError(f"Token {token} not found in account.")
            
            return {
                'available': all_balances[token]['free'],
                'locked': all_balances[token]['used'],
                'total': all_balances[token]['total']
            }
        except Exception as err:
            raise Exception(f"Balance fetch failed: {str(err)}")
    
    def calculate_portfolio_usdt(self) -> float:
        """
        Calculate total portfolio value in USDT.
        
        Returns:
            Total portfolio value as float
        """
        try:
            all_balances = self.client.fetch_balance()
            price_data = self.client.fetch_tickers()
            portfolio_value = 0.0
            
            for token, amount in all_balances['total'].items():
                if amount <= 0:
                    continue
                    
                if token == 'USDT':
                    portfolio_value += amount
                else:
                    pair = f"{token}/USDT"
                    if pair in price_data and price_data[pair]['last']:
                        portfolio_value += amount * price_data[pair]['last']
                    else:
                        print(f"⚠️ Skipping {token}: No price data available")
            
            return portfolio_value
            
        except Exception as err:
            raise Exception(f"Portfolio calculation failed: {str(err)}")
    
    def submit_order(
        self, 
        pair: str, 
        order_type: str, 
        side: str, 
        quantity: float, 
        price: Optional[float] = None
    ) -> Dict:
        """
        Submit a trade order to the exchange.
        
        Args:
            pair: Trading pair (e.g., 'BTC/USDT')
            order_type: 'limit' or 'market'
            side: 'buy' or 'sell'
            quantity: Amount to trade
            price: Limit price (required for limit orders)
            
        Returns:
            Order response from exchange
        """
        try:
            if order_type == 'limit':
                if price is None:
                    raise ValueError("Limit orders require a price.")
                return self.client.create_limit_order(pair, side, quantity, price)
            elif order_type == 'market':
                return self.client.create_market_order(pair, side, quantity)
            else:
                raise ValueError(f"Unknown order type: {order_type}")
        except Exception as err:
            raise Exception(f"Order submission failed: {str(err)}")
    
    def get_current_price(self, pair: str) -> float:
        """
        Get the current market price for a trading pair.
        
        Args:
            pair: Trading pair (e.g., 'BTC/USDT')
            
        Returns:
            Current price as float
        """
        try:
            ticker = self.client.fetch_ticker(pair)
            return ticker['last']
        except Exception as err:
            raise Exception(f"Price fetch failed: {str(err)}")

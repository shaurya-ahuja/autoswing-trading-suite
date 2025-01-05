"""
AutoSwing Trading Suite - Trading Bot Engines
Grid trading and DCA strategy implementations.

Author: AutoSwing Team
License: MIT
"""

from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class OrderResult:
    """Represents the result of an order placement."""
    success: bool
    price: float
    quantity: float
    order_id: Optional[str] = None
    error: Optional[str] = None


class GridTradingEngine:
    """
    Grid Trading Strategy Engine.
    
    Places multiple limit buy orders at evenly spaced price levels
    within a defined price range.
    """
    
    def __init__(
        self, 
        exchange, 
        trading_pair: str, 
        num_levels: int, 
        price_floor: float, 
        price_ceiling: float,
        order_size: float = 1.0
    ):
        """
        Initialize the grid trading engine.
        
        Args:
            exchange: Exchange client instance
            trading_pair: Trading pair symbol (e.g., 'BTC/USDT')
            num_levels: Number of grid levels
            price_floor: Lowest price in the grid
            price_ceiling: Highest price in the grid
            order_size: Size of each order
        """
        self.exchange = exchange
        self.trading_pair = trading_pair
        self.num_levels = num_levels
        self.price_floor = price_floor
        self.price_ceiling = price_ceiling
        self.order_size = order_size
        
        # Calculate spacing between grid levels
        self.level_spacing = (price_ceiling - price_floor) / num_levels
        self.placed_orders: List[OrderResult] = []
    
    def calculate_grid_prices(self) -> List[float]:
        """Calculate all price levels for the grid."""
        prices = []
        for i in range(self.num_levels):
            level_price = self.price_floor + (i * self.level_spacing)
            prices.append(round(level_price, 2))
        return prices
    
    def place_grid_orders(self) -> List[OrderResult]:
        """
        Place all grid orders on the exchange.
        
        Returns:
            List of OrderResult objects
        """
        grid_prices = self.calculate_grid_prices()
        results = []
        
        for price in grid_prices:
            try:
                order = self.exchange.submit_order(
                    pair=self.trading_pair,
                    order_type='limit',
                    side='buy',
                    quantity=self.order_size,
                    price=price
                )
                result = OrderResult(
                    success=True,
                    price=price,
                    quantity=self.order_size,
                    order_id=order.get('id')
                )
            except Exception as e:
                result = OrderResult(
                    success=False,
                    price=price,
                    quantity=self.order_size,
                    error=str(e)
                )
            
            results.append(result)
            self.placed_orders.append(result)
        
        return results
    
    def get_summary(self) -> Dict:
        """Get a summary of the grid configuration."""
        return {
            'pair': self.trading_pair,
            'levels': self.num_levels,
            'price_range': f"${self.price_floor:,.2f} - ${self.price_ceiling:,.2f}",
            'spacing': f"${self.level_spacing:,.2f}",
            'orders_placed': len([o for o in self.placed_orders if o.success])
        }


class DollarCostAverager:
    """
    Dollar Cost Averaging (DCA) Strategy Engine.
    
    Splits a total investment into equal portions and executes
    market buy orders at regular intervals.
    """
    
    def __init__(
        self, 
        exchange, 
        trading_pair: str, 
        num_intervals: int, 
        investment_amount: float
    ):
        """
        Initialize the DCA engine.
        
        Args:
            exchange: Exchange client instance
            trading_pair: Trading pair symbol (e.g., 'BTC/USDT')
            num_intervals: Number of purchase intervals
            investment_amount: Total amount to invest
        """
        self.exchange = exchange
        self.trading_pair = trading_pair
        self.num_intervals = num_intervals
        self.investment_amount = investment_amount
        
        # Calculate amount per purchase
        self.amount_per_purchase = investment_amount / num_intervals
        self.executed_purchases: List[OrderResult] = []
    
    def execute_purchases(self) -> List[OrderResult]:
        """
        Execute all DCA purchases.
        
        Returns:
            List of OrderResult objects
        """
        results = []
        
        for interval in range(self.num_intervals):
            try:
                order = self.exchange.submit_order(
                    pair=self.trading_pair,
                    order_type='market',
                    side='buy',
                    quantity=self.amount_per_purchase
                )
                result = OrderResult(
                    success=True,
                    price=order.get('price', 0),
                    quantity=self.amount_per_purchase,
                    order_id=order.get('id')
                )
            except Exception as e:
                result = OrderResult(
                    success=False,
                    price=0,
                    quantity=self.amount_per_purchase,
                    error=str(e)
                )
            
            results.append(result)
            self.executed_purchases.append(result)
        
        return results
    
    def get_summary(self) -> Dict:
        """Get a summary of the DCA configuration."""
        return {
            'pair': self.trading_pair,
            'intervals': self.num_intervals,
            'total_investment': f"${self.investment_amount:,.2f}",
            'per_purchase': f"${self.amount_per_purchase:,.2f}",
            'purchases_completed': len([p for p in self.executed_purchases if p.success])
        }

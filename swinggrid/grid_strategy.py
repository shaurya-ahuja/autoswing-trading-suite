"""
AutoSwing Grid Trading Strategy
Simulated grid trading logic for the dashboard.
"""

from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field
import config


@dataclass
class Trade:
    """Represents a single trade."""
    time: datetime
    type: str  # 'BUY' or 'SELL'
    price: float
    amount: float  # BTC amount
    value: float  # USDT value
    pnl: Optional[float] = None  # Profit/Loss for sells


@dataclass
class GridTrader:
    """
    Simulated grid trading strategy.
    
    Buys when price drops below reference by buy_threshold%.
    Sells when price rises above reference by sell_threshold%.
    """
    
    buy_threshold: float = config.DEFAULT_BUY_THRESHOLD
    sell_threshold: float = config.DEFAULT_SELL_THRESHOLD
    usdt_balance: float = config.STARTING_USDT_BALANCE
    btc_balance: float = config.STARTING_BTC_BALANCE
    trade_amount_usdt: float = config.TRADE_AMOUNT_USDT
    
    # Internal state
    reference_price: Optional[float] = None
    trades: List[Trade] = field(default_factory=list)
    total_realized_pnl: float = 0.0
    buy_prices: List[float] = field(default_factory=list)  # Track buy prices for P&L
    initial_portfolio_value: Optional[float] = None
    
    def initialize(self, current_price: float):
        """Initialize the trader with current market price."""
        self.reference_price = current_price
        self.initial_portfolio_value = self.calculate_portfolio_value(current_price)
    
    def calculate_portfolio_value(self, current_price: float) -> float:
        """Calculate total portfolio value in USDT."""
        return self.usdt_balance + (self.btc_balance * current_price)
    
    def calculate_unrealized_pnl(self, current_price: float) -> float:
        """Calculate unrealized P&L based on current BTC holdings."""
        if not self.buy_prices or self.btc_balance <= 0:
            return 0.0
        
        avg_buy_price = sum(self.buy_prices) / len(self.buy_prices)
        return self.btc_balance * (current_price - avg_buy_price)
    
    def calculate_total_pnl(self, current_price: float) -> float:
        """Calculate total P&L (realized + unrealized)."""
        if self.initial_portfolio_value is None:
            return 0.0
        
        current_value = self.calculate_portfolio_value(current_price)
        return current_value - self.initial_portfolio_value
    
    def check_and_execute(self, current_price: float) -> Optional[Trade]:
        """
        Check if a trade should be executed based on current price.
        
        Args:
            current_price: Current market price
        
        Returns:
            Trade object if a trade was executed, None otherwise
        """
        if self.reference_price is None:
            self.initialize(current_price)
            return None
        
        price_change_pct = ((current_price - self.reference_price) / self.reference_price) * 100
        
        trade = None
        
        # Check for buy signal (price dropped below threshold)
        if price_change_pct <= self.buy_threshold:
            trade = self._execute_buy(current_price)
            if trade:
                # Update reference price after buy
                self.reference_price = current_price
        
        # Check for sell signal (price rose above threshold)
        elif price_change_pct >= self.sell_threshold:
            trade = self._execute_sell(current_price)
            if trade:
                # Update reference price after sell
                self.reference_price = current_price
        
        return trade
    
    def _execute_buy(self, price: float) -> Optional[Trade]:
        """Execute a simulated buy order."""
        if self.usdt_balance < self.trade_amount_usdt:
            return None  # Insufficient balance
        
        btc_amount = self.trade_amount_usdt / price
        
        # Update balances
        self.usdt_balance -= self.trade_amount_usdt
        self.btc_balance += btc_amount
        
        # Track buy price for P&L calculation
        self.buy_prices.append(price)
        
        trade = Trade(
            time=datetime.now(),
            type="BUY",
            price=price,
            amount=btc_amount,
            value=self.trade_amount_usdt,
            pnl=None
        )
        
        self.trades.append(trade)
        return trade
    
    def _execute_sell(self, price: float) -> Optional[Trade]:
        """Execute a simulated sell order."""
        if self.btc_balance <= 0:
            return None  # No BTC to sell
        
        # Sell all or a portion
        btc_to_sell = min(self.btc_balance, self.trade_amount_usdt / price)
        usdt_received = btc_to_sell * price
        
        # Calculate P&L for this sell
        pnl = 0.0
        if self.buy_prices:
            avg_buy_price = sum(self.buy_prices) / len(self.buy_prices)
            pnl = btc_to_sell * (price - avg_buy_price)
            self.total_realized_pnl += pnl
        
        # Update balances
        self.btc_balance -= btc_to_sell
        self.usdt_balance += usdt_received
        
        # Clear buy prices if we sold all BTC
        if self.btc_balance < 0.00000001:
            self.btc_balance = 0
            self.buy_prices.clear()
        
        trade = Trade(
            time=datetime.now(),
            type="SELL",
            price=price,
            amount=btc_to_sell,
            value=usdt_received,
            pnl=pnl
        )
        
        self.trades.append(trade)
        return trade
    
    def get_trade_history(self, limit: int = 10) -> List[Dict]:
        """Get recent trade history as list of dicts."""
        recent_trades = self.trades[-limit:] if len(self.trades) > limit else self.trades
        return [
            {
                "time": t.time,
                "type": t.type,
                "price": t.price,
                "amount": t.amount,
                "value": t.value,
                "pnl": t.pnl,
            }
            for t in reversed(recent_trades)
        ]
    
    def get_stats(self, current_price: float) -> Dict:
        """Get current trading statistics."""
        return {
            "usdt_balance": self.usdt_balance,
            "btc_balance": self.btc_balance,
            "portfolio_value": self.calculate_portfolio_value(current_price),
            "realized_pnl": self.total_realized_pnl,
            "unrealized_pnl": self.calculate_unrealized_pnl(current_price),
            "total_pnl": self.calculate_total_pnl(current_price),
            "total_trades": len(self.trades),
            "reference_price": self.reference_price,
        }
    
    def reset(self):
        """Reset the trader to initial state."""
        self.usdt_balance = config.STARTING_USDT_BALANCE
        self.btc_balance = config.STARTING_BTC_BALANCE
        self.reference_price = None
        self.trades.clear()
        self.buy_prices.clear()
        self.total_realized_pnl = 0.0
        self.initial_portfolio_value = None
    
    def update_thresholds(self, buy_threshold: float, sell_threshold: float):
        """Update the buy/sell thresholds."""
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

"""
Mag 7 Alpha + Beta Market Neutral Strategy

Long Mag 7 tech stocks (Alpha) + Short QQQ (Beta) market neutral strategy
"""

from AlgorithmImports import *


class Mag7AlphaBetaStrategy(QCAlgorithm):
"""
    Long Mag 7 (Alpha) + Short QQQ (Beta) market neutral strategy
    
    Strategy logic:
    - Long 60% position in Mag 7 stocks (equal weight)
    - Short 60% position in QQQ ETF as Beta hedge
    - Rebalance every 5 trading days
    
    Objectives:
    - Capture excess returns of Mag 7 relative to market (Alpha)
    - Hedge market risk through short QQQ (Beta)
    """

    # Strategy metadata
    name = "Mag7AlphaBetaStrategy"
    description = "Long Mag 7 + Short QQQ market neutral strategy"

    def initialize(self):
# Backtest period: past 6 months
        self.set_start_date(2025, 7, 1)
        self.set_end_date(2026, 1, 1)
        
        # Initial capital
        self.set_cash(1000000)
        
        # Benchmark
        self.set_benchmark("QQQ")
        
        # Mag 7 stocks
        self.mag7_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
        self.mag7_symbols = []
        
        for ticker in self.mag7_tickers:
            equity = self.add_equity(ticker, Resolution.DAILY)
            self.mag7_symbols.append(equity.symbol)
        
        # QQQ ETF (hedge)
        self.qqq = self.add_equity("QQQ", Resolution.DAILY)
        
        # Strategy parameters
        self.alpha_total_weight = 0.6  # 60% long Mag 7
        self.beta_hedge_weight = 0.6   # 60% short QQQ
        
        # Rebalancing
        self.rebalance_period = 5
        self.days_since_rebalance = 0
        self.is_invested = False
        
        # Scheduled rebalancing
        self.schedule.on(
            self.date_rules.every_day(),
            self.time_rules.after_market_open("AAPL", 30),
            self.rebalance,
        )

        self.debug("Mag 7 Alpha + Beta strategy initialization complete")

    def rebalance(self):
        """Execute rebalancing"""
        self.days_since_rebalance += 1

        if self.days_since_rebalance < self.rebalance_period and self.is_invested:
            return

        self.days_since_rebalance = 0

# Long Mag 7
        weight_per_stock = self.alpha_total_weight / len(self.mag7_tickers)
        for symbol in self.mag7_symbols:
            if self.securities[symbol].price > 0:
                self.set_holdings(symbol, weight_per_stock)
        
        # Short QQQ
        self.set_holdings("QQQ", -self.beta_hedge_weight)
        
        self.is_invested = True
        self.debug(f"[{self.time}] Rebalancing complete")

    def on_data(self, data):
        pass

    def on_end_of_algorithm(self):
        self.debug("=" * 50)
        self.debug("Strategy backtest complete")
        total_return = (self.portfolio.total_portfolio_value / 1000000 - 1) * 100
        self.debug(f"Total return: {total_return:.2f}%")
        self.debug("=" * 50)

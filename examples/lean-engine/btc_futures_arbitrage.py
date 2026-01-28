"""
BTC Futures Spot Arbitrage Strategy

Use Coinbase BTC spot + CME BTC futures for cash-futures arbitrage

Strategy logic:
- When futures premium exceeds threshold: Long spot + Short futures (cash-and-carry arbitrage)
- Close position for profit when spread converges or expires
"""

from AlgorithmImports import *


class BTCFuturesArbitrageStrategy(QCAlgorithm):
"""
    BTC Futures Spot Arbitrage Strategy
    
    Exploit price difference between CME BTC futures and Coinbase spot
    
    Strategy logic:
    1. Monitor futures premium relative to spot (basis)
    2. When basis > entry threshold, long spot + short futures
    3. When basis < exit threshold, close position for profit
    4. Force close and roll to next contract as futures near expiry
    
    Risk control:
    - Only cash-and-carry arbitrage (when futures premium exists)
    - Limit single-side position to max 40% of account
    - Force close 5 days before futures expiry
    """

    # Strategy metadata
    name = "BTCFuturesArbitrageStrategy"
    description = "BTC futures spot arbitrage - Coinbase spot vs CME futures"

    def initialize(self):
# Backtest period
        self.set_start_date(2024, 1, 1)
        self.set_end_date(2025, 1, 1)
        
        # Initial capital
        self.set_cash(1000000)
        
        # Set timezone to US Eastern (CME trading hours)
        self.set_time_zone(TimeZones.NEW_YORK)
        
        # ========== Add Coinbase BTC Spot ==========
        self.btc_spot = self.add_crypto("BTCUSD", Resolution.HOUR, Market.COINBASE)
        self.btc_spot_symbol = self.btc_spot.symbol
        
        # ========== Add CME BTC Futures ==========
        # CME BTC futures symbol: BTC
        self.btc_future = self.add_future(
            Futures.Currencies.BTC,
            Resolution.HOUR,
            data_normalization_mode=DataNormalizationMode.BACKWARDS_RATIO,
            data_mapping_mode=DataMappingMode.OPEN_INTEREST,
            contract_depth_offset=0,  # Use front month contract
        )

        # Set futures filter - select most liquid contracts
        self.btc_future.set_filter(lambda x: x.front_month())

# ========== Strategy Parameters ==========
        # Arbitrage thresholds (annualized return)
        self.entry_basis_threshold = 0.08   # Entry: annualized premium > 8%
        self.exit_basis_threshold = 0.02    # Exit: annualized premium < 2%
        
        # Position management
        self.position_size = 0.4  # Single-side position 40%
        
        # Expiry risk control
        self.days_before_expiry_to_close = 5  # Close 5 days before expiry
        
        # State tracking
        self.current_future_contract = None
        self.is_arbitrage_position = False
        self.entry_basis = 0
        self.entry_time = None

        # Data window
        self.spot_prices = []
        self.future_prices = []
        self.basis_history = []
        self.window_size = 24  # 24-hour window

        # Scheduled tasks
        self.schedule.on(
            self.date_rules.every_day(),
            self.time_rules.at(10, 0),  # Check daily at 10 AM
            self.check_arbitrage_opportunity,
        )

        # Set benchmark
        self.set_benchmark(self.btc_spot_symbol)

        self.debug("BTC futures spot arbitrage strategy initialization complete")
        self.debug(f"Entry threshold: {self.entry_basis_threshold * 100:.1f}% annualized")
        self.debug(f"Exit threshold: {self.exit_basis_threshold * 100:.1f}% annualized")

    def on_data(self, data: Slice):
        """Process each data point"""
        # Get spot price
        if not data.contains_key(self.btc_spot_symbol):
            return

        spot_price = data[self.btc_spot_symbol].close

        # Get futures contract and price
        future_contract = self.get_front_month_future()
        if future_contract is None:
            return

        if not data.contains_key(future_contract):
            return

        future_price = data[future_contract].close

        # Update price window
        self.spot_prices.append(spot_price)
        self.future_prices.append(future_price)

        if len(self.spot_prices) > self.window_size:
            self.spot_prices.pop(0)
            self.future_prices.pop(0)

        # Calculate annualized basis
        days_to_expiry = self.get_days_to_expiry(future_contract)
        if days_to_expiry <= 0:
            return

        basis = self.calculate_annualized_basis(
            spot_price, future_price, days_to_expiry
        )

        self.basis_history.append(basis)
        if len(self.basis_history) > 100:
            self.basis_history.pop(0)

        # Update current contract
        if self.current_future_contract != future_contract:
            if self.is_arbitrage_position:
                self.debug(f"[{self.time}] Futures contract switched, need to roll position")
                self.roll_futures_position(future_contract)
            self.current_future_contract = future_contract

    def check_arbitrage_opportunity(self):
        """Check arbitrage opportunity"""
        if len(self.spot_prices) < 5:
            return

        future_contract = self.get_front_month_future()
        if future_contract is None:
            return

        spot_price = self.spot_prices[-1]
        future_price = self.future_prices[-1]
        days_to_expiry = self.get_days_to_expiry(future_contract)

        if days_to_expiry <= self.days_before_expiry_to_close:
            if self.is_arbitrage_position:
                self.debug(f"[{self.time}] Futures near expiry ({days_to_expiry} days), closing position")
                self.close_arbitrage_position()
            return

        basis = self.calculate_annualized_basis(
            spot_price, future_price, days_to_expiry
        )

        # Entry logic
        if not self.is_arbitrage_position:
            if basis > self.entry_basis_threshold:
                self.open_arbitrage_position(
                    spot_price, future_price, basis, future_contract
                )

        # Exit logic
        else:
            if basis < self.exit_basis_threshold:
                self.debug(f"[{self.time}] Basis converged to {basis * 100:.2f}%, closing for profit")
                self.close_arbitrage_position()

    def open_arbitrage_position(self, spot_price, future_price, basis, future_contract):
        """Entry: Long spot + Short futures"""
        # Calculate position size
        portfolio_value = self.portfolio.total_portfolio_value
        target_value = portfolio_value * self.position_size

        # Long BTC spot
        spot_quantity = target_value / spot_price
        self.market_order(self.btc_spot_symbol, spot_quantity)

        # Short CME BTC futures
        # CME BTC futures contract size is 5 BTC
        contract_size = 5
        future_contracts = int(spot_quantity / contract_size)

        if future_contracts > 0:
            self.market_order(future_contract, -future_contracts)

            self.is_arbitrage_position = True
            self.entry_basis = basis
            self.entry_time = self.time

            self.debug("=" * 50)
self.debug(f"[{self.time}] Opening arbitrage position")
            self.debug(f"  Spot price: ${spot_price:,.2f}")
            self.debug(f"  Future price: ${future_price:,.2f}")
            self.debug(f"  Annualized basis: {basis*100:.2f}%")
            self.debug(f"  Spot quantity: {spot_quantity:.4f} BTC")
            self.debug(f"  Future contracts: {future_contracts} (short)")
            self.debug("=" * 50)

    def close_arbitrage_position(self):
        """Close arbitrage position"""
        # Close spot position
        spot_holding = self.portfolio[self.btc_spot_symbol]
        if spot_holding.quantity != 0:
            self.market_order(self.btc_spot_symbol, -spot_holding.quantity)

        # Close futures position
        for kvp in self.portfolio:
            if kvp.value.symbol.security_type == SecurityType.FUTURE:
                if kvp.value.quantity != 0:
                    self.market_order(kvp.value.symbol, -kvp.value.quantity)

        if self.is_arbitrage_position:
            holding_days = (self.time - self.entry_time).days if self.entry_time else 0
            pnl = self.portfolio.total_portfolio_value - 1000000

            self.debug("=" * 50)
self.debug(f"[{self.time}] Closing arbitrage position")
            self.debug(f"  Holding days: {holding_days}")
            self.debug(f"  Entry basis: {self.entry_basis*100:.2f}%")
            self.debug(f"  Cumulative P&L: ${pnl:,.2f}")
            self.debug("=" * 50)

        self.is_arbitrage_position = False
        self.entry_basis = 0
        self.entry_time = None

    def roll_futures_position(self, new_contract):
        """Roll futures position to new contract"""
        # Close old futures contract
        for kvp in self.portfolio:
            if kvp.value.symbol.security_type == SecurityType.FUTURE:
                if kvp.value.quantity != 0:
                    old_quantity = kvp.value.quantity
                    self.market_order(kvp.value.symbol, -kvp.value.quantity)

                    # Open same position on new contract
                    self.market_order(new_contract, old_quantity)
                    self.debug(
                        f"[{self.time}] Rolling futures: {kvp.value.symbol} -> {new_contract}"
                    )

    def get_front_month_future(self):
        """Get front month futures contract"""
        chain = self.current_slice.future_chains.get(self.btc_future.symbol)
        if chain is None:
            return None

        # Select nearest expiry with liquidity
        contracts = [c for c in chain if c.expiry > self.time]
        if not contracts:
            return None

        # Sort by expiry date, take nearest
        contracts.sort(key=lambda x: x.expiry)
        return contracts[0].symbol

    def get_days_to_expiry(self, future_symbol):
        """Calculate days to futures expiry"""
        if future_symbol is None:
            return 0

        expiry = future_symbol.id.date
        return (expiry - self.time).days

    def calculate_annualized_basis(self, spot_price, future_price, days_to_expiry):
        """
        Calculate annualized basis yield

        basis = (F - S) / S * (365 / T)

        Where:
        - F: Futures price
        - S: Spot price
        - T: Days to expiry
        """
        if spot_price <= 0 or days_to_expiry <= 0:
            return 0

        raw_basis = (future_price - spot_price) / spot_price
        annualized_basis = raw_basis * (365 / days_to_expiry)

        return annualized_basis

    def on_end_of_algorithm(self):
        """Backtest complete"""
        self.debug("=" * 60)
        self.debug("BTC Futures Spot Arbitrage Strategy Backtest Complete")
        self.debug("=" * 60)

        total_return = (self.portfolio.total_portfolio_value / 1000000 - 1) * 100
        self.debug(f"Initial capital: $1,000,000")
        self.debug(f"Final capital: ${self.portfolio.total_portfolio_value:,.2f}")
        self.debug(f"Total return: {total_return:.2f}%")

        if self.basis_history:
            avg_basis = sum(self.basis_history) / len(self.basis_history)
            max_basis = max(self.basis_history)
            min_basis = min(self.basis_history)
            self.debug(f"Average annualized basis: {avg_basis * 100:.2f}%")
            self.debug(f"Maximum annualized basis: {max_basis * 100:.2f}%")
            self.debug(f"Minimum annualized basis: {min_basis * 100:.2f}%")

        self.debug("=" * 60)

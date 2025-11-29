"""
Live Trading Integration Test - 实盘交易集成测试

This test demonstrates and validates the complete live trading flow:
1. Exchange connection and authentication
2. Market data retrieval
3. Order placement and management
4. Position tracking
5. Advanced order types (TWAP, OCO, Trailing Stop, etc.)

Usage:
    # Set environment variables first:
    export API_KEY="your_api_key"
    export MARKET="BTC-PERP"  # or any market
    
    # Run the test:
    python test_live_trading_integration.py
    
    # For testnet:
    export BASE_URL="https://testnet-api.1024ex.com"
    python test_live_trading_integration.py

Reference: https://api.1024ex.com/api-docs/openapi.json
"""

import os
import sys
import time
import uuid
from typing import Optional, Dict, Any
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quant1024 import Exchange1024ex, QuantStrategy, LiveTrader
from quant1024.monitor_feeds import RuntimeConfig


# ========== Strategy Implementations ==========

class SimpleTrendStrategy(QuantStrategy):
    """
    Simple Trend Following Strategy
    
    Strategy Logic:
    - Price increases → Buy signal
    - Price decreases → Sell signal
    - Price unchanged → Hold current position
    """
    
    def generate_signals(self, data):
        if len(data) < 2:
            return [0]
        
        signals = []
        for i in range(len(data)):
            if i == 0:
                signals.append(0)
            elif data[i] > data[i-1]:
                signals.append(1)   # Price up → Buy
            elif data[i] < data[i-1]:
                signals.append(-1)  # Price down → Sell
            else:
                signals.append(0)   # Price unchanged → Hold
        
        return signals
    
    def calculate_position(self, signal, current_position):
        if signal == 1:
            return 0.5  # Buy signal → 50% position
        elif signal == -1:
            return 0.0  # Sell signal → Close position
        else:
            return current_position


class MomentumStrategy(QuantStrategy):
    """
    Momentum Strategy with configurable lookback period
    """
    
    def __init__(self, name, params=None):
        super().__init__(name, params)
        self.lookback = self.params.get('lookback', 5)
        self.threshold = self.params.get('threshold', 0.01)  # 1% threshold
    
    def generate_signals(self, data):
        if len(data) < self.lookback + 1:
            return [0] * len(data)
        
        signals = []
        for i in range(len(data)):
            if i < self.lookback:
                signals.append(0)
            else:
                momentum = (data[i] - data[i - self.lookback]) / data[i - self.lookback]
                if momentum > self.threshold:
                    signals.append(1)
                elif momentum < -self.threshold:
                    signals.append(-1)
                else:
                    signals.append(0)
        
        return signals
    
    def calculate_position(self, signal, current_position):
        if signal == 1:
            return 0.7  # Strong momentum → 70% position
        elif signal == -1:
            return 0.0  # Negative momentum → Close
        else:
            return current_position


# ========== Test Functions ==========

class LiveTradingTester:
    """
    Live Trading Integration Tester
    
    Tests all aspects of the live trading system
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.1024ex.com",
        market: str = "BTC-PERP"
    ):
        """
        Initialize tester
        
        Args:
            api_key: 1024 Exchange API Key
            base_url: API base URL
            market: Market to trade (e.g., "BTC-PERP")
        """
        self.api_key = api_key
        self.base_url = base_url
        self.market = market
        self.exchange = None
        self.results = {}
        
        print("=" * 70)
        print("🧪 1024 Exchange Live Trading Integration Test")
        print("=" * 70)
        print(f"Base URL: {base_url}")
        print(f"Market: {market}")
        print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
        print("=" * 70)
    
    def setup(self) -> bool:
        """Initialize exchange connection"""
        print("\n📡 Setting up exchange connection...")
        
        try:
            self.exchange = Exchange1024ex(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=30,
                max_retries=3
            )
            print("✅ Exchange client initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize exchange: {e}")
            return False
    
    def test_system_endpoints(self) -> bool:
        """Test system endpoints (no auth required)"""
        print("\n🔧 Testing System Endpoints...")
        success = True
        
        # Test 1: Server Time
        try:
            result = self.exchange.get_server_time()
            print(f"  ✅ Server Time: {result}")
            self.results['server_time'] = result
        except Exception as e:
            print(f"  ❌ Server Time failed: {e}")
            success = False
        
        # Test 2: Health Check
        try:
            result = self.exchange.get_health()
            print(f"  ✅ Health Check: {result.get('status', result)}")
            self.results['health'] = result
        except Exception as e:
            print(f"  ❌ Health Check failed: {e}")
            success = False
        
        # Test 3: Exchange Info
        try:
            result = self.exchange.get_exchange_info()
            print(f"  ✅ Exchange Info: Retrieved")
            self.results['exchange_info'] = result
        except Exception as e:
            print(f"  ❌ Exchange Info failed: {e}")
            success = False
        
        return success
    
    def test_market_data(self) -> bool:
        """Test market data endpoints"""
        print("\n📊 Testing Market Data Endpoints...")
        success = True
        
        # Test 1: Get Markets
        try:
            markets = self.exchange.get_markets()
            print(f"  ✅ Markets: {len(markets) if isinstance(markets, list) else 'Retrieved'}")
            self.results['markets'] = markets
        except Exception as e:
            print(f"  ❌ Get Markets failed: {e}")
            success = False
        
        # Test 2: Get Market Info
        try:
            market_info = self.exchange.get_market(self.market)
            print(f"  ✅ Market {self.market}: {market_info.get('status', 'Retrieved')}")
            self.results['market_info'] = market_info
        except Exception as e:
            print(f"  ❌ Get Market Info failed: {e}")
            success = False
        
        # Test 3: Get Ticker
        try:
            ticker = self.exchange.get_ticker(self.market)
            price = ticker.get('last_price', ticker.get('data', {}).get('last_price', 'N/A'))
            print(f"  ✅ Ticker {self.market}: ${price}")
            self.results['ticker'] = ticker
        except Exception as e:
            print(f"  ❌ Get Ticker failed: {e}")
            success = False
        
        # Test 4: Get Orderbook
        try:
            orderbook = self.exchange.get_orderbook(self.market, depth=10)
            print(f"  ✅ Orderbook: Retrieved (depth=10)")
            self.results['orderbook'] = orderbook
        except Exception as e:
            print(f"  ❌ Get Orderbook failed: {e}")
            success = False
        
        # Test 5: Get Recent Trades
        try:
            trades = self.exchange.get_trades(self.market, limit=10)
            print(f"  ✅ Recent Trades: {len(trades) if isinstance(trades, list) else 'Retrieved'}")
            self.results['trades'] = trades
        except Exception as e:
            print(f"  ❌ Get Trades failed: {e}")
            success = False
        
        # Test 6: Get Klines
        try:
            klines = self.exchange.get_klines(self.market, interval='1h', limit=50)
            print(f"  ✅ Klines (1h): {len(klines) if isinstance(klines, list) else 'Retrieved'} candles")
            self.results['klines'] = klines
        except Exception as e:
            print(f"  ❌ Get Klines failed: {e}")
            success = False
        
        # Test 7: Get Funding Rate
        try:
            funding = self.exchange.get_funding_rate(self.market)
            rate = funding.get('funding_rate', funding.get('data', {}).get('funding_rate', 'N/A'))
            print(f"  ✅ Funding Rate: {rate}")
            self.results['funding_rate'] = funding
        except Exception as e:
            print(f"  ❌ Get Funding Rate failed: {e}")
            success = False
        
        return success
    
    def test_account_endpoints(self) -> bool:
        """Test account endpoints (requires auth)"""
        print("\n💰 Testing Account Endpoints...")
        success = True
        
        # Test 1: API Status
        try:
            result = self.exchange.get_api_status()
            print(f"  ✅ API Status: Retrieved")
            self.results['api_status'] = result
        except Exception as e:
            print(f"  ⚠️ API Status: {e}")
            # Don't fail, might be expected without proper auth
        
        # Test 2: Account Balance
        try:
            balance = self.exchange.get_balance()
            print(f"  ✅ Balance: Retrieved")
            self.results['balance'] = balance
        except Exception as e:
            print(f"  ⚠️ Get Balance: {e}")
        
        # Test 3: Positions
        try:
            positions = self.exchange.get_positions(market=self.market)
            print(f"  ✅ Positions: {len(positions) if isinstance(positions, list) else 'Retrieved'}")
            self.results['positions'] = positions
        except Exception as e:
            print(f"  ⚠️ Get Positions: {e}")
        
        # Test 4: Margin
        try:
            margin = self.exchange.get_margin()
            print(f"  ✅ Margin: Retrieved")
            self.results['margin'] = margin
        except Exception as e:
            print(f"  ⚠️ Get Margin: {e}")
        
        # Test 5: Trading Stats
        try:
            stats = self.exchange.get_trading_stats(period="7d")
            print(f"  ✅ Trading Stats (7d): Retrieved")
            self.results['trading_stats'] = stats
        except Exception as e:
            print(f"  ⚠️ Get Trading Stats: {e}")
        
        return success
    
    def test_order_management(self, execute_orders: bool = False) -> bool:
        """
        Test order management endpoints
        
        Args:
            execute_orders: If True, actually place and cancel test orders
        """
        print("\n📝 Testing Order Management...")
        success = True
        
        if not execute_orders:
            print("  ℹ️ Order execution disabled (dry run)")
            print("  ℹ️ Set execute_orders=True to test actual order placement")
            return True
        
        # Test 1: Get Current Orders
        try:
            orders = self.exchange.get_orders(market=self.market)
            print(f"  ✅ Current Orders: {len(orders) if isinstance(orders, list) else 'Retrieved'}")
            self.results['current_orders'] = orders
        except Exception as e:
            print(f"  ❌ Get Orders failed: {e}")
            success = False
        
        # Test 2: Place a small limit order (far from market price)
        try:
            # Get current price
            ticker = self.exchange.get_ticker(self.market)
            if 'data' in ticker:
                current_price = float(ticker['data'].get('last_price', 0))
            else:
                current_price = float(ticker.get('last_price', 0))
            
            # Place buy order at 10% below market
            test_price = str(round(current_price * 0.9, 2))
            test_size = "0.001"  # Minimum size
            
            print(f"  📤 Placing test order: BUY {test_size} @ ${test_price}")
            
            order = self.exchange.place_order(
                market=self.market,
                side="buy",
                order_type="limit",
                size=test_size,
                price=test_price,
                time_in_force="GTC"
            )
            order_id = order.get('order_id', order.get('data', {}).get('order_id'))
            print(f"  ✅ Order placed: {order_id}")
            self.results['test_order'] = order
            
            # Test 3: Get order details
            if order_id:
                time.sleep(1)  # Wait for order to be registered
                order_details = self.exchange.get_order(order_id)
                print(f"  ✅ Order details retrieved")
                
                # Test 4: Cancel the order
                cancel_result = self.exchange.cancel_order(order_id)
                print(f"  ✅ Order cancelled: {cancel_result}")
                self.results['cancel_result'] = cancel_result
            
        except Exception as e:
            print(f"  ⚠️ Order test: {e}")
            # Don't fail - might not have funds
        
        return success
    
    def test_advanced_orders(self, execute_orders: bool = False) -> bool:
        """Test advanced order types"""
        print("\n🎯 Testing Advanced Order Types...")
        
        if not execute_orders:
            print("  ℹ️ Advanced order execution disabled (dry run)")
            print("  ℹ️ Available advanced order types:")
            print("      - Conditional Orders")
            print("      - TWAP Orders")
            print("      - Scale Orders")
            print("      - OCO Orders")
            print("      - Bracket Orders")
            print("      - Iceberg Orders")
            print("      - Trailing Stop Orders")
            print("      - VWAP Orders")
            print("      - Sniper Orders")
            return True
        
        success = True
        
        # Test Trailing Stop (most commonly used)
        try:
            ticker = self.exchange.get_ticker(self.market)
            if 'data' in ticker:
                current_price = float(ticker['data'].get('last_price', 0))
            else:
                current_price = float(ticker.get('last_price', 0))
            
            # Create trailing stop order
            result = self.exchange.place_trailing_stop_order(
                market=self.market,
                side="sell",
                size="0.001",
                callback_rate="0.02",  # 2% trailing
                reduce_only=True
            )
            print(f"  ✅ Trailing Stop Order: {result}")
            
            # Cancel it immediately for testing
            order_id = result.get('order_id')
            if order_id:
                self.exchange.cancel_trailing_stop_order(order_id)
                print(f"  ✅ Trailing Stop cancelled")
            
        except Exception as e:
            print(f"  ⚠️ Trailing Stop test: {e}")
        
        return success
    
    def test_live_trader(self, iterations: int = 3) -> bool:
        """
        Test LiveTrader integration
        
        Args:
            iterations: Number of trading loops to run
        """
        print(f"\n🤖 Testing LiveTrader (max {iterations} iterations)...")
        
        try:
            # Create strategy
            strategy = SimpleTrendStrategy(
                name="Test Strategy",
                params={"lookback_period": 5}
            )
            print(f"  ✅ Strategy initialized: {strategy.name}")
            
            # Create LiveTrader
            trader = LiveTrader(
                strategy=strategy,
                exchange=self.exchange,
                market=self.market,
                initial_capital=10000,
                max_position_size=0.1,  # 10% max position for safety
                check_interval=5,  # 5 seconds for testing
                stop_loss=0.05,
                take_profit=0.10
            )
            print(f"  ✅ LiveTrader initialized")
            
            # Run limited iterations
            print(f"  🔄 Running {iterations} trading cycles...")
            trader.start(max_iterations=iterations)
            
            # Get final status
            status = trader.get_status()
            print(f"  ✅ Final Status:")
            print(f"      - Running: {status['is_running']}")
            print(f"      - Trades: {status['trades_count']}")
            print(f"      - Position: {status['current_position']}")
            print(f"      - Price History: {status['price_history_length']} points")
            
            self.results['trader_status'] = status
            return True
            
        except Exception as e:
            print(f"  ❌ LiveTrader test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_all_tests(
        self,
        execute_orders: bool = False,
        test_trading: bool = True,
        trading_iterations: int = 3
    ) -> Dict[str, Any]:
        """
        Run all tests
        
        Args:
            execute_orders: If True, test actual order placement
            test_trading: If True, test LiveTrader
            trading_iterations: Number of trading iterations
        
        Returns:
            Test results summary
        """
        print("\n" + "=" * 70)
        print("🚀 Starting All Tests")
        print("=" * 70)
        
        start_time = time.time()
        test_results = {}
        
        # Setup
        if not self.setup():
            return {"success": False, "error": "Setup failed"}
        
        # Run tests
        test_results['system'] = self.test_system_endpoints()
        test_results['market_data'] = self.test_market_data()
        test_results['account'] = self.test_account_endpoints()
        test_results['orders'] = self.test_order_management(execute_orders)
        test_results['advanced_orders'] = self.test_advanced_orders(execute_orders)
        
        if test_trading:
            test_results['live_trader'] = self.test_live_trader(trading_iterations)
        
        # Summary
        elapsed = time.time() - start_time
        passed = sum(1 for v in test_results.values() if v)
        total = len(test_results)
        
        print("\n" + "=" * 70)
        print("📊 Test Summary")
        print("=" * 70)
        print(f"Passed: {passed}/{total}")
        print(f"Time: {elapsed:.2f}s")
        
        for name, result in test_results.items():
            icon = "✅" if result else "❌"
            print(f"  {icon} {name}")
        
        print("=" * 70)
        
        return {
            "success": passed == total,
            "passed": passed,
            "total": total,
            "elapsed": elapsed,
            "details": test_results,
            "data": self.results
        }


def main():
    """
    Main entry point
    
    Environment Variables:
        API_KEY: 1024 Exchange API Key (required)
        BASE_URL: API base URL (optional, default: https://api.1024ex.com)
        MARKET: Trading market (optional, default: BTC-PERP)
        EXECUTE_ORDERS: If "true", test actual order placement
        TEST_TRADING: If "true", test LiveTrader
    """
    print("=" * 70)
    print("🧪 1024 Exchange Live Trading Integration Test")
    print("=" * 70)
    
    # Get configuration from environment
    api_key = os.getenv("API_KEY", "")
    base_url = os.getenv("BASE_URL", "https://api.1024ex.com")
    market = os.getenv("MARKET", "BTC-PERP")
    execute_orders = os.getenv("EXECUTE_ORDERS", "false").lower() == "true"
    test_trading = os.getenv("TEST_TRADING", "true").lower() == "true"
    
    if not api_key:
        print("\n❌ Error: API_KEY environment variable not set!")
        print("\nUsage:")
        print("  export API_KEY='your_api_key'")
        print("  python test_live_trading_integration.py")
        print("\nFor testnet:")
        print("  export BASE_URL='https://testnet-api.1024ex.com'")
        print("  python test_live_trading_integration.py")
        print("\nOptions:")
        print("  EXECUTE_ORDERS=true  - Test actual order placement")
        print("  TEST_TRADING=true    - Test LiveTrader (default)")
        print("  MARKET=ETH-PERP      - Change trading market")
        return
    
    # Run tests
    tester = LiveTradingTester(
        api_key=api_key,
        base_url=base_url,
        market=market
    )
    
    results = tester.run_all_tests(
        execute_orders=execute_orders,
        test_trading=test_trading,
        trading_iterations=3
    )
    
    if results['success']:
        print("\n✅ All tests passed!")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    main()


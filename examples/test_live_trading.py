"""
Live Trading Test - 实盘交易测试

Based on the 1024 Quant platform strategy template.
Tests the complete live trading flow with the quant1024 framework.

================================================================================
ENVIRONMENT VARIABLES (环境变量)
================================================================================

必需 (Required):
    EXCHANGE_API_KEY    - 1024 Exchange API Key（用于交易）
                          Get from: https://1024ex.com -> Settings -> API Keys

可选 - 监控功能 (Optional - Monitoring):
    PLATFORM_API_KEY    - 1024 Quant 平台 API Key（用于记录监控）
                          Get from: https://1024quant.com -> Settings -> API Keys
    STRATEGY_ID         - 策略 ID（从平台获取）

可选 - 交易配置 (Optional - Trading Config):
    MARKET              - 交易市场（默认 BTC-PERP）
    INITIAL_CAPITAL     - 初始资金（默认 10000）
    MAX_POSITION_SIZE   - 最大仓位比例（默认 0.5，即50%）
    CHECK_INTERVAL      - 检查间隔秒数（默认 60）
    STOP_LOSS           - 止损比例（默认 0.05，即5%）
    TAKE_PROFIT         - 止盈比例（默认 0.10，即10%）
    EXCHANGE_BASE_URL   - 交易所 API 地址
                          默认: https://api.1024ex.com
                          测试网: https://testnet-api.1024ex.com

================================================================================
USAGE (使用方法)
================================================================================

# 1. Run basic tests (no API key required for public endpoints)
python test_live_trading.py

# 2. Run with mock exchange (offline testing)
python test_live_trading.py --mock

# 3. Run actual live trading (requires API key)
export EXCHANGE_API_KEY="your_exchange_api_key"
python test_live_trading.py --live

# 4. Run with monitoring enabled
export EXCHANGE_API_KEY="your_exchange_api_key"
export PLATFORM_API_KEY="your_platform_api_key"
export STRATEGY_ID="your_strategy_id"
python test_live_trading.py --live

# 5. Use testnet for safety
export EXCHANGE_API_KEY="your_testnet_api_key"
export EXCHANGE_BASE_URL="https://testnet-api.1024ex.com"
python test_live_trading.py --live

================================================================================
API DOCUMENTATION
================================================================================
Exchange API: https://api.1024ex.com/api-docs/openapi.json
Platform API: https://docs.1024quant.com
"""

import sys
import os
import argparse
from typing import List, Dict, Any, Optional
from unittest.mock import Mock, MagicMock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quant1024 import QuantStrategy, Exchange1024ex
from quant1024.live_trading import LiveTrader, start_trading
from quant1024.monitor_feeds import RuntimeConfig


# ========== Strategy Implementations ==========

class SimpleTrendStrategy(QuantStrategy):
    """
    Simple Trend Following Strategy (from template)
    
    Strategy Logic:
    - Price increases → Buy signal
    - Price decreases → Sell signal
    - Price unchanged → Hold current position
    """
    
    def generate_signals(self, data: List[float]) -> List[int]:
        """Generate trading signals from price data"""
        if len(data) < 2:
            return [0]
        
        signals = []
        for i in range(len(data)):
            if i == 0:
                signals.append(0)  # No signal for first data point
            elif data[i] > data[i-1]:
                signals.append(1)   # Price up → Buy
            elif data[i] < data[i-1]:
                signals.append(-1)  # Price down → Sell
            else:
                signals.append(0)   # Price unchanged → Hold
        
        return signals
    
    def calculate_position(self, signal: int, current_position: float) -> float:
        """Calculate target position based on signal"""
        if signal == 1:
            return 0.5  # Buy signal → 50% position
        elif signal == -1:
            return 0.0  # Sell signal → Close position
        else:
            return current_position  # Hold → Maintain position


class MomentumStrategy(QuantStrategy):
    """
    Momentum Strategy with configurable lookback period
    """
    
    def __init__(self, name: str, params: Dict = None):
        super().__init__(name, params)
        self.lookback = self.params.get('lookback', 5)
        self.threshold = self.params.get('threshold', 0.01)  # 1% threshold
    
    def generate_signals(self, data: List[float]) -> List[int]:
        """Generate signals based on momentum"""
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
    
    def calculate_position(self, signal: int, current_position: float) -> float:
        """Calculate position based on momentum signal"""
        if signal == 1:
            return 0.7  # Strong momentum → 70% position
        elif signal == -1:
            return 0.0  # Negative momentum → Close
        else:
            return current_position


# ========== Mock Exchange ==========

def create_mock_exchange():
    """Create a mock exchange for testing without network"""
    mock_exchange = Mock()
    
    # Simulated price sequence (BTC price starting at 50000, gradually rising)
    price_sequence = [50000, 50100, 50200, 50150, 50300, 50400, 50350, 50500, 50600, 50550]
    price_index = [0]
    
    def mock_get_ticker(market):
        """Mock ticker retrieval"""
        idx = price_index[0] % len(price_sequence)
        price = price_sequence[idx]
        price_index[0] += 1
        return {
            'last_price': str(price),
            'mark_price': str(price),
            'volume_24h': '1000000'
        }
    
    def mock_get_positions(market=None):
        """Mock position retrieval"""
        return []
    
    def mock_place_order(market, side, order_type, size, **kwargs):
        """Mock order placement"""
        return {
            'order_id': f'test_order_{price_index[0]}',
            'status': 'filled',
            'market': market,
            'side': side,
            'size': size
        }
    
    # Set up mock methods
    mock_exchange.get_ticker = MagicMock(side_effect=mock_get_ticker)
    mock_exchange.get_positions = MagicMock(side_effect=mock_get_positions)
    mock_exchange.place_order = MagicMock(side_effect=mock_place_order)
    
    return mock_exchange


# ========== Test Functions ==========

def test_exchange_connection() -> bool:
    """Test exchange connection using public endpoints"""
    print("\n📡 Testing Exchange Connection...")
    
    try:
        base_url = os.getenv("EXCHANGE_BASE_URL", "https://api.1024ex.com")
        exchange = Exchange1024ex(
            api_key="",  # Not needed for public endpoints
            base_url=base_url
        )
        
        # Test 1: Health check
        health = exchange.get_health()
        print(f"  ✅ Health: {health.get('status', 'ok')}")
        
        # Test 2: Get markets
        markets = exchange.get_markets()
        market_count = len(markets) if isinstance(markets, list) else "N/A"
        print(f"  ✅ Markets: {market_count} available")
        
        # Test 3: Get ticker
        ticker = exchange.get_ticker("BTC-PERP")
        if 'data' in ticker:
            price = ticker['data'].get('last_price', 'N/A')
        else:
            price = ticker.get('last_price', 'N/A')
        print(f"  ✅ BTC-PERP: ${price}")
        
        return True
    except Exception as e:
        print(f"  ❌ Connection failed: {e}")
        return False


def test_strategy_signals() -> bool:
    """Test strategy signal generation"""
    print("\n🧠 Testing Strategy Signal Generation...")
    
    # Test SimpleTrendStrategy
    strategy1 = SimpleTrendStrategy(name="Trend")
    data = [100.0, 101.0, 102.0, 101.0, 103.0, 104.0]
    signals = strategy1.generate_signals(data)
    
    print(f"  Prices: {data}")
    print(f"  Signals: {signals}")
    
    expected = [0, 1, 1, -1, 1, 1]
    if signals == expected:
        print(f"  ✅ SimpleTrendStrategy: Correct")
    else:
        print(f"  ❌ SimpleTrendStrategy: Expected {expected}")
        return False
    
    # Test MomentumStrategy
    strategy2 = MomentumStrategy(
        name="Momentum",
        params={"lookback": 3, "threshold": 0.02}
    )
    data2 = [100.0, 101.0, 102.0, 103.0, 106.0, 108.0]  # 3% rise
    signals2 = strategy2.generate_signals(data2)
    
    print(f"  Prices: {data2}")
    print(f"  Signals: {signals2}")
    
    # After lookback, should see buy signals due to momentum > 2%
    if signals2[-1] == 1:
        print(f"  ✅ MomentumStrategy: Correct")
    else:
        print(f"  ❌ MomentumStrategy: Expected buy signal at end")
        return False
    
    return True


def test_position_calculation() -> bool:
    """Test position calculation"""
    print("\n📊 Testing Position Calculation...")
    
    strategy = SimpleTrendStrategy(name="Test")
    
    # Test buy signal
    pos1 = strategy.calculate_position(1, 0.0)
    if pos1 == 0.5:
        print(f"  ✅ Buy signal → 50% position")
    else:
        print(f"  ❌ Buy signal: Expected 0.5, got {pos1}")
        return False
    
    # Test sell signal
    pos2 = strategy.calculate_position(-1, 0.5)
    if pos2 == 0.0:
        print(f"  ✅ Sell signal → 0% position")
    else:
        print(f"  ❌ Sell signal: Expected 0.0, got {pos2}")
        return False
    
    # Test hold signal
    pos3 = strategy.calculate_position(0, 0.3)
    if pos3 == 0.3:
        print(f"  ✅ Hold signal → Maintain position")
    else:
        print(f"  ❌ Hold signal: Expected 0.3, got {pos3}")
        return False
    
    return True


def test_live_trader_with_mock() -> bool:
    """Test LiveTrader with mock exchange"""
    print("\n🤖 Testing LiveTrader with Mock Exchange...")
    
    mock_exchange = create_mock_exchange()
    strategy = SimpleTrendStrategy(name="Test Strategy")
    
    try:
        trader = LiveTrader(
            strategy=strategy,
            exchange=mock_exchange,
            market="BTC-PERP",
            initial_capital=10000,
            max_position_size=0.5,
            check_interval=1,
            stop_loss=0.05,
            take_profit=0.10
        )
        
        print(f"  ✅ LiveTrader created")
        print(f"      Strategy: {trader.strategy.name}")
        print(f"      Market: {trader.market}")
        
        # Run a few iterations
        print(f"  🔄 Running 5 trading cycles...")
        trader.start(max_iterations=5)
        
        status = trader.get_status()
        print(f"  ✅ Final Status:")
        print(f"      Trades: {status['trades_count']}")
        print(f"      Position: {status['current_position']}")
        print(f"      Price History: {status['price_history_length']} points")
        
        return True
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_live_trader_with_monitoring() -> bool:
    """Test LiveTrader with RuntimeConfig (monitoring)"""
    print("\n📈 Testing LiveTrader with Monitoring Config...")
    
    mock_exchange = create_mock_exchange()
    strategy = SimpleTrendStrategy(name="Monitored Strategy")
    
    try:
        # Create RuntimeConfig (like the platform does)
        runtime_config = RuntimeConfig(
            api_key="test_platform_api_key",
            runtime_id="test-runtime-123",
            strategy_id="test-strategy-456",
            api_base_url="https://api.1024quant.com",
            environment="test"
        )
        
        print(f"  ✅ RuntimeConfig created")
        print(f"      Runtime ID: {runtime_config.runtime_id}")
        print(f"      Strategy ID: {runtime_config.strategy_id}")
        
        # Create trader with monitoring (will fail to connect but that's OK)
        trader = LiveTrader(
            strategy=strategy,
            exchange=mock_exchange,
            market="BTC-PERP",
            initial_capital=10000,
            max_position_size=0.5,
            check_interval=1,
            runtime_config=runtime_config
        )
        
        print(f"  ✅ LiveTrader with monitoring initialized")
        print(f"      Monitoring: {'Enabled' if trader.runtime_reporter else 'Disabled (expected)'}")
        
        return True
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False


def test_advanced_orders() -> bool:
    """Test that advanced order methods exist"""
    print("\n🎯 Testing Advanced Order Methods...")
    
    exchange = Exchange1024ex(
        api_key="test_key",
        base_url="https://api.1024ex.com"
    )
    
    # Check that advanced order methods exist
    advanced_methods = [
        'place_conditional_order',
        'place_twap_order',
        'place_scale_order',
        'place_oco_order',
        'place_bracket_order',
        'place_iceberg_order',
        'place_trailing_stop_order',
        'place_vwap_order',
        'place_sniper_order'
    ]
    
    all_exist = True
    for method in advanced_methods:
        if hasattr(exchange, method):
            print(f"  ✅ {method}")
        else:
            print(f"  ❌ {method} not found")
            all_exist = False
    
    return all_exist


def test_risk_management() -> bool:
    """Test risk management features"""
    print("\n🛡️ Testing Risk Management...")
    
    mock_exchange = create_mock_exchange()
    strategy = SimpleTrendStrategy(name="Risk Test")
    
    # Test different risk configurations
    configs = [
        {"stop_loss": 0.05, "take_profit": 0.10, "max_position_size": 0.5, "desc": "Conservative"},
        {"stop_loss": 0.02, "take_profit": 0.05, "max_position_size": 0.3, "desc": "Tight stops"},
        {"stop_loss": None, "take_profit": None, "max_position_size": 1.0, "desc": "No stops"},
    ]
    
    for config in configs:
        desc = config.pop("desc")
        try:
            trader = LiveTrader(
                strategy=strategy,
                exchange=mock_exchange,
                market="BTC-PERP",
                initial_capital=10000,
                check_interval=1,
                **config
            )
            print(f"  ✅ {desc}: Created successfully")
        except Exception as e:
            print(f"  ❌ {desc}: Failed - {e}")
            return False
    
    return True


def run_live_trading_test(iterations: int = 5):
    """
    Run actual live trading test
    
    Uses environment variables for configuration.
    """
    print("\n" + "=" * 70)
    print("🚀 Live Trading Test")
    print("=" * 70)
    
    # Load configuration from environment
    api_key = os.getenv("EXCHANGE_API_KEY", "")
    base_url = os.getenv("EXCHANGE_BASE_URL", "https://api.1024ex.com")
    market = os.getenv("MARKET", "BTC-PERP")
    initial_capital = float(os.getenv("INITIAL_CAPITAL", "10000"))
    max_position_size = float(os.getenv("MAX_POSITION_SIZE", "0.5"))
    check_interval = int(os.getenv("CHECK_INTERVAL", "5"))  # 5 seconds for testing
    stop_loss = float(os.getenv("STOP_LOSS", "0.05"))
    take_profit = float(os.getenv("TAKE_PROFIT", "0.10"))
    
    # Monitoring configuration (optional)
    platform_api_key = os.getenv("PLATFORM_API_KEY", "")
    strategy_id = os.getenv("STRATEGY_ID", "")
    
    print(f"Configuration:")
    print(f"  Exchange API Key: {'✅ Set' if api_key else '❌ Missing'}")
    print(f"  Platform API Key: {'✅ Set' if platform_api_key else '⚪ Not set (monitoring disabled)'}")
    print(f"  Strategy ID: {strategy_id or '(auto-generated)'}")
    print(f"  Base URL: {base_url}")
    print(f"  Market: {market}")
    print(f"  Initial Capital: ${initial_capital:,.2f}")
    print(f"  Max Position Size: {max_position_size * 100:.0f}%")
    print(f"  Check Interval: {check_interval}s")
    print(f"  Stop Loss: {stop_loss * 100:.0f}%")
    print(f"  Take Profit: {take_profit * 100:.0f}%")
    print(f"  Iterations: {iterations}")
    print("=" * 70)
    
    if not api_key:
        print("\n❌ Error: EXCHANGE_API_KEY environment variable not set")
        print("\nTo set it:")
        print("  export EXCHANGE_API_KEY='your_api_key'")
        print("\nFor testnet (recommended for testing):")
        print("  export EXCHANGE_BASE_URL='https://testnet-api.1024ex.com'")
        return
    
    # Create exchange connection
    exchange = Exchange1024ex(
        api_key=api_key,
        base_url=base_url
    )
    
    # Create strategy
    strategy = SimpleTrendStrategy(
        name="Live Test Strategy",
        params={"risk_tolerance": 0.02}
    )
    
    # Create runtime config if platform API key is provided
    runtime_config = None
    if platform_api_key:
        runtime_config = RuntimeConfig(
            api_key=platform_api_key,
            strategy_id=strategy_id if strategy_id else None,
            environment="test"
        )
        print(f"\n✅ Monitoring enabled (Runtime ID: {runtime_config.runtime_id})")
    
    # Create trader with conservative settings
    trader = LiveTrader(
        strategy=strategy,
        exchange=exchange,
        market=market,
        initial_capital=initial_capital,
        max_position_size=max_position_size,
        check_interval=check_interval,
        stop_loss=stop_loss,
        take_profit=take_profit,
        runtime_config=runtime_config
    )
    
    print("\n✅ LiveTrader initialized")
    print("💡 Starting trading loop...")
    print("   Press Ctrl+C to stop\n")
    
    try:
        trader.start(max_iterations=iterations)
    except KeyboardInterrupt:
        print("\n\n🛑 Trading stopped by user")
    
    # Print final status
    status = trader.get_status()
    print("\n📊 Final Status:")
    print(f"   Trades executed: {status['trades_count']}")
    print(f"   Current position: {status['current_position']}")
    print(f"   Price history: {status['price_history_length']} points")


def print_env_help():
    """Print environment variable help"""
    print("""
================================================================================
ENVIRONMENT VARIABLES FOR LIVE TRADING
================================================================================

必需 (Required):
    EXCHANGE_API_KEY    - 1024 Exchange API Key（用于交易）
                          从 https://1024ex.com -> Settings -> API Keys 获取

可选 - 监控功能 (Optional - Monitoring):
    PLATFORM_API_KEY    - 1024 Quant 平台 API Key（用于记录监控）
                          从 https://1024quant.com -> Settings -> API Keys 获取
    STRATEGY_ID         - 策略 ID（从平台获取）

可选 - 交易配置 (Optional - Trading Config):
    MARKET              - 交易市场（默认 BTC-PERP）
    INITIAL_CAPITAL     - 初始资金（默认 10000）
    MAX_POSITION_SIZE   - 最大仓位比例（默认 0.5）
    CHECK_INTERVAL      - 检查间隔秒数（默认 60）
    STOP_LOSS           - 止损比例（默认 0.05）
    TAKE_PROFIT         - 止盈比例（默认 0.10）
    EXCHANGE_BASE_URL   - 交易所 API 地址
                          生产环境: https://api.1024ex.com (默认)
                          测试网: https://testnet-api.1024ex.com

示例 (Example):
    export EXCHANGE_API_KEY="your_exchange_api_key"
    export PLATFORM_API_KEY="your_platform_api_key"
    export STRATEGY_ID="your_strategy_id"
    export MARKET="BTC-PERP"
    python test_live_trading.py --live

使用测试网 (Use Testnet - Recommended for testing):
    export EXCHANGE_API_KEY="your_testnet_api_key"
    export EXCHANGE_BASE_URL="https://testnet-api.1024ex.com"
    python test_live_trading.py --live
================================================================================
""")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Live Trading Test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_live_trading.py           # Run basic tests
  python test_live_trading.py --mock    # Run with mock exchange (offline)
  python test_live_trading.py --live    # Run actual live trading
  python test_live_trading.py --env     # Show environment variable help
        """
    )
    parser.add_argument('--live', action='store_true', help='Run actual live trading test')
    parser.add_argument('--mock', action='store_true', help='Run with mock exchange only')
    parser.add_argument('--env', action='store_true', help='Show environment variable help')
    parser.add_argument('--market', default='BTC-PERP', help='Market to trade')
    parser.add_argument('--iterations', type=int, default=5, help='Number of iterations')
    args = parser.parse_args()
    
    if args.env:
        print_env_help()
        return
    
    print("=" * 70)
    print("🧪 quant1024 Live Trading Test")
    print("=" * 70)
    
    results = []
    
    if args.mock:
        # Only run mock tests
        results.append(("Strategy Signals", test_strategy_signals()))
        results.append(("Position Calculation", test_position_calculation()))
        results.append(("LiveTrader Mock", test_live_trader_with_mock()))
        results.append(("LiveTrader Monitoring", test_live_trader_with_monitoring()))
        results.append(("Risk Management", test_risk_management()))
    else:
        # Run all tests
        results.append(("Exchange Connection", test_exchange_connection()))
        results.append(("Strategy Signals", test_strategy_signals()))
        results.append(("Position Calculation", test_position_calculation()))
        results.append(("LiveTrader Mock", test_live_trader_with_mock()))
        results.append(("LiveTrader Monitoring", test_live_trader_with_monitoring()))
        results.append(("Advanced Orders", test_advanced_orders()))
        results.append(("Risk Management", test_risk_management()))
    
    # Print results
    print("\n" + "=" * 70)
    print("📊 Test Results")
    print("=" * 70)
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n  Total: {passed}/{len(results)} tests passed")
    
    # Run live trading if requested
    if args.live:
        run_live_trading_test(iterations=args.iterations)
    else:
        print("\n💡 Tips:")
        print("   python test_live_trading.py --mock     Run offline testing")
        print("   python test_live_trading.py --live     Run actual trading (requires EXCHANGE_API_KEY)")
        print("   python test_live_trading.py --env      Show environment variable help")


if __name__ == "__main__":
    main()

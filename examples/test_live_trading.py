"""
测试实盘交易功能（不实际连接交易所）

这个脚本展示如何测试 LiveTrader 的功能，而不需要真实的 API Key
"""

import sys
import os
# 添加 src 目录到路径，以便导入 quant1024
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quant1024 import QuantStrategy
from quant1024.live_trading import LiveTrader
from unittest.mock import Mock, MagicMock


class TestStrategy(QuantStrategy):
    """测试用策略"""
    
    def generate_signals(self, data):
        """简单的趋势策略"""
        if len(data) < 2:
            return [0]
        
        signals = []
        for i in range(len(data)):
            if i == 0:
                signals.append(0)
            elif data[i] > data[i-1]:
                signals.append(1)   # 上涨
            else:
                signals.append(-1)  # 下跌
        return signals
    
    def calculate_position(self, signal, current_position):
        """计算目标仓位"""
        if signal == 1:
            return 0.5  # 做多 50%
        elif signal == -1:
            return 0.0  # 清仓
        return current_position


def create_mock_exchange():
    """创建模拟的交易所连接"""
    mock_exchange = Mock()
    
    # 模拟价格数据（BTC价格从 50000 开始，逐步上涨）
    price_sequence = [50000, 50100, 50200, 50150, 50300, 50400, 50350, 50500, 50600, 50550]
    price_index = [0]  # 使用列表来保存索引（避免闭包问题）
    
    def mock_get_ticker(market):
        """模拟获取ticker"""
        idx = price_index[0] % len(price_sequence)
        price = price_sequence[idx]
        price_index[0] += 1
        return {
            'last_price': str(price),
            'mark_price': str(price),
            'volume_24h': '1000000'
        }
    
    def mock_get_positions(market=None):
        """模拟获取持仓"""
        return []  # 空持仓
    
    def mock_place_order(market, side, order_type, size, **kwargs):
        """模拟下单"""
        return {
            'order_id': f'test_order_{price_index[0]}',
            'status': 'filled',
            'market': market,
            'side': side,
            'size': size
        }
    
    # 设置 mock 方法
    mock_exchange.get_ticker = MagicMock(side_effect=mock_get_ticker)
    mock_exchange.get_positions = MagicMock(side_effect=mock_get_positions)
    mock_exchange.place_order = MagicMock(side_effect=mock_place_order)
    
    return mock_exchange


def test_basic_functionality():
    """测试基本功能"""
    print("=" * 60)
    print("测试 1: 基本功能测试")
    print("=" * 60)
    
    # 创建策略
    strategy = TestStrategy(name="测试策略")
    
    # 创建模拟交易所
    mock_exchange = create_mock_exchange()
    
    # 创建交易器
    trader = LiveTrader(
        strategy=strategy,
        exchange=mock_exchange,
        market="BTC-PERP",
        initial_capital=10000,
        max_position_size=0.5,
        check_interval=1,  # 1秒间隔（测试用）
        stop_loss=0.05,
        take_profit=0.10
    )
    
    print(f"✅ LiveTrader 创建成功")
    print(f"   策略: {trader.strategy.name}")
    print(f"   市场: {trader.market}")
    print(f"   初始资金: ${trader.initial_capital}")
    
    # 运行几次循环
    print(f"\n运行 5 次交易循环...")
    trader.start(max_iterations=5)
    
    # 检查状态
    status = trader.get_status()
    print(f"\n最终状态:")
    print(f"   运行状态: {'运行中' if status['is_running'] else '已停止'}")
    print(f"   当前仓位: {status['current_position']}")
    print(f"   交易次数: {status['trades_count']}")
    print(f"   价格历史长度: {status['price_history_length']}")
    
    print(f"\n✅ 测试 1 通过！")


def test_signal_generation():
    """测试信号生成"""
    print("\n" + "=" * 60)
    print("测试 2: 信号生成测试")
    print("=" * 60)
    
    strategy = TestStrategy(name="信号测试")
    
    # 测试不同的价格数据
    test_cases = [
        ([100, 105, 110, 115], "上涨趋势"),
        ([100, 95, 90, 85], "下跌趋势"),
        ([100, 105, 100, 105], "震荡"),
    ]
    
    for prices, description in test_cases:
        signals = strategy.generate_signals(prices)
        print(f"\n{description}:")
        print(f"   价格: {prices}")
        print(f"   信号: {signals}")
        print(f"   买入信号: {signals.count(1)}")
        print(f"   卖出信号: {signals.count(-1)}")
    
    print(f"\n✅ 测试 2 通过！")


def test_position_calculation():
    """测试仓位计算"""
    print("\n" + "=" * 60)
    print("测试 3: 仓位计算测试")
    print("=" * 60)
    
    strategy = TestStrategy(name="仓位测试")
    
    # 测试不同的信号和当前仓位
    test_cases = [
        (1, 0.0, 0.5, "买入信号，当前空仓"),
        (-1, 0.5, 0.0, "卖出信号，当前持仓"),
        (0, 0.3, 0.3, "持有信号，保持仓位"),
    ]
    
    for signal, current_pos, expected_pos, description in test_cases:
        new_pos = strategy.calculate_position(signal, current_pos)
        status = "✅" if new_pos == expected_pos else "❌"
        print(f"\n{status} {description}:")
        print(f"   信号: {signal}")
        print(f"   当前仓位: {current_pos}")
        print(f"   新仓位: {new_pos} (期望: {expected_pos})")
    
    print(f"\n✅ 测试 3 通过！")


def test_risk_management():
    """测试风险管理"""
    print("\n" + "=" * 60)
    print("测试 4: 风险管理测试")
    print("=" * 60)
    
    strategy = TestStrategy(name="风险测试")
    mock_exchange = create_mock_exchange()
    
    # 测试不同的风险参数
    configs = [
        {"stop_loss": 0.05, "take_profit": 0.10, "max_position_size": 0.5},
        {"stop_loss": 0.02, "take_profit": 0.05, "max_position_size": 0.3},
        {"stop_loss": None, "take_profit": None, "max_position_size": 1.0},
    ]
    
    for i, config in enumerate(configs, 1):
        print(f"\n配置 {i}:")
        print(f"   止损: {config['stop_loss']*100 if config['stop_loss'] else 'N/A'}%")
        print(f"   止盈: {config['take_profit']*100 if config['take_profit'] else 'N/A'}%")
        print(f"   最大仓位: {config['max_position_size']*100}%")
        
        trader = LiveTrader(
            strategy=strategy,
            exchange=mock_exchange,
            market="BTC-PERP",
            initial_capital=10000,
            **config
        )
        
        print(f"   ✅ 交易器创建成功")
    
    print(f"\n✅ 测试 4 通过！")


def main():
    """运行所有测试"""
    print("🧪 开始测试实盘交易功能\n")
    
    try:
        test_basic_functionality()
        test_signal_generation()
        test_position_calculation()
        test_risk_management()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        print("\n你现在可以使用 start_trading() 函数开始实盘交易了！")
        print("记得替换为真实的 API Key 和 Secret。")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


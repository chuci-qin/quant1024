"""
实盘交易示例 - 展示如何使用 start_trading 快速开始交易

这是最简单的实盘交易方式！
"""

from quant1024 import QuantStrategy, start_trading


class SimpleTrendStrategy(QuantStrategy):
    """
    简单趋势策略
    
    策略逻辑：
    - 价格上涨 -> 买入
    - 价格下跌 -> 卖出
    """
    
    def generate_signals(self, data):
        """生成交易信号"""
        if len(data) < 2:
            return [0]
        
        signals = []
        for i in range(len(data)):
            if i == 0:
                signals.append(0)
            elif data[i] > data[i-1]:
                signals.append(1)   # 上涨，买入信号
            else:
                signals.append(-1)  # 下跌，卖出信号
        
        return signals
    
    def calculate_position(self, signal, current_position):
        """计算目标仓位"""
        if signal == 1:
            return 0.5  # 买入信号，持有50%仓位
        elif signal == -1:
            return 0.0  # 卖出信号，清空仓位
        else:
            return current_position  # 保持当前仓位


class MomentumStrategy(QuantStrategy):
    """
    动量策略
    
    策略逻辑：
    - 计算短期动量
    - 动量为正 -> 做多
    - 动量为负 -> 平仓
    """
    
    def __init__(self, name, params=None):
        super().__init__(name, params)
        self.lookback = self.params.get('lookback', 5)
    
    def generate_signals(self, data):
        """生成交易信号"""
        if len(data) < self.lookback + 1:
            return [0] * len(data)
        
        signals = []
        for i in range(len(data)):
            if i < self.lookback:
                signals.append(0)
            else:
                # 计算动量（当前价格 vs N期前价格）
                momentum = (data[i] - data[i - self.lookback]) / data[i - self.lookback]
                
                if momentum > 0.01:  # 上涨超过1%
                    signals.append(1)
                elif momentum < -0.01:  # 下跌超过1%
                    signals.append(-1)
                else:
                    signals.append(0)
        
        return signals
    
    def calculate_position(self, signal, current_position):
        """计算目标仓位"""
        if signal == 1:
            return 0.7  # 动量为正，持有70%仓位
        elif signal == -1:
            return 0.0  # 动量为负，清空仓位
        else:
            return current_position


class MAStrategy(QuantStrategy):
    """
    移动平均线策略
    
    策略逻辑：
    - 短期均线 > 长期均线 -> 做多
    - 短期均线 < 长期均线 -> 平仓
    """
    
    def __init__(self, name, params=None):
        super().__init__(name, params)
        self.short_period = self.params.get('short_period', 5)
        self.long_period = self.params.get('long_period', 20)
    
    def calculate_ma(self, data, period):
        """计算移动平均线"""
        if len(data) < period:
            return None
        return sum(data[-period:]) / period
    
    def generate_signals(self, data):
        """生成交易信号"""
        if len(data) < self.long_period:
            return [0] * len(data)
        
        signals = []
        for i in range(len(data)):
            if i < self.long_period:
                signals.append(0)
            else:
                # 计算短期和长期均线
                short_ma = sum(data[i-self.short_period+1:i+1]) / self.short_period
                long_ma = sum(data[i-self.long_period+1:i+1]) / self.long_period
                
                if short_ma > long_ma:
                    signals.append(1)   # 金叉，买入
                elif short_ma < long_ma:
                    signals.append(-1)  # 死叉，卖出
                else:
                    signals.append(0)
        
        return signals
    
    def calculate_position(self, signal, current_position):
        """计算目标仓位"""
        if signal == 1:
            return 0.8  # 金叉，持有80%仓位
        elif signal == -1:
            return 0.0  # 死叉，清空仓位
        else:
            return current_position


def example_1_simple_trend():
    """
    示例 1：最简单的趋势策略
    
    只需几行代码即可开始交易！
    """
    print("=" * 60)
    print("示例 1：简单趋势策略")
    print("=" * 60)
    
    # 创建策略
    strategy = SimpleTrendStrategy(name="简单趋势")
    
    # 开始交易！就这么简单！
    trader = start_trading(
        strategy=strategy,
        api_key="your_api_key_here",
        api_secret="your_api_secret_here",
        market="BTC-PERP",
        initial_capital=10000,
        max_position_size=0.5,    # 最多用50%仓位
        check_interval=60,         # 每60秒检查一次
        stop_loss=0.05,            # 5%止损
        take_profit=0.10           # 10%止盈
    )
    
    print(f"交易器状态: {trader.get_status()}")


def example_2_momentum():
    """
    示例 2：动量策略
    
    带参数的策略
    """
    print("\n" + "=" * 60)
    print("示例 2：动量策略（带参数）")
    print("=" * 60)
    
    # 创建带参数的策略
    strategy = MomentumStrategy(
        name="动量策略",
        params={
            "lookback": 10  # 回看10个周期
        }
    )
    
    # 开始交易
    trader = start_trading(
        strategy=strategy,
        api_key="your_api_key_here",
        api_secret="your_api_secret_here",
        market="ETH-PERP",
        initial_capital=10000,
        max_position_size=0.7,
        check_interval=120,        # 每2分钟检查一次
        stop_loss=0.03,            # 3%止损
        take_profit=0.08           # 8%止盈
    )


def example_3_ma_strategy():
    """
    示例 3：移动平均线策略
    
    经典的双均线策略
    """
    print("\n" + "=" * 60)
    print("示例 3：移动平均线策略")
    print("=" * 60)
    
    # 创建均线策略
    strategy = MAStrategy(
        name="双均线",
        params={
            "short_period": 5,   # 5周期短期均线
            "long_period": 20    # 20周期长期均线
        }
    )
    
    # 开始交易
    trader = start_trading(
        strategy=strategy,
        api_key="your_api_key_here",
        api_secret="your_api_secret_here",
        market="BTC-PERP",
        initial_capital=20000,
        max_position_size=0.8,
        check_interval=300,        # 每5分钟检查一次
        stop_loss=0.04,            # 4%止损
        take_profit=0.12           # 12%止盈
    )


def example_4_manual_control():
    """
    示例 4：手动控制交易器
    
    如果你想更细粒度地控制交易过程
    """
    print("\n" + "=" * 60)
    print("示例 4：手动控制交易器")
    print("=" * 60)
    
    from quant1024 import Exchange1024ex, LiveTrader
    
    # 1. 创建策略
    strategy = SimpleTrendStrategy(name="手动控制")
    
    # 2. 创建交易所连接
    exchange = Exchange1024ex(
        api_key="your_api_key_here",
        api_secret="your_api_secret_here"
    )
    
    # 3. 创建交易器（不自动启动）
    trader = LiveTrader(
        strategy=strategy,
        exchange=exchange,
        market="BTC-PERP",
        initial_capital=10000,
        max_position_size=0.5,
        check_interval=60
    )
    
    # 4. 手动启动，限制迭代次数（用于测试）
    try:
        trader.start(max_iterations=10)  # 只运行10次循环
    except KeyboardInterrupt:
        print("\n用户中断")
    
    # 5. 查看状态
    print(f"\n最终状态: {trader.get_status()}")


def main():
    """
    主函数 - 运行示例
    
    ⚠️ 注意：请替换为你自己的 API Key 和 Secret！
    """
    print("🚀 quant1024 实盘交易示例")
    print("\n这些示例展示了如何用最简单的方式开始实盘交易。")
    print("你只需要：")
    print("  1. 创建一个策略（继承 QuantStrategy）")
    print("  2. 调用 start_trading() 函数")
    print("  3. 就这样！系统会自动执行交易。")
    print("\n" + "=" * 60)
    
    # 取消注释你想运行的示例：
    
    # example_1_simple_trend()      # 最简单的例子
    # example_2_momentum()          # 动量策略
    # example_3_ma_strategy()       # 均线策略
    # example_4_manual_control()    # 手动控制
    
    print("\n⚠️  提示：请先替换 API Key 和 Secret，然后取消注释相应的示例！")
    print("\n💡 开始你的第一笔交易：")
    print("   1. 编辑 API Key 和 Secret")
    print("   2. 取消注释 example_1_simple_trend()")
    print("   3. 运行这个文件！")


if __name__ == "__main__":
    main()


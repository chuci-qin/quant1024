"""
示例代码：展示如何使用 quant1024 包

这个文件展示了外部软件如何调用 quant1024 包的功能
"""

from quant1024 import QuantStrategy, calculate_returns, calculate_sharpe_ratio


# 示例1: 创建一个简单的均值回归策略
class MeanReversionStrategy(QuantStrategy):
    """均值回归策略"""
    
    def generate_signals(self, data):
        """
        生成交易信号
        当价格偏离均值超过阈值时产生反向信号
        """
        signals = []
        window = self.params.get("window", 10)
        threshold = self.params.get("threshold", 0.02)
        
        for i in range(len(data)):
            if i < window:
                signals.append(0)
                continue
            
            # 计算移动平均
            ma = sum(data[i-window:i]) / window
            
            # 计算偏离度
            deviation = (data[i] - ma) / ma
            
            # 生成信号：价格过高时卖出，价格过低时买入
            if deviation > threshold:
                signals.append(-1)  # 卖出
            elif deviation < -threshold:
                signals.append(1)   # 买入
            else:
                signals.append(0)   # 持有
        
        return signals
    
    def calculate_position(self, signal, current_position):
        """计算仓位大小"""
        max_position = self.params.get("max_position", 1.0)
        
        if signal == 1:
            return max_position  # 满仓
        elif signal == -1:
            return 0.0  # 空仓
        else:
            return current_position  # 保持当前仓位


# 示例2: 创建一个动量策略
class MomentumStrategy(QuantStrategy):
    """动量策略"""
    
    def generate_signals(self, data):
        """
        生成交易信号
        当价格上涨趋势强时买入，下跌趋势强时卖出
        """
        signals = []
        lookback = self.params.get("lookback", 5)
        
        for i in range(len(data)):
            if i < lookback:
                signals.append(0)
                continue
            
            # 计算动量（当前价格相对于N天前的涨跌幅）
            momentum = (data[i] - data[i-lookback]) / data[i-lookback]
            
            # 根据动量生成信号
            if momentum > 0.03:
                signals.append(1)   # 强势上涨，买入
            elif momentum < -0.03:
                signals.append(-1)  # 强势下跌，卖出
            else:
                signals.append(0)   # 震荡，持有
        
        return signals
    
    def calculate_position(self, signal, current_position):
        """计算仓位"""
        if signal == 1:
            return 1.0
        elif signal == -1:
            return 0.0
        else:
            return current_position


def main():
    """主函数：演示如何使用包"""
    
    print("=" * 60)
    print("quant1024 包使用示例")
    print("=" * 60)
    print()
    
    # 准备测试数据（模拟股票价格）
    import random
    random.seed(42)
    
    # 生成模拟价格数据
    prices = [100]
    for i in range(50):
        change = random.uniform(-2, 2)
        new_price = prices[-1] * (1 + change / 100)
        prices.append(new_price)
    
    print(f"测试数据: {len(prices)} 个价格点")
    print(f"价格范围: {min(prices):.2f} - {max(prices):.2f}")
    print()
    
    # 示例1: 使用均值回归策略
    print("-" * 60)
    print("示例1: 均值回归策略")
    print("-" * 60)
    
    mean_reversion = MeanReversionStrategy(
        name="MeanReversion",
        params={
            "window": 10,
            "threshold": 0.02,
            "max_position": 1.0
        }
    )
    
    result1 = mean_reversion.backtest(prices)
    print(f"策略名称: {result1['strategy_name']}")
    print(f"总信号数: {result1['total_signals']}")
    print(f"买入信号: {result1['buy_signals']}")
    print(f"卖出信号: {result1['sell_signals']}")
    print(f"夏普比率: {result1['sharpe_ratio']:.4f}")
    print()
    
    # 示例2: 使用动量策略
    print("-" * 60)
    print("示例2: 动量策略")
    print("-" * 60)
    
    momentum = MomentumStrategy(
        name="Momentum",
        params={
            "lookback": 5,
        }
    )
    
    result2 = momentum.backtest(prices)
    print(f"策略名称: {result2['strategy_name']}")
    print(f"总信号数: {result2['total_signals']}")
    print(f"买入信号: {result2['buy_signals']}")
    print(f"卖出信号: {result2['sell_signals']}")
    print(f"夏普比率: {result2['sharpe_ratio']:.4f}")
    print()
    
    # 示例3: 使用工具函数
    print("-" * 60)
    print("示例3: 使用工具函数")
    print("-" * 60)
    
    returns = calculate_returns(prices)
    print(f"计算得到 {len(returns)} 个收益率")
    print(f"平均收益率: {sum(returns)/len(returns):.4f}")
    print(f"最大收益率: {max(returns):.4f}")
    print(f"最小收益率: {min(returns):.4f}")
    
    sharpe = calculate_sharpe_ratio(returns)
    print(f"夏普比率: {sharpe:.4f}")
    print()
    
    # 示例4: 直接使用策略方法
    print("-" * 60)
    print("示例4: 直接调用策略方法")
    print("-" * 60)
    
    custom_strategy = MeanReversionStrategy(
        name="Custom",
        params={"window": 5, "threshold": 0.01}
    )
    custom_strategy.initialize()
    
    # 直接生成信号
    test_prices = [100, 101, 102, 103, 104, 105, 104, 103, 102, 101]
    signals = custom_strategy.generate_signals(test_prices)
    
    print(f"价格序列: {test_prices}")
    print(f"信号序列: {signals}")
    print("(1=买入, -1=卖出, 0=持有)")
    print()
    
    # 计算仓位变化
    positions = []
    current_pos = 0.0
    for sig in signals:
        new_pos = custom_strategy.calculate_position(sig, current_pos)
        positions.append(new_pos)
        current_pos = new_pos
    
    print(f"仓位序列: {positions}")
    print()
    
    print("=" * 60)
    print("示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()


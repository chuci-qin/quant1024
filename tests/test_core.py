"""
测试核心功能，验证外部调用的正确性
"""

import pytest
from quant1024 import QuantStrategy, calculate_returns, calculate_sharpe_ratio


class SimpleMovingAverageStrategy(QuantStrategy):
    """简单移动平均策略（用于测试）"""
    
    def generate_signals(self, data):
        """生成简单的交易信号"""
        signals = []
        for i in range(len(data)):
            if i < 5:
                signals.append(0)
            else:
                # 简单策略：当前价格高于前5天平均价格时买入
                avg = sum(data[i-5:i]) / 5
                if data[i] > avg:
                    signals.append(1)
                elif data[i] < avg:
                    signals.append(-1)
                else:
                    signals.append(0)
        return signals
    
    def calculate_position(self, signal, current_position):
        """计算仓位"""
        if signal == 1:
            return 1.0  # 满仓
        elif signal == -1:
            return 0.0  # 空仓
        else:
            return float(current_position)  # 保持当前仓位


class TestQuantStrategyImport:
    """测试外部软件能否正确导入和使用"""
    
    def test_can_import_base_class(self):
        """测试能否导入抽象基类"""
        assert QuantStrategy is not None
        assert hasattr(QuantStrategy, 'generate_signals')
        assert hasattr(QuantStrategy, 'calculate_position')
        assert hasattr(QuantStrategy, 'backtest')
    
    def test_can_import_utility_functions(self):
        """测试能否导入工具函数"""
        assert calculate_returns is not None
        assert calculate_sharpe_ratio is not None
    
    def test_can_create_custom_strategy(self):
        """测试外部代码能否继承并创建自定义策略"""
        strategy = SimpleMovingAverageStrategy(
            name="TestStrategy",
            params={"window": 5}
        )
        
        assert strategy.name == "TestStrategy"
        assert strategy.params["window"] == 5
    
    def test_strategy_initialization(self):
        """测试策略初始化"""
        strategy = SimpleMovingAverageStrategy(name="Test")
        assert not strategy._is_initialized
        
        strategy.initialize()
        assert strategy._is_initialized
    
    def test_generate_signals(self):
        """测试信号生成功能"""
        strategy = SimpleMovingAverageStrategy(name="Test")
        test_data = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
        
        signals = strategy.generate_signals(test_data)
        
        assert len(signals) == len(test_data)
        assert all(s in [-1, 0, 1] for s in signals)
    
    def test_calculate_position(self):
        """测试仓位计算"""
        strategy = SimpleMovingAverageStrategy(name="Test")
        
        # 测试买入信号
        new_position = strategy.calculate_position(1, 0.0)
        assert new_position == 1.0
        
        # 测试卖出信号
        new_position = strategy.calculate_position(-1, 1.0)
        assert new_position == 0.0
        
        # 测试持有信号
        new_position = strategy.calculate_position(0, 0.5)
        assert new_position == 0.5


class TestUtilityFunctions:
    """测试工具函数"""
    
    def test_calculate_returns_basic(self):
        """测试收益率计算基本功能"""
        prices = [100, 110, 105, 115]
        returns = calculate_returns(prices)
        
        assert len(returns) == 3
        assert abs(returns[0] - 0.1) < 0.001  # (110-100)/100
        assert abs(returns[1] - (-0.0454545)) < 0.001  # (105-110)/110
    
    def test_calculate_returns_empty(self):
        """测试空数据"""
        returns = calculate_returns([])
        assert returns == []
        
        returns = calculate_returns([100])
        assert returns == []
    
    def test_calculate_returns_with_zero(self):
        """测试包含零的价格数据"""
        prices = [0, 100, 110]
        returns = calculate_returns(prices)
        
        assert returns[0] == 0.0  # 除数为0时返回0
        assert abs(returns[1] - 0.1) < 0.001
    
    def test_calculate_sharpe_ratio_basic(self):
        """测试夏普比率计算"""
        returns = [0.01, 0.02, -0.01, 0.03, 0.01]
        sharpe = calculate_sharpe_ratio(returns)
        
        assert isinstance(sharpe, float)
        assert sharpe != 0.0
    
    def test_calculate_sharpe_ratio_empty(self):
        """测试空收益率"""
        sharpe = calculate_sharpe_ratio([])
        assert sharpe == 0.0
    
    def test_calculate_sharpe_ratio_single_value(self):
        """测试单个收益率值"""
        sharpe = calculate_sharpe_ratio([0.01])
        assert sharpe == 0.0
    
    def test_calculate_sharpe_ratio_zero_std(self):
        """测试标准差为0的情况"""
        returns = [0.01, 0.01, 0.01, 0.01]
        sharpe = calculate_sharpe_ratio(returns)
        assert sharpe == 0.0


class TestBacktest:
    """测试回测功能"""
    
    def test_backtest_execution(self):
        """测试完整的回测流程"""
        strategy = SimpleMovingAverageStrategy(
            name="BacktestStrategy",
            params={"window": 5}
        )
        
        # 模拟价格数据
        test_data = [100 + i + (i % 3) for i in range(20)]
        
        result = strategy.backtest(test_data)
        
        assert "strategy_name" in result
        assert result["strategy_name"] == "BacktestStrategy"
        assert "total_signals" in result
        assert "buy_signals" in result
        assert "sell_signals" in result
        assert "sharpe_ratio" in result
        assert result["total_signals"] == len(test_data)
    
    def test_backtest_auto_initialize(self):
        """测试回测会自动初始化策略"""
        strategy = SimpleMovingAverageStrategy(name="Test")
        assert not strategy._is_initialized
        
        test_data = [100, 101, 102, 103, 104, 105]
        strategy.backtest(test_data)
        
        assert strategy._is_initialized


class TestExternalPackageIntegration:
    """测试外部软件集成场景"""
    
    def test_typical_usage_workflow(self):
        """测试典型的使用流程"""
        # 1. 外部软件导入包
        from quant1024 import QuantStrategy, calculate_returns, calculate_sharpe_ratio
        
        # 2. 创建自定义策略
        class CustomStrategy(QuantStrategy):
            def generate_signals(self, data):
                return [1 if i % 2 == 0 else -1 for i in range(len(data))]
            
            def calculate_position(self, signal, current_position):
                return signal if signal > 0 else 0
        
        # 3. 初始化策略
        strategy = CustomStrategy(name="Custom", params={"test": True})
        strategy.initialize()
        
        # 4. 运行回测
        data = [100 + i for i in range(10)]
        result = strategy.backtest(data)
        
        # 5. 验证结果
        assert result is not None
        assert isinstance(result, dict)
        assert result["strategy_name"] == "Custom"
    
    def test_can_use_without_backtest(self):
        """测试可以直接使用策略功能而不调用回测"""
        strategy = SimpleMovingAverageStrategy(name="Direct")
        strategy.initialize()
        
        # 直接调用方法
        data = [100, 101, 102, 103, 104, 105, 106]
        signals = strategy.generate_signals(data)
        
        assert len(signals) > 0
        
        position = strategy.calculate_position(signals[0], 0)
        assert isinstance(position, float)
    
    def test_multiple_strategies_can_coexist(self):
        """测试可以同时创建多个策略实例"""
        strategy1 = SimpleMovingAverageStrategy(name="Strategy1")
        strategy2 = SimpleMovingAverageStrategy(name="Strategy2")
        
        assert strategy1.name != strategy2.name
        assert strategy1 is not strategy2
        
        # 两个策略可以独立运行
        data = [100, 101, 102, 103, 104, 105]
        result1 = strategy1.backtest(data)
        result2 = strategy2.backtest(data)
        
        assert result1["strategy_name"] == "Strategy1"
        assert result2["strategy_name"] == "Strategy2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


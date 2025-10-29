# 快速开始指南

## 安装

```bash
# 使用 uv 安装（推荐）
uv pip install -e .

# 或使用 pip
pip install -e .

# 安装开发依赖
uv pip install -e ".[dev]"
```

## 5分钟上手

### 1. 创建你的第一个策略

```python
from quant1024 import QuantStrategy

class MyFirstStrategy(QuantStrategy):
    def generate_signals(self, data):
        """生成交易信号"""
        signals = []
        for i in range(len(data)):
            if i == 0:
                signals.append(0)
            elif data[i] > data[i-1]:
                signals.append(1)   # 买入
            else:
                signals.append(-1)  # 卖出
        return signals
    
    def calculate_position(self, signal, current_position):
        """计算仓位"""
        if signal == 1:
            return 1.0
        elif signal == -1:
            return 0.0
        else:
            return current_position

# 创建策略
strategy = MyFirstStrategy(name="MyStrategy")

# 运行回测
prices = [100, 102, 101, 105, 103, 108]
result = strategy.backtest(prices)
print(result)
```

### 2. 使用工具函数

```python
from quant1024 import calculate_returns, calculate_sharpe_ratio

# 计算收益率
prices = [100, 110, 105, 115]
returns = calculate_returns(prices)

# 计算夏普比率
sharpe = calculate_sharpe_ratio(returns)
print(f"夏普比率: {sharpe}")
```

## 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行示例代码
python examples/usage_example.py
```

## 外部调用验证

本项目已通过完整的外部调用测试，包括：
- ✅ 包导入测试
- ✅ 抽象类继承测试
- ✅ 策略回测测试
- ✅ 工具函数测试
- ✅ 多策略并行测试

查看 `tests/test_core.py` 了解详细的测试用例。

## 下一步

- 查看 `examples/usage_example.py` 了解更多高级用法
- 阅读 `README.md` 了解完整的API文档
- 创建自己的策略并进行回测

## 常见问题

**Q: 如何调试我的策略？**

A: 在策略的 `generate_signals` 或 `calculate_position` 方法中添加打印语句。

**Q: 如何添加自定义参数？**

A: 在初始化策略时传入 `params` 字典，然后在方法中使用 `self.params.get('key', default)`。

**Q: 策略必须实现哪些方法？**

A: 必须实现两个抽象方法：`generate_signals` 和 `calculate_position`。


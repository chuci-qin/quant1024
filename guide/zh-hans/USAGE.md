# 使用指南

本文档详细说明如何在不同场景下使用 `quant1024` 包。

## 💡 基本使用

### 创建自定义策略

```python
from quant1024 import QuantStrategy

class MyStrategy(QuantStrategy):
    """自定义交易策略"""
    
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
            return 1.0  # 满仓
        elif signal == -1:
            return 0.0  # 空仓
        else:
            return current_position

# 使用策略
strategy = MyStrategy(name="Simple")
result = strategy.backtest([100, 102, 101, 105, 103])
print(result)
```

---

## 📊 使用工具函数

### 计算收益率

```python
from quant1024 import calculate_returns

prices = [100, 110, 105, 115]
returns = calculate_returns(prices)
print(returns)  # [0.1, -0.0454..., 0.0952...]
```

### 计算夏普比率

```python
from quant1024 import calculate_sharpe_ratio

returns = [0.1, -0.05, 0.08, 0.12]
sharpe = calculate_sharpe_ratio(returns)
print(f"夏普比率: {sharpe}")
```

---

## 🎯 高级用法

### 使用策略参数

```python
class ParameterizedStrategy(QuantStrategy):
    def __init__(self, name, params=None):
        super().__init__(name, params)
        self.threshold = self.params.get('threshold', 0.02)
    
    def generate_signals(self, data):
        signals = []
        for i in range(len(data)):
            if i == 0:
                signals.append(0)
            else:
                change = (data[i] - data[i-1]) / data[i-1]
                if change > self.threshold:
                    signals.append(1)
                elif change < -self.threshold:
                    signals.append(-1)
                else:
                    signals.append(0)
        return signals
    
    def calculate_position(self, signal, current_position):
        if signal == 1:
            return 1.0
        elif signal == -1:
            return 0.0
        else:
            return current_position

# 使用自定义参数
strategy = ParameterizedStrategy(
    name="Threshold Strategy",
    params={"threshold": 0.03}
)
```

### 自定义初始化逻辑

```python
class InitializedStrategy(QuantStrategy):
    def initialize(self):
        """在回测前进行初始化"""
        self.trade_count = 0
        self.last_signal = 0
        print(f"策略 {self.name} 初始化完成")
    
    def generate_signals(self, data):
        # 你的信号生成逻辑
        return [1, -1, 0, 1]
    
    def calculate_position(self, signal, current_position):
        if signal != self.last_signal:
            self.trade_count += 1
        self.last_signal = signal
        return 1.0 if signal == 1 else 0.0
```

---

## 📦 在其他项目中集成

### 示例 1：简单脚本

创建文件 `my_strategy.py`：

```python
from quant1024 import QuantStrategy

class SimpleStrategy(QuantStrategy):
    def generate_signals(self, data):
        return [1 if data[i] > data[i-1] else -1 
                for i in range(1, len(data))]
    
    def calculate_position(self, signal, current_position):
        return 1.0 if signal == 1 else 0.0

if __name__ == "__main__":
    strategy = SimpleStrategy(name="Simple")
    prices = [100, 102, 101, 105, 103, 108]
    result = strategy.backtest(prices)
    print(result)
```

运行：
```bash
python my_strategy.py
```

---

### 示例 2：完整项目结构

```
my_project/
├── requirements.txt
├── strategies/
│   ├── __init__.py
│   ├── momentum.py
│   └── mean_reversion.py
├── backtest.py
└── README.md
```

**requirements.txt**：
```txt
quant1024>=0.1.0
numpy>=1.20.0
pandas>=1.3.0
```

**strategies/momentum.py**：
```python
from quant1024 import QuantStrategy

class MomentumStrategy(QuantStrategy):
    def generate_signals(self, data):
        # 你的动量策略逻辑
        pass
    
    def calculate_position(self, signal, current_position):
        # 你的仓位计算逻辑
        pass
```

**backtest.py**：
```python
from strategies.momentum import MomentumStrategy

def main():
    strategy = MomentumStrategy(name="Momentum")
    # 加载数据并运行回测
    prices = load_historical_data()
    result = strategy.backtest(prices)
    print(result)

if __name__ == "__main__":
    main()
```

---

## 🧪 测试你的策略

### 单元测试示例

```python
import pytest
from quant1024 import QuantStrategy

class TestStrategy(QuantStrategy):
    def generate_signals(self, data):
        return [1] * len(data)
    
    def calculate_position(self, signal, current_position):
        return 1.0

def test_strategy_initialization():
    strategy = TestStrategy(name="Test")
    assert strategy.name == "Test"

def test_strategy_backtest():
    strategy = TestStrategy(name="Test")
    result = strategy.backtest([100, 101, 102])
    assert "strategy_name" in result
    assert result["strategy_name"] == "Test"
```

运行测试：
```bash
pytest test_my_strategy.py -v
```

---

## 📊 实战示例

### RSI 策略

```python
from quant1024 import QuantStrategy

class RSIStrategy(QuantStrategy):
    def __init__(self, name, params=None):
        super().__init__(name, params)
        self.period = self.params.get('period', 14)
        self.oversold = self.params.get('oversold', 30)
        self.overbought = self.params.get('overbought', 70)
    
    def calculate_rsi(self, prices):
        """计算 RSI 指标"""
        if len(prices) < self.period + 1:
            return [50] * len(prices)
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains[:self.period]) / self.period
        avg_loss = sum(losses[:self.period]) / self.period
        
        rsi_values = [50]  # 初始值
        
        for i in range(self.period, len(gains)):
            avg_gain = (avg_gain * (self.period - 1) + gains[i]) / self.period
            avg_loss = (avg_loss * (self.period - 1) + losses[i]) / self.period
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(rsi)
        
        return rsi_values
    
    def generate_signals(self, data):
        rsi_values = self.calculate_rsi(data)
        signals = []
        
        for rsi in rsi_values:
            if rsi < self.oversold:
                signals.append(1)   # 超卖，买入
            elif rsi > self.overbought:
                signals.append(-1)  # 超买，卖出
            else:
                signals.append(0)   # 持有
        
        return signals
    
    def calculate_position(self, signal, current_position):
        if signal == 1:
            return 1.0
        elif signal == -1:
            return 0.0
        else:
            return current_position

# 使用 RSI 策略
strategy = RSIStrategy(
    name="RSI Strategy",
    params={"period": 14, "oversold": 30, "overbought": 70}
)
```

---

## 🔧 调试技巧

### 添加日志

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DebuggableStrategy(QuantStrategy):
    def generate_signals(self, data):
        logger.debug(f"生成信号，数据长度: {len(data)}")
        signals = []
        for i, price in enumerate(data):
            signal = 1 if i > 0 and price > data[i-1] else -1
            logger.debug(f"第 {i} 个价格 {price}, 信号: {signal}")
            signals.append(signal)
        return signals
    
    def calculate_position(self, signal, current_position):
        new_position = 1.0 if signal == 1 else 0.0
        logger.debug(f"信号 {signal}, 当前仓位 {current_position}, 新仓位 {new_position}")
        return new_position
```

---

## 📚 相关文档

- [快速开始](QUICKSTART.md) - 5分钟上手
- [安装指南](INSTALLATION.md) - 安装说明
- [发布指南](PUBLISHING.md) - 如何发布
- [API 文档](../../README.md) - 完整 API 参考


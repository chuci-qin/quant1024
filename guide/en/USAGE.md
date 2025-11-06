# Usage Guide

This document provides detailed instructions on how to use the `quant1024` package in different scenarios.

## 💡 Basic Usage

### Create Custom Strategy

```python
from quant1024 import QuantStrategy

class MyStrategy(QuantStrategy):
    """Custom trading strategy"""
    
    def generate_signals(self, data):
        """Generate trading signals"""
        signals = []
        for i in range(len(data)):
            if i == 0:
                signals.append(0)
            elif data[i] > data[i-1]:
                signals.append(1)   # Buy
            else:
                signals.append(-1)  # Sell
        return signals
    
    def calculate_position(self, signal, current_position):
        """Calculate position size"""
        if signal == 1:
            return 1.0  # Full position
        elif signal == -1:
            return 0.0  # No position
        else:
            return current_position

# Use strategy
strategy = MyStrategy(name="Simple")
result = strategy.backtest([100, 102, 101, 105, 103])
print(result)
```

---

## 📊 Using Utility Functions

### Calculate Returns

```python
from quant1024 import calculate_returns

prices = [100, 110, 105, 115]
returns = calculate_returns(prices)
print(returns)  # [0.1, -0.0454..., 0.0952...]
```

### Calculate Sharpe Ratio

```python
from quant1024 import calculate_sharpe_ratio

returns = [0.1, -0.05, 0.08, 0.12]
sharpe = calculate_sharpe_ratio(returns)
print(f"Sharpe Ratio: {sharpe}")
```

---

## 🎯 Advanced Usage

### Using Strategy Parameters

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

# Use custom parameters
strategy = ParameterizedStrategy(
    name="Threshold Strategy",
    params={"threshold": 0.03}
)
```

### Custom Initialization Logic

```python
class InitializedStrategy(QuantStrategy):
    def initialize(self):
        """Initialize before backtest"""
        self.trade_count = 0
        self.last_signal = 0
        print(f"Strategy {self.name} initialized")
    
    def generate_signals(self, data):
        # Your signal generation logic
        return [1, -1, 0, 1]
    
    def calculate_position(self, signal, current_position):
        if signal != self.last_signal:
            self.trade_count += 1
        self.last_signal = signal
        return 1.0 if signal == 1 else 0.0
```

---

## 📦 Integration in Other Projects

### Example 1: Simple Script

Create file `my_strategy.py`:

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

Run:
```bash
python my_strategy.py
```

---

### Example 2: Complete Project Structure

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

**requirements.txt**:
```txt
quant1024>=0.1.0
numpy>=1.20.0
pandas>=1.3.0
```

**strategies/momentum.py**:
```python
from quant1024 import QuantStrategy

class MomentumStrategy(QuantStrategy):
    def generate_signals(self, data):
        # Your momentum strategy logic
        pass
    
    def calculate_position(self, signal, current_position):
        # Your position calculation logic
        pass
```

**backtest.py**:
```python
from strategies.momentum import MomentumStrategy

def main():
    strategy = MomentumStrategy(name="Momentum")
    # Load data and run backtest
    prices = load_historical_data()
    result = strategy.backtest(prices)
    print(result)

if __name__ == "__main__":
    main()
```

---

## 🧪 Testing Your Strategy

### Unit Test Example

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

Run tests:
```bash
pytest test_my_strategy.py -v
```

---

## 📊 Real-World Example

### RSI Strategy

```python
from quant1024 import QuantStrategy

class RSIStrategy(QuantStrategy):
    def __init__(self, name, params=None):
        super().__init__(name, params)
        self.period = self.params.get('period', 14)
        self.oversold = self.params.get('oversold', 30)
        self.overbought = self.params.get('overbought', 70)
    
    def calculate_rsi(self, prices):
        """Calculate RSI indicator"""
        if len(prices) < self.period + 1:
            return [50] * len(prices)
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains[:self.period]) / self.period
        avg_loss = sum(losses[:self.period]) / self.period
        
        rsi_values = [50]  # Initial value
        
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
                signals.append(1)   # Oversold, buy
            elif rsi > self.overbought:
                signals.append(-1)  # Overbought, sell
            else:
                signals.append(0)   # Hold
        
        return signals
    
    def calculate_position(self, signal, current_position):
        if signal == 1:
            return 1.0
        elif signal == -1:
            return 0.0
        else:
            return current_position

# Use RSI strategy
strategy = RSIStrategy(
    name="RSI Strategy",
    params={"period": 14, "oversold": 30, "overbought": 70}
)
```

---

## 🔧 Debugging Tips

### Add Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DebuggableStrategy(QuantStrategy):
    def generate_signals(self, data):
        logger.debug(f"Generating signals, data length: {len(data)}")
        signals = []
        for i, price in enumerate(data):
            signal = 1 if i > 0 and price > data[i-1] else -1
            logger.debug(f"Price {i}: {price}, Signal: {signal}")
            signals.append(signal)
        return signals
    
    def calculate_position(self, signal, current_position):
        new_position = 1.0 if signal == 1 else 0.0
        logger.debug(f"Signal {signal}, Current position {current_position}, New position {new_position}")
        return new_position
```

---

## 📚 Related Documentation

- [Quick Start](QUICKSTART.md) - Get started in 5 minutes
- [Installation Guide](INSTALLATION.md) - Installation instructions
- [Publishing Guide](PUBLISHING.md) - How to publish
- [API Documentation](../../README.md) - Complete API reference


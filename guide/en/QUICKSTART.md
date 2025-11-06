# Quick Start Guide

## Installation

```bash
# Install using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .

# Install development dependencies
uv pip install -e ".[dev]"
```

## Get Started in 5 Minutes

### 1. Create Your First Strategy

```python
from quant1024 import QuantStrategy

class MyFirstStrategy(QuantStrategy):
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
            return 1.0
        elif signal == -1:
            return 0.0
        else:
            return current_position

# Create strategy
strategy = MyFirstStrategy(name="MyStrategy")

# Run backtest
prices = [100, 102, 101, 105, 103, 108]
result = strategy.backtest(prices)
print(result)
```

### 2. Use Utility Functions

```python
from quant1024 import calculate_returns, calculate_sharpe_ratio

# Calculate returns
prices = [100, 110, 105, 115]
returns = calculate_returns(prices)

# Calculate Sharpe ratio
sharpe = calculate_sharpe_ratio(returns)
print(f"Sharpe Ratio: {sharpe}")
```

## Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run example code
python examples/usage_example.py
```

## External Call Validation

This project has passed comprehensive external call tests, including:
- ✅ Package import tests
- ✅ Abstract class inheritance tests
- ✅ Strategy backtest tests
- ✅ Utility function tests
- ✅ Multi-strategy parallel tests

See `tests/test_core.py` for detailed test cases.

## Next Steps

- Check `examples/usage_example.py` for more advanced usage
- Read `README.md` for complete API documentation
- Create your own strategies and run backtests

## FAQ

**Q: How to debug my strategy?**

A: Add print statements in your strategy's `generate_signals` or `calculate_position` methods.

**Q: How to add custom parameters?**

A: Pass a `params` dictionary when initializing the strategy, then use `self.params.get('key', default)` in your methods.

**Q: What methods must be implemented?**

A: You must implement two abstract methods: `generate_signals` and `calculate_position`.


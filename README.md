# quant1024

A quantitative trading toolkit providing an abstract strategy framework and common quantitative analysis functions.

**Documentation**: [English](guide/en/) | [中文](guide/zh-hans/) | [中文文档](README_zh.md)

## Features

- 🎯 **Abstract Strategy Base Class**: Provides `QuantStrategy` abstract base class for rapid custom strategy development
- 📊 **Quantitative Tool Functions**: Built-in indicators including returns calculation, Sharpe ratio, and more
- 🧪 **Comprehensive Testing**: Full test coverage ensuring stable and reliable external API calls
- 🚀 **Easy to Extend**: Clear interface design for easy inheritance and customization

## Installation

### Method 1: Install from PyPI (after package is published)

```bash
pip install quant1024
```

### Method 2: Install from Git Repository

```bash
pip install git+https://github.com/yourusername/quant1024.git
```

### Method 3: Install from Local Source

```bash
# After cloning or downloading the repository
cd quant1024

# Development mode installation (recommended for development)
pip install -e .

# Or normal installation
pip install .
```

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

## Quick Start

### 1. Create a Custom Strategy

```python
from quant1024 import QuantStrategy

class MyStrategy(QuantStrategy):
    """Custom trading strategy"""
    
    def generate_signals(self, data):
        """Generate trading signals"""
        signals = []
        for i, price in enumerate(data):
            if i == 0:
                signals.append(0)
            elif price > data[i-1]:
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
```

### 2. Run Backtest

```python
# Create strategy instance
strategy = MyStrategy(
    name="MyFirstStrategy",
    params={"param1": "value1"}
)

# Prepare price data
prices = [100, 102, 101, 105, 103, 108, 110]

# Run backtest
result = strategy.backtest(prices)

print(result)
# Output:
# {
#     'strategy_name': 'MyFirstStrategy',
#     'total_signals': 7,
#     'buy_signals': 4,
#     'sell_signals': 2,
#     'sharpe_ratio': 0.1234
# }
```

### 3. Use Utility Functions

```python
from quant1024 import calculate_returns, calculate_sharpe_ratio

# Calculate returns
prices = [100, 110, 105, 115]
returns = calculate_returns(prices)
print(returns)  # [0.1, -0.0454..., 0.0952...]

# Calculate Sharpe ratio
sharpe = calculate_sharpe_ratio(returns)
print(sharpe)  # 1.2345
```

## API Documentation

### `QuantStrategy` Abstract Base Class

All strategies must inherit from this base class and implement the following methods:

#### Methods

- `__init__(name: str, params: Optional[Dict[str, Any]] = None)`
  - Initialize the strategy
  - `name`: Strategy name
  - `params`: Strategy parameters dictionary (optional)

- `initialize() -> None`
  - Initialize the strategy (called automatically before backtesting)

- `generate_signals(data: List[float]) -> List[int]` **[Abstract Method]**
  - Generate trading signals
  - `data`: List of price data
  - Returns: List of signals (1=buy, -1=sell, 0=hold)

- `calculate_position(signal: int, current_position: float) -> float` **[Abstract Method]**
  - Calculate position size based on signal
  - `signal`: Trading signal
  - `current_position`: Current position size
  - Returns: New position size

- `backtest(data: List[float]) -> Dict[str, Any]`
  - Run backtest
  - `data`: Historical price data
  - Returns: Backtest results dictionary

### Utility Functions

- `calculate_returns(prices: List[float]) -> List[float]`
  - Calculate returns series
  - `prices`: Price series
  - Returns: Returns series

- `calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.0) -> float`
  - Calculate Sharpe ratio
  - `returns`: Returns series
  - `risk_free_rate`: Risk-free rate (default 0)
  - Returns: Sharpe ratio value

## Documentation

For detailed guides and tutorials, please visit:

- 📖 [Quick Start Guide](guide/en/QUICKSTART.md) - Get started in 5 minutes
- 📦 [Installation Guide](guide/en/INSTALLATION.md) - Detailed installation instructions
- 💡 [Usage Guide](guide/en/USAGE.md) - Comprehensive usage examples
- 🚀 [Publishing Guide](guide/en/PUBLISHING.md) - How to publish to PyPI

中文用户请访问 [中文指南](guide/zh-hans/)

## Examples

See `examples/usage_example.py` for more detailed examples, including:

- Mean reversion strategy
- Momentum strategy
- Utility function usage
- Direct strategy method calls

Run the example:

```bash
cd examples
python usage_example.py
```

## Development

### Install Development Dependencies

```bash
uv pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/ -v
```

### Test Coverage

```bash
pytest tests/ --cov=quant1024 --cov-report=html
```

## Project Structure

```
quant1024/
├── src/quant1024/          # Source code
│   ├── __init__.py         # Package initialization
│   └── core.py             # Core functionality
├── tests/                  # Test code
│   ├── __init__.py
│   └── test_core.py        # Core functionality tests
├── examples/               # Example code
│   └── usage_example.py    # Usage examples
├── guide/                  # Documentation guides
│   ├── en/                 # English guides
│   └── zh-hans/            # Chinese guides
├── pyproject.toml          # Project configuration
├── README.md               # Project documentation (English)
├── README_zh.md            # Project documentation (Chinese)
└── LICENSE                 # License
```

## Testing

This project includes comprehensive test cases to ensure external software can properly call the API:

- ✅ **Import Tests**: Verify all public APIs can be correctly imported
- ✅ **Inheritance Tests**: Verify external code can inherit from the abstract base class
- ✅ **Functionality Tests**: Verify all methods work correctly
- ✅ **Integration Tests**: Verify typical use cases
- ✅ **Edge Case Tests**: Verify exception handling

Run tests to ensure everything works:

```bash
pytest tests/ -v
```

## License

See the LICENSE file for license information.

## Contributing

Issues and Pull Requests are welcome!

## Contact

For questions or suggestions, please submit an Issue.

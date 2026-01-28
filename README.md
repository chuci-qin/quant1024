# quant1024

[![PyPI version](https://badge.fury.io/py/quant1024.svg)](https://pypi.org/project/quant1024/)
[![Python versions](https://img.shields.io/pypi/pyversions/quant1024.svg)](https://pypi.org/project/quant1024/)
[![License](https://img.shields.io/pypi/l/quant1024.svg)](https://github.com/chuci-qin/quant1024/blob/main/LICENSE)
[![Downloads](https://pepy.tech/badge/quant1024)](https://pepy.tech/project/quant1024)

**A cross-exchange quantitative trading toolkit for structured data retrieval, real-time trading, and cloud backtesting**

跨券商跨交易所的开源量化交易工具包，支持结构化数据获取、快速连接多个交易所、实时交易和 QuantConnect 云端回测。

**Documentation**: [English](guide/en/) | [中文](guide/zh-hans/) | [中文文档](README_zh.md)

## Features

- 🌐 **Multi-Exchange Support**: Unified interface for multiple exchanges
  - ✅ 1024 Exchange (Decentralized Perpetuals)
  - 🔄 Binance (Crypto Exchange)
  - 🔄 IBKR (Interactive Brokers - Traditional Finance)
  - 🔄 More exchanges coming...

- 📊 **Structured Data Retrieval**: Multi-source aggregation and standardized format
  - **Multi-source aggregation**: Combine data from multiple exchanges/brokers
  - **Historical time series**: Get historical data for any trading pair
    * Klines (1m, 5m, 1h, 1d, etc.)
    * Trade history
    * Order history
    * Funding rate history
  - **Multiple trading pairs**: Perpetuals, Spot, Futures, Options
  - **Cross-exchange data**: Compare and arbitrage across exchanges
  - **Standardized format**: Same data structure across all sources

- 🔌 **Real-time Data Push**: Live data via WebSocket and Webhook
  - WebSocket for price updates
  - Webhook callbacks for order events
  - Continuous live trading data

- 🚀 **Quick Connection**: One-line code to connect any exchange
  - Auto-handled authentication
  - Unified API interface
  - Easy to switch between exchanges

- 🧪 **QuantConnect Cloud Backtesting**: Full QuantConnect REST API integration
  - Cloud-based strategy backtesting
  - Complete result processing and export
  - Support for stocks, crypto, futures, and options

## Installation

### Method 1: Install from PyPI

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

## Public API

quant1024 exposes two main public APIs:

1. **`Exchange1024ex`** - 1024 Exchange connector for live trading
2. **`qc`** - QuantConnect API infrastructure for cloud backtesting

## Quick Start

### 1. Connect to 1024 Exchange

```python
from quant1024 import Exchange1024ex

# Create exchange instance
exchange = Exchange1024ex(
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# Get market data
markets = exchange.perp.get_markets()
print(markets)

# Get account info
account = exchange.account.get_account_info()
print(account)

# Place an order
order = exchange.perp.place_order(
    market="ETH-PERP",
    side="buy",
    size=0.1,
    price=3000.0
)
print(order)
```

### 2. QuantConnect Cloud Backtesting

```python
from quant1024 import qc

# Quick backtest run
qc.run_backtest(
    user_id="your_user_id",
    api_token="your_api_token",
    strategy_file="my_strategy.py",
    export_json=True,  # Export full results
)
```

### 3. Advanced QuantConnect API Usage

```python
from quant1024 import qc

# Create credentials and API client
credentials = qc.QCCredentials(
    user_id="your_user_id",
    api_token="your_api_token"
)
api = qc.QuantConnectAPI(credentials)

# Authenticate
api.authenticate()

# Create project
project_id = api.create_project("MyStrategy")

# Upload strategy code
with open("my_strategy.py") as f:
    api.create_file(project_id, "main.py", f.read())

# Compile
compile_id = api.compile(project_id)
api.wait_for_compile(project_id, compile_id)

# Run backtest
backtest_id = api.create_backtest(project_id, compile_id, "test_run")
result = api.wait_for_backtest(project_id, backtest_id)

# Get result summary
summary = qc.BacktestResultProcessor.get_summary(result)
print(summary)
# Output:
# {
#     '总收益率': '15.5%',
#     '年化收益率': '31.2%',
#     '夏普比率': '1.85',
#     '最大回撤': '-8.2%',
#     ...
# }
```

## API Documentation

### Exchange1024ex

The main exchange connector for 1024 Exchange:

```python
from quant1024 import Exchange1024ex

exchange = Exchange1024ex(api_key="xxx", api_secret="xxx")

# Modules available:
exchange.perp       # Perpetual futures trading
exchange.spot       # Spot trading
exchange.account    # Account management
exchange.prediction # Prediction markets
exchange.championship # Championship trading
```

### qc Module

QuantConnect API infrastructure for cloud backtesting:

#### `qc.run_backtest()`
Quick function to run a complete backtest:

```python
qc.run_backtest(
    user_id: str,           # QuantConnect User ID
    api_token: str,         # QuantConnect API Token
    strategy_file: str,     # Path to strategy file
    project_name: str = None,  # Optional project name
    export_json: bool = False  # Export results to JSON
) -> Dict
```

#### `qc.QCCredentials`
Data class for API credentials:

```python
credentials = qc.QCCredentials(
    user_id="your_user_id",
    api_token="your_api_token"
)
```

#### `qc.QuantConnectAPI`
Full API client with methods:

- `authenticate()` - Verify authentication
- `create_project(name)` - Create a new project
- `create_file(project_id, name, content)` - Upload file to project
- `compile(project_id)` - Compile project
- `wait_for_compile(project_id, compile_id)` - Wait for compilation
- `create_backtest(project_id, compile_id, name)` - Start backtest
- `wait_for_backtest(project_id, backtest_id)` - Wait for backtest completion
- `get_backtest_orders(project_id, backtest_id)` - Get order records
- `get_full_backtest_with_charts(project_id, backtest_id)` - Get full results with charts

#### `qc.BacktestResultProcessor`
Result processing utilities:

- `get_summary(backtest)` - Extract key metrics
- `get_full_data(backtest)` - Get complete data for custom dashboards
- `export_chart_data(backtest)` - Export chart data for frontend
- `parse_equity_curve(charts_data)` - Parse equity curve data
- `parse_drawdown_curve(charts_data)` - Parse drawdown data
- `export_to_json(...)` - Export full data to JSON file

## Examples

### Example Directory Structure

```
examples/
├── lean-engine/              # QuantConnect strategy examples
│   ├── main.py               # Mag 7 Alpha + Beta strategy
│   ├── btc_futures_arbitrage.py  # BTC futures arbitrage
│   ├── backtest.py           # Backtest runner
│   └── README.md             # Detailed usage guide
├── sdk-examples/             # SDK usage examples
│   ├── sdk_usage_example.py  # Basic SDK usage
│   ├── dual_ma_backtest.py   # Dual MA strategy backtest
│   └── price_trigger_buy.py  # Price trigger trading
├── live_trading_example.py   # Live trading example
├── example_1024ex.py         # 1024 Exchange example
└── usage_example.py          # General usage examples
```

### Run Lean Engine Examples

```bash
cd examples/lean-engine

# Set credentials (or modify backtest.py)
export QC_USER_ID="your_user_id"
export QC_API_TOKEN="your_api_token"

# Run backtest
python backtest.py
```

### Strategy Examples

#### Mag 7 Alpha + Beta Market Neutral Strategy

Long Mag 7 tech stocks + Short QQQ for market hedging:

```python
# See examples/lean-engine/main.py
from AlgorithmImports import *

class Mag7AlphaBetaStrategy(QCAlgorithm):
    def initialize(self):
        self.set_start_date(2025, 7, 1)
        self.set_end_date(2026, 1, 1)
        self.set_cash(1000000)
        
        # Long Mag 7
        self.mag7_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
        for ticker in self.mag7_tickers:
            self.add_equity(ticker, Resolution.DAILY)
        
        # Short QQQ for hedge
        self.add_equity("QQQ", Resolution.DAILY)
```

#### BTC Futures Spot Arbitrage Strategy

Cash-and-carry arbitrage using Coinbase spot + CME futures:

```python
# See examples/lean-engine/btc_futures_arbitrage.py
from AlgorithmImports import *

class BTCFuturesArbitrageStrategy(QCAlgorithm):
    def initialize(self):
        self.set_start_date(2024, 1, 1)
        self.set_end_date(2025, 1, 1)
        self.set_cash(1000000)
        
        # Coinbase BTC spot
        self.btc_spot = self.add_crypto("BTCUSD", Resolution.HOUR, Market.COINBASE)
        
        # CME BTC futures
        self.btc_future = self.add_future(Futures.Currencies.BTC, Resolution.HOUR)
```

## Project Structure

```
quant1024/
├── src/quant1024/          # Source code
│   ├── __init__.py         # Package initialization (public API)
│   ├── exchanges/          # Exchange connectors
│   │   ├── exchange_1024ex.py  # 1024 Exchange
│   │   └── modules/        # Trading modules
│   ├── qc/                 # QuantConnect API
│   │   ├── client.py       # REST API client
│   │   ├── models.py       # Data models
│   │   ├── runner.py       # Backtest runner
│   │   └── result_processor.py  # Result processing
│   ├── interfaces/         # Trading interfaces
│   ├── models/             # Data models
│   └── utils/              # Utilities
├── tests/                  # Test code
├── examples/               # Example code
│   └── lean-engine/        # QuantConnect strategy examples
├── guide/                  # Documentation
│   ├── en/                 # English guides
│   └── zh-hans/            # Chinese guides
├── pyproject.toml          # Project configuration
├── README.md               # This file
├── README_zh.md            # Chinese documentation
└── LICENSE                 # License
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

## Testing

This project includes comprehensive test cases:

- ✅ **Import Tests**: Verify public APIs can be correctly imported
- ✅ **Exchange Tests**: Verify exchange connector functionality
- ✅ **QC API Tests**: Verify QuantConnect API integration
- ✅ **Integration Tests**: Verify typical use cases
- ✅ **Edge Case Tests**: Verify exception handling

```bash
pytest tests/ -v
```

## License

See the LICENSE file for license information.

## Contributing

Issues and Pull Requests are welcome!

## Contact

For questions or suggestions, please submit an Issue.

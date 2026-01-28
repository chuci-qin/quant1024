# Lean Engine Examples

QuantConnect cloud backtesting examples using the quant1024 SDK.

## Overview

This directory contains strategy examples using the QuantConnect cloud backtesting API:

- `main.py` - Mag 7 Alpha + Beta Market Neutral Strategy (Long tech giants + Short QQQ hedge)
- `btc_futures_arbitrage.py` - BTC Futures Spot Arbitrage Strategy (Coinbase spot + CME futures)

## Requirements

```bash
# Install quant1024 SDK
pip install quant1024

# Or install from source
pip install -e /path/to/quant1024
```

## Usage

### 1. Configure QuantConnect Authentication

Get your QuantConnect API credentials:
- Log in to [QuantConnect](https://www.quantconnect.com/)
- Go to Account → API Access
- Copy your User ID and API Token

### 2. Set Environment Variables (Recommended)

```bash
export QC_USER_ID="your_user_id"
export QC_API_TOKEN="your_api_token"
```

### 3. Run Backtest

```bash
# Run Mag 7 strategy backtest
python backtest.py
```

### 4. Modify Strategy

Edit the strategy parameters in `main.py` or `btc_futures_arbitrage.py`, then re-run the backtest.

To backtest a different strategy, modify the `STRATEGY_FILE` variable in `backtest.py`:

```python
# Use Mag 7 strategy
STRATEGY_FILE = "main.py"

# Or use BTC futures arbitrage strategy
STRATEGY_FILE = "btc_futures_arbitrage.py"
```

## Using the SDK qc Module

```python
from quant1024 import qc

# Method 1: Quick run with run_backtest
qc.run_backtest(
    user_id="your_user_id",
    api_token="your_api_token",
    strategy_file="main.py",
    export_json=True,  # Export complete backtest data
)

# Method 2: Fine-grained control with QuantConnectAPI
credentials = qc.QCCredentials(user_id="xxx", api_token="xxx")
api = qc.QuantConnectAPI(credentials)

# Authenticate
api.authenticate()

# Create project
project_id = api.create_project("MyStrategy")

# Upload code
with open("main.py") as f:
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
```

## Backtest Results

After the backtest completes, results are saved in the `backtest_result/` directory, including:

- Equity curve data
- Drawdown curve
- Order records
- Complete statistics

## Strategy Descriptions

### Mag 7 Alpha + Beta Strategy (main.py)

- **Concept**: Long Mag 7 tech giants (Alpha) + Short QQQ (Beta hedge)
- **Position**: 60% long Mag 7 + 60% short QQQ
- **Rebalance**: Every 5 trading days
- **Objective**: Capture excess returns of Mag 7 relative to market

### BTC Futures Spot Arbitrage Strategy (btc_futures_arbitrage.py)

- **Concept**: Exploit CME futures premium over Coinbase spot for risk-free arbitrage
- **Entry**: When annualized basis > 8%, long spot + short futures
- **Exit**: When annualized basis < 2%, close for profit
- **Risk Control**: Force close 5 days before futures expiry

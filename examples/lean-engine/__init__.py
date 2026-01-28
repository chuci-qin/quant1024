"""
Lean Engine - QuantConnect REST API 回测框架

模块结构:
- main.py: 策略代码 (Mag 7 Alpha + Beta)
- run.py: 运行回测入口
- qc_api/: QuantConnect API 基础设施
- strategies/: 其他策略模块
"""

from qc_api import (
    QuantConnectAPI,
    QCCredentials,
    BacktestConfig,
    run_backtest,
    BacktestResultProcessor,
)

__all__ = [
    "QuantConnectAPI",
    "QCCredentials",
    "BacktestConfig",
    "run_backtest",
    "BacktestResultProcessor",
]

__version__ = "0.1.0"

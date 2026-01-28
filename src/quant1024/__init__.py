"""
quant1024 - Quantitative Trading Toolkit

Public API:
- Exchange1024ex: 1024 Exchange connector for live trading
- qc: QuantConnect API infrastructure for cloud backtesting

All other modules are internal. While they can be accessed via direct import
paths (e.g., `from quant1024.core import ...`), they are not part of the
public API and may change without notice.
"""

__version__ = "0.5.5"

# Define public API
__all__ = ["Exchange1024ex", "qc"]

# Names that are blocked from top-level import
_BLOCKED_NAMES = frozenset({
    # Core module
    "QuantStrategy", "calculate_returns", "calculate_sharpe_ratio",
    # Exchange modules
    "BaseExchange",
    "PerpModule", "SpotModule", "PredictionModule", "ChampionshipModule", "AccountModule",
    # Interfaces
    "IMarketData", "ITrading", "IPositions", "IAdvancedOrders",
    # Data module
    "DataRetriever", "BacktestDataset",
    # Live trading
    "start_trading", "LiveTrader",
    # Monitor feeds
    "RuntimeConfig", "RuntimeReporter",
    # Exceptions (available via quant1024.exceptions)
    "Quant1024Exception", "AuthenticationError", "RateLimitError",
    "InvalidParameterError", "InsufficientMarginError", "OrderNotFoundError",
    "MarketNotFoundError", "APIError",
    # Module names
    "core", "exchanges", "interfaces", "data", "live_trading",
    "monitor_feeds", "exceptions", "auth", "models", "utils",
})


def __getattr__(name: str):
    """
    Control what can be imported from the quant1024 package.
    
    Only Exchange1024ex and qc are exposed as public API.
    Other modules must be imported via their full path.
    """
    if name in _BLOCKED_NAMES:
        raise ImportError(
            f"Cannot import '{name}' from 'quant1024'. "
            f"This is an internal module and not part of the public API. "
            f"Only 'Exchange1024ex' and 'qc' are available for import. "
            f"For internal usage, import directly: from quant1024.xxx import {name}"
        )
    
    if name == "Exchange1024ex":
        from .exchanges.exchange_1024ex import Exchange1024ex
        return Exchange1024ex
    
    if name == "qc":
        import importlib
        return importlib.import_module("quant1024.qc")
    
    raise AttributeError(
        f"module 'quant1024' has no attribute '{name}'. "
        f"Only 'Exchange1024ex' and 'qc' are available for import."
    )


def __dir__():
    """List public API members."""
    return ["Exchange1024ex", "qc", "__version__"]

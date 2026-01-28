"""
quant1024 - Quantitative Trading Toolkit

This module exposes ONLY the following public APIs:
- Exchange1024ex: 1024 Exchange connector for live trading
- qc: QuantConnect API infrastructure for cloud backtesting

All other modules are INTERNAL and NOT accessible.
Attempting to import any other module will raise ImportError.
"""

import sys
import importlib.abc
import importlib.machinery

__version__ = "0.5.1"


class Quant1024ImportBlocker(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """
    Strict import blocker that prevents importing internal submodules.
    Only allows:
    - quant1024.Exchange1024ex
    - quant1024.qc (and its submodules)
    """

    _ALLOWED_PATTERNS = (
        "quant1024.qc",
        "quant1024.exchanges.exchange_1024ex",
        "quant1024.exchanges",
        "quant1024.exchanges.base",
        "quant1024.exchanges.modules",
        "quant1024.auth",
        "quant1024.auth.hmac_auth",
        "quant1024.exceptions",
    )

    def find_spec(self, fullname, path, target=None):
        if not fullname.startswith("quant1024."):
            return None
        if fullname == "quant1024":
            return None
        for pattern in self._ALLOWED_PATTERNS:
            if fullname == pattern or fullname.startswith(pattern + "."):
                return None
        return importlib.machinery.ModuleSpec(fullname, self)

    def create_module(self, spec):
        raise ImportError(
            f"Cannot import '{spec.name}'. "
            f"This is an internal module and not part of the public API. "
            f"Only 'quant1024.Exchange1024ex' and 'quant1024.qc' are available."
        )

    def exec_module(self, module):
        pass


_blocker_instance = Quant1024ImportBlocker()
sys.meta_path = [f for f in sys.meta_path if not isinstance(f, Quant1024ImportBlocker)]
sys.meta_path.insert(0, _blocker_instance)


_BLOCKED_NAMES = frozenset({
    "QuantStrategy", "calculate_returns", "calculate_sharpe_ratio",
    "BaseExchange",
    "PerpModule", "SpotModule", "PredictionModule", "ChampionshipModule", "AccountModule",
    "IMarketData", "ITrading", "IPositions", "IAdvancedOrders",
    "DataRetriever", "BacktestDataset",
    "start_trading", "LiveTrader",
    "RuntimeConfig", "RuntimeReporter",
    "Quant1024Exception", "AuthenticationError", "RateLimitError",
    "InvalidParameterError", "InsufficientMarginError", "OrderNotFoundError",
    "MarketNotFoundError", "APIError",
    "core", "exchanges", "interfaces", "data", "live_trading",
    "monitor_feeds", "exceptions", "auth", "models", "utils",
})


def __getattr__(name: str):
    if name in _BLOCKED_NAMES:
        raise ImportError(
            f"Cannot import '{name}' from 'quant1024'. "
            f"This is an internal module and not part of the public API. "
            f"Only 'Exchange1024ex' and 'qc' are available for import."
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
    return ["Exchange1024ex", "qc", "__version__"]


__all__ = ["Exchange1024ex", "qc"]

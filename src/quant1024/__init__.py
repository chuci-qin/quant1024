"""
quant1024 - A quantitative trading toolkit

全数据源的开源量化工具包
- 结构化数据获取（交易所、金融数据、区块链）
- 快速连接多种数据源
- 实时数据推送
- 专为回测优化
"""

from .core import QuantStrategy, calculate_returns, calculate_sharpe_ratio
from .exchanges import BaseExchange, Exchange1024ex
from .data import DataRetriever, BacktestDataset
from .exceptions import (
    Quant1024Exception,
    AuthenticationError,
    RateLimitError,
    InvalidParameterError,
    InsufficientMarginError,
    OrderNotFoundError,
    MarketNotFoundError,
    APIError
)

__version__ = "0.3.0"
__all__ = [
    # Core
    "QuantStrategy",
    "calculate_returns",
    "calculate_sharpe_ratio",
    # Exchanges
    "BaseExchange",
    "Exchange1024ex",
    # Data Retrieval (v0.3.0)
    "DataRetriever",
    "BacktestDataset",
    # Exceptions
    "Quant1024Exception",
    "AuthenticationError",
    "RateLimitError",
    "InvalidParameterError",
    "InsufficientMarginError",
    "OrderNotFoundError",
    "MarketNotFoundError",
    "APIError",
]


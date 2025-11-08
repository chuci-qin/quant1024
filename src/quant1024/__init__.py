"""
quant1024 - A quantitative trading toolkit

跨券商跨交易所的开源量化工具包
- 结构化数据获取
- 快速连接交易所和券商
- 实时数据推送
"""

from .core import QuantStrategy, calculate_returns, calculate_sharpe_ratio
from .exchanges import BaseExchange, Exchange1024ex
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

__version__ = "0.2.0"
__all__ = [
    # Core
    "QuantStrategy",
    "calculate_returns",
    "calculate_sharpe_ratio",
    # Exchanges
    "BaseExchange",
    "Exchange1024ex",
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


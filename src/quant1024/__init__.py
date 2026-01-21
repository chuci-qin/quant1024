"""
quant1024 - A quantitative trading toolkit

全数据源的开源量化工具包
- 结构化数据获取（交易所、金融数据、区块链）
- 快速连接多种数据源
- 实时数据推送
- 专为回测优化

v0.4.0 新增:
- 模块化 API 架构 (exchange.perp.xxx(), exchange.spot.xxx() 等)
- 统一接口定义 (IMarketData, ITrading, IPositions, IAdvancedOrders)
- 5 个功能模块: Perp, Spot, Prediction, Championship, Account
"""

from .core import QuantStrategy, calculate_returns, calculate_sharpe_ratio
from .exchanges import BaseExchange, Exchange1024ex
from .exchanges.modules import (
    PerpModule,
    SpotModule,
    PredictionModule,
    ChampionshipModule,
    AccountModule,
)
from .interfaces import (
    IMarketData,
    ITrading,
    IPositions,
    IAdvancedOrders,
)
from .data import DataRetriever, BacktestDataset
from .live_trading import start_trading, LiveTrader
from .monitor_feeds import RuntimeConfig, RuntimeReporter
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

__version__ = "0.4.0"
__all__ = [
    # Core
    "QuantStrategy",
    "calculate_returns",
    "calculate_sharpe_ratio",
    
    # Exchanges
    "BaseExchange",
    "Exchange1024ex",
    
    # Exchange Modules (v0.4.0)
    "PerpModule",
    "SpotModule",
    "PredictionModule",
    "ChampionshipModule",
    "AccountModule",
    
    # Interfaces (v0.4.0)
    "IMarketData",
    "ITrading",
    "IPositions",
    "IAdvancedOrders",
    
    # Data Retrieval
    "DataRetriever",
    "BacktestDataset",
    
    # Live Trading
    "start_trading",
    "LiveTrader",
    
    # Monitor Feeds
    "RuntimeConfig",
    "RuntimeReporter",
    
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

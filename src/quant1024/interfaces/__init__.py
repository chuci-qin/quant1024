"""
统一接口定义

使用 Python Protocol 定义统一接口，实现接口隔离原则 (ISP)。
不同模块实现相同接口，上层代码只依赖接口而非具体实现。

Interfaces:
- IMarketData: 市场数据接口
- ITrading: 交易接口
- IPositions: 持仓接口
- IAdvancedOrders: 高级订单接口
"""

from .market_data import IMarketData
from .trading import ITrading
from .positions import IPositions
from .advanced_orders import IAdvancedOrders

__all__ = [
    "IMarketData",
    "ITrading",
    "IPositions",
    "IAdvancedOrders",
]


"""
IMarketData - 市场数据接口

定义获取市场数据的标准接口，所有提供市场数据的模块都应实现此接口。
"""

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@runtime_checkable
class IMarketData(Protocol):
    """
    市场数据接口
    
    提供市场行情、订单簿、K线等数据的标准访问方式。
    
    Implementations:
        - PerpModule: 永续合约市场数据
        - SpotModule: 现货市场数据
        - PredictionModule: 预测市场数据
    
    Example:
        >>> def fetch_price(provider: IMarketData, symbol: str) -> float:
        ...     ticker = provider.get_ticker(symbol)
        ...     return float(ticker.get("last", 0))
    """
    
    def get_markets(self) -> List[Dict[str, Any]]:
        """
        获取所有市场列表
        
        Returns:
            市场信息列表，每个市场包含 symbol, base_currency, quote_currency 等字段
        """
        ...
    
    def get_market(self, symbol: str) -> Dict[str, Any]:
        """
        获取单个市场信息
        
        Args:
            symbol: 市场符号 (如 BTC-USDC, BTC/USDC)
        
        Returns:
            市场详细信息
        """
        ...
    
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        获取市场行情 (24小时统计)
        
        Args:
            symbol: 市场符号
        
        Returns:
            行情数据，包含 last, bid, ask, high, low, volume 等字段
        """
        ...
    
    def get_orderbook(
        self,
        symbol: str,
        depth: int = 20
    ) -> Dict[str, Any]:
        """
        获取订单簿
        
        Args:
            symbol: 市场符号
            depth: 深度档位数量 (默认 20)
        
        Returns:
            订单簿数据，包含 bids 和 asks 列表
        """
        ...
    
    def get_trades(
        self,
        symbol: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取最近成交记录
        
        Args:
            symbol: 市场符号
            limit: 返回数量限制
        
        Returns:
            成交记录列表
        """
        ...
    
    def get_klines(
        self,
        symbol: str,
        interval: str = "1h",
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取K线数据
        
        Args:
            symbol: 市场符号
            interval: 时间间隔 (1m, 5m, 15m, 1h, 4h, 1d)
            start_time: 开始时间戳 (毫秒)
            end_time: 结束时间戳 (毫秒)
            limit: 返回数量限制
        
        Returns:
            K线数据列表，每条包含 open, high, low, close, volume, timestamp
        """
        ...


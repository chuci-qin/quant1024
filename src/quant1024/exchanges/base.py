"""
Base exchange class - abstract interface for all exchanges
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseExchange(ABC):
    """
    交易所基类 - 所有交易所连接器的抽象接口
    
    这是一个抽象类，定义了跨交易所的统一接口。
    不同交易所（1024ex, Binance, IBKR 等）都实现这个接口，
    使得用户代码可以无缝切换交易所。
    """
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str,
        **kwargs
    ):
        """
        初始化交易所连接
        
        Args:
            api_key: API Key
            api_secret: API Secret
            base_url: API 基础 URL
            **kwargs: 其他参数
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.extra_params = kwargs
    
    # ========== 系统接口 ==========
    
    @abstractmethod
    def get_server_time(self) -> Dict[str, Any]:
        """获取服务器时间"""
        pass
    
    @abstractmethod
    def get_health(self) -> Dict[str, Any]:
        """健康检查"""
        pass
    
    @abstractmethod
    def get_exchange_info(self) -> Dict[str, Any]:
        """获取交易所信息"""
        pass
    
    # ========== 市场数据 ==========
    
    @abstractmethod
    def get_markets(self) -> List[Dict[str, Any]]:
        """获取所有市场"""
        pass
    
    @abstractmethod
    def get_market(self, market: str) -> Dict[str, Any]:
        """获取单个市场信息"""
        pass
    
    @abstractmethod
    def get_ticker(self, market: str) -> Dict[str, Any]:
        """获取24小时行情"""
        pass
    
    @abstractmethod
    def get_orderbook(self, market: str, depth: int = 20) -> Dict[str, Any]:
        """获取订单簿"""
        pass
    
    @abstractmethod
    def get_trades(self, market: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取最近成交"""
        pass
    
    @abstractmethod
    def get_klines(
        self,
        market: str,
        interval: str = '1h',
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取K线数据"""
        pass
    
    # ========== 交易接口 ==========
    
    @abstractmethod
    def place_order(
        self,
        market: str,
        side: str,
        order_type: str,
        size: str,
        price: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """下单"""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """撤单"""
        pass
    
    @abstractmethod
    def get_orders(
        self,
        market: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取当前委托"""
        pass
    
    @abstractmethod
    def get_order(self, order_id: str) -> Dict[str, Any]:
        """获取订单详情"""
        pass
    
    # ========== 账户接口 ==========
    
    @abstractmethod
    def get_balance(self) -> Dict[str, Any]:
        """获取账户余额"""
        pass
    
    @abstractmethod
    def get_positions(
        self,
        market: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取持仓"""
        pass
    
    @abstractmethod
    def get_margin(self) -> Dict[str, Any]:
        """获取保证金信息"""
        pass


"""
ITrading - 交易接口

定义交易操作的标准接口，所有提供交易功能的模块都应实现此接口。
"""

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@runtime_checkable
class ITrading(Protocol):
    """
    交易接口
    
    提供下单、撤单、查询订单的标准访问方式。
    
    Implementations:
        - PerpModule: 永续合约交易
        - SpotModule: 现货交易
        - PredictionModule: 预测市场交易
    
    Example:
        >>> def place_market_buy(trader: ITrading, symbol: str, size: str):
        ...     return trader.place_order(
        ...         market=symbol,
        ...         side="buy",
        ...         order_type="market",
        ...         size=size
        ...     )
    """
    
    def place_order(
        self,
        market: str,
        side: str,
        order_type: str,
        size: str,
        price: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        下单
        
        Args:
            market: 市场符号
            side: 方向 (buy/sell 或 long/short)
            order_type: 订单类型 (limit/market)
            size: 数量
            price: 价格 (限价单必填)
            **kwargs: 其他参数 (reduce_only, post_only, time_in_force 等)
        
        Returns:
            订单信息，包含 order_id, status 等字段
        """
        ...
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        撤销订单
        
        Args:
            order_id: 订单ID
        
        Returns:
            撤单结果
        """
        ...
    
    def cancel_all_orders(
        self,
        market: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        批量撤销订单
        
        Args:
            market: 市场符号 (可选，不填则撤销所有市场的订单)
        
        Returns:
            批量撤单结果
        """
        ...
    
    def get_orders(
        self,
        market: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取当前订单列表
        
        Args:
            market: 市场符号 (可选)
            status: 订单状态过滤 (可选)
        
        Returns:
            订单列表
        """
        ...
    
    def get_order(self, order_id: str) -> Dict[str, Any]:
        """
        获取订单详情
        
        Args:
            order_id: 订单ID
        
        Returns:
            订单详细信息
        """
        ...
    
    def update_order(
        self,
        order_id: str,
        price: str,
        size: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        修改订单
        
        Args:
            order_id: 订单ID
            price: 新价格
            size: 新数量 (可选)
        
        Returns:
            修改后的订单信息
        """
        ...
    
    def batch_place_orders(
        self,
        orders: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        批量下单
        
        Args:
            orders: 订单列表，每个订单包含 market, side, type, size 等字段
        
        Returns:
            批量下单结果
        """
        ...
    
    def get_order_history(
        self,
        market: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取历史订单
        
        Args:
            market: 市场符号 (可选)
            limit: 返回数量限制
        
        Returns:
            历史订单列表
        """
        ...
    
    def get_trade_history(
        self,
        market: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取成交历史
        
        Args:
            market: 市场符号 (可选)
            limit: 返回数量限制
        
        Returns:
            成交历史列表
        """
        ...


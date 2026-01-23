"""
IPositions - 持仓接口

定义持仓管理的标准接口，适用于保证金交易（永续合约等）。
"""

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@runtime_checkable
class IPositions(Protocol):
    """
    持仓接口
    
    提供持仓查询和管理的标准访问方式。
    
    Implementations:
        - PerpModule: 永续合约持仓
    
    Example:
        >>> def check_position(pm: IPositions, symbol: str) -> float:
        ...     pos = pm.get_position(symbol)
        ...     return float(pos.get("size", 0))
    """
    
    def get_positions(
        self,
        market: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取持仓列表
        
        Args:
            market: 市场符号 (可选，不填返回所有持仓)
        
        Returns:
            持仓列表，每个持仓包含 market, side, size, entry_price, pnl 等字段
        """
        ...
    
    def get_position(self, market: str) -> Dict[str, Any]:
        """
        获取单个市场的持仓
        
        Args:
            market: 市场符号
        
        Returns:
            持仓信息
        """
        ...
    
    def close_position(
        self,
        market: str,
        size: Optional[str] = None,
        price: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        平仓
        
        Args:
            market: 市场符号
            size: 平仓数量 (可选，不填则全部平仓)
            price: 限价 (可选，不填则市价平仓)
        
        Returns:
            平仓订单信息
        """
        ...
    
    def set_leverage(
        self,
        market: str,
        leverage: int
    ) -> Dict[str, Any]:
        """
        设置杠杆倍数
        
        Args:
            market: 市场符号
            leverage: 杠杆倍数
        
        Returns:
            设置结果
        """
        ...
    
    def get_leverage(self, market: str) -> Dict[str, Any]:
        """
        获取当前杠杆设置
        
        Args:
            market: 市场符号
        
        Returns:
            杠杆信息
        """
        ...
    
    def set_tpsl(
        self,
        market: str,
        take_profit_price: Optional[str] = None,
        stop_loss_price: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        设置止盈止损
        
        Args:
            market: 市场符号
            take_profit_price: 止盈价格
            stop_loss_price: 止损价格
        
        Returns:
            设置结果
        """
        ...





"""
IAdvancedOrders - 高级订单接口

定义高级订单类型的标准接口，包括 TWAP、VWAP、OCO、Bracket、Iceberg 等。
"""

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@runtime_checkable
class IAdvancedOrders(Protocol):
    """
    高级订单接口
    
    提供各种高级订单类型的创建和管理。
    
    Implementations:
        - PerpModule: 永续合约高级订单
    
    Order Types:
        - TWAP: 时间加权平均价格
        - VWAP: 成交量加权平均价格
        - OCO: One-Cancels-Other
        - Bracket: 括号订单 (入场+止盈+止损)
        - Iceberg: 冰山订单
        - Scale: 阶梯订单
        - Trailing Stop: 追踪止损
        - Conditional: 条件订单
    """
    
    # ========== TWAP 订单 ==========
    
    def create_twap(
        self,
        market: str,
        side: str,
        total_size: str,
        duration_seconds: int,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        创建 TWAP 订单 (时间加权平均价格)
        
        将大订单分割成多个小订单，在指定时间内均匀执行。
        
        Args:
            market: 市场符号
            side: 方向 (buy/sell)
            total_size: 总数量
            duration_seconds: 执行时长 (秒)
            **kwargs: interval_seconds, slippage_tolerance, reduce_only 等
        
        Returns:
            TWAP 订单信息
        """
        ...
    
    def get_twap(self, order_id: str) -> Dict[str, Any]:
        """获取 TWAP 订单详情"""
        ...
    
    def cancel_twap(self, order_id: str) -> Dict[str, Any]:
        """取消 TWAP 订单"""
        ...
    
    # ========== VWAP 订单 ==========
    
    def create_vwap(
        self,
        market: str,
        side: str,
        total_size: str,
        duration_seconds: int,
        participation_rate: float,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        创建 VWAP 订单 (成交量加权平均价格)
        
        根据市场成交量分配订单执行。
        
        Args:
            market: 市场符号
            side: 方向
            total_size: 总数量
            duration_seconds: 执行时长
            participation_rate: 参与率 (0.0-1.0)
        
        Returns:
            VWAP 订单信息
        """
        ...
    
    def get_vwap(self, order_id: str) -> Dict[str, Any]:
        """获取 VWAP 订单详情"""
        ...
    
    def cancel_vwap(self, order_id: str) -> Dict[str, Any]:
        """取消 VWAP 订单"""
        ...
    
    # ========== OCO 订单 ==========
    
    def create_oco(
        self,
        market: str,
        side: str,
        size: str,
        limit_price: str,
        stop_price: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        创建 OCO 订单 (One-Cancels-Other)
        
        同时创建限价单和止损单，一个成交后自动取消另一个。
        
        Args:
            market: 市场符号
            side: 方向
            size: 数量
            limit_price: 限价单价格
            stop_price: 止损触发价格
        
        Returns:
            OCO 订单信息
        """
        ...
    
    def get_oco(self, order_id: str) -> Dict[str, Any]:
        """获取 OCO 订单详情"""
        ...
    
    def cancel_oco(self, order_id: str) -> Dict[str, Any]:
        """取消 OCO 订单"""
        ...
    
    # ========== Bracket 订单 ==========
    
    def create_bracket(
        self,
        market: str,
        side: str,
        size: str,
        entry_price: str,
        take_profit_price: str,
        stop_loss_price: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        创建 Bracket 订单 (括号订单)
        
        入场订单 + 止盈订单 + 止损订单的组合。
        
        Args:
            market: 市场符号
            side: 方向
            size: 数量
            entry_price: 入场价格
            take_profit_price: 止盈价格
            stop_loss_price: 止损价格
        
        Returns:
            Bracket 订单信息
        """
        ...
    
    def get_bracket(self, order_id: str) -> Dict[str, Any]:
        """获取 Bracket 订单详情"""
        ...
    
    def cancel_bracket(self, order_id: str) -> Dict[str, Any]:
        """取消 Bracket 订单"""
        ...
    
    # ========== Iceberg 订单 ==========
    
    def create_iceberg(
        self,
        market: str,
        side: str,
        total_size: str,
        display_size: str,
        price: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        创建冰山订单
        
        将大订单分成小订单显示，隐藏真实订单量。
        
        Args:
            market: 市场符号
            side: 方向
            total_size: 总数量 (隐藏)
            display_size: 显示数量
            price: 价格
        
        Returns:
            冰山订单信息
        """
        ...
    
    def get_iceberg(self, order_id: str) -> Dict[str, Any]:
        """获取冰山订单详情"""
        ...
    
    def cancel_iceberg(self, order_id: str) -> Dict[str, Any]:
        """取消冰山订单"""
        ...
    
    # ========== Scale 订单 ==========
    
    def create_scale(
        self,
        market: str,
        side: str,
        total_size: str,
        num_orders: int,
        start_price: str,
        end_price: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        创建阶梯订单
        
        在价格区间内按分布创建多个限价订单。
        
        Args:
            market: 市场符号
            side: 方向
            total_size: 总数量
            num_orders: 订单数量
            start_price: 起始价格
            end_price: 结束价格
        
        Returns:
            阶梯订单信息
        """
        ...
    
    def get_scale(self, order_id: str) -> Dict[str, Any]:
        """获取阶梯订单详情"""
        ...
    
    def cancel_scale(self, order_id: str) -> Dict[str, Any]:
        """取消阶梯订单"""
        ...
    
    # ========== Trailing Stop 订单 ==========
    
    def create_trailing_stop(
        self,
        market: str,
        side: str,
        size: str,
        callback_rate: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        创建追踪止损订单
        
        止损价格随市场价格移动，锁定利润。
        
        Args:
            market: 市场符号
            side: 方向
            size: 数量
            callback_rate: 回调比率 (如 "0.01" 表示 1%)
        
        Returns:
            追踪止损订单信息
        """
        ...
    
    def get_trailing_stop(self, order_id: str) -> Dict[str, Any]:
        """获取追踪止损订单详情"""
        ...
    
    def cancel_trailing_stop(self, order_id: str) -> Dict[str, Any]:
        """取消追踪止损订单"""
        ...
    
    # ========== Conditional 订单 ==========
    
    def create_conditional(
        self,
        market: str,
        side: str,
        order_type: str,
        size: str,
        trigger_price: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        创建条件订单
        
        当价格达到触发条件时下单。
        
        Args:
            market: 市场符号
            side: 方向
            order_type: 订单类型 (limit/market)
            size: 数量
            trigger_price: 触发价格
        
        Returns:
            条件订单信息
        """
        ...
    
    def get_conditional_orders(
        self,
        market: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取条件订单列表"""
        ...
    
    def cancel_conditional(self, order_id: str) -> Dict[str, Any]:
        """取消条件订单"""
        ...





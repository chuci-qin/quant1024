"""
Order and position models
"""

from typing import Optional
from pydantic import BaseModel, Field


class OrderRequest(BaseModel):
    """下单请求"""
    market: str
    side: str = Field(..., description="方向: buy/sell")
    type: str = Field(..., description="订单类型: limit/market")
    price: Optional[str] = Field(None, description="价格（限价单必填）")
    size: str = Field(..., description="数量")
    leverage: Optional[int] = Field(None, description="杠杆倍数")
    reduce_only: Optional[bool] = Field(False, description="只减仓")
    post_only: Optional[bool] = Field(False, description="只做 Maker")
    time_in_force: Optional[str] = Field("GTC", description="有效期类型")
    client_order_id: Optional[str] = Field(None, description="客户端订单ID")


class Order(BaseModel):
    """订单信息"""
    order_id: str
    client_order_id: Optional[str] = None
    market: str
    side: str
    type: str
    status: str = Field(..., description="状态: pending/open/filled/cancelled")
    price: Optional[str] = None
    size: str
    filled_size: str = Field(..., description="已成交数量")
    remaining_size: Optional[str] = Field(None, description="剩余数量")
    average_fill_price: Optional[str] = Field(None, description="平均成交价")
    created_at: int
    updated_at: Optional[int] = None


class Position(BaseModel):
    """持仓信息"""
    market: str
    side: str = Field(..., description="方向: long/short")
    size: str = Field(..., description="持仓数量")
    entry_price: str = Field(..., description="开仓均价")
    mark_price: str = Field(..., description="标记价格")
    liquidation_price: str = Field(..., description="强平价格")
    leverage: int
    unrealized_pnl: str = Field(..., description="未实现盈亏")
    realized_pnl: Optional[str] = Field(None, description="已实现盈亏")
    margin: str = Field(..., description="占用保证金")
    margin_ratio: Optional[str] = Field(None, description="保证金率")


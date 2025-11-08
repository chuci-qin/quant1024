"""
Market data models
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class MarketInfo(BaseModel):
    """市场信息"""
    market: str = Field(..., description="市场名称，如 BTC-PERP")
    base_asset: str = Field(..., description="基础资产")
    quote_asset: str = Field(..., description="计价资产")
    status: str = Field(..., description="市场状态")
    tick_size: str = Field(..., description="最小价格变动")
    step_size: str = Field(..., description="最小数量变动")
    max_leverage: int = Field(..., description="最大杠杆")
    min_order_size: Optional[str] = Field(None, description="最小订单数量")
    max_order_size: Optional[str] = Field(None, description="最大订单数量")


class TickerData(BaseModel):
    """24小时行情数据"""
    market: str
    last_price: str = Field(..., description="最新价格")
    mark_price: str = Field(..., description="标记价格")
    index_price: Optional[str] = Field(None, description="指数价格")
    bid: str = Field(..., description="买一价")
    ask: str = Field(..., description="卖一价")
    high_24h: str = Field(..., description="24小时最高价")
    low_24h: str = Field(..., description="24小时最低价")
    volume_24h: str = Field(..., description="24小时成交量")
    funding_rate: Optional[str] = Field(None, description="资金费率")
    open_interest: Optional[str] = Field(None, description="持仓量")


class OrderBookLevel(BaseModel):
    """订单簿价格档位"""
    price: str
    size: str


class OrderBook(BaseModel):
    """订单簿"""
    market: str
    bids: List[OrderBookLevel] = Field(..., description="买单")
    asks: List[OrderBookLevel] = Field(..., description="卖单")
    timestamp: int = Field(..., description="时间戳")


class Trade(BaseModel):
    """成交记录"""
    id: str = Field(..., description="成交ID")
    market: str
    price: str
    size: str
    side: str = Field(..., description="方向: buy/sell")
    timestamp: int


class Kline(BaseModel):
    """K线数据"""
    timestamp: int
    open: str
    high: str
    low: str
    close: str
    volume: str


class FundingRate(BaseModel):
    """资金费率"""
    market: str
    funding_rate: str = Field(..., description="当前资金费率")
    next_funding_time: int = Field(..., description="下次结算时间")
    estimated_rate: Optional[str] = Field(None, description="预估费率")


class MarketStats(BaseModel):
    """市场统计"""
    market: str
    open_interest: str = Field(..., description="持仓量")
    volume_24h: str = Field(..., description="24小时成交量")
    turnover_24h: Optional[str] = Field(None, description="24小时成交额")
    funding_rate: str
    next_funding_time: int


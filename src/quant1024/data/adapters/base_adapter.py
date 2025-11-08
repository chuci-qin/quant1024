"""
Base adapter - 适配器基类
"""

from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime
import pandas as pd


class BaseAdapter(ABC):
    """
    数据源适配器基类
    
    所有数据源适配器都需要实现这个接口
    """
    
    def __init__(self, source: str, **credentials):
        """
        初始化适配器
        
        Args:
            source: 数据源名称
            **credentials: 认证信息
        """
        self.source = source
        self.credentials = credentials
    
    @abstractmethod
    def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        limit: Optional[int]
    ) -> pd.DataFrame:
        """
        获取K线数据
        
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        pass
    
    @abstractmethod
    def get_trades(
        self,
        symbol: str,
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        limit: int
    ) -> pd.DataFrame:
        """
        获取成交数据
        
        Returns:
            DataFrame with columns: timestamp, price, size, side, trade_id
        """
        pass
    
    @abstractmethod
    def get_funding_rates(
        self,
        symbol: str,
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        limit: int
    ) -> pd.DataFrame:
        """
        获取资金费率（仅加密货币交易所）
        
        Returns:
            DataFrame with columns: timestamp, funding_rate, mark_price
        """
        pass


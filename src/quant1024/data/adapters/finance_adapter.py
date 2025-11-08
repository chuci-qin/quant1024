"""
Finance Adapter - 金融数据适配器

封装金融数据提供商API（Yahoo Finance, Bloomberg等）
"""

from typing import Optional
from datetime import datetime
import pandas as pd
from .base_adapter import BaseAdapter


class FinanceAdapter(BaseAdapter):
    """
    金融数据适配器
    
    封装: Yahoo Finance, Bloomberg等
    """
    
    def __init__(self, source: str, **credentials):
        super().__init__(source, **credentials)
        
        # 初始化金融数据客户端
        if source == "yahoo":
            try:
                import yfinance as yf
                self.client = yf
            except ImportError:
                raise ImportError(
                    "Yahoo Finance 需要 yfinance 库\n"
                    "安装: pip install yfinance"
                )
        
        elif source == "bloomberg":
            # Bloomberg API（需要订阅）
            # TODO: 实现 Bloomberg API
            raise NotImplementedError("Bloomberg 适配器还未实现")
        
        elif source == "alphavantage":
            # Alpha Vantage API
            # TODO: 实现 Alpha Vantage API
            raise NotImplementedError("Alpha Vantage 适配器还未实现")
        
        else:
            raise ValueError(f"不支持的金融数据源: {source}")
    
    def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        limit: Optional[int]
    ) -> pd.DataFrame:
        """从金融数据源获取K线数据"""
        
        if self.source == "yahoo":
            # Yahoo Finance 的时间间隔映射
            interval_map = {
                '1m': '1m',
                '5m': '5m',
                '15m': '15m',
                '30m': '30m',
                '1h': '1h',
                '1d': '1d',
                '1w': '1wk',
            }
            yf_interval = interval_map.get(interval, '1d')
            
            # 创建 Ticker 对象
            ticker = self.client.Ticker(symbol)
            
            # 获取数据
            if start_time and end_time:
                # 使用精确时间范围
                df = ticker.history(
                    start=start_time,
                    end=end_time,
                    interval=yf_interval
                )
            else:
                # 使用 period 参数（更简单）
                if limit:
                    # 根据 limit 估算 period
                    period_map = {
                        '1m': f"{limit}m",
                        '1h': f"{limit}h",
                        '1d': f"{min(limit, 730)}d",  # Yahoo最多2年
                    }
                    period = period_map.get(interval, "30d")
                else:
                    period = "30d"
                
                df = ticker.history(period=period, interval=yf_interval)
            
            # 格式化列名
            df = df.reset_index()
            df = df.rename(columns={
                'Date': 'timestamp',
                'Datetime': 'timestamp',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # 确保时间是UTC
            if df['timestamp'].dtype.tz is None:
                df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize('UTC')
            else:
                df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_convert('UTC')
            
            # 只保留需要的列
            cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            df = df[[col for col in cols if col in df.columns]]
            
            return df
        
        else:
            raise NotImplementedError(f"金融数据源 '{self.source}' 的 get_klines 还未实现")
    
    def get_trades(
        self,
        symbol: str,
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        limit: int
    ) -> pd.DataFrame:
        """金融数据源通常不提供成交数据"""
        raise NotImplementedError(f"金融数据源 '{self.source}' 不支持成交数据")
    
    def get_funding_rates(
        self,
        symbol: str,
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        limit: int
    ) -> pd.DataFrame:
        """金融数据源不提供资金费率"""
        raise NotImplementedError(f"金融数据源 '{self.source}' 不支持资金费率")


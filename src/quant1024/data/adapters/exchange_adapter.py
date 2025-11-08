"""
Exchange Adapter - 交易所适配器

封装各交易所API（1024ex, Binance等）
"""

from typing import Optional
from datetime import datetime
import pandas as pd
from .base_adapter import BaseAdapter


class ExchangeAdapter(BaseAdapter):
    """
    交易所适配器
    
    封装: 1024ex, Binance, Coinbase等
    """
    
    def __init__(self, source: str, **credentials):
        super().__init__(source, **credentials)
        
        # 初始化交易所客户端
        if source == "1024ex":
            from ...exchanges import Exchange1024ex
            self.client = Exchange1024ex(
                api_key=credentials.get('api_key', ''),
                api_secret=credentials.get('api_secret', ''),
            )
        else:
            raise NotImplementedError(f"交易所 '{source}' 还未实现")
    
    def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        limit: Optional[int]
    ) -> pd.DataFrame:
        """从交易所获取K线数据"""
        
        if self.source == "1024ex":
            # 转换时间为毫秒时间戳
            start_ts = int(start_time.timestamp() * 1000) if start_time else None
            end_ts = int(end_time.timestamp() * 1000) if end_time else None
            
            # 调用 1024ex API
            raw_data = self.client.get_klines(
                market=symbol,
                interval=interval,
                start_time=start_ts,
                end_time=end_ts,
                limit=limit or 1000
            )
            
            # 格式化为DataFrame
            records = []
            for item in raw_data:
                records.append({
                    'timestamp': pd.to_datetime(item['timestamp'], unit='ms', utc=True),
                    'open': float(item['open']),
                    'high': float(item['high']),
                    'low': float(item['low']),
                    'close': float(item['close']),
                    'volume': float(item['volume'])
                })
            
            df = pd.DataFrame(records)
            return df
        
        else:
            raise NotImplementedError(f"交易所 '{self.source}' 的 get_klines 还未实现")
    
    def get_trades(
        self,
        symbol: str,
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        limit: int
    ) -> pd.DataFrame:
        """从交易所获取成交数据"""
        
        if self.source == "1024ex":
            raw_data = self.client.get_trades(market=symbol, limit=limit)
            
            records = []
            for item in raw_data:
                records.append({
                    'timestamp': pd.to_datetime(item['timestamp'], unit='ms', utc=True),
                    'price': float(item['price']),
                    'size': float(item['size']),
                    'side': item['side'],
                    'trade_id': item['id']
                })
            
            return pd.DataFrame(records)
        
        else:
            raise NotImplementedError(f"交易所 '{self.source}' 的 get_trades 还未实现")
    
    def get_funding_rates(
        self,
        symbol: str,
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        limit: int
    ) -> pd.DataFrame:
        """从交易所获取资金费率"""
        
        if self.source == "1024ex":
            raw_data = self.client.get_funding_history(market=symbol, limit=limit)
            
            records = []
            for item in raw_data:
                records.append({
                    'timestamp': pd.to_datetime(item['timestamp'], unit='ms', utc=True),
                    'funding_rate': float(item['funding_rate']),
                    'mark_price': float(item.get('mark_price', 0))
                })
            
            return pd.DataFrame(records)
        
        else:
            raise NotImplementedError(f"交易所 '{self.source}' 的 get_funding_rates 还未实现")


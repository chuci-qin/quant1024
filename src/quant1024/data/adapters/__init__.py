"""
Data source adapters - 数据源适配器

将不同数据源的API统一为标准接口
"""

from .base_adapter import BaseAdapter
from .exchange_adapter import ExchangeAdapter
from .finance_adapter import FinanceAdapter
from .blockchain_adapter import BlockchainAdapter


def get_adapter(source: str, **credentials):
    """
    工厂方法：根据数据源创建对应的适配器
    
    Args:
        source: 数据源名称
        **credentials: 认证信息
    
    Returns:
        适配器实例
    """
    # 交易所类
    if source in ['1024ex', 'binance', 'coinbase']:
        return ExchangeAdapter(source, **credentials)
    
    # 金融数据类
    elif source in ['yahoo', 'bloomberg', 'alphavantage']:
        return FinanceAdapter(source, **credentials)
    
    # 区块链类
    elif source in ['chainlink', 'thegraph']:
        return BlockchainAdapter(source, **credentials)
    
    else:
        raise ValueError(f"未知的数据源: {source}")


__all__ = [
    "BaseAdapter",
    "ExchangeAdapter",
    "FinanceAdapter",
    "BlockchainAdapter",
    "get_adapter"
]


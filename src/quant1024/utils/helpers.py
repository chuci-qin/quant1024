"""
Helper utility functions
"""

import re
from datetime import datetime
from typing import Optional


def validate_symbol(symbol: str) -> bool:
    """
    验证交易对符号格式
    
    Args:
        symbol: 交易对符号（如 BTC-PERP, ETH-PERP）
    
    Returns:
        是否有效
    """
    # 1024ex 格式: XXX-PERP
    pattern = r'^[A-Z0-9]+-PERP$'
    return bool(re.match(pattern, symbol))


def format_timestamp(timestamp: Optional[int] = None) -> str:
    """
    格式化时间戳
    
    Args:
        timestamp: Unix 时间戳（毫秒），None 则使用当前时间
    
    Returns:
        ISO 格式时间字符串
    """
    if timestamp is None:
        return datetime.utcnow().isoformat() + 'Z'
    
    dt = datetime.utcfromtimestamp(timestamp / 1000)
    return dt.isoformat() + 'Z'


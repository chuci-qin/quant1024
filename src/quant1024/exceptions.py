"""
Custom exceptions for quant1024
"""


class Quant1024Exception(Exception):
    """基础异常类"""
    pass


class AuthenticationError(Quant1024Exception):
    """认证错误"""
    pass


class RateLimitError(Quant1024Exception):
    """速率限制错误"""
    pass


class InvalidParameterError(Quant1024Exception):
    """参数错误"""
    pass


class InsufficientMarginError(Quant1024Exception):
    """保证金不足"""
    pass


class OrderNotFoundError(Quant1024Exception):
    """订单未找到"""
    pass


class MarketNotFoundError(Quant1024Exception):
    """市场未找到"""
    pass


class APIError(Quant1024Exception):
    """API 错误"""
    pass


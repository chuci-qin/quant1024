"""
quant1024 - A quantitative trading toolkit
"""

from .core import QuantStrategy, calculate_returns, calculate_sharpe_ratio

__version__ = "0.1.0"
__all__ = ["QuantStrategy", "calculate_returns", "calculate_sharpe_ratio"]


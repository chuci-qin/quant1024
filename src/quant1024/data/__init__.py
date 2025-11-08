"""
Data retrieval module for quant1024

支持多数据源的结构化数据获取，专为量化回测优化
"""

from .retriever import DataRetriever
from .dataset import BacktestDataset

__all__ = ["DataRetriever", "BacktestDataset"]


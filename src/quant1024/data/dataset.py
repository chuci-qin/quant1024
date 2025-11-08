"""
Backtest Dataset - 回测专用数据集

提供便捷的回测数据准备功能
"""

from typing import List, Dict, Optional, Union
from datetime import datetime
import pandas as pd


class BacktestDataset:
    """
    回测数据集
    
    专为回测场景设计，提供：
    - 批量数据获取
    - 时间戳对齐
    - 数据质量检查
    - 训练/测试集分割
    - 性能优化
    
    Examples:
        >>> from quant1024 import BacktestDataset
        >>> 
        >>> # 创建回测数据集
        >>> dataset = BacktestDataset(
        ...     source="yahoo",
        ...     symbols=["BTC-USD", "ETH-USD", "AAPL", "SPY"],
        ...     interval="1d",
        ...     days=365
        ... )
        >>> 
        >>> # 获取所有数据
        >>> data_dict = dataset.load()
        >>> 
        >>> # 分割训练/测试集
        >>> train, test = dataset.split(train_ratio=0.8)
    """
    
    def __init__(
        self,
        source: str = "yahoo",
        symbols: List[str] = None,
        interval: str = "1d",
        start_time: Optional[Union[datetime, str]] = None,
        end_time: Optional[Union[datetime, str]] = None,
        days: int = 365,
        enable_cache: bool = True,
        **source_credentials
    ):
        """
        初始化回测数据集
        
        Args:
            source: 数据源
            symbols: 标的列表
            interval: 时间间隔
            start_time: 开始时间
            end_time: 结束时间
            days: 最近N天
            enable_cache: 启用缓存（回测强烈推荐）
            **source_credentials: 数据源认证信息
        """
        from .retriever import DataRetriever
        
        self.source = source
        self.symbols = symbols or []
        self.interval = interval
        self.start_time = start_time
        self.end_time = end_time
        self.days = days
        self.enable_cache = enable_cache
        
        # 初始化数据获取器
        self.retriever = DataRetriever(
            source=source,
            enable_cache=enable_cache,
            **source_credentials
        )
        
        self._data = None
    
    def load(
        self,
        fill_missing: bool = True,
        validate_data: bool = True,
        add_indicators: bool = True,
        align_timestamps: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        加载所有数据
        
        Args:
            fill_missing: 填充缺失值
            validate_data: 验证数据
            add_indicators: 添加指标
            align_timestamps: 对齐时间戳
        
        Returns:
            Dict[symbol, DataFrame]
        """
        self._data = self.retriever.get_backtest_dataset(
            symbols=self.symbols,
            interval=self.interval,
            start_time=self.start_time,
            end_time=self.end_time,
            days=self.days,
            fill_missing=fill_missing,
            validate_data=validate_data,
            add_indicators=add_indicators,
            align_timestamps=align_timestamps
        )
        return self._data
    
    def split(
        self,
        train_ratio: float = 0.8,
        shuffle: bool = False
    ) -> tuple:
        """
        分割训练集和测试集
        
        Args:
            train_ratio: 训练集比例（0-1）
            shuffle: 是否随机打乱（回测一般不打乱）
        
        Returns:
            (train_dict, test_dict) - 训练集和测试集
        
        Examples:
            >>> dataset = BacktestDataset(symbols=["BTC-USD"], days=365)
            >>> dataset.load()
            >>> train, test = dataset.split(train_ratio=0.8)
            >>> print(f"训练集: {len(train['BTC-USD'])} 行")
            >>> print(f"测试集: {len(test['BTC-USD'])} 行")
        """
        if self._data is None:
            self.load()
        
        train_dict = {}
        test_dict = {}
        
        for symbol, df in self._data.items():
            split_idx = int(len(df) * train_ratio)
            
            if shuffle:
                df = df.sample(frac=1).reset_index(drop=True)
            
            train_dict[symbol] = df.iloc[:split_idx].reset_index(drop=True)
            test_dict[symbol] = df.iloc[split_idx:].reset_index(drop=True)
        
        return train_dict, test_dict
    
    def get_summary(self) -> pd.DataFrame:
        """
        获取数据集摘要
        
        Returns:
            DataFrame with summary statistics
        """
        if self._data is None:
            self.load()
        
        summaries = []
        for symbol, df in self._data.items():
            summary = {
                'symbol': symbol,
                'rows': len(df),
                'start_date': df['timestamp'].min(),
                'end_date': df['timestamp'].max(),
                'days': (df['timestamp'].max() - df['timestamp'].min()).days,
                'missing_values': df.isnull().sum().sum(),
                'avg_price': df['close'].mean() if 'close' in df.columns else None,
                'volatility': df['returns'].std() if 'returns' in df.columns else None,
            }
            summaries.append(summary)
        
        return pd.DataFrame(summaries)
    
    def to_csv(self, output_dir: str = "./backtest_data"):
        """
        导出为CSV文件
        
        Args:
            output_dir: 输出目录
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        if self._data is None:
            self.load()
        
        for symbol, df in self._data.items():
            # 安全的文件名
            safe_symbol = symbol.replace('/', '_').replace('-', '_')
            filepath = os.path.join(output_dir, f"{safe_symbol}_{self.interval}.csv")
            df.to_csv(filepath, index=False)
            print(f"已保存: {filepath}")
    
    def from_csv(self, input_dir: str = "./backtest_data"):
        """
        从CSV文件加载
        
        Args:
            input_dir: 输入目录
        """
        import os
        import glob
        
        self._data = {}
        
        pattern = os.path.join(input_dir, f"*_{self.interval}.csv")
        files = glob.glob(pattern)
        
        for filepath in files:
            df = pd.read_csv(filepath)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # 从文件名提取symbol
            filename = os.path.basename(filepath)
            symbol = filename.replace(f"_{self.interval}.csv", "").replace('_', '-')
            
            self._data[symbol] = df
        
        return self._data


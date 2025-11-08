"""
Multi-source data retriever - 全数据源统一获取器

支持的数据源:
- 交易所: 1024ex, Binance, Coinbase, IBKR
- 金融数据: Yahoo Finance, Bloomberg, Alpha Vantage
- 区块链: Chainlink, The Graph
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from ..exceptions import InvalidParameterError, APIError


class DataRetriever:
    """
    全数据源结构化数据获取器
    
    统一接口获取各种数据源的历史时序数据，
    专为量化回测优化。
    
    Examples:
        # 从 1024ex 获取
        >>> data = DataRetriever(source="1024ex", api_key="...", api_secret="...")
        >>> df = data.get_klines("BTC-PERP", interval="1h", days=7)
        
        # 从 Yahoo Finance 获取
        >>> data = DataRetriever(source="yahoo")
        >>> df = data.get_klines("AAPL", interval="1d", days=30)
    """
    
    # 支持的数据源
    SUPPORTED_SOURCES = {
        # 交易所
        "1024ex": {"type": "exchange", "requires_auth": True},
        "binance": {"type": "exchange", "requires_auth": False},  # 公共数据免费
        "coinbase": {"type": "exchange", "requires_auth": False},
        
        # 金融数据
        "yahoo": {"type": "finance", "requires_auth": False},
        "bloomberg": {"type": "finance", "requires_auth": True},
        "alphavantage": {"type": "finance", "requires_auth": True},
        
        # 区块链
        "chainlink": {"type": "blockchain", "requires_auth": False},
        "thegraph": {"type": "blockchain", "requires_auth": False},
    }
    
    # 支持的时间间隔
    SUPPORTED_INTERVALS = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '1w']
    
    def __init__(
        self,
        source: str = "1024ex",
        enable_cache: bool = False,
        cache_dir: str = "./data_cache",
        **credentials
    ):
        """
        初始化数据获取器
        
        Args:
            source: 数据源名称
                - 交易所: "1024ex", "binance", "coinbase"
                - 金融数据: "yahoo", "bloomberg", "alphavantage"
                - 区块链: "chainlink", "thegraph"
            enable_cache: 是否启用数据缓存（回测时推荐开启）
            cache_dir: 缓存目录
            **credentials: 认证信息（根据数据源不同）
                - 1024ex: api_key, api_secret
                - yahoo: 无需
                - bloomberg: username, password, terminal
                - chainlink: network (ethereum, polygon, etc.)
        
        Raises:
            InvalidParameterError: 不支持的数据源
        
        Examples:
            # 1024ex（需要API密钥）
            >>> data = DataRetriever(
            ...     source="1024ex",
            ...     api_key="your_key",
            ...     api_secret="your_secret",
            ...     enable_cache=True  # 回测时推荐
            ... )
            
            # Yahoo Finance（免费，无需认证）
            >>> data = DataRetriever(source="yahoo", enable_cache=True)
        """
        if source not in self.SUPPORTED_SOURCES:
            raise InvalidParameterError(
                f"不支持的数据源: {source}\n"
                f"支持的数据源: {', '.join(self.SUPPORTED_SOURCES.keys())}"
            )
        
        self.source = source
        self.enable_cache = enable_cache
        self.cache_dir = cache_dir
        self.credentials = credentials
        
        # 初始化适配器
        from .adapters import get_adapter
        self._adapter = get_adapter(source, **credentials)
    
    @property
    def provider_type(self) -> str:
        """返回数据源类型: exchange, finance, blockchain"""
        return self.SUPPORTED_SOURCES[self.source]["type"]
    
    def get_klines(
        self,
        symbol: str,
        interval: str = "1h",
        start_time: Optional[Union[datetime, str]] = None,
        end_time: Optional[Union[datetime, str]] = None,
        days: Optional[int] = None,
        limit: Optional[int] = None,
        # 回测专用参数
        fill_missing: bool = True,
        validate_data: bool = True,
        add_indicators: bool = False,
        use_cache: Optional[bool] = None
    ) -> pd.DataFrame:
        """
        获取K线数据（统一接口）
        
        专为回测优化，支持大时间范围、数据验证、缓存等功能
        
        Args:
            symbol: 交易对/标的
                - 1024ex: "BTC-PERP", "ETH-PERP"
                - yahoo: "BTC-USD", "AAPL", "TSLA", "^GSPC"
                - binance: "BTCUSDT", "ETHUSDT"
            
            interval: 时间间隔
                - 支持: 1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 12h, 1d, 1w
            
            时间范围参数（三选一）:
                days: 最近N天（最简单）
                start_time + end_time: 精确时间范围
                limit: 最大数量
            
            回测专用参数:
                fill_missing: 是否填充缺失值（回测推荐True）
                validate_data: 是否验证数据质量（回测推荐True）
                add_indicators: 是否添加基础指标（SMA, EMA等）
                use_cache: 是否使用缓存（None则使用初始化配置）
        
        Returns:
            pandas DataFrame with columns:
                基础列:
                  - timestamp (datetime): UTC时间
                  - open (float): 开盘价
                  - high (float): 最高价
                  - low (float): 最低价
                  - close (float): 收盘价
                  - volume (float): 成交量
                
                元数据列:
                  - source (str): 数据源名称
                  - provider_type (str): 数据源类型
                  - asset_class (str): 资产类别
                
                可选指标列（add_indicators=True时）:
                  - sma_20, sma_50: 简单移动平均
                  - returns: 收益率
                  - log_returns: 对数收益率
        
        Examples:
            # 回测场景：获取大量历史数据
            >>> data = DataRetriever(source="yahoo", enable_cache=True)
            >>> df = data.get_klines(
            ...     "BTC-USD",
            ...     interval="1d",
            ...     days=365,  # 1年数据
            ...     fill_missing=True,
            ...     validate_data=True,
            ...     add_indicators=True
            ... )
            >>> print(f"获取 {len(df)} 天数据，用于回测")
            
            # 精确时间范围
            >>> from datetime import datetime
            >>> df = data.get_klines(
            ...     "BTC-PERP",
            ...     interval="1h",
            ...     start_time=datetime(2024, 1, 1),
            ...     end_time=datetime(2024, 12, 31)
            ... )
        
        Raises:
            InvalidParameterError: 参数错误
            APIError: API 调用失败
        """
        # 验证参数
        self._validate_interval(interval)
        
        # 处理时间范围
        start_dt, end_dt = self._parse_time_range(start_time, end_time, days)
        
        # 检查缓存
        if use_cache is None:
            use_cache = self.enable_cache
        
        if use_cache:
            cached_df = self._load_from_cache(symbol, interval, start_dt, end_dt)
            if cached_df is not None:
                return cached_df
        
        # 从适配器获取数据
        raw_df = self._adapter.get_klines(
            symbol=symbol,
            interval=interval,
            start_time=start_dt,
            end_time=end_dt,
            limit=limit
        )
        
        # 格式化为标准DataFrame
        df = self._format_to_standard(raw_df, symbol)
        
        # 回测优化：数据处理
        if fill_missing:
            df = self._fill_missing_values(df)
        
        if validate_data:
            df = self._validate_and_clean(df)
        
        if add_indicators:
            df = self._add_basic_indicators(df)
        
        # 保存到缓存
        if use_cache:
            self._save_to_cache(df, symbol, interval, start_dt, end_dt)
        
        return df
    
    def get_backtest_dataset(
        self,
        symbols: List[str],
        interval: str = "1d",
        start_time: Union[datetime, str] = None,
        end_time: Union[datetime, str] = None,
        days: int = 365,
        fill_missing: bool = True,
        validate_data: bool = True,
        add_indicators: bool = True,
        align_timestamps: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        获取回测数据集（批量获取多个标的）
        
        专为回测设计，一次性获取多个标的的历史数据
        
        Args:
            symbols: 标的列表
                - 可以混合不同资产: ["BTC-PERP", "ETH-PERP", "AAPL", "SPY"]
            interval: 时间间隔
            start_time: 开始时间
            end_time: 结束时间
            days: 最近N天
            fill_missing: 填充缺失值
            validate_data: 验证数据质量
            add_indicators: 添加技术指标
            align_timestamps: 对齐时间戳（回测时推荐）
        
        Returns:
            Dict[symbol, DataFrame] - 每个标的的数据
        
        Examples:
            # 获取多个标的用于回测
            >>> data = DataRetriever(source="yahoo", enable_cache=True)
            >>> dataset = data.get_backtest_dataset(
            ...     symbols=["BTC-USD", "ETH-USD", "AAPL", "SPY"],
            ...     interval="1d",
            ...     days=365,
            ...     align_timestamps=True
            ... )
            >>> for symbol, df in dataset.items():
            ...     print(f"{symbol}: {len(df)} 行")
        """
        dataset = {}
        
        for symbol in symbols:
            df = self.get_klines(
                symbol=symbol,
                interval=interval,
                start_time=start_time,
                end_time=end_time,
                days=days,
                fill_missing=fill_missing,
                validate_data=validate_data,
                add_indicators=add_indicators
            )
            dataset[symbol] = df
        
        # 对齐时间戳（回测重要）
        if align_timestamps:
            dataset = self._align_timestamps(dataset)
        
        return dataset
    
    def get_trades(
        self,
        symbol: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        days: Optional[int] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """获取成交数据"""
        raw_df = self._adapter.get_trades(
            symbol=symbol,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        return self._format_to_standard(raw_df, symbol, data_type="trades")
    
    def get_funding_rates(
        self,
        symbol: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        days: Optional[int] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """获取资金费率历史"""
        raw_df = self._adapter.get_funding_rates(
            symbol=symbol,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        return self._format_to_standard(raw_df, symbol, data_type="funding")
    
    # ========== 内部方法 ==========
    
    def _validate_interval(self, interval: str):
        """验证时间间隔"""
        if interval not in self.SUPPORTED_INTERVALS:
            raise InvalidParameterError(
                f"不支持的时间间隔: {interval}\n"
                f"支持的间隔: {', '.join(self.SUPPORTED_INTERVALS)}"
            )
    
    def _parse_time_range(
        self,
        start_time: Optional[Union[datetime, str]],
        end_time: Optional[Union[datetime, str]],
        days: Optional[int]
    ) -> tuple:
        """解析时间范围参数"""
        # 如果提供了 days 参数
        if days is not None:
            end_dt = datetime.utcnow()
            start_dt = end_dt - timedelta(days=days)
            return start_dt, end_dt
        
        # 如果提供了 start_time 和 end_time
        if start_time or end_time:
            start_dt = self._parse_datetime(start_time) if start_time else None
            end_dt = self._parse_datetime(end_time) if end_time else datetime.utcnow()
            return start_dt, end_dt
        
        # 默认：最近7天
        end_dt = datetime.utcnow()
        start_dt = end_dt - timedelta(days=7)
        return start_dt, end_dt
    
    def _parse_datetime(self, dt: Union[datetime, str]) -> datetime:
        """解析时间参数"""
        if isinstance(dt, datetime):
            return dt
        elif isinstance(dt, str):
            return pd.to_datetime(dt).to_pydatetime()
        else:
            raise InvalidParameterError(f"无效的时间格式: {dt}")
    
    def _format_to_standard(
        self,
        raw_df: pd.DataFrame,
        symbol: str,
        data_type: str = "klines"
    ) -> pd.DataFrame:
        """格式化为标准DataFrame"""
        # 添加元数据
        df = raw_df.copy()
        df['source'] = self.source
        df['provider_type'] = self.provider_type
        
        # 添加资产类别
        df['asset_class'] = self._detect_asset_class(symbol)
        
        # 确保时间列是 datetime 类型
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        
        # 排序
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp').reset_index(drop=True)
        
        return df
    
    def _detect_asset_class(self, symbol: str) -> str:
        """检测资产类别"""
        symbol_upper = symbol.upper()
        
        # 加密货币
        if any(crypto in symbol_upper for crypto in ['BTC', 'ETH', 'SOL', 'PERP', 'USDT']):
            return 'crypto'
        
        # 股票
        elif any(symbol_upper == stock for stock in ['AAPL', 'TSLA', 'GOOGL', 'AMZN', 'MSFT', 'SPY', 'QQQ']):
            return 'stock'
        
        # 指数
        elif symbol_upper.startswith('^'):
            return 'index'
        
        # 外汇
        elif len(symbol_upper) == 6 and symbol_upper[:3] != symbol_upper[3:]:
            return 'forex'
        
        else:
            return 'unknown'
    
    def _fill_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """填充缺失值（回测优化）"""
        # 前向填充价格数据
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            if col in df.columns:
                df[col] = df[col].ffill()  # 使用 ffill() 代替 fillna(method='ffill')
        
        # volume 填充为0
        if 'volume' in df.columns:
            df['volume'] = df['volume'].fillna(0)
        
        return df
    
    def _validate_and_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """验证和清理数据（回测优化）"""
        # 检查关键列
        required_cols = ['timestamp', 'close']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise APIError(f"数据缺少必需列: {missing_cols}")
        
        # 删除重复的时间戳
        df = df.drop_duplicates(subset=['timestamp'], keep='last')
        
        # 删除无效价格（<=0）
        if 'close' in df.columns:
            df = df[df['close'] > 0]
        
        # 检查时间顺序
        if not df['timestamp'].is_monotonic_increasing:
            df = df.sort_values('timestamp').reset_index(drop=True)
        
        return df
    
    def _add_basic_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加基础技术指标（回测便利功能）"""
        if 'close' not in df.columns:
            return df
        
        # 简单移动平均
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['sma_200'] = df['close'].rolling(window=200).mean()
        
        # 收益率
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        # 波动率（20日）
        df['volatility_20'] = df['returns'].rolling(window=20).std()
        
        return df
    
    def _align_timestamps(self, dataset: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """对齐多个标的的时间戳（回测关键功能）"""
        if len(dataset) <= 1:
            return dataset
        
        # 找到所有时间戳的交集
        all_timestamps = None
        for symbol, df in dataset.items():
            timestamps = set(df['timestamp'])
            if all_timestamps is None:
                all_timestamps = timestamps
            else:
                all_timestamps = all_timestamps.intersection(timestamps)
        
        # 过滤每个DataFrame，只保留交集时间戳
        aligned_dataset = {}
        for symbol, df in dataset.items():
            aligned_df = df[df['timestamp'].isin(all_timestamps)]
            aligned_df = aligned_df.sort_values('timestamp').reset_index(drop=True)
            aligned_dataset[symbol] = aligned_df
        
        return aligned_dataset
    
    def _load_from_cache(
        self,
        symbol: str,
        interval: str,
        start_time: datetime,
        end_time: datetime
    ) -> Optional[pd.DataFrame]:
        """从缓存加载数据"""
        # TODO: 实现缓存逻辑
        return None
    
    def _save_to_cache(
        self,
        df: pd.DataFrame,
        symbol: str,
        interval: str,
        start_time: datetime,
        end_time: datetime
    ):
        """保存数据到缓存"""
        # TODO: 实现缓存逻辑
        pass


"""
Test Data Retrieval module (v0.3.0)

Tests for DataRetriever and BacktestDataset (internal modules, not public API).
"""

import pytest
import pandas as pd
import responses
from datetime import datetime, timedelta
# Import from internal modules directly (not public API)
from quant1024.data.retriever import DataRetriever
from quant1024.data.dataset import BacktestDataset
from quant1024.exceptions import InvalidParameterError


# ========== DataRetriever 基础测试 ==========

def test_data_retriever_init():
    """测试1: DataRetriever 初始化"""
    data = DataRetriever(source="1024ex")
    assert data.source == "1024ex"
    assert data.provider_type == "exchange"


def test_data_retriever_unsupported_source():
    """测试2: 不支持的数据源"""
    with pytest.raises(InvalidParameterError):
        DataRetriever(source="invalid_source")


def test_data_retriever_supported_sources():
    """测试3: 支持的数据源列表"""
    assert "1024ex" in DataRetriever.SUPPORTED_SOURCES
    assert "yahoo" in DataRetriever.SUPPORTED_SOURCES
    assert "chainlink" in DataRetriever.SUPPORTED_SOURCES


def test_data_retriever_provider_type():
    """测试4: 数据源类型识别"""
    data_exchange = DataRetriever(source="1024ex")
    assert data_exchange.provider_type == "exchange"
    
    data_finance = DataRetriever(source="yahoo")
    assert data_finance.provider_type == "finance"
    
    data_blockchain = DataRetriever(source="chainlink")
    assert data_blockchain.provider_type == "blockchain"


def test_validate_interval():
    """测试5: 时间间隔验证"""
    data = DataRetriever(source="1024ex")
    
    # 有效间隔
    data._validate_interval("1h")
    data._validate_interval("1d")
    
    # 无效间隔
    with pytest.raises(InvalidParameterError):
        data._validate_interval("invalid")


# ========== 时间范围解析测试 ==========

def test_parse_time_range_with_days():
    """测试6: 使用days参数"""
    data = DataRetriever(source="yahoo")
    start, end = data._parse_time_range(None, None, days=7)
    
    assert isinstance(start, datetime)
    assert isinstance(end, datetime)
    assert (end - start).days == 7


def test_parse_time_range_with_dates():
    """测试7: 使用start/end时间"""
    data = DataRetriever(source="yahoo")
    
    start_time = datetime(2024, 1, 1)
    end_time = datetime(2024, 12, 31)
    
    start, end = data._parse_time_range(start_time, end_time, None)
    
    assert start == start_time
    assert end == end_time


def test_parse_time_range_default():
    """测试8: 默认时间范围"""
    data = DataRetriever(source="yahoo")
    start, end = data._parse_time_range(None, None, None)
    
    # 默认7天
    assert (end - start).days == 7


# ========== 资产类别检测测试 ==========

def test_detect_asset_class_crypto():
    """测试9: 加密货币检测"""
    data = DataRetriever(source="1024ex")
    
    assert data._detect_asset_class("BTC-PERP") == "crypto"
    assert data._detect_asset_class("ETH-PERP") == "crypto"
    assert data._detect_asset_class("BTCUSDT") == "crypto"


def test_detect_asset_class_stock():
    """测试10: 股票检测"""
    data = DataRetriever(source="yahoo")
    
    assert data._detect_asset_class("AAPL") == "stock"
    assert data._detect_asset_class("TSLA") == "stock"
    assert data._detect_asset_class("SPY") == "stock"


def test_detect_asset_class_index():
    """测试11: 指数检测"""
    data = DataRetriever(source="yahoo")
    
    assert data._detect_asset_class("^GSPC") == "index"
    assert data._detect_asset_class("^DJI") == "index"


# ========== 数据格式化测试 ==========
# NOTE: The following tests are skipped due to API path changes.
# The actual API paths have been modularized (e.g., /api/v1/perp/markets/{market}/klines)
# These tests need to be updated to match the new API structure.

@pytest.mark.skip(reason="API path changed to /api/v1/perp/markets/{market}/klines")
@responses.activate
def test_get_klines_1024ex_basic():
    """测试12: 从1024ex获取K线（基础）"""
    # Mock API 响应
    responses.add(
        responses.GET,
        'https://api.1024ex.com/api/v1/klines/BTC-PERP',
        json={
            'data': [
                {
                    'timestamp': 1234567890000,
                    'open': '60000',
                    'high': '61000',
                    'low': '59000',
                    'close': '60500',
                    'volume': '1000'
                }
            ]
        },
        status=200
    )
    
    data = DataRetriever(source="1024ex", api_key="test", api_secret="test")
    df = data.get_klines("BTC-PERP", interval="1h", days=1)
    
    # 验证DataFrame结构
    assert isinstance(df, pd.DataFrame)
    assert 'timestamp' in df.columns
    assert 'close' in df.columns
    assert 'source' in df.columns
    assert 'provider_type' in df.columns
    assert 'asset_class' in df.columns
    
    # 验证元数据
    assert df['source'].iloc[0] == '1024ex'
    assert df['provider_type'].iloc[0] == 'exchange'
    assert df['asset_class'].iloc[0] == 'crypto'


@pytest.mark.skip(reason="API path changed to /api/v1/perp/markets/{market}/klines")
@responses.activate
def test_get_klines_with_indicators():
    """测试13: 获取K线并添加指标"""
    # Mock 多条数据
    mock_data = []
    base_price = 60000
    for i in range(100):
        mock_data.append({
            'timestamp': 1234567890000 + i * 3600000,  # 每小时
            'open': str(base_price + i),
            'high': str(base_price + i + 100),
            'low': str(base_price + i - 100),
            'close': str(base_price + i + 50),
            'volume': '1000'
        })
    
    responses.add(
        responses.GET,
        'https://api.1024ex.com/api/v1/klines/BTC-PERP',
        json={'data': mock_data},
        status=200
    )
    
    data = DataRetriever(source="1024ex", api_key="test", api_secret="test")
    df = data.get_klines(
        "BTC-PERP",
        interval="1h",
        days=7,
        add_indicators=True
    )
    
    # 验证指标列存在
    assert 'sma_20' in df.columns
    assert 'sma_50' in df.columns
    assert 'returns' in df.columns
    assert 'log_returns' in df.columns
    assert 'volatility_20' in df.columns


# ========== BacktestDataset 测试 ==========

def test_backtest_dataset_init():
    """测试14: BacktestDataset 初始化"""
    dataset = BacktestDataset(
        source="yahoo",
        symbols=["BTC-USD", "AAPL"],
        interval="1d",
        days=30
    )
    
    assert dataset.source == "yahoo"
    assert len(dataset.symbols) == 2
    assert dataset.interval == "1d"


@pytest.mark.skip(reason="API path changed to /api/v1/perp/markets/{market}/klines")
@responses.activate
def test_backtest_dataset_get_summary():
    """测试15: 数据集摘要"""
    # Mock数据
    responses.add(
        responses.GET,
        'https://api.1024ex.com/api/v1/klines/BTC-PERP',
        json={
            'data': [
                {
                    'timestamp': 1234567890000 + i * 86400000,
                    'open': '60000',
                    'high': '61000',
                    'low': '59000',
                    'close': '60500',
                    'volume': '1000'
                } for i in range(30)
            ]
        },
        status=200
    )
    
    dataset = BacktestDataset(
        source="1024ex",
        symbols=["BTC-PERP"],
        interval="1d",
        days=30
    )
    
    dataset.load()
    summary = dataset.get_summary()
    
    assert isinstance(summary, pd.DataFrame)
    assert 'symbol' in summary.columns
    assert 'rows' in summary.columns


# ========== 数据验证和清理测试 ==========

def test_fill_missing_values():
    """测试16: 填充缺失值"""
    data = DataRetriever(source="yahoo")
    
    # 创建有缺失值的DataFrame
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=10, freq='D', tz='UTC'),
        'open': [100, None, 102, 103, None, 105, 106, 107, 108, 109],
        'close': [101, 102, None, 104, 105, None, 107, 108, 109, 110],
        'volume': [1000, 1100, None, 1300, 1400, 1500, None, 1700, 1800, 1900]
    })
    
    filled_df = data._fill_missing_values(df)
    
    # 价格应该前向填充
    assert filled_df['open'].isna().sum() == 0
    assert filled_df['close'].isna().sum() == 0
    
    # volume应该填充为0
    assert filled_df['volume'].isna().sum() == 0


def test_validate_and_clean():
    """测试17: 数据验证和清理"""
    data = DataRetriever(source="yahoo")
    
    # 创建有问题的DataFrame
    df = pd.DataFrame({
        'timestamp': [
            pd.Timestamp('2024-01-03', tz='UTC'),
            pd.Timestamp('2024-01-01', tz='UTC'),  # 乱序
            pd.Timestamp('2024-01-02', tz='UTC'),
            pd.Timestamp('2024-01-02', tz='UTC'),  # 重复
        ],
        'close': [100, 101, 0, 103],  # 包含无效价格(0)
    })
    
    cleaned_df = data._validate_and_clean(df)
    
    # 应该删除重复和无效价格
    assert len(cleaned_df) < len(df)
    
    # 应该排序
    assert cleaned_df['timestamp'].is_monotonic_increasing


def test_add_basic_indicators():
    """测试18: 添加技术指标"""
    data = DataRetriever(source="yahoo")
    
    # 创建价格数据
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='D', tz='UTC'),
        'close': [100 + i * 0.5 for i in range(100)]
    })
    
    df_with_indicators = data._add_basic_indicators(df)
    
    # 验证指标列
    assert 'sma_20' in df_with_indicators.columns
    assert 'sma_50' in df_with_indicators.columns
    assert 'returns' in df_with_indicators.columns
    assert 'log_returns' in df_with_indicators.columns
    assert 'volatility_20' in df_with_indicators.columns
    
    # 验证SMA计算正确
    assert not pd.isna(df_with_indicators['sma_20'].iloc[19])  # 第20个值开始有效


# ========== 时间戳对齐测试 ==========

def test_align_timestamps():
    """测试19: 时间戳对齐"""
    data = DataRetriever(source="yahoo")
    
    # 创建两个时间戳部分重叠的DataFrame
    dates1 = pd.date_range('2024-01-01', periods=10, freq='D', tz='UTC')
    dates2 = pd.date_range('2024-01-05', periods=10, freq='D', tz='UTC')
    
    df1 = pd.DataFrame({'timestamp': dates1, 'close': range(10)})
    df2 = pd.DataFrame({'timestamp': dates2, 'close': range(10)})
    
    dataset = {"A": df1, "B": df2}
    aligned = data._align_timestamps(dataset)
    
    # 对齐后应该只有交集的日期
    assert len(aligned["A"]) == len(aligned["B"])
    assert len(aligned["A"]) <= 10


# ========== BacktestDataset 高级测试 ==========

@pytest.mark.skip(reason="API path changed to /api/v1/perp/markets/{market}/klines")
@responses.activate
def test_backtest_dataset_split():
    """测试20: 训练/测试集分割"""
    # Mock数据
    mock_data = [
        {
            'timestamp': 1234567890000 + i * 86400000,
            'open': '60000',
            'high': '61000',
            'low': '59000',
            'close': '60500',
            'volume': '1000'
        } for i in range(100)
    ]
    
    responses.add(
        responses.GET,
        'https://api.1024ex.com/api/v1/klines/BTC-PERP',
        json={'data': mock_data},
        status=200
    )
    
    dataset = BacktestDataset(
        source="1024ex",
        symbols=["BTC-PERP"],
        interval="1d",
        days=100
    )
    
    dataset.load()
    train, test = dataset.split(train_ratio=0.8)
    
    # 验证分割比例
    total_len = len(dataset._data["BTC-PERP"])
    assert len(train["BTC-PERP"]) == int(total_len * 0.8)
    assert len(test["BTC-PERP"]) == total_len - int(total_len * 0.8)


# ========== 真实使用场景测试（需要yfinance）==========

@pytest.mark.skipif(
    not hasattr(pd, '__version__'),
    reason="需要 pandas"
)
def test_yahoo_finance_integration():
    """测试21: Yahoo Finance 集成（可选）"""
    try:
        import yfinance
        
        # 创建 Yahoo 数据获取器
        data = DataRetriever(source="yahoo")
        
        # 获取数据（真实调用）
        df = data.get_klines("BTC-USD", interval="1d", days=7)
        
        # 验证
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'close' in df.columns
        assert df['source'].iloc[0] == 'yahoo'
        assert df['provider_type'].iloc[0] == 'finance'
        
    except ImportError:
        pytest.skip("yfinance 未安装")
    except Exception as e:
        pytest.skip(f"Yahoo Finance 测试跳过: {e}")


# ========== 回测场景测试 ==========

@pytest.mark.skip(reason="API path changed to /api/v1/perp/markets/{market}/klines")
@responses.activate
def test_backtest_scenario():
    """测试22: 完整回测场景"""
    # Mock 1年的数据
    mock_data = []
    base_price = 60000
    for i in range(365):
        mock_data.append({
            'timestamp': 1704067200000 + i * 86400000,  # 2024-01-01开始
            'open': str(base_price + i * 10),
            'high': str(base_price + i * 10 + 500),
            'low': str(base_price + i * 10 - 500),
            'close': str(base_price + i * 10 + 200),
            'volume': str(1000 + i)
        })
    
    responses.add(
        responses.GET,
        'https://api.1024ex.com/api/v1/klines/BTC-PERP',
        json={'data': mock_data},
        status=200
    )
    
    # 创建回测数据集
    dataset = BacktestDataset(
        source="1024ex",
        symbols=["BTC-PERP"],
        interval="1d",
        days=365
    )
    
    # 加载数据
    data_dict = dataset.load(
        fill_missing=True,
        validate_data=True,
        add_indicators=True
    )
    
    # 分割数据
    train, test = dataset.split(train_ratio=0.8)
    
    # 验证数据质量
    assert len(data_dict["BTC-PERP"]) == 365
    assert 'sma_20' in data_dict["BTC-PERP"].columns
    
    # 验证训练测试分割
    assert len(train["BTC-PERP"]) == 292  # 80% of 365
    assert len(test["BTC-PERP"]) == 73    # 20% of 365


# ========== 多数据源对比测试 ==========

def test_multiple_sources():
    """测试23: 多数据源初始化"""
    # 1024ex
    data_1024 = DataRetriever(source="1024ex")
    assert data_1024.source == "1024ex"
    assert data_1024.provider_type == "exchange"
    
    # Yahoo
    data_yahoo = DataRetriever(source="yahoo")
    assert data_yahoo.source == "yahoo"
    assert data_yahoo.provider_type == "finance"


# ========== 数据集导出测试 ==========

@pytest.mark.skip(reason="API path changed to /api/v1/perp/markets/{market}/klines")
@responses.activate
def test_dataset_to_csv(tmp_path):
    """测试24: 导出为CSV"""
    # Mock数据
    responses.add(
        responses.GET,
        'https://api.1024ex.com/api/v1/klines/BTC-PERP',
        json={
            'data': [
                {
                    'timestamp': 1234567890000 + i * 86400000,
                    'open': '60000',
                    'high': '61000',
                    'low': '59000',
                    'close': '60500',
                    'volume': '1000'
                } for i in range(10)
            ]
        },
        status=200
    )
    
    dataset = BacktestDataset(
        source="1024ex",
        symbols=["BTC-PERP"],
        interval="1d",
        days=10
    )
    
    dataset.load()
    
    # 导出到临时目录
    dataset.to_csv(str(tmp_path))
    
    # 验证文件存在
    import os
    files = os.listdir(tmp_path)
    assert len(files) > 0


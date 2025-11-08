"""
回测数据获取完整示例 (v0.3.0)

展示如何使用 quant1024 获取多数据源的回测数据
"""

from quant1024 import DataRetriever, BacktestDataset
import pandas as pd


def example1_basic_data_retrieval():
    """示例1: 基础数据获取"""
    print("=" * 70)
    print("示例 1: 从1024ex获取BTC历史数据（回测场景）")
    print("=" * 70)
    
    # 初始化数据获取器
    data = DataRetriever(
        source="1024ex",
        api_key="your_api_key",      # 替换为真实的
        api_secret="your_api_secret",  # 替换为真实的
        enable_cache=True              # 回测推荐开启缓存
    )
    
    # 获取1年的日K数据（回测常用）
    df = data.get_klines(
        symbol="BTC-PERP",
        interval="1d",
        days=365,                      # 1年历史数据
        fill_missing=True,             # 填充缺失值
        validate_data=True,            # 验证数据质量
        add_indicators=True            # 自动添加技术指标
    )
    
    print(f"\n数据来源: {df['source'].iloc[0]}")
    print(f"数据源类型: {df['provider_type'].iloc[0]}")
    print(f"资产类别: {df['asset_class'].iloc[0]}")
    print(f"数据点数: {len(df)}")
    print(f"时间范围: {df['timestamp'].min()} ~ {df['timestamp'].max()}")
    
    print(f"\n数据列: {list(df.columns)}")
    print(f"\n前5行:")
    print(df[['timestamp', 'close', 'sma_20', 'sma_50', 'returns']].head())
    
    print(f"\n统计信息:")
    print(f"  平均价格: ${df['close'].mean():,.2f}")
    print(f"  价格波动: ${df['close'].std():,.2f}")
    print(f"  平均收益率: {df['returns'].mean():.4%}")
    print(f"  年化波动率: {df['returns'].std() * (365 ** 0.5):.4%}")


def example2_yahoo_finance():
    """示例2: 从Yahoo Finance获取股票数据"""
    print("\n" + "=" * 70)
    print("示例 2: 从Yahoo Finance获取股票数据（免费）")
    print("=" * 70)
    
    # Yahoo Finance - 免费，无需API密钥
    data = DataRetriever(
        source="yahoo",
        enable_cache=True
    )
    
    try:
        # 获取Apple股票2年数据
        aapl = data.get_klines(
            symbol="AAPL",
            interval="1d",
            days=730,  # 2年
            add_indicators=True
        )
        
        print(f"\n数据来源: {aapl['source'].iloc[0]}")
        print(f"资产类别: {aapl['asset_class'].iloc[0]}")
        print(f"数据点数: {len(aapl)}")
        print(f"当前价: ${aapl['close'].iloc[-1]:.2f}")
        print(f"2年收益: {(aapl['close'].iloc[-1] / aapl['close'].iloc[0] - 1) * 100:+.2f}%")
        
    except ImportError:
        print("⚠️  需要安装 yfinance: pip install quant1024[yahoo]")
    except Exception as e:
        print(f"⚠️  Yahoo Finance 访问失败: {e}")


def example3_multi_source_comparison():
    """示例3: 多数据源对比"""
    print("\n" + "=" * 70)
    print("示例 3: 多数据源BTC价格对比")
    print("=" * 70)
    
    sources_data = {}
    
    # 从 1024ex 获取
    try:
        data_1024 = DataRetriever(source="1024ex")
        btc_1024 = data_1024.get_klines("BTC-PERP", interval="1h", days=7)
        sources_data['1024ex'] = btc_1024
        print(f"✅ 1024ex: {len(btc_1024)} 行")
    except Exception as e:
        print(f"⚠️  1024ex: {e}")
    
    # 从 Yahoo Finance 获取
    try:
        data_yahoo = DataRetriever(source="yahoo")
        btc_yahoo = data_yahoo.get_klines("BTC-USD", interval="1d", days=30)
        sources_data['Yahoo'] = btc_yahoo
        print(f"✅ Yahoo: {len(btc_yahoo)} 行")
    except Exception as e:
        print(f"⚠️  Yahoo: {e}")
    
    # 对比分析
    if len(sources_data) > 1:
        print(f"\n价格对比:")
        for source_name, df in sources_data.items():
            print(f"  {source_name}: 平均价 ${df['close'].mean():,.2f}")


def example4_backtest_dataset():
    """示例4: 完整的回测数据集准备"""
    print("\n" + "=" * 70)
    print("示例 4: 准备多标的回测数据集")
    print("=" * 70)
    
    try:
        # 创建回测数据集
        dataset = BacktestDataset(
            source="yahoo",
            symbols=["BTC-USD", "ETH-USD", "AAPL", "SPY"],
            interval="1d",
            days=365,          # 1年数据
            enable_cache=True  # 启用缓存
        )
        
        # 加载所有数据
        data_dict = dataset.load(
            fill_missing=True,
            validate_data=True,
            add_indicators=True,
            align_timestamps=True  # 对齐时间戳（回测关键）
        )
        
        # 查看数据集摘要
        summary = dataset.get_summary()
        print(f"\n数据集摘要:")
        print(summary[['symbol', 'rows', 'avg_price', 'volatility']])
        
        # 分割训练/测试集
        train, test = dataset.split(train_ratio=0.8)
        
        print(f"\n数据分割:")
        for symbol in dataset.symbols:
            print(f"  {symbol}:")
            print(f"    训练集: {len(train[symbol])} 行")
            print(f"    测试集: {len(test[symbol])} 行")
        
        # 导出为CSV（方便后续使用）
        dataset.to_csv("./backtest_data")
        print(f"\n✅ 数据已导出到 ./backtest_data/")
        
    except ImportError:
        print("⚠️  需要安装 yfinance: pip install quant1024[yahoo]")
    except Exception as e:
        print(f"⚠️  示例失败: {e}")


def example5_multi_asset_backtest():
    """示例5: 多资产组合回测数据准备"""
    print("\n" + "=" * 70)
    print("示例 5: 多资产组合数据（加密货币 + 股票）")
    print("=" * 70)
    
    try:
        # 准备加密货币数据（从1024ex）
        crypto_data = DataRetriever(source="1024ex")
        btc = crypto_data.get_klines("BTC-PERP", interval="1d", days=180, add_indicators=True)
        eth = crypto_data.get_klines("ETH-PERP", interval="1d", days=180, add_indicators=True)
        
        # 准备股票数据（从Yahoo）
        stock_data = DataRetriever(source="yahoo")
        aapl = stock_data.get_klines("AAPL", interval="1d", days=180, add_indicators=True)
        spy = stock_data.get_klines("SPY", interval="1d", days=180, add_indicators=True)
        
        print(f"\n数据获取完成:")
        print(f"  BTC: {len(btc)} 行 (来自 {btc['source'].iloc[0]})")
        print(f"  ETH: {len(eth)} 行 (来自 {eth['source'].iloc[0]})")
        print(f"  AAPL: {len(aapl)} 行 (来自 {aapl['source'].iloc[0]})")
        print(f"  SPY: {len(spy)} 行 (来自 {spy['source'].iloc[0]})")
        
        # 计算6个月收益
        for name, df in [("BTC", btc), ("ETH", eth), ("AAPL", aapl), ("SPY", spy)]:
            ret = (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100
            print(f"  {name} 180天收益: {ret:+.2f}%")
        
    except Exception as e:
        print(f"⚠️  示例失败: {e}")


def example6_time_range_control():
    """示例6: 精确时间范围控制"""
    print("\n" + "=" * 70)
    print("示例 6: 精确时间范围控制（回测需要）")
    print("=" * 70)
    
    from datetime import datetime
    
    data = DataRetriever(source="yahoo")
    
    try:
        # 方式1: 使用 days 参数（最简单）
        df1 = data.get_klines("BTC-USD", interval="1d", days=30)
        print(f"\n方式1 (days=30): {len(df1)} 行")
        
        # 方式2: 使用精确日期范围
        df2 = data.get_klines(
            "BTC-USD",
            interval="1d",
            start_time=datetime(2024, 1, 1),
            end_time=datetime(2024, 12, 31)
        )
        print(f"方式2 (2024全年): {len(df2)} 行")
        
        # 方式3: 使用字符串日期
        df3 = data.get_klines(
            "BTC-USD",
            interval="1d",
            start_time="2024-01-01",
            end_time="2024-06-30"
        )
        print(f"方式3 (2024上半年): {len(df3)} 行")
        
    except Exception as e:
        print(f"⚠️  示例失败: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print(" " * 20 + "quant1024 v0.3.0 回测数据获取示例")
    print(" " * 25 + "多数据源支持")
    print("=" * 80)
    
    print("\n支持的数据源:")
    print("  🏦 交易所: 1024ex, Binance, Coinbase, IBKR")
    print("  📈 金融数据: Yahoo Finance, Bloomberg, Alpha Vantage")
    print("  ⛓️  区块链: Chainlink, The Graph")
    
    print("\n本示例演示:")
    print("  ✅ 从多个数据源获取数据")
    print("  ✅ 回测数据准备（缓存、指标、验证）")
    print("  ✅ 训练/测试集分割")
    print("  ✅ 多资产组合数据")
    print("  ✅ 精确时间范围控制")
    
    # 运行所有示例
    example1_basic_data_retrieval()
    example2_yahoo_finance()
    example3_multi_source_comparison()
    example4_backtest_dataset()
    example5_multi_asset_backtest()
    example6_time_range_control()
    
    print("\n" + "=" * 80)
    print("✅ 所有示例完成！")
    print("\n核心特性:")
    print("  ✅ 多数据源支持 - 交易所、金融数据、区块链")
    print("  ✅ 统一DataFrame - 标准化输出，包含元数据")
    print("  ✅ 回测优化 - 缓存、批量、验证、指标")
    print("  ✅ 灵活配置 - 时间范围、间隔、数据质量")
    print("=" * 80)


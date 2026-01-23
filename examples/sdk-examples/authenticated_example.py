#!/usr/bin/env python3
"""
quant1024 SDK 认证示例

使用 1024-trading-api-key-quant.json 配置文件进行 API 认证。

使用方法:
    cd quant1024
    source .venv/bin/activate
    python examples/sdk-examples/authenticated_example.py
"""

import json
import os
import sys
from pathlib import Path

from quant1024 import Exchange1024ex


def load_api_config(config_path: str = None) -> dict:
    """
    加载 API 配置文件
    
    Args:
        config_path: 配置文件路径，默认查找项目根目录的 1024-trading-api-key-quant.json
    
    Returns:
        配置字典 {api_key, secret_key, label, permissions, ...}
    """
    if config_path is None:
        # 默认查找项目根目录 (1024ex/)
        # 路径: examples/sdk-examples/authenticated_example.py -> quant1024 -> 1024ex
        config_path = Path(__file__).parent.parent.parent.parent / "1024-trading-api-key-quant.json"
    
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # 验证必要字段
    required_fields = ["api_key", "secret_key"]
    for field in required_fields:
        if field not in config:
            raise ValueError(f"配置文件缺少必要字段: {field}")
    
    return config


def main():
    print("=" * 60)
    print("🔐 quant1024 SDK 认证示例")
    print("=" * 60)
    
    # 1. 加载配置
    print("\n📄 加载 API 配置...")
    try:
        config = load_api_config()
        print(f"  ✅ 配置加载成功")
        print(f"  📋 Label: {config.get('label', 'N/A')}")
        print(f"  🔑 API Key: {config['api_key'][:20]}...")
        print(f"  📝 权限: 读取={config['permissions']['can_read']}, "
              f"交易={config['permissions']['can_trade']}, "
              f"提现={config['permissions']['can_withdraw']}")
    except FileNotFoundError as e:
        print(f"  ❌ {e}")
        return 1
    except Exception as e:
        print(f"  ❌ 配置加载失败: {e}")
        return 1
    
    # 2. 初始化 SDK
    print("\n🚀 初始化 Exchange1024ex 客户端...")
    exchange = Exchange1024ex(
        api_key=config["api_key"],
        secret_key=config["secret_key"],
        base_url="https://api.1024ex.com"
    )
    print(f"  ✅ 客户端初始化完成")
    
    # 3. 测试公开接口
    print("\n📊 测试公开接口...")
    print("-" * 50)
    
    try:
        # 获取永续合约市场
        markets = exchange.perp.get_markets()
        print(f"  ✅ 永续合约市场: {len(markets)} 个")
        
        # 获取 BTC 行情
        ticker = exchange.perp.get_ticker("BTC-USDC")
        last_price = ticker.get("data", {}).get("last_price", "N/A")
        print(f"  ✅ BTC-USDC 最新价: ${last_price}")
        
        # 获取锦标赛
        championships = exchange.championship.list_championships(status="active")
        print(f"  ✅ 活跃锦标赛: {len(championships)} 个")
        
    except Exception as e:
        print(f"  ❌ 公开接口测试失败: {e}")
    
    # 4. 测试认证接口
    print("\n🔒 测试认证接口...")
    print("-" * 50)
    
    try:
        # 获取账户概览
        overview = exchange.account.get_overview()
        if overview.get("success"):
            data = overview.get("data", {})
            wallet = data.get("wallet_address", "N/A")[:20] + "..." if data.get("wallet_address") else "N/A"
            print(f"  ✅ 账户概览: 钱包 {wallet}")
        else:
            print(f"  ⚠️  账户概览: {overview.get('message', '未知错误')}")
    except Exception as e:
        print(f"  ❌ 账户概览: {e}")
    
    try:
        # 获取 Perp 保证金
        margin = exchange.account.get_perp_margin()
        if margin.get("success"):
            data = margin.get("data", {})
            total = data.get("total_margin", "N/A")
            available = data.get("available_margin", "N/A")
            print(f"  ✅ Perp 保证金: 总计 {total}, 可用 {available}")
        else:
            print(f"  ⚠️  Perp 保证金: {margin.get('message', '未知错误')}")
    except Exception as e:
        print(f"  ❌ Perp 保证金: {e}")
    
    try:
        # 获取持仓
        positions = exchange.perp.get_positions()
        if isinstance(positions, list):
            print(f"  ✅ 当前持仓: {len(positions)} 个")
            for pos in positions[:3]:  # 显示前3个
                market = pos.get("market", "N/A")
                side = pos.get("side", "N/A")
                size = pos.get("size", "N/A")
                print(f"      - {market}: {side} {size}")
        else:
            print(f"  ✅ 当前持仓: 无")
    except Exception as e:
        print(f"  ❌ 当前持仓: {e}")
    
    try:
        # 获取活跃订单
        orders = exchange.perp.get_orders()
        if isinstance(orders, list):
            print(f"  ✅ 活跃订单: {len(orders)} 个")
        else:
            print(f"  ✅ 活跃订单: 无")
    except Exception as e:
        print(f"  ❌ 活跃订单: {e}")
    
    # 5. 测试预测市场
    print("\n🎯 测试预测市场...")
    print("-" * 50)
    
    try:
        # 获取市场列表
        pm_markets = exchange.prediction.list_markets(status="active", page_size=5)
        if isinstance(pm_markets, list):
            print(f"  ✅ 活跃预测市场: {len(pm_markets)} 个")
        elif isinstance(pm_markets, dict):
            markets_data = pm_markets.get("data", {}).get("markets", [])
            print(f"  ✅ 活跃预测市场: {len(markets_data)} 个")
        else:
            print(f"  ✅ 活跃预测市场: 0 个")
    except Exception as e:
        print(f"  ❌ 预测市场列表: {e}")
    
    try:
        # 获取用户持仓
        my_positions = exchange.prediction.get_my_positions()
        if isinstance(my_positions, list):
            print(f"  ✅ 预测市场持仓: {len(my_positions)} 个")
        elif isinstance(my_positions, dict) and my_positions.get("success"):
            # data 可能是 list 或 dict
            data = my_positions.get("data", [])
            if isinstance(data, list):
                pos_data = data
            else:
                pos_data = data.get("positions", [])
            print(f"  ✅ 预测市场持仓: {len(pos_data)} 个")
            for pos in pos_data[:3]:  # 显示前3个
                market_id = pos.get("market_id", "N/A")
                outcome = pos.get("outcome_index", "N/A")
                shares = pos.get("shares", 0)
                print(f"      - 市场#{market_id} 结果{outcome}: {shares} 份额")
        else:
            msg = my_positions.get("message", "未知错误") if isinstance(my_positions, dict) else str(my_positions)
            print(f"  ⚠️  预测市场持仓: {msg}")
    except Exception as e:
        print(f"  ❌ 预测市场持仓: {e}")
    
    # 6. 显示现货余额
    print("\n💰 测试现货账户...")
    print("-" * 50)
    
    try:
        balances = exchange.spot.get_balances()
        if balances.get("success"):
            data = balances.get("data", {})
            print(f"  ✅ 现货余额获取成功")
            # 显示非零余额
            if isinstance(data, dict):
                for symbol, info in list(data.items())[:5]:
                    if isinstance(info, dict):
                        available = info.get("available", 0)
                        if float(available) > 0:
                            print(f"      - {symbol}: {available}")
        else:
            print(f"  ⚠️  现货余额: {balances.get('message', '未知错误')}")
    except Exception as e:
        print(f"  ❌ 现货余额: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 认证测试完成!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

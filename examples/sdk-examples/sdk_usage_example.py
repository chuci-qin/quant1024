#!/usr/bin/env python3
"""
quant1024 SDK 使用示例

演示如何使用 quant1024 SDK 的各个模块接口。

安装方式:
    cd quant1024
    pip install -e .
    # 或使用 uv:
    uv pip install -e .
"""

from quant1024 import Exchange1024ex


def main():
    # ============================================
    # 1. 初始化客户端
    # ============================================
    exchange = Exchange1024ex(
        api_key="your_api_key",          # 替换为真实 API Key
        secret_key="your_secret_key",    # 替换为真实 Secret Key
        base_url="https://api.1024ex.com"  # 生产环境
    )
    
    print("=" * 50)
    print("quant1024 SDK 使用示例")
    print("=" * 50)
    
    # ============================================
    # 2. Perp 模块 - 永续合约
    # ============================================
    print("\n📊 Perp 模块 (永续合约)")
    print("-" * 40)
    
    # 获取所有市场
    # markets = exchange.perp.get_markets()
    # print(f"永续合约市场数量: {len(markets)}")
    
    # 获取 BTC-USDC 行情
    # ticker = exchange.perp.get_ticker("BTC-USDC")
    # print(f"BTC-USDC 最新价: {ticker.get('last_price')}")
    
    # 获取订单簿
    # orderbook = exchange.perp.get_orderbook("BTC-USDC", depth=10)
    
    # 下单
    # order = exchange.perp.place_order(
    #     market="BTC-USDC",
    #     side="long",
    #     order_type="limit",
    #     size="0.01",
    #     price="50000"
    # )
    
    # TWAP 订单
    # twap = exchange.perp.create_twap(
    #     market="BTC-USDC",
    #     side="long",
    #     total_size="1.0",
    #     duration_seconds=3600
    # )
    
    print("  - exchange.perp.get_markets()")
    print("  - exchange.perp.get_ticker(market)")
    print("  - exchange.perp.place_order(...)")
    print("  - exchange.perp.create_twap(...)")
    
    # ============================================
    # 3. Spot 模块 - 现货交易
    # ============================================
    print("\n💰 Spot 模块 (现货交易)")
    print("-" * 40)
    
    # 获取余额
    # balances = exchange.spot.get_balances()
    
    # 现货下单
    # order = exchange.spot.place_order(
    #     market="BTC/USDC",
    #     side="buy",
    #     order_type="limit",
    #     size="0.01",
    #     price="50000"
    # )
    
    print("  - exchange.spot.get_balances()")
    print("  - exchange.spot.get_markets()")
    print("  - exchange.spot.place_order(...)")
    
    # ============================================
    # 4. Prediction 模块 - 预测市场
    # ============================================
    print("\n🎯 Prediction 模块 (预测市场)")
    print("-" * 40)
    
    # 获取市场列表
    # markets = exchange.prediction.list_markets(category="crypto")
    # trending = exchange.prediction.list_trending_markets(limit=10)
    
    # 铸造代币 (需要真实 USDC)
    # result = exchange.prediction.mint(market_id=123, amount=100_000_000)
    
    # 下单
    # order = exchange.prediction.place_order(
    #     market_id=123,
    #     side=0,           # 0=买, 1=卖
    #     outcome_index=0,  # 0=Yes, 1=No
    #     price_e6=650000,  # $0.65
    #     amount=100
    # )
    
    print("  - exchange.prediction.list_markets()")
    print("  - exchange.prediction.list_trending_markets()")
    print("  - exchange.prediction.mint(...)")
    print("  - exchange.prediction.place_order(...)")
    
    # ============================================
    # 5. Championship 模块 - 锦标赛
    # ============================================
    print("\n🏆 Championship 模块 (锦标赛)")
    print("-" * 40)
    
    # 获取锦标赛列表
    # championships = exchange.championship.list_championships(status="active")
    
    # 获取排行榜
    # leaderboard = exchange.championship.get_leaderboard("weekly-pnl")
    
    print("  - exchange.championship.list_championships()")
    print("  - exchange.championship.get_leaderboard(slug)")
    print("  - exchange.championship.get_my_rank(slug)")
    
    # ============================================
    # 6. Account 模块 - 账户管理
    # ============================================
    print("\n👤 Account 模块 (账户管理)")
    print("-" * 40)
    
    # 获取账户概览
    # overview = exchange.account.get_overview()
    
    # 获取保证金信息
    # margin = exchange.account.get_perp_margin()
    
    # 获取充值历史
    # deposits = exchange.account.get_deposits()
    
    print("  - exchange.account.get_overview()")
    print("  - exchange.account.get_perp_margin()")
    print("  - exchange.account.get_deposits()")
    print("  - exchange.account.request_withdrawal(...)")
    
    # ============================================
    # 7. 系统接口
    # ============================================
    print("\n⚙️  系统接口")
    print("-" * 40)
    
    # 这些不需要认证，可以直接调用
    try:
        server_time = exchange.get_server_time()
        print(f"  服务器时间: {server_time}")
    except Exception as e:
        print(f"  (需要网络连接才能获取服务器时间)")
    
    print("\n" + "=" * 50)
    print("完整 API 文档: https://api.1024ex.com/api-docs")
    print("=" * 50)


if __name__ == "__main__":
    main()

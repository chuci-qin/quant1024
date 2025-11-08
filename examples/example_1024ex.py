"""
1024ex Exchange 使用示例

展示如何使用 quant1024 连接 1024ex 交易所
"""

from quant1024 import Exchange1024ex


def main():
    """主函数 - 展示 1024ex 各种功能"""
    
    # 初始化客户端
    client = Exchange1024ex(
        api_key="your_api_key_here",
        api_secret="your_api_secret_here",
        base_url="https://api.1024ex.com"  # 可选，默认为此地址
    )
    
    print("=" * 60)
    print("1024ex Exchange 使用示例")
    print("=" * 60)
    
    # ========== 系统接口 ==========
    print("\n1. 获取服务器时间")
    try:
        server_time = client.get_server_time()
        print(f"   服务器时间: {server_time}")
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n2. 健康检查")
    try:
        health = client.get_health()
        print(f"   系统状态: {health.get('status', 'unknown')}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # ========== 市场数据 ==========
    print("\n3. 获取所有市场")
    try:
        markets = client.get_markets()
        print(f"   可用市场数: {len(markets)}")
        if markets:
            print(f"   第一个市场: {markets[0].get('market', 'N/A')}")
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n4. 获取 BTC-PERP 行情")
    try:
        ticker = client.get_ticker("BTC-PERP")
        print(f"   最新价格: {ticker.get('last_price', 'N/A')}")
        print(f"   标记价格: {ticker.get('mark_price', 'N/A')}")
        print(f"   24h成交量: {ticker.get('volume_24h', 'N/A')}")
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n5. 获取订单簿")
    try:
        orderbook = client.get_orderbook("BTC-PERP", depth=5)
        bids = orderbook.get('bids', [])
        asks = orderbook.get('asks', [])
        print(f"   买单档位: {len(bids)}")
        print(f"   卖单档位: {len(asks)}")
        if bids:
            print(f"   最高买价: {bids[0].get('price', 'N/A')}")
        if asks:
            print(f"   最低卖价: {asks[0].get('price', 'N/A')}")
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n6. 获取K线数据")
    try:
        klines = client.get_klines("BTC-PERP", interval="1h", limit=10)
        print(f"   K线数量: {len(klines)}")
        if klines:
            latest = klines[-1]
            print(f"   最新K线 - 开:{latest.get('open')} 高:{latest.get('high')} 低:{latest.get('low')} 收:{latest.get('close')}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # ========== 账户接口（需要认证）==========
    print("\n7. 获取账户余额")
    try:
        balance = client.get_balance()
        balances = balance.get('balances', [])
        print(f"   资产种类: {len(balances)}")
        for bal in balances[:3]:  # 显示前3个
            print(f"   {bal.get('asset', 'N/A')}: 总额={bal.get('total', 'N/A')}, 可用={bal.get('available', 'N/A')}")
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n8. 获取持仓")
    try:
        positions = client.get_positions()
        print(f"   持仓数量: {len(positions)}")
        for pos in positions[:3]:  # 显示前3个
            print(f"   {pos.get('market', 'N/A')}: 方向={pos.get('side', 'N/A')}, 数量={pos.get('size', 'N/A')}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # ========== 交易接口（需要认证）==========
    print("\n9. 下限价单示例")
    print("   （实际交易请谨慎，这里仅作演示）")
    # 取消注释以下代码进行实际下单
    # try:
    #     order = client.place_order(
    #         market="BTC-PERP",
    #         side="buy",
    #         order_type="limit",
    #         price="50000.00",  # 设置一个较低的价格避免立即成交
    #         size="0.001",      # 最小数量
    #         post_only=True     # 只做 Maker
    #     )
    #     print(f"   订单ID: {order.get('order_id', 'N/A')}")
    #     print(f"   状态: {order.get('status', 'N/A')}")
    # except Exception as e:
    #     print(f"   错误: {e}")
    
    print("\n10. 查询当前委托")
    try:
        orders = client.get_orders(market="BTC-PERP")
        print(f"   当前委托数: {len(orders)}")
        for order in orders[:3]:  # 显示前3个
            print(f"   订单 {order.get('order_id', 'N/A')}: {order.get('side', 'N/A')} {order.get('size', 'N/A')} @ {order.get('price', 'N/A')}")
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n" + "=" * 60)
    print("示例完成！")
    print("=" * 60)


def cross_exchange_example():
    """
    跨交易所示例 - 展示 quant1024 的真正优势
    
    未来可以同时连接多个交易所进行对比和套利
    """
    print("\n" + "=" * 60)
    print("跨交易所示例（未来功能预览）")
    print("=" * 60)
    
    # 1024ex
    ex1024 = Exchange1024ex(
        api_key="1024_api_key",
        api_secret="1024_api_secret"
    )
    
    # 未来: Binance
    # binance = Binance(
    #     api_key="binance_api_key",
    #     api_secret="binance_api_secret"
    # )
    
    # 未来: IBKR
    # ibkr = IBKR(
    #     account="ibkr_account",
    #     token="ibkr_token"
    # )
    
    # 对比价格
    print("\n对比 BTC 价格:")
    try:
        price_1024 = ex1024.get_ticker("BTC-PERP")['last_price']
        print(f"  1024ex: ${price_1024}")
        
        # 未来可以对比其他交易所
        # price_binance = binance.get_ticker("BTCUSDT")['last_price']
        # print(f"  Binance: ${price_binance}")
        
        # price_diff = float(price_1024) - float(price_binance)
        # print(f"  价差: ${price_diff}")
    except Exception as e:
        print(f"  错误: {e}")
    
    print("\n这就是 quant1024 的核心价值:")
    print("  ✓ 统一接口，无缝切换交易所")
    print("  ✓ 跨交易所价格对比")
    print("  ✓ 套利机会发现")
    print("  ✓ 多平台数据聚合")


if __name__ == "__main__":
    # 运行基础示例
    main()
    
    # 运行跨交易所示例
    cross_exchange_example()


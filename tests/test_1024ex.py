"""
测试 1024ex Exchange 连接器

包含 80 个测试用例，覆盖 38 个 API 端点
"""

import pytest
import responses
import json
from quant1024.exchanges import Exchange1024ex
from quant1024.exceptions import (
    AuthenticationError,
    RateLimitError,
    MarketNotFoundError,
    APIError
)


# ========== Fixtures ==========

@pytest.fixture
def client():
    """创建测试客户端"""
    return Exchange1024ex(
        api_key="test_api_key",
        base_url="https://api.1024ex.com"
    )


@pytest.fixture
def mock_response():
    """Mock 响应辅助函数"""
    def _mock(method, path, json_data=None, status=200):
        responses.add(
            method=getattr(responses, method),
            url=f"https://api.1024ex.com{path}",
            json=json_data or {"success": True},
            status=status
        )
    return _mock


# ========== 系统接口测试（6个）==========

@responses.activate
def test_get_server_time(client, mock_response):
    """测试1: 获取服务器时间"""
    mock_response("GET", "/api/v1/time", {
        "success": True,
        "data": {
            "server_time": 1762911479265,
            "timezone": "UTC"
        },
        "timestamp": 1762911479265
    })
    
    result = client.get_server_time()
    assert result["success"] == True
    assert "data" in result
    assert "server_time" in result["data"]
    assert "timezone" in result["data"]


@responses.activate
def test_get_server_time_format(client, mock_response):
    """测试2: 验证时间格式"""
    mock_response("GET", "/api/v1/time", {
        "success": True,
        "data": {
            "server_time": 1762911479265,
            "timezone": "UTC"
        },
        "timestamp": 1762911479265
    })
    
    result = client.get_server_time()
    assert isinstance(result["data"]["server_time"], int)
    assert isinstance(result["data"]["timezone"], str)
    assert isinstance(result["timestamp"], int)


@responses.activate
def test_get_health(client, mock_response):
    """测试3: 健康检查"""
    mock_response("GET", "/api/v1/health", {
        "status": "ok",
        "services": {"database": "ok", "redis": "ok"}
    })
    
    result = client.get_health()
    assert result["status"] == "ok"
    assert "services" in result


@responses.activate
def test_get_health_services(client, mock_response):
    """测试4: 验证服务状态"""
    mock_response("GET", "/api/v1/health", {
        "status": "ok",
        "services": {"database": "ok"}
    })
    
    result = client.get_health()
    assert result["services"]["database"] == "ok"


@responses.activate
def test_get_exchange_info(client, mock_response):
    """测试5: 获取交易所信息"""
    mock_response("GET", "/api/v1/exchange-info", {
        "name": "1024ex",
        "version": "1.0.0"
    })
    
    result = client.get_exchange_info()
    assert "name" in result


@responses.activate
def test_get_exchange_info_markets(client, mock_response):
    """测试6: 验证市场列表"""
    mock_response("GET", "/api/v1/exchange-info", {
        "markets": ["BTC-PERP", "ETH-PERP"]
    })
    
    result = client.get_exchange_info()
    assert "markets" in result


# ========== 市场数据测试（16个）==========

@responses.activate
def test_get_markets(client, mock_response):
    """测试7: 获取所有市场"""
    mock_response("GET", "/api/v1/markets", {
        "data": [
            {"market": "BTC-PERP", "base_asset": "BTC"},
            {"market": "ETH-PERP", "base_asset": "ETH"}
        ]
    })
    
    result = client.get_markets()
    assert len(result) == 2
    assert result[0]["market"] == "BTC-PERP"


@responses.activate
def test_get_markets_structure(client, mock_response):
    """测试8: 验证数据结构"""
    mock_response("GET", "/api/v1/markets", {
        "data": [{"market": "BTC-PERP", "base_asset": "BTC"}]
    })
    
    result = client.get_markets()
    assert isinstance(result, list)
    assert "market" in result[0]


@responses.activate
def test_get_market(client, mock_response):
    """测试9: 获取单个市场"""
    mock_response("GET", "/api/v1/markets/BTC-PERP", {
        "market": "BTC-PERP",
        "status": "active"
    })
    
    result = client.get_market("BTC-PERP")
    assert result["market"] == "BTC-PERP"


@responses.activate
def test_get_market_invalid(client):
    """测试10: 不存在的市场"""
    responses.add(
        responses.GET,
        "https://api.1024ex.com/api/v1/markets/INVALID",
        status=404
    )
    
    with pytest.raises(MarketNotFoundError):
        client.get_market("INVALID")


@responses.activate
def test_get_ticker(client, mock_response):
    """测试11: 获取行情"""
    mock_response("GET", "/api/v1/ticker/BTC-PERP", {
        "market": "BTC-PERP",
        "last_price": "60000.00",
        "mark_price": "60001.00"
    })
    
    result = client.get_ticker("BTC-PERP")
    assert result["market"] == "BTC-PERP"
    assert "last_price" in result


@responses.activate
def test_get_ticker_price_format(client, mock_response):
    """测试12: 验证价格格式"""
    mock_response("GET", "/api/v1/ticker/BTC-PERP", {
        "last_price": "60000.00"
    })
    
    result = client.get_ticker("BTC-PERP")
    assert isinstance(result["last_price"], str)


@responses.activate
def test_get_orderbook(client, mock_response):
    """测试13: 获取订单簿"""
    mock_response("GET", "/api/v1/orderbook/BTC-PERP?depth=20", {
        "market": "BTC-PERP",
        "bids": [{"price": "60000", "size": "1.0"}],
        "asks": [{"price": "60001", "size": "1.0"}]
    })
    
    result = client.get_orderbook("BTC-PERP", depth=20)
    assert "bids" in result
    assert "asks" in result


@responses.activate
def test_get_orderbook_depth(client, mock_response):
    """测试14: 验证深度参数"""
    mock_response("GET", "/api/v1/orderbook/BTC-PERP?depth=50", {
        "bids": [],
        "asks": []
    })
    
    result = client.get_orderbook("BTC-PERP", depth=50)
    assert isinstance(result["bids"], list)


@responses.activate
def test_get_trades(client, mock_response):
    """测试15: 获取最近成交"""
    mock_response("GET", "/api/v1/trades/BTC-PERP?limit=50", {
        "data": [
            {"id": "1", "price": "60000", "size": "0.1", "side": "buy"}
        ]
    })
    
    result = client.get_trades("BTC-PERP", limit=50)
    assert len(result) >= 1
    assert "id" in result[0]


@responses.activate
def test_get_trades_limit(client, mock_response):
    """测试16: 验证数量限制"""
    mock_response("GET", "/api/v1/trades/BTC-PERP?limit=100", {
        "data": []
    })
    
    result = client.get_trades("BTC-PERP", limit=100)
    assert isinstance(result, list)


@responses.activate
def test_get_klines(client, mock_response):
    """测试17: 获取K线数据"""
    mock_response("GET", "/api/v1/klines/BTC-PERP?interval=1h&limit=100", {
        "data": [
            {"timestamp": 1234567890, "open": "60000", "close": "60100"}
        ]
    })
    
    result = client.get_klines("BTC-PERP", interval="1h")
    assert len(result) >= 1


@responses.activate
def test_get_klines_interval(client, mock_response):
    """测试18: 验证时间间隔"""
    mock_response("GET", "/api/v1/klines/BTC-PERP?interval=5m&limit=100", {
        "data": []
    })
    
    result = client.get_klines("BTC-PERP", interval="5m")
    assert isinstance(result, list)


@responses.activate
def test_get_funding_rate(client, mock_response):
    """测试19: 获取资金费率"""
    mock_response("GET", "/api/v1/funding-rate/BTC-PERP", {
        "market": "BTC-PERP",
        "funding_rate": "0.0001"
    })
    
    result = client.get_funding_rate("BTC-PERP")
    assert "funding_rate" in result


@responses.activate
def test_get_funding_rate_value(client, mock_response):
    """测试20: 验证费率值"""
    mock_response("GET", "/api/v1/funding-rate/BTC-PERP", {
        "funding_rate": "0.0001"
    })
    
    result = client.get_funding_rate("BTC-PERP")
    assert isinstance(result["funding_rate"], str)


@responses.activate
def test_get_market_stats(client, mock_response):
    """测试21: 获取市场统计"""
    mock_response("GET", "/api/v1/market-stats/BTC-PERP", {
        "market": "BTC-PERP",
        "open_interest": "1000000"
    })
    
    result = client.get_market_stats("BTC-PERP")
    assert "open_interest" in result


@responses.activate
def test_get_market_stats_structure(client, mock_response):
    """测试22: 验证统计结构"""
    mock_response("GET", "/api/v1/market-stats/BTC-PERP", {
        "open_interest": "1000000",
        "volume_24h": "50000000"
    })
    
    result = client.get_market_stats("BTC-PERP")
    assert isinstance(result, dict)


# ========== 交易接口测试（20个）==========

@responses.activate
def test_place_order_limit(client, mock_response):
    """测试23: 限价单"""
    mock_response("POST", "/api/v1/orders", {
        "order_id": "order_123",
        "status": "accepted"
    })
    
    result = client.place_order(
        market="BTC-PERP",
        side="buy",
        order_type="limit",
        price="60000",
        size="0.01"
    )
    assert result["order_id"] == "order_123"


@responses.activate
def test_place_order_market(client, mock_response):
    """测试24: 市价单"""
    mock_response("POST", "/api/v1/orders", {
        "order_id": "order_124",
        "type": "market"
    })
    
    result = client.place_order(
        market="BTC-PERP",
        side="sell",
        order_type="market",
        size="0.01"
    )
    assert "order_id" in result


@responses.activate
def test_place_order_with_leverage(client, mock_response):
    """测试25: 带杠杆下单"""
    mock_response("POST", "/api/v1/orders", {
        "order_id": "order_125",
        "leverage": 10
    })
    
    result = client.place_order(
        market="BTC-PERP",
        side="buy",
        order_type="limit",
        price="60000",
        size="0.01",
        leverage=10
    )
    assert "order_id" in result


@responses.activate
def test_place_order_invalid_market(client):
    """测试26: 无效市场"""
    responses.add(
        responses.POST,
        "https://api.1024ex.com/api/v1/orders",
        json={"error": "Invalid market"},
        status=400
    )
    
    with pytest.raises(APIError):
        client.place_order(
            market="INVALID",
            side="buy",
            order_type="limit",
            price="1000",
            size="0.01"
        )


@responses.activate
def test_cancel_order(client, mock_response):
    """测试27: 撤单"""
    mock_response("DELETE", "/api/v1/orders/order_123", {
        "success": True,
        "order_id": "order_123"
    })
    
    result = client.cancel_order("order_123")
    assert result["success"] == True


@responses.activate
def test_cancel_order_not_found(client):
    """测试28: 订单不存在"""
    responses.add(
        responses.DELETE,
        "https://api.1024ex.com/api/v1/orders/invalid",
        status=404
    )
    
    with pytest.raises(MarketNotFoundError):
        client.cancel_order("invalid")


@responses.activate
def test_cancel_all_orders(client, mock_response):
    """测试29: 批量撤单"""
    mock_response("DELETE", "/api/v1/orders", {
        "cancelled": 5
    })
    
    result = client.cancel_all_orders()
    assert "cancelled" in result


@responses.activate
def test_cancel_all_orders_by_market(client, mock_response):
    """测试30: 按市场撤单"""
    mock_response("DELETE", "/api/v1/orders?market=BTC-PERP", {
        "cancelled": 3
    })
    
    result = client.cancel_all_orders(market="BTC-PERP")
    assert isinstance(result, dict)


@responses.activate
def test_get_orders(client, mock_response):
    """测试31: 获取当前委托"""
    mock_response("GET", "/api/v1/orders", {
        "data": [
            {"order_id": "1", "status": "open"}
        ]
    })
    
    result = client.get_orders()
    assert isinstance(result, list)


@responses.activate
def test_get_orders_by_market(client, mock_response):
    """测试32: 按市场查询"""
    mock_response("GET", "/api/v1/orders?market=BTC-PERP", {
        "data": []
    })
    
    result = client.get_orders(market="BTC-PERP")
    assert isinstance(result, list)


@responses.activate
def test_get_order(client, mock_response):
    """测试33: 获取订单详情"""
    mock_response("GET", "/api/v1/orders/order_123", {
        "order_id": "order_123",
        "status": "filled"
    })
    
    result = client.get_order("order_123")
    assert result["order_id"] == "order_123"


@responses.activate
def test_get_order_status(client, mock_response):
    """测试34: 验证订单状态"""
    mock_response("GET", "/api/v1/orders/order_123", {
        "status": "open"
    })
    
    result = client.get_order("order_123")
    assert result["status"] == "open"


@responses.activate
def test_update_order(client, mock_response):
    """测试35: 修改订单"""
    mock_response("PUT", "/api/v1/orders/order_123", {
        "order_id": "order_123",
        "price": "61000"
    })
    
    result = client.update_order("order_123", price="61000")
    assert "order_id" in result


@responses.activate
def test_update_order_price_and_size(client, mock_response):
    """测试36: 修改价格和数量"""
    mock_response("PUT", "/api/v1/orders/order_123", {
        "order_id": "order_123"
    })
    
    result = client.update_order("order_123", price="61000", size="0.02")
    assert "order_id" in result


@responses.activate
def test_batch_place_orders(client, mock_response):
    """测试37: 批量下单"""
    mock_response("POST", "/api/v1/orders/batch", {
        "orders": [
            {"order_id": "1"},
            {"order_id": "2"}
        ]
    })
    
    result = client.batch_place_orders([
        {"market": "BTC-PERP", "side": "buy", "type": "limit", "price": "60000", "size": "0.01"}
    ])
    assert "orders" in result


@responses.activate
def test_batch_place_orders_multiple(client, mock_response):
    """测试38: 多个订单"""
    mock_response("POST", "/api/v1/orders/batch", {
        "orders": []
    })
    
    result = client.batch_place_orders([])
    assert isinstance(result, dict)


@responses.activate
def test_set_tpsl(client, mock_response):
    """测试39: 设置止盈止损"""
    mock_response("PUT", "/api/v1/positions/BTC-PERP/tpsl", {
        "success": True
    })
    
    result = client.set_tpsl("BTC-PERP", tp_price="65000", sl_price="58000")
    assert result["success"] == True


@responses.activate
def test_set_tpsl_tp_only(client, mock_response):
    """测试40: 只设置止盈"""
    mock_response("PUT", "/api/v1/positions/BTC-PERP/tpsl", {
        "success": True
    })
    
    result = client.set_tpsl("BTC-PERP", tp_price="65000")
    assert "success" in result


@responses.activate
def test_set_tpsl_sl_only(client, mock_response):
    """测试41: 只设置止损"""
    mock_response("PUT", "/api/v1/positions/BTC-PERP/tpsl", {
        "success": True
    })
    
    result = client.set_tpsl("BTC-PERP", sl_price="58000")
    assert "success" in result


@responses.activate
def test_place_order_post_only(client, mock_response):
    """测试42: Post-Only 订单"""
    mock_response("POST", "/api/v1/orders", {
        "order_id": "order_126",
        "post_only": True
    })
    
    result = client.place_order(
        market="BTC-PERP",
        side="buy",
        order_type="limit",
        price="60000",
        size="0.01",
        post_only=True
    )
    assert "order_id" in result


# ========== 账户接口测试（12个）==========

@responses.activate
def test_get_balance(client, mock_response):
    """测试43: 获取余额"""
    mock_response("GET", "/api/v1/account/balance", {
        "balances": [
            {"asset": "USDC", "total": "10000", "available": "9000"}
        ]
    })
    
    result = client.get_balance()
    assert "balances" in result


@responses.activate
def test_get_balance_structure(client, mock_response):
    """测试44: 验证余额结构"""
    mock_response("GET", "/api/v1/account/balance", {
        "balances": [{"asset": "USDC", "total": "10000"}]
    })
    
    result = client.get_balance()
    assert isinstance(result["balances"], list)


@responses.activate
def test_get_positions(client, mock_response):
    """测试45: 获取持仓"""
    mock_response("GET", "/api/v1/account/positions", {
        "data": [
            {"market": "BTC-PERP", "size": "0.1", "side": "long"}
        ]
    })
    
    result = client.get_positions()
    assert isinstance(result, list)


@responses.activate
def test_get_positions_by_market(client, mock_response):
    """测试46: 按市场查询持仓"""
    mock_response("GET", "/api/v1/account/positions?market=BTC-PERP", {
        "data": [{"market": "BTC-PERP"}]
    })
    
    result = client.get_positions(market="BTC-PERP")
    assert isinstance(result, list)


@responses.activate
def test_get_margin(client, mock_response):
    """测试47: 获取保证金"""
    mock_response("GET", "/api/v1/account/margin", {
        "total_margin": "1000",
        "used_margin": "500"
    })
    
    result = client.get_margin()
    assert "total_margin" in result


@responses.activate
def test_get_margin_values(client, mock_response):
    """测试48: 验证保证金值"""
    mock_response("GET", "/api/v1/account/margin", {
        "used_margin": "500",
        "available_margin": "500"
    })
    
    result = client.get_margin()
    assert "used_margin" in result


@responses.activate
def test_get_leverage(client, mock_response):
    """测试49: 查询杠杆"""
    mock_response("GET", "/api/v1/account/leverage/BTC-PERP", {
        "market": "BTC-PERP",
        "leverage": 10
    })
    
    result = client.get_leverage("BTC-PERP")
    assert result["leverage"] == 10


@responses.activate
def test_get_leverage_value(client, mock_response):
    """测试50: 验证杠杆值"""
    mock_response("GET", "/api/v1/account/leverage/BTC-PERP", {
        "leverage": 20
    })
    
    result = client.get_leverage("BTC-PERP")
    assert isinstance(result["leverage"], int)


@responses.activate
def test_set_leverage(client, mock_response):
    """测试51: 设置杠杆"""
    mock_response("PUT", "/api/v1/account/leverage/BTC-PERP", {
        "success": True,
        "leverage": 15
    })
    
    result = client.set_leverage("BTC-PERP", 15)
    assert result["success"] == True


@responses.activate
def test_set_leverage_different_values(client, mock_response):
    """测试52: 设置不同杠杆值"""
    mock_response("PUT", "/api/v1/account/leverage/BTC-PERP", {
        "leverage": 5
    })
    
    result = client.set_leverage("BTC-PERP", 5)
    assert "leverage" in result


@responses.activate
def test_get_sub_accounts(client, mock_response):
    """测试53: 获取子账户"""
    mock_response("GET", "/api/v1/account/sub-accounts", {
        "data": [
            {"sub_account_id": "sub_1", "nickname": "Trading"}
        ]
    })
    
    result = client.get_sub_accounts()
    assert isinstance(result, list)


@responses.activate
def test_get_sub_accounts_empty(client, mock_response):
    """测试54: 无子账户"""
    mock_response("GET", "/api/v1/account/sub-accounts", {
        "data": []
    })
    
    result = client.get_sub_accounts()
    assert len(result) == 0


# ========== 资金接口测试（8个）==========

@responses.activate
def test_get_deposit_address(client, mock_response):
    """测试55: 获取充值地址"""
    mock_response("POST", "/api/v1/account/deposit", {
        "asset": "USDC",
        "address": "0x123..."
    })
    
    result = client.get_deposit_address("USDC")
    assert "address" in result


@responses.activate
def test_get_deposit_address_different_asset(client, mock_response):
    """测试56: 不同资产充值地址"""
    mock_response("POST", "/api/v1/account/deposit", {
        "asset": "BTC",
        "address": "bc1..."
    })
    
    result = client.get_deposit_address("BTC")
    assert "address" in result


@responses.activate
def test_withdraw(client, mock_response):
    """测试57: 提现"""
    mock_response("POST", "/api/v1/account/withdraw", {
        "withdraw_id": "withdraw_123",
        "status": "pending"
    })
    
    result = client.withdraw("USDC", "1000", "0xabc...")
    assert "withdraw_id" in result


@responses.activate
def test_withdraw_with_memo(client, mock_response):
    """测试58: 带备注提现"""
    mock_response("POST", "/api/v1/account/withdraw", {
        "withdraw_id": "withdraw_124"
    })
    
    result = client.withdraw("USDC", "1000", "0xabc...", memo="test")
    assert "withdraw_id" in result


@responses.activate
def test_get_deposit_history(client, mock_response):
    """测试59: 充值历史"""
    mock_response("GET", "/api/v1/account/deposits?limit=50", {
        "data": [
            {"id": "dep_1", "asset": "USDC", "amount": "1000"}
        ]
    })
    
    result = client.get_deposit_history()
    assert isinstance(result, list)


@responses.activate
def test_get_deposit_history_by_asset(client, mock_response):
    """测试60: 按资产查询充值"""
    mock_response("GET", "/api/v1/account/deposits?limit=50&asset=USDC", {
        "data": []
    })
    
    result = client.get_deposit_history(asset="USDC")
    assert isinstance(result, list)


@responses.activate
def test_get_withdraw_history(client, mock_response):
    """测试61: 提现历史"""
    mock_response("GET", "/api/v1/account/withdrawals?limit=50", {
        "data": [
            {"id": "with_1", "asset": "USDC", "amount": "500"}
        ]
    })
    
    result = client.get_withdraw_history()
    assert isinstance(result, list)


@responses.activate
def test_get_withdraw_history_limit(client, mock_response):
    """测试62: 提现历史限制"""
    mock_response("GET", "/api/v1/account/withdrawals?limit=100&asset=USDC", {
        "data": []
    })
    
    result = client.get_withdraw_history(asset="USDC", limit=100)
    assert isinstance(result, list)


# ========== 历史数据测试（10个）==========

@responses.activate
def test_get_order_history(client, mock_response):
    """测试63: 历史订单"""
    mock_response("GET", "/api/v1/orders/history?limit=100", {
        "data": [
            {"order_id": "1", "status": "filled"}
        ]
    })
    
    result = client.get_order_history()
    assert isinstance(result, list)


@responses.activate
def test_get_order_history_by_market(client, mock_response):
    """测试64: 按市场查询历史"""
    mock_response("GET", "/api/v1/orders/history?limit=100&market=BTC-PERP", {
        "data": []
    })
    
    result = client.get_order_history(market="BTC-PERP")
    assert isinstance(result, list)


@responses.activate
def test_get_trade_history(client, mock_response):
    """测试65: 成交历史"""
    mock_response("GET", "/api/v1/trades/history?limit=100", {
        "data": [
            {"id": "trade_1", "price": "60000"}
        ]
    })
    
    result = client.get_trade_history()
    assert isinstance(result, list)


@responses.activate
def test_get_trade_history_limit(client, mock_response):
    """测试66: 成交历史限制"""
    mock_response("GET", "/api/v1/trades/history?limit=50&market=BTC-PERP", {
        "data": []
    })
    
    result = client.get_trade_history(market="BTC-PERP", limit=50)
    assert isinstance(result, list)


@responses.activate
def test_get_funding_history(client, mock_response):
    """测试67: 资金费历史"""
    mock_response("GET", "/api/v1/funding/history?limit=100", {
        "data": [
            {"market": "BTC-PERP", "rate": "0.0001"}
        ]
    })
    
    result = client.get_funding_history()
    assert isinstance(result, list)


@responses.activate
def test_get_funding_history_by_market(client, mock_response):
    """测试68: 按市场查询资金费"""
    mock_response("GET", "/api/v1/funding/history?limit=100&market=BTC-PERP", {
        "data": []
    })
    
    result = client.get_funding_history(market="BTC-PERP")
    assert isinstance(result, list)


@responses.activate
def test_get_liquidation_history(client, mock_response):
    """测试69: 强平历史"""
    mock_response("GET", "/api/v1/liquidations/history?limit=100", {
        "data": [
            {"market": "BTC-PERP", "size": "0.5"}
        ]
    })
    
    result = client.get_liquidation_history()
    assert isinstance(result, list)


@responses.activate
def test_get_liquidation_history_empty(client, mock_response):
    """测试70: 无强平记录"""
    mock_response("GET", "/api/v1/liquidations/history?limit=100", {
        "data": []
    })
    
    result = client.get_liquidation_history()
    assert len(result) == 0


@responses.activate
def test_get_pnl_summary(client, mock_response):
    """测试71: 盈亏汇总"""
    mock_response("GET", "/api/v1/pnl/summary?period=30d", {
        "total_pnl": "1000.00",
        "period": "30d"
    })
    
    result = client.get_pnl_summary()
    assert "total_pnl" in result


@responses.activate
def test_get_pnl_summary_different_period(client, mock_response):
    """测试72: 不同周期盈亏"""
    mock_response("GET", "/api/v1/pnl/summary?period=7d", {
        "total_pnl": "500.00"
    })
    
    result = client.get_pnl_summary(period="7d")
    assert "total_pnl" in result


# ========== Smart ADL 测试（8个）==========

@responses.activate
def test_get_smart_adl_config(client, mock_response):
    """测试73: 获取ADL配置"""
    mock_response("GET", "/api/v1/smart-adl/config", {
        "enabled": True,
        "mode": "auto"
    })
    
    result = client.get_smart_adl_config()
    assert "enabled" in result


@responses.activate
def test_get_smart_adl_config_disabled(client, mock_response):
    """测试74: ADL禁用状态"""
    mock_response("GET", "/api/v1/smart-adl/config", {
        "enabled": False
    })
    
    result = client.get_smart_adl_config()
    assert result["enabled"] == False


@responses.activate
def test_update_smart_adl_config(client, mock_response):
    """测试75: 更新ADL配置"""
    mock_response("PUT", "/api/v1/smart-adl/config", {
        "success": True,
        "enabled": True
    })
    
    result = client.update_smart_adl_config(enabled=True, mode="manual")
    assert result["success"] == True


@responses.activate
def test_update_smart_adl_config_partial(client, mock_response):
    """测试76: 部分更新ADL配置"""
    mock_response("PUT", "/api/v1/smart-adl/config", {
        "enabled": True
    })
    
    result = client.update_smart_adl_config(enabled=True)
    assert "enabled" in result


@responses.activate
def test_get_protection_pool(client, mock_response):
    """测试77: 获取保护池"""
    mock_response("GET", "/api/v1/smart-adl/protection-pool", {
        "data": [
            {"market": "BTC-PERP", "pool_size": "10000"}
        ]
    })
    
    result = client.get_protection_pool()
    assert isinstance(result, list)


@responses.activate
def test_get_protection_pool_empty(client, mock_response):
    """测试78: 空保护池"""
    mock_response("GET", "/api/v1/smart-adl/protection-pool", {
        "data": []
    })
    
    result = client.get_protection_pool()
    assert len(result) == 0


@responses.activate
def test_get_smart_adl_history(client, mock_response):
    """测试79: ADL历史"""
    mock_response("GET", "/api/v1/smart-adl/history?limit=50", {
        "data": [
            {"id": "adl_1", "market": "BTC-PERP"}
        ]
    })
    
    result = client.get_smart_adl_history()
    assert isinstance(result, list)


@responses.activate
def test_get_smart_adl_history_limit(client, mock_response):
    """测试80: ADL历史限制"""
    mock_response("GET", "/api/v1/smart-adl/history?limit=100", {
        "data": []
    })
    
    result = client.get_smart_adl_history(limit=100)
    assert isinstance(result, list)


# ========== 认证和错误处理测试 ==========

@responses.activate
def test_authentication_error(client):
    """测试81: 认证错误"""
    responses.add(
        responses.GET,
        "https://api.1024ex.com/api/v1/account/balance",
        status=401
    )
    
    with pytest.raises(AuthenticationError):
        client.get_balance()


@responses.activate
def test_rate_limit_error(client):
    """测试82: 速率限制"""
    responses.add(
        responses.GET,
        "https://api.1024ex.com/api/v1/markets",
        status=429,
        headers={'Retry-After': '60'}
    )
    
    with pytest.raises(RateLimitError):
        client.get_markets()


@responses.activate
def test_api_error(client):
    """测试83: API错误"""
    responses.add(
        responses.POST,
        "https://api.1024ex.com/api/v1/orders",
        json={"message": "Insufficient margin"},
        status=400
    )
    
    with pytest.raises(APIError):
        client.place_order(
            market="BTC-PERP",
            side="buy",
            order_type="limit",
            price="60000",
            size="100"
        )


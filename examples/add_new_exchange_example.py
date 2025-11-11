"""
示例：如何添加新的交易所支持

这个文件展示了如何为 quant1024 添加新的交易所（以 Binance 为例）
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from typing import Dict, List, Any, Optional
import requests
import time
import hmac
import hashlib

from quant1024.exchanges.base import BaseExchange
from quant1024.exceptions import APIError, AuthenticationError


class BinanceExample(BaseExchange):
    """
    Binance 交易所连接器示例
    
    这个示例展示了如何实现 BaseExchange 接口来支持新的交易所
    
    注意：这只是一个简化的示例，实际生产环境需要更完善的实现
    """
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = "https://fapi.binance.com",  # 期货 API
        **kwargs
    ):
        """初始化 Binance 连接器"""
        super().__init__(api_key, api_secret, base_url, **kwargs)
        self.session = requests.Session()
    
    def _generate_signature(self, query_string: str) -> str:
        """生成 Binance API 签名"""
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _request(self, method: str, path: str, params: Optional[Dict] = None,
                signed: bool = False) -> Any:
        """发送 HTTP 请求"""
        url = f"{self.base_url}{path}"
        headers = {'X-MBX-APIKEY': self.api_key}
        
        if params is None:
            params = {}
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            params['signature'] = self._generate_signature(query_string)
        
        response = self.session.request(method, url, params=params, headers=headers)
        
        if response.status_code != 200:
            raise APIError(f"Binance API error: {response.text}")
        
        return response.json()
    
    # ========== 必须实现的核心方法（LiveTrader 使用） ==========
    
    def get_ticker(self, market: str) -> Dict[str, Any]:
        """
        获取行情（核心方法 1/3）
        
        LiveTrader 需要：获取当前价格
        """
        # 调用 Binance API
        response = self._request("GET", "/fapi/v1/ticker/24hr", {"symbol": market})
        
        # 转换为标准格式（关键！）
        return {
            'last_price': response['lastPrice'],       # 标准字段名
            'mark_price': response.get('weightedAvgPrice'),
            'volume_24h': response['volume'],
            'high_24h': response['highPrice'],
            'low_24h': response['lowPrice']
        }
    
    def get_positions(self, market: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取持仓（核心方法 2/3）
        
        LiveTrader 需要：检查当前持仓
        """
        # 调用 Binance API
        response = self._request("GET", "/fapi/v2/positionRisk", signed=True)
        
        # 转换为标准格式（关键！）
        positions = []
        for pos in response:
            position_amt = float(pos['positionAmt'])
            
            # 过滤掉零持仓
            if position_amt == 0:
                continue
            
            # 如果指定了市场，只返回该市场
            if market and pos['symbol'] != market:
                continue
            
            positions.append({
                'market': pos['symbol'],                   # 标准字段名
                'size': str(abs(position_amt)),            # 持仓大小
                'side': 'long' if position_amt > 0 else 'short',  # 方向
                'entry_price': pos['entryPrice'],          # 入场价格
                'unrealized_pnl': pos['unRealizedProfit']  # 未实现盈亏
            })
        
        return positions
    
    def place_order(
        self,
        market: str,
        side: str,
        order_type: str,
        size: str,
        price: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        下单（核心方法 3/3）
        
        LiveTrader 需要：执行买卖订单
        """
        # 构造 Binance 订单参数
        params = {
            'symbol': market,
            'side': side.upper(),         # BUY / SELL
            'type': order_type.upper(),   # MARKET / LIMIT
            'quantity': size
        }
        
        # 如果是限价单，需要价格
        if order_type.lower() == 'limit' and price:
            params['price'] = price
            params['timeInForce'] = 'GTC'  # Good Till Cancel
        
        # 添加额外参数
        params.update(kwargs)
        
        # 调用 Binance API
        response = self._request("POST", "/fapi/v1/order", params=params, signed=True)
        
        # 转换为标准格式（关键！）
        return {
            'order_id': str(response['orderId']),      # 标准字段名
            'status': response['status'].lower(),      # 订单状态
            'filled_size': response['executedQty'],    # 已成交数量
            'avg_price': response.get('avgPrice', '0') # 平均成交价
        }
    
    # ========== 其他必须实现的方法 ==========
    
    def get_server_time(self) -> Dict[str, Any]:
        """获取服务器时间"""
        response = self._request("GET", "/fapi/v1/time")
        return {'timestamp': response['serverTime']}
    
    def get_health(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            self._request("GET", "/fapi/v1/ping")
            return {'status': 'ok'}
        except:
            return {'status': 'error'}
    
    def get_exchange_info(self) -> Dict[str, Any]:
        """获取交易所信息"""
        return self._request("GET", "/fapi/v1/exchangeInfo")
    
    def get_markets(self) -> List[Dict[str, Any]]:
        """获取所有市场"""
        info = self.get_exchange_info()
        return info.get('symbols', [])
    
    def get_market(self, market: str) -> Dict[str, Any]:
        """获取单个市场信息"""
        markets = self.get_markets()
        for m in markets:
            if m['symbol'] == market:
                return m
        raise APIError(f"Market {market} not found")
    
    def get_orderbook(self, market: str, depth: int = 20) -> Dict[str, Any]:
        """获取订单簿"""
        response = self._request("GET", "/fapi/v1/depth", {
            "symbol": market,
            "limit": depth
        })
        return response
    
    def get_trades(self, market: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取最近成交"""
        response = self._request("GET", "/fapi/v1/trades", {
            "symbol": market,
            "limit": limit
        })
        return response
    
    def get_klines(
        self,
        market: str,
        interval: str = '1h',
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取K线数据"""
        params = {
            "symbol": market,
            "interval": interval,
            "limit": limit
        }
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
        
        response = self._request("GET", "/fapi/v1/klines", params)
        
        # 转换为标准格式
        klines = []
        for k in response:
            klines.append({
                'timestamp': k[0],
                'open': k[1],
                'high': k[2],
                'low': k[3],
                'close': k[4],
                'volume': k[5]
            })
        return klines
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """撤单"""
        response = self._request("DELETE", "/fapi/v1/order", {
            "orderId": order_id
        }, signed=True)
        return response
    
    def get_orders(
        self,
        market: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取当前委托"""
        params = {}
        if market:
            params['symbol'] = market
        
        response = self._request("GET", "/fapi/v1/openOrders", params, signed=True)
        return response
    
    def get_order(self, order_id: str) -> Dict[str, Any]:
        """获取订单详情"""
        response = self._request("GET", "/fapi/v1/order", {
            "orderId": order_id
        }, signed=True)
        return response
    
    def get_balance(self) -> Dict[str, Any]:
        """获取账户余额"""
        response = self._request("GET", "/fapi/v2/balance", signed=True)
        return {'balances': response}
    
    def get_margin(self) -> Dict[str, Any]:
        """获取保证金信息"""
        response = self._request("GET", "/fapi/v2/account", signed=True)
        return response


# ========== 使用示例 ==========

def example_1_test_binance_methods():
    """示例 1：测试 Binance 连接器的方法"""
    print("=" * 60)
    print("示例 1：测试 Binance 连接器")
    print("=" * 60)
    
    # 创建 Binance 连接器
    binance = BinanceExample(
        api_key="your_binance_api_key",
        api_secret="your_binance_api_secret"
    )
    
    # 测试核心方法
    try:
        # 1. 获取行情
        print("\n1. 获取 BTCUSDT 行情:")
        ticker = binance.get_ticker("BTCUSDT")
        print(f"   最新价格: ${ticker['last_price']}")
        print(f"   24h成交量: {ticker['volume_24h']}")
        
        # 2. 获取持仓
        print("\n2. 获取持仓:")
        positions = binance.get_positions()
        print(f"   持仓数量: {len(positions)}")
        
        # 3. 下单（演示，不实际执行）
        print("\n3. 下单示例（不实际执行）:")
        print("   order = binance.place_order(")
        print("       market='BTCUSDT',")
        print("       side='buy',")
        print("       order_type='market',")
        print("       size='0.001'")
        print("   )")
        
    except Exception as e:
        print(f"   错误: {e}")
        print("   （请确保 API Key 正确）")


def example_2_use_with_live_trader():
    """示例 2：在 LiveTrader 中使用 Binance"""
    print("\n" + "=" * 60)
    print("示例 2：在 LiveTrader 中使用 Binance")
    print("=" * 60)
    
    from quant1024 import QuantStrategy
    from quant1024.live_trading import LiveTrader
    
    # 定义策略
    class SimpleStrategy(QuantStrategy):
        def generate_signals(self, data):
            if len(data) < 2:
                return [0]
            return [1 if data[-1] > data[-2] else -1]
        
        def calculate_position(self, signal, current_position):
            return 0.3 if signal == 1 else 0.0
    
    # 创建 Binance 连接器
    binance = BinanceExample(
        api_key="your_binance_api_key",
        api_secret="your_binance_api_secret"
    )
    
    # 创建交易器（使用 Binance！）
    trader = LiveTrader(
        strategy=SimpleStrategy(name="简单策略"),
        exchange=binance,  # 使用 Binance！
        market="BTCUSDT",
        initial_capital=10000,
        max_position_size=0.3,
        check_interval=60
    )
    
    print("\n✅ LiveTrader 已创建，使用 Binance 交易所")
    print("   策略可以无缝切换交易所，无需修改策略代码！")
    
    # 运行几次循环（测试）
    # trader.start(max_iterations=3)


def example_3_switch_exchanges():
    """示例 3：同一个策略，不同交易所"""
    print("\n" + "=" * 60)
    print("示例 3：跨交易所使用同一个策略")
    print("=" * 60)
    
    from quant1024 import QuantStrategy, Exchange1024ex
    from quant1024.live_trading import LiveTrader
    
    # 定义策略（只需定义一次！）
    class MyStrategy(QuantStrategy):
        def generate_signals(self, data):
            if len(data) < 2:
                return [0]
            return [1 if data[-1] > data[-2] else -1]
        
        def calculate_position(self, signal, current_position):
            return 0.5 if signal == 1 else 0.0
    
    strategy = MyStrategy(name="通用策略")
    
    # 在 1024ex 上运行
    print("\n在 1024ex 上运行:")
    exchange_1024 = Exchange1024ex(
        api_key="1024_api_key",
        api_secret="1024_api_secret"
    )
    trader_1024 = LiveTrader(
        strategy=strategy,  # 同一个策略！
        exchange=exchange_1024,
        market="BTC-PERP",
        initial_capital=10000
    )
    print("   ✅ 已创建 1024ex 交易器")
    
    # 在 Binance 上运行
    print("\n在 Binance 上运行:")
    exchange_binance = BinanceExample(
        api_key="binance_api_key",
        api_secret="binance_api_secret"
    )
    trader_binance = LiveTrader(
        strategy=strategy,  # 同一个策略！
        exchange=exchange_binance,
        market="BTCUSDT",
        initial_capital=10000
    )
    print("   ✅ 已创建 Binance 交易器")
    
    print("\n🎉 同一个策略，可以在不同交易所运行！")
    print("   这就是 BaseExchange 抽象接口的威力！")


def main():
    """主函数"""
    print("🚀 如何添加新的交易所支持\n")
    print("本示例展示了如何为 quant1024 添加新的交易所")
    print("以 Binance 为例，演示了完整的实现过程。")
    print("\n步骤：")
    print("  1. 继承 BaseExchange 类")
    print("  2. 实现必需的抽象方法")
    print("  3. 转换数据为统一格式")
    print("  4. 在 LiveTrader 中使用")
    
    # 运行示例
    # example_1_test_binance_methods()      # 测试 Binance 方法
    # example_2_use_with_live_trader()      # 在 LiveTrader 中使用
    # example_3_switch_exchanges()          # 跨交易所使用
    
    print("\n\n📖 更多信息:")
    print("   查看 ARCHITECTURE_LIVE_TRADING.md 了解详细设计")
    print("\n⚠️  注意:")
    print("   这只是一个简化示例，生产环境需要:")
    print("   - 完善的错误处理")
    print("   - 重试机制")
    print("   - 速率限制")
    print("   - 完整的 API 实现")


if __name__ == "__main__":
    main()


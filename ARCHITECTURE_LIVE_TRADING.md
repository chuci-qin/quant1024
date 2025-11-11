# 实盘交易架构设计

## 📐 抽象层次设计

### 架构图

```
┌─────────────────────────────────────────────────────────┐
│                      用户层                              │
│  start_trading() / LiveTrader                           │
│  - 策略执行                                              │
│  - 风险管理                                              │
│  - 交易逻辑                                              │
└──────────────────┬──────────────────────────────────────┘
                   │ 依赖
                   ▼
┌─────────────────────────────────────────────────────────┐
│                   抽象接口层                             │
│  BaseExchange (ABC)                                     │
│  - get_ticker(market)                                   │
│  - get_positions(market)                                │
│  - place_order(...)                                     │
│  - get_balance()                                        │
│  - ... (更多统一接口)                                    │
└──────────────────┬──────────────────────────────────────┘
                   │ 实现
                   ▼
┌─────────────────────────────────────────────────────────┐
│                 具体交易所实现                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Exchange     │  │   Binance    │  │     IBKR     │  │
│  │   1024ex     │  │  (未来支持)   │  │  (未来支持)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 🎯 核心设计原则

### 1. 依赖倒置原则 (DIP)

`LiveTrader` **不依赖具体的交易所实现**，而是依赖 `BaseExchange` 抽象接口：

```python
class LiveTrader:
    def __init__(self, strategy: QuantStrategy, exchange: BaseExchange, ...):
        #                                              ^^^^^^^^^^^^
        #                                        依赖抽象，而非具体实现
        self.exchange = exchange
```

**好处**：
- ✅ 任何实现 `BaseExchange` 的交易所都可以使用
- ✅ 无需修改 `LiveTrader` 代码即可支持新交易所
- ✅ 易于测试（可以 Mock `BaseExchange`）

### 2. 最小依赖原则

`LiveTrader` 只使用 **3 个核心方法**：

```python
# LiveTrader 实际使用的交易所接口
self.exchange.get_ticker(market)       # 获取价格
self.exchange.get_positions(market)    # 获取持仓
self.exchange.place_order(            # 下单
    market=...,
    side=...,
    order_type=...,
    size=...,
    **kwargs
)
```

**好处**：
- ✅ 接口简单，易于实现
- ✅ 降低了交易所适配的复杂度
- ✅ 不同交易所只需实现这 3 个核心方法即可工作

### 3. 统一接口，个性化扩展

`BaseExchange` 定义了完整的统一接口：

```python
class BaseExchange(ABC):
    # 市场数据
    @abstractmethod
    def get_ticker(self, market: str) -> Dict[str, Any]: ...
    
    @abstractmethod
    def get_positions(self, market: Optional[str] = None) -> List[Dict[str, Any]]: ...
    
    # 交易接口
    @abstractmethod
    def place_order(self, market: str, side: str, order_type: str, 
                   size: str, price: Optional[str] = None, **kwargs) -> Dict[str, Any]: ...
    
    # ... 更多方法
```

**好处**：
- ✅ 统一的返回数据格式
- ✅ `**kwargs` 允许交易所特定参数
- ✅ 用户代码可以无缝切换交易所

## 🔌 如何添加新交易所

### 步骤 1：实现 BaseExchange

创建新的交易所类，继承 `BaseExchange`：

```python
# src/quant1024/exchanges/binance.py

from .base import BaseExchange
from typing import Dict, List, Any, Optional

class Binance(BaseExchange):
    """Binance 交易所连接器"""
    
    def __init__(self, api_key: str, api_secret: str, 
                 base_url: str = "https://api.binance.com", **kwargs):
        super().__init__(api_key, api_secret, base_url, **kwargs)
        # Binance 特定的初始化
        self.session = requests.Session()
    
    def get_ticker(self, market: str) -> Dict[str, Any]:
        """获取 Binance 行情"""
        # 调用 Binance API
        response = self._request("GET", f"/api/v3/ticker/24hr?symbol={market}")
        
        # 转换为统一格式
        return {
            'last_price': response['lastPrice'],
            'volume_24h': response['volume'],
            'high_24h': response['highPrice'],
            'low_24h': response['lowPrice']
        }
    
    def get_positions(self, market: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取 Binance 持仓"""
        # 调用 Binance API
        response = self._request("GET", "/fapi/v2/positionRisk")
        
        # 转换为统一格式
        positions = []
        for pos in response:
            if market is None or pos['symbol'] == market:
                positions.append({
                    'market': pos['symbol'],
                    'size': pos['positionAmt'],
                    'side': 'long' if float(pos['positionAmt']) > 0 else 'short',
                    'entry_price': pos['entryPrice']
                })
        return positions
    
    def place_order(self, market: str, side: str, order_type: str,
                   size: str, price: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """在 Binance 下单"""
        # 构造 Binance 订单参数
        params = {
            'symbol': market,
            'side': side.upper(),
            'type': order_type.upper(),
            'quantity': size
        }
        
        if price:
            params['price'] = price
        
        # 调用 Binance API
        response = self._request("POST", "/fapi/v1/order", data=params)
        
        # 转换为统一格式
        return {
            'order_id': response['orderId'],
            'status': response['status'].lower(),
            'filled_size': response['executedQty']
        }
    
    # 实现其他必需的抽象方法...
    def get_server_time(self) -> Dict[str, Any]: ...
    def get_health(self) -> Dict[str, Any]: ...
    def get_exchange_info(self) -> Dict[str, Any]: ...
    # ...
```

### 步骤 2：注册到 __init__.py

```python
# src/quant1024/exchanges/__init__.py

from .base import BaseExchange
from .exchange_1024ex import Exchange1024ex
from .binance import Binance  # 新增

__all__ = ["BaseExchange", "Exchange1024ex", "Binance"]
```

### 步骤 3：更新 start_trading()

```python
# src/quant1024/live_trading.py

def start_trading(..., exchange: str = "1024ex", ...):
    # 创建交易所连接
    if exchange.lower() == "1024ex":
        exchange_client = Exchange1024ex(...)
    elif exchange.lower() == "binance":
        from .exchanges import Binance
        exchange_client = Binance(...)
    else:
        raise InvalidParameterError(f"暂不支持交易所: {exchange}")
    
    # 创建交易器（无需修改这部分代码！）
    trader = LiveTrader(
        strategy=strategy,
        exchange=exchange_client,  # BaseExchange 类型
        ...
    )
```

### 步骤 4：立即可用！

```python
from quant1024 import start_trading, MyStrategy

# 使用 1024ex
start_trading(
    strategy=MyStrategy(...),
    exchange="1024ex",
    market="BTC-PERP",
    ...
)

# 使用 Binance（无需修改策略代码！）
start_trading(
    strategy=MyStrategy(...),  # 同一个策略！
    exchange="binance",
    market="BTCUSDT",
    ...
)
```

## 🎨 数据标准化

### 问题：不同交易所返回格式不同

```python
# 1024ex
{
    'last_price': '50000.00',
    'mark_price': '49990.00',
    'volume_24h': '1000000'
}

# Binance
{
    'lastPrice': '50000.00',
    'markPrice': '49990.00',
    'volume': '1000000'
}
```

### 解决方案：在交易所实现层标准化

每个交易所的实现负责将原始数据转换为统一格式：

```python
class Exchange1024ex(BaseExchange):
    def get_ticker(self, market: str) -> Dict[str, Any]:
        response = self._request("GET", f"/api/v1/ticker/{market}")
        # 已经是标准格式，直接返回
        return response

class Binance(BaseExchange):
    def get_ticker(self, market: str) -> Dict[str, Any]:
        response = self._request("GET", f"/api/v3/ticker/24hr?symbol={market}")
        # 转换为标准格式
        return {
            'last_price': response['lastPrice'],      # 标准字段名
            'mark_price': response.get('markPrice'),
            'volume_24h': response['volume']
        }
```

**好处**：
- ✅ `LiveTrader` 无需关心数据格式差异
- ✅ 用户代码可以无缝切换交易所
- ✅ 每个交易所实现负责自己的数据转换

## 🧪 易于测试

使用 Mock 对象测试 `LiveTrader`：

```python
from unittest.mock import Mock
from quant1024.live_trading import LiveTrader

def test_live_trader():
    # 创建 Mock 交易所
    mock_exchange = Mock(spec=BaseExchange)
    mock_exchange.get_ticker.return_value = {'last_price': '50000'}
    mock_exchange.get_positions.return_value = []
    mock_exchange.place_order.return_value = {'order_id': '123'}
    
    # 测试 LiveTrader
    trader = LiveTrader(
        strategy=TestStrategy(),
        exchange=mock_exchange,  # 使用 Mock！
        market="BTC-PERP",
        initial_capital=10000
    )
    
    trader.start(max_iterations=1)
    
    # 验证调用
    assert mock_exchange.get_ticker.called
```

## 📊 当前实现状态

### 已实现
- ✅ `BaseExchange` 抽象接口
- ✅ `Exchange1024ex` 完整实现（38个端点）
- ✅ `LiveTrader` 使用抽象接口

### 未来支持
- 🔄 `Binance` - 币安
- 🔄 `IBKR` - 盈透证券
- 🔄 更多交易所...

## 💡 最佳实践

### ✅ 推荐做法

1. **保持接口稳定**
   - 不要随意修改 `BaseExchange` 的方法签名
   - 新增功能优先通过 `**kwargs` 扩展

2. **统一数据格式**
   - 每个交易所实现负责数据标准化
   - 保持返回字段的一致性

3. **充分测试**
   - 使用 Mock 测试 `LiveTrader`
   - 单独测试每个交易所实现

### ❌ 避免做法

1. **不要在 LiveTrader 中硬编码交易所特定逻辑**
   ```python
   # ❌ 错误
   if isinstance(self.exchange, Exchange1024ex):
       # 特殊处理
   
   # ✅ 正确
   # 通过抽象接口调用，无需判断具体类型
   ticker = self.exchange.get_ticker(market)
   ```

2. **不要直接访问交易所私有方法**
   ```python
   # ❌ 错误
   result = self.exchange._request(...)
   
   # ✅ 正确
   result = self.exchange.get_ticker(...)
   ```

## 🎯 总结

这个架构设计实现了：

1. **高度抽象** - `LiveTrader` 依赖接口，不依赖具体实现
2. **易于扩展** - 添加新交易所只需实现 `BaseExchange`
3. **数据统一** - 统一的接口和数据格式
4. **易于测试** - 可以使用 Mock 对象
5. **用户友好** - 用户无需关心底层差异

**核心优势**：用户的策略代码可以在**任何交易所**上运行，无需修改！

```python
# 同一个策略，不同交易所
strategy = MyStrategy(name="趋势策略")

# 1024ex
start_trading(strategy=strategy, exchange="1024ex", ...)

# Binance
start_trading(strategy=strategy, exchange="binance", ...)

# IBKR
start_trading(strategy=strategy, exchange="ibkr", ...)
```

这就是**跨交易所量化交易工具包**的核心价值！🚀


# Monitor Feeds - Runtime 监控模块

> 基于 IMPLEMENTATION_GUIDE_V2.md 实现

## 📋 概述

这个模块提供了 LiveTrading 的 Runtime 监控功能，可以将交易数据实时发送到监控服务器。

### 核心特性

✅ **简化设计** - 只需一个 `runtime_config` 参数  
✅ **灵活配置** - 支持自定义记录服务  
✅ **异步报告** - 不影响交易性能  
✅ **完整监控** - 信号、交易、持仓全覆盖  

---

## 📦 模块结构

```
monitor_feeds/
├── __init__.py              # 模块导出
├── types.py                 # RuntimeConfig 类型定义
├── runtime_reporter.py      # RuntimeReporter 报告器
└── README.md               # 本文档
```

---

## 🚀 快速开始

### 1. 最简单的使用（只需一个 api_key）

```python
from quant1024 import start_trading, QuantStrategy

class MyStrategy(QuantStrategy):
    def generate_signals(self, data):
        if len(data) < 2:
            return [0]
        return [1 if data[-1] > data[-2] else -1]
    
    def calculate_position(self, signal, current_position):
        if signal == 1:
            return 1.0
        elif signal == -1:
            return 0.0
        return current_position

# 启用监控 - 最简单！
trader = start_trading(
    strategy=MyStrategy(name="趋势策略"),
    api_key="exchange_api_key",
    api_secret="exchange_api_secret",
    market="BTC-PERP",
    
    # ✨ 只需这一个参数启用监控
    runtime_config={
        "api_key": "server_api_key"  # 记录服务的 API Key
    }
)
```

**自动行为：**
- `runtime_id`: 自动生成 UUID
- `strategy_id`: 从环境变量 `STRATEGY_ID` 读取
- `api_base_url`: 默认 `https://api.1024ex.com`
- `environment`: 从环境变量 `ENVIRONMENT` 读取，默认 `"local"`

---

### 2. 完整配置

```python
trader = start_trading(
    strategy=MyStrategy(name="策略"),
    api_key="exchange_api_key",
    api_secret="exchange_api_secret",
    market="BTC-PERP",
    
    runtime_config={
        "api_key": "server_api_key",           # 必填
        "api_base_url": "https://custom.com",  # 可选，自定义记录服务
        "runtime_id": "custom-runtime-id",     # 可选，自定义 runtime ID
        "strategy_id": "strategy-uuid",        # 可选，策略 ID
        "environment": "production",           # 可选，运行环境
        "metadata": {                          # 可选，额外元数据
            "version": "1.0",
            "description": "生产环境策略"
        }
    }
)
```

---

### 3. 不启用监控

```python
# 不传 runtime_config，不启用监控
trader = start_trading(
    strategy=MyStrategy(name="策略"),
    api_key="exchange_api_key",
    api_secret="exchange_api_secret",
    market="BTC-PERP"
    # runtime_config=None (默认)
)
```

---

## 🔧 高级用法

### 使用环境变量

```bash
# 设置环境变量
export STRATEGY_ID="my-strategy-uuid"
export ENVIRONMENT="production"
export API_BASE_URL="https://custom-api.com"  # 可选
```

```python
# Python 代码中会自动读取
trader = start_trading(
    strategy=MyStrategy(name="策略"),
    api_key="exchange_api_key",
    api_secret="exchange_api_secret",
    market="BTC-PERP",
    runtime_config={
        "api_key": "server_api_key"
        # strategy_id 和 environment 会从环境变量读取
    }
)
```

---

### 直接使用 RuntimeReporter

```python
from quant1024.monitor_feeds import RuntimeConfig, RuntimeReporter

# 创建配置
config = RuntimeConfig(
    api_key="server_api_key",
    api_base_url="https://api.1024ex.com"
)

# 创建报告器
reporter = RuntimeReporter(config)

# 创建 Runtime
reporter.create_runtime(
    market="BTC-PERP",
    initial_capital=10000,
    max_position_size=0.5
)

# 报告交易
reporter.report_trade(
    market="BTC-PERP",
    side="buy",
    size=0.1,
    price=50000,
    order_id="order-123"
)

# 报告信号
reporter.report_signal(
    market="BTC-PERP",
    signal=1,  # 1=buy, -1=sell, 0=hold
    price=50000
)

# 报告持仓
reporter.report_position(
    market="BTC-PERP",
    position_size=0.1,
    entry_price=50000,
    current_price=51000
)

# 更新状态
reporter.update_runtime_status(
    "stopped",
    total_trades=10
)
```

---

## 📡 监控数据类型

### 1. Runtime 创建
```json
{
  "runtime_id": "uuid",
  "strategy_id": "uuid",
  "market": "BTC-PERP",
  "initial_capital": 10000,
  "max_position_size": 0.5,
  "environment": "local",
  "sdk_version": "1.0.0",
  "status": "running",
  "start_time": "2024-11-11T10:00:00Z"
}
```

### 2. 交易报告
```json
{
  "runtime_id": "uuid",
  "strategy_id": "uuid",
  "market": "BTC-PERP",
  "side": "buy",
  "size": 0.1,
  "price": 50000,
  "order_id": "order-123",
  "timestamp": "2024-11-11T10:00:00Z"
}
```

### 3. 信号报告
```json
{
  "runtime_id": "uuid",
  "strategy_id": "uuid",
  "market": "BTC-PERP",
  "signal": 1,
  "price": 50000,
  "timestamp": "2024-11-11T10:00:00Z"
}
```

### 4. 持仓报告
```json
{
  "runtime_id": "uuid",
  "strategy_id": "uuid",
  "market": "BTC-PERP",
  "position_size": 0.1,
  "entry_price": 50000,
  "current_price": 51000,
  "pnl": 100,
  "pnl_pct": 0.02,
  "timestamp": "2024-11-11T10:00:00Z"
}
```

---

## 🔑 关键概念

### api_base_url 的作用

**重要理解**：
- `api_base_url` 是**记录服务**的地址
- 与 `exchange`（交易所）**无关**
- 默认使用 1024ex 的记录服务
- 可自定义（如自建记录服务）

**示例：**

```
┌─────────────────────────────────────────────────────────┐
│              交易 vs 记录                                 │
└─────────────────────────────────────────────────────────┘

交易所 API (exchange):
  - 用途: 执行交易
  - 配置: api_key, api_secret, base_url
  - 示例: 
    * 1024ex: https://api.1024ex.com (交易)
    * Binance: https://api.binance.com (交易)

记录服务 API (runtime_config.api_base_url):
  - 用途: 记录交易数据、Runtime 统计
  - 配置: runtime_config.api_base_url
  - 示例:
    * 1024ex 记录服务: https://api.1024ex.com
    * 自建记录服务: https://my-api.com

可以混搭:
  ✅ 在 Binance 交易 + 使用 1024ex 记录
  ✅ 在 1024ex 交易 + 使用自建记录
  ✅ 在任意交易所 + 使用任意记录服务
```

---

## ⚡ 性能说明

### 异步报告

所有监控报告都是**异步执行**的，不会阻塞交易主流程：

- 使用 `ThreadPoolExecutor` 异步发送
- 最多 3 个并发线程
- 超时时间 10 秒
- 失败会记录日志，但不影响交易

### 资源清理

- 使用 `atexit` 注册清理函数
- 程序退出时自动清理资源
- 等待所有挂起的任务完成（最多 5 秒）

---

## 🛡️ 错误处理

### 创建 Runtime 失败

```python
# 如果创建 Runtime 失败，会禁用监控但不影响交易
trader = start_trading(
    strategy=MyStrategy(name="策略"),
    api_key="exchange_api_key",
    api_secret="exchange_api_secret",
    market="BTC-PERP",
    runtime_config={
        "api_key": "invalid_key"  # 错误的 key
    }
)
# 交易会继续，但监控被禁用
```

### 报告失败

```python
# 报告失败只会记录警告日志，不会抛出异常
reporter.report_trade(...)  # 即使失败，也不影响交易
```

---

## 📊 使用场景

### 场景 1: 开发测试

```python
# 本地开发，使用默认配置
trader = start_trading(
    strategy=MyStrategy(name="测试策略"),
    api_key="test_key",
    api_secret="test_secret",
    market="BTC-PERP",
    runtime_config={
        "api_key": "test_server_key"
    }
)
# environment 自动为 "local"
```

### 场景 2: 生产环境

```python
# 生产环境，完整配置
trader = start_trading(
    strategy=MyStrategy(name="生产策略"),
    api_key="prod_key",
    api_secret="prod_secret",
    market="BTC-PERP",
    runtime_config={
        "api_key": "prod_server_key",
        "environment": "production",
        "strategy_id": "prod-strategy-uuid",
        "metadata": {
            "version": "2.0.0",
            "deployed_by": "auto-deploy"
        }
    }
)
```

### 场景 3: 自建监控服务

```python
# 使用自己的监控服务
trader = start_trading(
    strategy=MyStrategy(name="策略"),
    api_key="exchange_key",
    api_secret="exchange_secret",
    market="BTC-PERP",
    runtime_config={
        "api_key": "my_server_key",
        "api_base_url": "https://my-monitoring.com"
    }
)
```

---

## 🧪 测试

### 单元测试示例

```python
import unittest
from unittest.mock import Mock, patch
from quant1024.monitor_feeds import RuntimeConfig, RuntimeReporter

class TestRuntimeReporter(unittest.TestCase):
    def test_create_runtime(self):
        config = RuntimeConfig(api_key="test_key")
        reporter = RuntimeReporter(config)
        
        with patch.object(reporter.session, 'post') as mock_post:
            mock_post.return_value.status_code = 200
            
            result = reporter.create_runtime(
                market="BTC-PERP",
                initial_capital=10000,
                max_position_size=0.5
            )
            
            self.assertTrue(result)
            self.assertTrue(mock_post.called)
```

---

## 📚 API 参考

### RuntimeConfig

```python
@dataclass
class RuntimeConfig:
    api_key: str                              # 必填
    runtime_id: str = uuid4()                 # 自动生成
    strategy_id: Optional[str] = None         # 可选
    api_base_url: str = "https://..."         # 默认值
    environment: str = "local"                # 默认值
    sdk_version: Optional[str] = None         # 自动填充
    extra_metadata: Optional[Dict] = None     # 可选
```

### RuntimeReporter

```python
class RuntimeReporter:
    def create_runtime(market, initial_capital, max_position_size) -> bool
    def update_runtime_status(status, **kwargs) -> None
    def report_trade(market, side, size, price, order_id, **kwargs) -> None
    def report_signal(market, signal, price, **kwargs) -> None
    def report_position(market, position_size, entry_price, current_price, **kwargs) -> None
```

---

## 📝 日志

### 日志级别

- **INFO**: Runtime 创建成功、交易报告成功
- **DEBUG**: 详细的报告信息
- **WARNING**: 创建失败、报告失败（不影响交易）
- **ERROR**: 严重错误

### 日志示例

```
2024-11-11 10:00:00 - INFO - RuntimeReporter initialized: runtime_id=xxx, api_base_url=https://...
2024-11-11 10:00:01 - INFO - Runtime created successfully: xxx
2024-11-11 10:00:02 - DEBUG - Trade reported successfully: buy 0.1 @ 50000
2024-11-11 10:00:03 - WARNING - Failed to report signal: status=500
```

---

## ✅ 最佳实践

1. **生产环境使用环境变量**
   ```bash
   export STRATEGY_ID="prod-strategy-uuid"
   export ENVIRONMENT="production"
   ```

2. **添加有用的元数据**
   ```python
   runtime_config={
       "api_key": "key",
       "metadata": {
           "version": "1.0.0",
           "git_commit": "abc123",
           "deployed_at": "2024-11-11"
       }
   }
   ```

3. **自定义 runtime_id 便于追踪**
   ```python
   import uuid
   runtime_config={
       "api_key": "key",
       "runtime_id": f"strategy-{uuid.uuid4()}"
   }
   ```

4. **开发环境禁用监控节省请求**
   ```python
   # 开发时不传 runtime_config
   trader = start_trading(
       strategy=strategy,
       api_key=api_key,
       api_secret=api_secret,
       market=market
   )
   ```

---

## 🔗 相关文档

- [IMPLEMENTATION_GUIDE_V2.md](../../../SDK_DOCUMENTS/Live%20trading%20data%20feed/IMPLEMENTATION_GUIDE_V2.md) - 完整实施指南
- [live_trading.py](../live_trading.py) - LiveTrader 实现

---

**版本**: 1.0  
**日期**: 2024-11-11  
**状态**: ✅ 已实现


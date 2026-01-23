# quant1024 SDK 使用示例

本目录包含 quant1024 SDK 的使用示例，展示如何通过 SDK 与 1024 Exchange API 交互。

## 文件说明

| 文件 | 说明 |
|------|------|
| `authenticated_example.py` | 使用 JSON 配置文件进行 API 认证的完整示例 |
| `sdk_usage_example.py` | SDK 基本使用示例 |
| `story_test_flows.py` | 基于测试故事的完整业务流程示例 |

## 快速开始

### 1. 安装 SDK

```bash
cd quant1024
source .venv/bin/activate  # 或创建新的虚拟环境
uv pip install -e .
```

### 2. 配置 API Key

在项目根目录 (`1024ex/`) 创建配置文件 `1024-trading-api-key-quant.json`:

```json
{
  "api_key": "1024_xxxxxxxx...",
  "secret_key": "yyyyyyyy...",
  "label": "quant",
  "permissions": {
    "can_trade": true,
    "can_read": true,
    "can_withdraw": false
  }
}
```

### 3. 运行示例

```bash
# 认证示例 - 测试 API 连接和认证
python examples/sdk-examples/authenticated_example.py

# SDK 使用示例 - 基本 API 调用
python examples/sdk-examples/sdk_usage_example.py

# 故事测试流程 - 完整业务流程 (dry-run 模式)
DRY_RUN=true python examples/sdk-examples/story_test_flows.py
```

## SDK 认证机制

SDK 使用 HMAC-SHA256 签名进行 API 认证:

```python
from quant1024 import Exchange1024ex

exchange = Exchange1024ex(
    api_key="1024_xxx...",
    secret_key="yyy...",
    base_url="https://api.1024ex.com"
)
```

### 认证 Headers

| Header | 说明 |
|--------|------|
| `X-API-KEY` | API Key |
| `X-SIGNATURE` | HMAC-SHA256 签名 |
| `X-TIMESTAMP` | Unix 时间戳 (毫秒) |
| `X-RECV-WINDOW` | 请求有效窗口 (默认 5000ms) |

### 签名算法

```
Signature = HMAC-SHA256(secret_key, timestamp + method + path + body)
```

## 模块概览

```python
exchange = Exchange1024ex(api_key, secret_key)

# 永续合约
exchange.perp.get_markets()
exchange.perp.get_ticker("BTC-USDC")
exchange.perp.place_order(...)
exchange.perp.get_positions()

# 现货
exchange.spot.get_balances()
exchange.spot.place_order(...)

# 预测市场
exchange.prediction.list_markets()
exchange.prediction.mint(...)
exchange.prediction.get_my_positions()

# 锦标赛
exchange.championship.list_championships()
exchange.championship.get_leaderboard(...)

# 账户
exchange.account.get_overview()
exchange.account.get_perp_margin()
exchange.account.deposit(...)
```

## 环境配置

| 环境 | BASE_URL |
|------|----------|
| 生产环境 | `https://api.1024ex.com` (默认) |
| 测试网 | `https://testnet-api.1024ex.com` |
| 本地开发 | `http://localhost:8090` |

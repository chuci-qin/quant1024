# quant1024 SDK 使用示例

本目录包含 quant1024 SDK 的使用示例，展示如何通过 SDK 与 1024 Exchange API 交互。

## 文件说明

| 文件 | 说明 |
|------|------|
| `authenticated_example.py` | 使用 JSON 配置文件进行 API 认证的完整示例 |
| `sdk_usage_example.py` | SDK 基本使用示例 |
| `story_test_flows.py` | 基于测试故事的完整业务流程示例 |
| `price_trigger_buy.py` | 价格触发自动购买脚本 - 监控价格并在到达目标时自动下单 |

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

# 价格触发自动购买 - 当价格到达目标时自动下单
python examples/sdk-examples/price_trigger_buy.py --market BTC-USDC --trigger-price 90000 --size 0.01
```

## 价格触发自动购买

`price_trigger_buy.py` 是一个监控价格并在到达目标价格时自动执行买入的脚本。

### 基本用法

```bash
# 当 BTC 跌到 90000 时市价买入 0.01 BTC (永续合约做多)
python price_trigger_buy.py --market BTC-USDC --trigger-price 90000 --size 0.01

# 当 BTC 跌到 90000 时，以 89500 限价买入
python price_trigger_buy.py --market BTC-USDC --trigger-price 90000 --size 0.01 --order-price 89500

# 当 ETH 涨到 4000 时买入 (追涨模式)
python price_trigger_buy.py --market ETH-USDC --trigger-price 4000 --size 0.1 --direction up

# 现货交易
python price_trigger_buy.py --market SOL-USDC --trigger-price 180 --size 5 --mode spot

# 设置杠杆倍数 (仅永续合约)
python price_trigger_buy.py --market BTC-USDC --trigger-price 90000 --size 0.1 --leverage 5

# 模拟运行 (不实际下单)
python price_trigger_buy.py --market BTC-USDC --trigger-price 90000 --size 0.01 --dry-run
```

### 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--market` | ✅ | 交易市场，如 BTC-USDC |
| `--trigger-price` | ✅ | 触发价格 |
| `--size` | ✅ | 购买数量 |
| `--order-price` | ❌ | 下单价格，不填则使用市价单 |
| `--direction` | ❌ | 触发方向: down=跌破买入, up=涨破买入 (默认: down) |
| `--mode` | ❌ | 交易模式: perp=永续合约, spot=现货 (默认: perp) |
| `--leverage` | ❌ | 杠杆倍数，仅永续合约 (默认: 1) |
| `--interval` | ❌ | 价格检查间隔秒数 (默认: 2) |
| `--dry-run` | ❌ | 模拟运行，不实际下单 |

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

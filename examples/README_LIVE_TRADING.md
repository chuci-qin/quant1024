# 🚀 实盘交易示例

这个文件夹包含了实盘交易的各种示例。

## 快速开始

只需三步即可开始交易：

### 1️⃣ 创建策略

```python
from quant1024 import QuantStrategy

class MyStrategy(QuantStrategy):
    def generate_signals(self, data):
        # 你的策略逻辑
        if len(data) < 2:
            return [0]
        return [1 if data[-1] > data[-2] else -1]
    
    def calculate_position(self, signal, current_position):
        return 0.5 if signal == 1 else 0.0
```

### 2️⃣ 配置 API

```python
API_KEY = "your_api_key_here"
API_SECRET = "your_api_secret_here"
```

### 3️⃣ 开始交易！

```python
from quant1024 import start_trading

start_trading(
    strategy=MyStrategy(name="我的策略"),
    api_key=API_KEY,
    api_secret=API_SECRET,
    market="BTC-PERP",
    initial_capital=10000
)
```

## 📁 示例文件

### `live_trading_example.py`

包含 4 个完整示例：

1. **简单趋势策略** - 最简单的入门示例
2. **动量策略** - 带参数的策略
3. **均线策略** - 经典双均线策略
4. **手动控制** - 更细粒度的控制

运行示例：

```bash
cd examples
python live_trading_example.py
```

## ⚠️ 重要提示

1. **替换 API Key**: 请将示例中的 `your_api_key_here` 替换为你自己的 API Key
2. **小资金测试**: 建议先用小资金测试策略
3. **充分回测**: 实盘前请确保策略经过充分回测
4. **风险管理**: 设置合理的止损止盈

## 📖 更多文档

- [实盘交易指南](../guide/zh-hans/LIVE_TRADING.md) - 完整文档
- [策略开发指南](../guide/zh-hans/USAGE.md) - 如何开发策略
- [API 文档](../README_zh.md) - 完整 API 参考

## 🎯 最佳实践

### ✅ 推荐做法

- 先回测，后实盘
- 小仓位开始（10-30%）
- 设置止损止盈
- 选择合理的检查间隔（避免过度交易）

### ❌ 避免做法

- 不要投入无法承受损失的资金
- 不要在未回测的情况下实盘
- 不要使用过高的杠杆
- 不要频繁修改策略参数

## 💡 示例策略说明

### 简单趋势策略
- **逻辑**: 价格上涨买入，下跌卖出
- **适用**: 趋势明显的市场
- **风险**: 震荡市场可能频繁止损

### 动量策略
- **逻辑**: 基于价格动量判断
- **适用**: 有明确趋势的市场
- **风险**: 动量反转时可能亏损

### 均线策略
- **逻辑**: 短期均线与长期均线交叉
- **适用**: 中长期趋势跟踪
- **风险**: 滞后性，可能错过最佳入场点

## 🆘 需要帮助？

- 查看 [详细文档](../guide/zh-hans/LIVE_TRADING.md)
- 提交 [Issue](https://github.com/yourusername/quant1024/issues)
- 参考其他 [示例代码](.)

**祝交易顺利！** 🎉


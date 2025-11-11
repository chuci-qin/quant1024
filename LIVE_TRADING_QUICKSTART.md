# 🚀 实盘交易快速入门

## 一行代码开始交易！

`quant1024` 现在支持**超简单的实盘交易**！只需要几行代码，你的策略就能开始实盘运行。

## ⚡ 5秒钟开始你的第一笔交易

```python
from quant1024 import QuantStrategy, start_trading

# 1. 定义策略（只需实现两个方法）
class MyStrategy(QuantStrategy):
    def generate_signals(self, data):
        # 你的策略逻辑
        if len(data) < 2:
            return [0]
        return [1 if data[-1] > data[-2] else -1]
    
    def calculate_position(self, signal, current_position):
        return 0.5 if signal == 1 else 0.0

# 2. 开始交易！（就一行！）
start_trading(
    strategy=MyStrategy(name="我的策略"),
    api_key="your_api_key",
    api_secret="your_api_secret",
    market="BTC-PERP",
    initial_capital=10000
)
```

**就这样！你的策略现在正在实盘交易！** 🎉

---

## 🎯 完整示例

```python
from quant1024 import QuantStrategy, start_trading

class SimpleTrendStrategy(QuantStrategy):
    """简单趋势跟踪策略"""
    
    def generate_signals(self, data):
        """
        生成交易信号
        - 价格上涨 -> 买入(1)
        - 价格下跌 -> 卖出(-1)
        """
        if len(data) < 2:
            return [0]
        
        signals = []
        for i in range(len(data)):
            if i == 0:
                signals.append(0)
            elif data[i] > data[i-1]:
                signals.append(1)   # 买入
            else:
                signals.append(-1)  # 卖出
        return signals
    
    def calculate_position(self, signal, current_position):
        """
        计算目标仓位
        - 买入信号 -> 持有 50% 仓位
        - 卖出信号 -> 清空仓位
        """
        if signal == 1:
            return 0.5  # 50% 仓位
        elif signal == -1:
            return 0.0  # 清仓
        return current_position

# 开始实盘交易
start_trading(
    strategy=SimpleTrendStrategy(name="趋势策略"),
    api_key="your_api_key_here",          # 替换为你的 API Key
    api_secret="your_api_secret_here",    # 替换为你的 API Secret
    market="BTC-PERP",                     # 交易对
    initial_capital=10000,                 # 初始资金 $10,000
    max_position_size=0.5,                 # 最多用 50% 仓位
    check_interval=60,                     # 每 60 秒检查一次
    stop_loss=0.05,                        # 5% 止损
    take_profit=0.10                       # 10% 止盈
)
```

---

## 📊 系统会自动为你做什么

当你调用 `start_trading()` 后，系统会自动：

✅ **连接交易所** - 自动处理认证和连接  
✅ **获取实时数据** - 每隔一定时间获取最新价格  
✅ **生成交易信号** - 使用你的策略分析市场  
✅ **执行交易** - 根据信号自动下单  
✅ **风险管理** - 自动止损止盈  
✅ **日志记录** - 实时输出交易状态  
✅ **错误处理** - 自动重试和错误恢复  

---

## ⚙️ 参数说明

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `strategy` | ✅ | - | 你的交易策略 |
| `api_key` | ✅ | - | API Key |
| `api_secret` | ✅ | - | API Secret |
| `market` | ✅ | - | 交易对（如 "BTC-PERP"） |
| `initial_capital` | ❌ | 10000 | 初始资金 |
| `max_position_size` | ❌ | 0.5 | 最大仓位比例（0-1） |
| `check_interval` | ❌ | 60 | 检查间隔（秒） |
| `stop_loss` | ❌ | 0.05 | 止损比例（5%） |
| `take_profit` | ❌ | 0.10 | 止盈比例（10%） |

---

## 🎮 控制交易

### 停止交易

按 `Ctrl+C` 即可安全停止交易。

### 查看状态

如果你想更多控制，可以这样：

```python
from quant1024 import Exchange1024ex, LiveTrader

# 手动创建交易器
exchange = Exchange1024ex(api_key="...", api_secret="...")
trader = LiveTrader(
    strategy=MyStrategy(...),
    exchange=exchange,
    market="BTC-PERP",
    initial_capital=10000
)

# 运行指定次数（测试用）
trader.start(max_iterations=10)

# 查看状态
print(trader.get_status())
```

---

## 📖 更多示例

查看 `examples/live_trading_example.py` 获取更多示例：

- ✅ 简单趋势策略
- ✅ 动量策略
- ✅ 均线策略
- ✅ 手动控制示例

运行示例：

```bash
cd examples
python live_trading_example.py
```

---

## 🛡️ 风险提示

⚠️ **实盘交易有风险，请谨慎操作！**

建议：
1. 先用回测验证策略
2. 从小资金开始（建议 < $1000）
3. 使用小仓位（建议 < 30%）
4. 设置合理的止损（建议 2-5%）
5. 不要投入超过你能承受损失的资金

---

## 💡 最佳实践

### ✅ 推荐做法

```python
# 1. 先回测
strategy = MyStrategy(name="测试")
result = strategy.backtest(historical_prices)

# 2. 如果夏普比率 > 1，再实盘
if result['sharpe_ratio'] > 1.0:
    start_trading(
        strategy=strategy,
        initial_capital=1000,       # 小资金
        max_position_size=0.2,      # 小仓位
        stop_loss=0.03,             # 严格止损
        ...
    )
```

### ❌ 避免做法

- ❌ 不回测就直接实盘
- ❌ 使用过大的仓位
- ❌ 不设置止损
- ❌ 频繁修改策略参数

---

## 🚀 立即开始

1. **安装包**
   ```bash
   pip install quant1024
   ```

2. **复制示例代码**
   - 替换 API Key 和 Secret
   - 调整参数（资金、仓位等）

3. **运行**
   ```bash
   python your_strategy.py
   ```

4. **监控日志**
   - 观察交易执行情况
   - 根据需要调整参数

---

## 📚 完整文档

- [实盘交易指南](guide/zh-hans/LIVE_TRADING.md) - 详细文档
- [策略开发指南](guide/zh-hans/USAGE.md) - 如何开发策略
- [API 参考](README_zh.md) - 完整 API 文档

---

## 🎉 开始你的交易之旅！

现在你已经掌握了使用 `quant1024` 进行实盘交易的所有知识。

记住：
- 从小开始
- 充分测试
- 严格风控

**祝交易顺利！** 🚀

---

## 需要帮助？

- 查看 [详细文档](guide/zh-hans/LIVE_TRADING.md)
- 运行 [示例代码](examples/live_trading_example.py)
- 提交 [Issue](https://github.com/yourusername/quant1024/issues)


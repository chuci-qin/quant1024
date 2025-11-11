# 实盘交易指南

## 🚀 最简单的实盘交易方式

`quant1024` 提供了 `start_trading()` 函数，让你用**一行代码**就能开始实盘交易！

## 快速开始

### 步骤 1：创建策略

```python
from quant1024 import QuantStrategy

class MyStrategy(QuantStrategy):
    """你的交易策略"""
    
    def generate_signals(self, data):
        """生成交易信号"""
        if len(data) < 2:
            return [0]
        
        # 简单的趋势跟踪
        if data[-1] > data[-2]:
            return [1]   # 买入
        else:
            return [-1]  # 卖出
    
    def calculate_position(self, signal, current_position):
        """计算仓位"""
        if signal == 1:
            return 0.5  # 50% 仓位
        elif signal == -1:
            return 0.0  # 清仓
        return current_position
```

### 步骤 2：开始交易

```python
from quant1024 import start_trading

# 就这么简单！
start_trading(
    strategy=MyStrategy(name="我的策略"),
    api_key="your_api_key",
    api_secret="your_api_secret",
    market="BTC-PERP",
    initial_capital=10000
)
```

完成！你的策略现在正在实盘运行！ 🎉

---

## 📖 完整参数说明

```python
start_trading(
    # === 必填参数 ===
    strategy=MyStrategy(name="策略名"),  # 你的策略
    api_key="...",                      # API Key
    api_secret="...",                   # API Secret
    market="BTC-PERP",                  # 交易对
    
    # === 可选参数 ===
    initial_capital=10000,              # 初始资金（默认 10000）
    exchange="1024ex",                  # 交易所（默认 1024ex）
    base_url="https://api.1024ex.com",  # API地址
    max_position_size=0.5,              # 最大仓位比例（默认 0.5 = 50%）
    check_interval=60,                  # 检查间隔秒数（默认 60秒）
    stop_loss=0.05,                     # 止损比例（默认 5%）
    take_profit=0.10                    # 止盈比例（默认 10%）
)
```

---

## 🎯 实战示例

### 示例 1：简单趋势策略

```python
from quant1024 import QuantStrategy, start_trading

class TrendStrategy(QuantStrategy):
    def generate_signals(self, data):
        if len(data) < 2:
            return [0]
        
        signals = []
        for i in range(len(data)):
            if i == 0:
                signals.append(0)
            elif data[i] > data[i-1]:
                signals.append(1)   # 上涨
            else:
                signals.append(-1)  # 下跌
        return signals
    
    def calculate_position(self, signal, current_position):
        if signal == 1:
            return 0.5  # 做多 50%
        elif signal == -1:
            return 0.0  # 平仓
        return current_position

# 开始交易
start_trading(
    strategy=TrendStrategy(name="趋势"),
    api_key="your_api_key",
    api_secret="your_api_secret",
    market="BTC-PERP",
    initial_capital=10000,
    max_position_size=0.5,
    check_interval=60,
    stop_loss=0.05,      # 5% 止损
    take_profit=0.10     # 10% 止盈
)
```

### 示例 2：动量策略

```python
class MomentumStrategy(QuantStrategy):
    def __init__(self, name, params=None):
        super().__init__(name, params)
        self.lookback = self.params.get('lookback', 10)
    
    def generate_signals(self, data):
        if len(data) < self.lookback + 1:
            return [0] * len(data)
        
        signals = []
        for i in range(len(data)):
            if i < self.lookback:
                signals.append(0)
            else:
                # 计算动量
                momentum = (data[i] - data[i-self.lookback]) / data[i-self.lookback]
                if momentum > 0.02:      # 涨超过2%
                    signals.append(1)
                elif momentum < -0.02:   # 跌超过2%
                    signals.append(-1)
                else:
                    signals.append(0)
        return signals
    
    def calculate_position(self, signal, current_position):
        if signal == 1:
            return 0.7  # 70% 仓位
        elif signal == -1:
            return 0.0
        return current_position

# 开始交易
start_trading(
    strategy=MomentumStrategy(
        name="动量",
        params={"lookback": 10}
    ),
    api_key="your_api_key",
    api_secret="your_api_secret",
    market="ETH-PERP",
    initial_capital=20000,
    max_position_size=0.7,
    check_interval=120,  # 2分钟
    stop_loss=0.03,
    take_profit=0.08
)
```

### 示例 3：均线策略

```python
class MAStrategy(QuantStrategy):
    def __init__(self, name, params=None):
        super().__init__(name, params)
        self.short_period = self.params.get('short_period', 5)
        self.long_period = self.params.get('long_period', 20)
    
    def generate_signals(self, data):
        if len(data) < self.long_period:
            return [0] * len(data)
        
        signals = []
        for i in range(len(data)):
            if i < self.long_period:
                signals.append(0)
            else:
                # 计算均线
                short_ma = sum(data[i-self.short_period+1:i+1]) / self.short_period
                long_ma = sum(data[i-self.long_period+1:i+1]) / self.long_period
                
                if short_ma > long_ma:
                    signals.append(1)   # 金叉
                else:
                    signals.append(-1)  # 死叉
        return signals
    
    def calculate_position(self, signal, current_position):
        if signal == 1:
            return 0.8  # 80% 仓位
        elif signal == -1:
            return 0.0
        return current_position

# 开始交易
start_trading(
    strategy=MAStrategy(
        name="双均线",
        params={
            "short_period": 5,
            "long_period": 20
        }
    ),
    api_key="your_api_key",
    api_secret="your_api_secret",
    market="BTC-PERP",
    initial_capital=15000,
    max_position_size=0.8,
    check_interval=300,  # 5分钟
    stop_loss=0.04,
    take_profit=0.12
)
```

---

## 🔌 跨交易所支持

### 设计优势

`LiveTrader` 使用 `BaseExchange` 抽象接口，支持多个交易所：

```python
# 架构图
LiveTrader (交易逻辑)
    ↓ 依赖抽象接口
BaseExchange (统一接口)
    ↓ 实现
Exchange1024ex / Binance / IBKR (具体交易所)
```

**核心优势**：
- ✅ 同一个策略可以在不同交易所运行
- ✅ 无需修改策略代码即可切换交易所
- ✅ 易于添加新的交易所支持

查看 [架构设计文档](../../ARCHITECTURE_LIVE_TRADING.md) 了解详情。

---

## 🎮 高级控制

如果你需要更细粒度的控制，可以使用 `LiveTrader` 类：

```python
from quant1024 import Exchange1024ex, LiveTrader

# 1. 创建交易所连接
exchange = Exchange1024ex(
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# 2. 创建交易器
trader = LiveTrader(
    strategy=MyStrategy(name="策略"),
    exchange=exchange,
    market="BTC-PERP",
    initial_capital=10000,
    max_position_size=0.5,
    check_interval=60,
    stop_loss=0.05,
    take_profit=0.10
)

# 3. 手动控制
try:
    trader.start(max_iterations=10)  # 运行10次循环（测试用）
    # trader.start()  # 无限运行
except KeyboardInterrupt:
    trader.stop()

# 4. 查看状态
print(trader.get_status())
```

---

## ⚙️ 系统运行流程

`start_trading()` 会自动执行以下流程：

1. **初始化**
   - 连接交易所
   - 初始化策略
   - 验证参数

2. **交易循环**（每隔 `check_interval` 秒）
   - 获取最新市场价格
   - 更新价格历史
   - 生成交易信号
   - 计算目标仓位
   - 执行交易（如需要）
   - 检查止损/止盈

3. **风险管理**
   - 自动止损
   - 自动止盈
   - 仓位限制
   - 滑点控制

4. **日志记录**
   - 实时输出交易状态
   - 记录所有交易
   - 错误处理和重试

---

## 🛡️ 风险管理

### 1. 仓位控制

```python
start_trading(
    strategy=MyStrategy(...),
    max_position_size=0.3,  # 最多使用 30% 资金
    ...
)
```

### 2. 止损止盈

```python
start_trading(
    strategy=MyStrategy(...),
    stop_loss=0.05,      # 亏损 5% 自动止损
    take_profit=0.10,    # 盈利 10% 自动止盈
    ...
)
```

### 3. 检查频率

```python
start_trading(
    strategy=MyStrategy(...),
    check_interval=300,  # 每 5 分钟检查一次（避免过度交易）
    ...
)
```

---

## 📊 监控和日志

系统会自动输出详细的日志：

```
2024-01-01 10:00:00 - INFO - ============================================================
2024-01-01 10:00:00 - INFO - 🚀 开始实盘交易
2024-01-01 10:00:00 - INFO - 策略: 趋势策略
2024-01-01 10:00:00 - INFO - 市场: BTC-PERP
2024-01-01 10:00:00 - INFO - 初始资金: $10000
2024-01-01 10:00:00 - INFO - 检查间隔: 60秒
2024-01-01 10:00:00 - INFO - ============================================================
2024-01-01 10:01:00 - INFO - 正在积累历史数据... (5/10)
2024-01-01 10:02:00 - INFO - 正在积累历史数据... (10/10)
2024-01-01 10:03:00 - INFO - 📊 状态 | 价格: $42350.50 | 信号: 🟢 BUY | 当前仓位: 0.0000 | 目标仓位: 0.5000
2024-01-01 10:03:01 - INFO - 📝 执行交易: BUY 0.5000 @ $42350.50
2024-01-01 10:03:02 - INFO - ✅ 交易成功! 订单ID: 123456
```

---

## 🔧 故障排除

### 问题 1：无法连接交易所

```python
# 检查 API Key 和 Secret 是否正确
# 检查网络连接
# 检查 base_url 是否正确
```

### 问题 2：策略不生成信号

```python
# 确保 generate_signals() 返回正确格式的列表
# 检查是否有足够的历史数据
# 添加日志输出调试
```

### 问题 3：交易失败

```python
# 检查账户余额
# 检查订单参数（价格、数量等）
# 查看详细错误日志
```

---

## 💡 最佳实践

### 1. 先回测，后实盘

```python
# 第一步：回测
strategy = MyStrategy(name="测试")
result = strategy.backtest(historical_prices)
print(f"夏普比率: {result['sharpe_ratio']}")

# 第二步：实盘（确认策略有效后）
if result['sharpe_ratio'] > 1.0:
    start_trading(strategy=strategy, ...)
```

### 2. 小仓位开始

```python
# 从小仓位开始测试
start_trading(
    strategy=MyStrategy(...),
    initial_capital=1000,        # 小资金
    max_position_size=0.1,       # 10% 仓位
    ...
)
```

### 3. 设置合理的止损

```python
start_trading(
    strategy=MyStrategy(...),
    stop_loss=0.02,     # 2% 止损（根据策略调整）
    take_profit=0.05,   # 2.5倍盈亏比
    ...
)
```

### 4. 避免过度交易

```python
start_trading(
    strategy=MyStrategy(...),
    check_interval=300,  # 5分钟检查一次（而不是每秒）
    ...
)
```

---

## 📚 相关文档

- [快速开始](QUICKSTART.md) - 5分钟上手
- [使用指南](USAGE.md) - 策略开发
- [API 文档](../../README_zh.md) - 完整API参考
- [示例代码](../../examples/live_trading_example.py) - 更多示例

---

## ⚠️ 风险提示

1. **实盘交易有风险，请谨慎操作**
2. 建议先用小资金测试
3. 确保充分回测策略
4. 设置合理的止损止盈
5. 不要投入超过你能承受损失的资金

---

## 🎉 开始你的第一笔交易！

```python
from quant1024 import QuantStrategy, start_trading

class MyFirstStrategy(QuantStrategy):
    def generate_signals(self, data):
        # 你的策略逻辑
        return [1] if len(data) > 0 else [0]
    
    def calculate_position(self, signal, current_position):
        return 0.3 if signal == 1 else 0.0

# 就是这么简单！
start_trading(
    strategy=MyFirstStrategy(name="我的第一个策略"),
    api_key="your_api_key",
    api_secret="your_api_secret",
    market="BTC-PERP",
    initial_capital=5000,
    max_position_size=0.3,
    stop_loss=0.03,
    take_profit=0.06
)
```

**祝交易顺利！** 🚀


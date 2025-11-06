# quant1024

一个量化交易工具包，提供抽象的策略框架和常用的量化分析函数。

**文档**: [中文](guide/zh-hans/) | [English](guide/en/) | [English README](README.md)

## 特性

- 🎯 **抽象策略基类**：提供 `QuantStrategy` 抽象基类，方便快速开发自定义策略
- 📊 **量化工具函数**：内置收益率计算、夏普比率等常用指标
- 🧪 **完整测试**：全面的测试覆盖，确保外部调用稳定可靠
- 🚀 **易于扩展**：清晰的接口设计，便于继承和定制

## 安装

### 方式 1: 从 PyPI 安装（包发布后）

```bash
pip install quant1024
```

### 方式 2: 从 Git 仓库安装

```bash
pip install git+https://github.com/yourusername/quant1024.git
```

### 方式 3: 从本地源码安装

```bash
# 克隆或下载本仓库后
cd quant1024

# 开发模式安装（推荐开发时使用）
pip install -e .

# 或正常安装
pip install .
```

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

## 快速开始

### 1. 创建自定义策略

```python
from quant1024 import QuantStrategy

class MyStrategy(QuantStrategy):
    """自定义交易策略"""
    
    def generate_signals(self, data):
        """生成交易信号"""
        signals = []
        for i, price in enumerate(data):
            if i == 0:
                signals.append(0)
            elif price > data[i-1]:
                signals.append(1)   # 买入
            else:
                signals.append(-1)  # 卖出
        return signals
    
    def calculate_position(self, signal, current_position):
        """计算仓位"""
        if signal == 1:
            return 1.0  # 满仓
        elif signal == -1:
            return 0.0  # 空仓
        else:
            return current_position
```

### 2. 运行回测

```python
# 创建策略实例
strategy = MyStrategy(
    name="MyFirstStrategy",
    params={"param1": "value1"}
)

# 准备价格数据
prices = [100, 102, 101, 105, 103, 108, 110]

# 运行回测
result = strategy.backtest(prices)

print(result)
# 输出:
# {
#     'strategy_name': 'MyFirstStrategy',
#     'total_signals': 7,
#     'buy_signals': 4,
#     'sell_signals': 2,
#     'sharpe_ratio': 0.1234
# }
```

### 3. 使用工具函数

```python
from quant1024 import calculate_returns, calculate_sharpe_ratio

# 计算收益率
prices = [100, 110, 105, 115]
returns = calculate_returns(prices)
print(returns)  # [0.1, -0.0454..., 0.0952...]

# 计算夏普比率
sharpe = calculate_sharpe_ratio(returns)
print(sharpe)  # 1.2345
```

## API 文档

### `QuantStrategy` 抽象基类

所有策略必须继承此基类并实现以下方法：

#### 方法

- `__init__(name: str, params: Optional[Dict[str, Any]] = None)`
  - 初始化策略
  - `name`: 策略名称
  - `params`: 策略参数字典（可选）

- `initialize() -> None`
  - 初始化策略（在回测前会自动调用）

- `generate_signals(data: List[float]) -> List[int]` **[抽象方法]**
  - 生成交易信号
  - `data`: 价格数据列表
  - 返回：信号列表（1=买入，-1=卖出，0=持有）

- `calculate_position(signal: int, current_position: float) -> float` **[抽象方法]**
  - 根据信号计算仓位
  - `signal`: 交易信号
  - `current_position`: 当前仓位
  - 返回：新的仓位大小

- `backtest(data: List[float]) -> Dict[str, Any]`
  - 运行回测
  - `data`: 历史价格数据
  - 返回：回测结果字典

### 工具函数

- `calculate_returns(prices: List[float]) -> List[float]`
  - 计算收益率序列
  - `prices`: 价格序列
  - 返回：收益率序列

- `calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.0) -> float`
  - 计算夏普比率
  - `returns`: 收益率序列
  - `risk_free_rate`: 无风险利率（默认为0）
  - 返回：夏普比率值

## 详细文档

更多详细指南和教程，请访问：

- 📖 [快速开始指南](guide/zh-hans/QUICKSTART.md) - 5分钟快速上手
- 📦 [安装指南](guide/zh-hans/INSTALLATION.md) - 详细安装说明
- 💡 [使用指南](guide/zh-hans/USAGE.md) - 完整的使用示例
- 🚀 [发布指南](guide/zh-hans/PUBLISHING.md) - 如何发布到 PyPI

English users please visit [English Guide](guide/en/)

## 示例代码

查看 `examples/usage_example.py` 获取更多详细示例，包括：

- 均值回归策略
- 动量策略
- 工具函数使用
- 策略方法直接调用

运行示例：

```bash
cd examples
python usage_example.py
```

## 开发

### 安装开发依赖

```bash
uv pip install -e ".[dev]"
```

### 运行测试

```bash
pytest tests/ -v
```

### 测试覆盖率

```bash
pytest tests/ --cov=quant1024 --cov-report=html
```

## 项目结构

```
quant1024/
├── src/quant1024/          # 源代码
│   ├── __init__.py         # 包初始化
│   └── core.py             # 核心功能
├── tests/                  # 测试代码
│   ├── __init__.py
│   └── test_core.py        # 核心功能测试
├── examples/               # 示例代码
│   └── usage_example.py    # 使用示例
├── guide/                  # 文档指南
│   ├── en/                 # 英文指南
│   └── zh-hans/            # 中文指南
├── pyproject.toml          # 项目配置
├── README.md               # 项目文档（英文）
├── README_zh.md            # 项目文档（中文）
└── LICENSE                 # 许可证
```

## 测试说明

本项目包含全面的测试用例，确保外部软件可以正常调用：

- ✅ **导入测试**：验证所有公共API可以被正确导入
- ✅ **继承测试**：验证外部代码可以继承抽象基类
- ✅ **功能测试**：验证所有方法正常工作
- ✅ **集成测试**：验证典型使用场景
- ✅ **边界测试**：验证异常情况处理

运行测试以确保一切正常：

```bash
pytest tests/ -v
```

## 许可证

请查看 LICENSE 文件了解许可证信息。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请提交 Issue。


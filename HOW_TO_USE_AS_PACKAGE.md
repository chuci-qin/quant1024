# 如何将 quant1024 作为 pip 包使用

本文档说明如何将 `quant1024` 打包、发布和在其他项目中使用。

## 📦 当前状态

✅ **已完成**：
- [x] 项目结构符合 Python 包标准
- [x] `pyproject.toml` 配置完善
- [x] 可以成功构建分发包
- [x] 包检查通过（twine check）
- [x] 本地安装测试通过
- [x] 外部项目集成测试通过

✅ **构建的包**：
- `dist/quant1024-0.1.0-py3-none-any.whl` (wheel 包)
- `dist/quant1024-0.1.0.tar.gz` (源码包)

---

## 🚀 三种使用方式

### 方式 1️⃣：从本地路径安装（推荐用于开发）

```bash
# 直接安装
pip install /Users/chuciqin/Desktop/project1024/quant1024

# 或可编辑模式（代码修改立即生效）
pip install -e /Users/chuciqin/Desktop/project1024/quant1024

# 或从 wheel 包安装
pip install /Users/chuciqin/Desktop/project1024/quant1024/dist/quant1024-0.1.0-py3-none-any.whl
```

**在 requirements.txt 中使用**：
```txt
/Users/chuciqin/Desktop/project1024/quant1024
```

**在 pyproject.toml 中使用**：
```toml
dependencies = [
    "quant1024 @ file:///Users/chuciqin/Desktop/project1024/quant1024",
]
```

---

### 方式 2️⃣：从 Git 仓库安装（推荐用于协作）

**前提**：先将代码推送到 Git 仓库（GitHub/GitLab）

```bash
# 从 GitHub 安装
pip install git+https://github.com/yourusername/quant1024.git

# 指定分支
pip install git+https://github.com/yourusername/quant1024.git@main

# 指定标签
pip install git+https://github.com/yourusername/quant1024.git@v0.1.0
```

**在 requirements.txt 中使用**：
```txt
git+https://github.com/yourusername/quant1024.git
```

**在 pyproject.toml 中使用**：
```toml
dependencies = [
    "quant1024 @ git+https://github.com/yourusername/quant1024.git",
]
```

---

### 方式 3️⃣：从 PyPI 安装（推荐用于生产）

**前提**：先发布到 PyPI（参考 PUBLISHING.md）

```bash
# 从 PyPI 安装
pip install quant1024

# 指定版本
pip install quant1024==0.1.0

# 最低版本要求
pip install quant1024>=0.1.0
```

**在 requirements.txt 中使用**：
```txt
quant1024>=0.1.0
```

**在 pyproject.toml 中使用**：
```toml
dependencies = [
    "quant1024>=0.1.0",
]
```

---

## 💻 在其他项目中使用示例

### 示例 1：简单使用

```python
# my_app.py
from quant1024 import QuantStrategy, calculate_returns

class MyStrategy(QuantStrategy):
    def generate_signals(self, data):
        return [1 if data[i] > data[i-1] else -1 
                for i in range(1, len(data))]
    
    def calculate_position(self, signal, current_position):
        return 1.0 if signal == 1 else 0.0

# 使用策略
strategy = MyStrategy(name="SimpleStrategy")
result = strategy.backtest([100, 102, 101, 105])
print(result)
```

### 示例 2：完整项目

查看 `/Users/chuciqin/Desktop/project1024/example_usage_project/` 获取完整的集成示例，包括：
- `requirements.txt` - 依赖配置
- `pyproject.toml` - 现代项目配置
- `my_strategy.py` - RSI 策略实现

---

## 🔄 发布流程（发布到 PyPI）

### 快速发布

```bash
# 1. 进入项目目录
cd /Users/chuciqin/Desktop/project1024/quant1024

# 2. 更新版本号（在 pyproject.toml 和 src/quant1024/__init__.py）

# 3. 运行测试
pytest tests/ -v

# 4. 构建包
rm -rf dist/ build/
python -m build

# 5. 检查包
twine check dist/*

# 6. 发布到 TestPyPI（测试）
twine upload --repository testpypi dist/*

# 7. 测试安装
pip install --index-url https://test.pypi.org/simple/ quant1024

# 8. 发布到正式 PyPI
twine upload dist/*
```

详细步骤参考：`PUBLISHING.md`

---

## ✅ 验证安装

无论使用哪种方式安装，都可以这样验证：

```python
import quant1024
from quant1024 import QuantStrategy, calculate_returns, calculate_sharpe_ratio

# 检查版本
print(quant1024.__version__)  # 应输出: 0.1.0

# 测试创建策略
class TestStrategy(QuantStrategy):
    def generate_signals(self, data):
        return [1] * len(data)
    def calculate_position(self, signal, current_position):
        return 1.0

strategy = TestStrategy(name="Test")
result = strategy.backtest([100, 101, 102])
print(result)  # 应成功输出回测结果
```

---

## 📊 项目示例对比

| 使用场景 | 推荐方式 | 配置示例 |
|---------|---------|---------|
| 本地开发调试 | 本地路径 `-e` | `pip install -e /path/to/quant1024` |
| 团队协作开发 | Git 仓库 | `pip install git+https://...` |
| 生产环境 | PyPI | `pip install quant1024==0.1.0` |
| CI/CD | PyPI 或 Git | `quant1024>=0.1.0` |

---

## 🎯 关键文件说明

### 项目结构
```
quant1024/
├── src/quant1024/          # 源代码（必需）
│   ├── __init__.py        # 包入口，定义 __version__ 和导出
│   └── core.py            # 核心功能
├── tests/                 # 测试（可选，但推荐）
├── pyproject.toml         # 项目配置（必需）
├── README.md              # 说明文档（必需）
├── LICENSE                # 许可证（必需）
└── dist/                  # 构建产物（自动生成）
    ├── *.whl             # wheel 包
    └── *.tar.gz          # 源码包
```

### pyproject.toml 关键配置

```toml
[project]
name = "quant1024"              # 包名（pip install 时使用）
version = "0.1.0"               # 版本号
dependencies = []               # 运行时依赖

[build-system]
requires = ["hatchling"]        # 构建工具
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/quant1024"]    # 打包的目录
```

---

## 🔍 故障排除

### 问题 1：安装后导入失败

```bash
# 检查包是否安装
pip list | grep quant1024

# 卸载重装
pip uninstall quant1024
pip install quant1024
```

### 问题 2：版本不匹配

```bash
# 查看已安装版本
pip show quant1024

# 强制重新安装
pip install --force-reinstall quant1024
```

### 问题 3：开发模式修改不生效

```bash
# 确保使用 -e 标志
pip install -e /path/to/quant1024

# 重启 Python 解释器
```

---

## 📚 相关文档

- `README.md` - 项目说明和使用文档
- `PUBLISHING.md` - 详细发布指南
- `QUICKSTART.md` - 快速开始指南
- `examples/usage_example.py` - 使用示例
- `/Users/chuciqin/Desktop/project1024/example_usage_project/` - 完整集成示例

---

## 🎉 总结

`quant1024` 已经是一个**完整的、可发布的 Python 包**！

✅ **可以立即使用**：
- ✓ 从本地路径安装
- ✓ 从 Git 仓库安装
- ✓ 构建的 wheel 包可以分发

🚀 **准备发布**：
- 更新 `pyproject.toml` 中的 GitHub 地址
- 推送代码到 GitHub
- 按照 `PUBLISHING.md` 发布到 PyPI

💡 **最佳实践**：
1. 开发阶段：使用 `pip install -e .`
2. 团队协作：推送到 Git，使用 Git URL 安装
3. 生产环境：发布到 PyPI，使用版本号固定依赖


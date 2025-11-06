# 📦 安装使用指南

## 🚀 三种安装方式

### 方式 1️⃣：从 PyPI 安装（推荐）

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
[project]
dependencies = [
    "quant1024>=0.1.0",
]
```

---

### 方式 2️⃣：从 GitHub 安装

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
[project]
dependencies = [
    "quant1024 @ git+https://github.com/yourusername/quant1024.git",
]
```

---

### 方式 3️⃣：从本地源码安装

```bash
# 克隆或下载本仓库后
cd quant1024

# 开发模式安装（推荐开发时使用）
pip install -e .

# 或正常安装
pip install .
```

---

## ✅ 验证安装

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

## 💻 在项目中使用

### 使用 pip + requirements.txt

```txt
# requirements.txt

# 从 PyPI（推荐）
quant1024>=0.1.0

# 或从 GitHub
git+https://github.com/yourusername/quant1024.git

# 或从本地
/path/to/quant1024
```

安装：
```bash
pip install -r requirements.txt
```

---

### 使用 uv + pyproject.toml

```toml
# pyproject.toml
[project]
name = "my-app"
version = "1.0.0"
dependencies = [
    "quant1024>=0.1.0",
]
```

安装：
```bash
uv pip install -e .
```

---

### 使用 Poetry

```toml
# pyproject.toml
[tool.poetry.dependencies]
python = "^3.8"
quant1024 = "^0.1.0"

# 或从 Git
# quant1024 = { git = "https://github.com/yourusername/quant1024.git" }

# 或从本地
# quant1024 = { path = "/path/to/quant1024", develop = true }
```

安装：
```bash
poetry install
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

- [快速开始](QUICKSTART.md) - 5分钟上手教程
- [发布指南](PUBLISHING.md) - 如何发布到 PyPI
- [使用指南](USAGE.md) - 详细的使用说明
- [API 文档](../../README.md) - 完整的 API 参考

---

## ❓ 常见问题

### Q: 如何确认安装成功？

```bash
# 检查包是否安装
pip list | grep quant1024

# 查看包信息
pip show quant1024

# 测试导入
python -c "import quant1024; print(quant1024.__version__)"
```

### Q: 如何更新到最新版本？

```bash
# 更新到最新版本
pip install --upgrade quant1024
```

### Q: 如何卸载？

```bash
pip uninstall quant1024
```


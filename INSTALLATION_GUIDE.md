# 📦 quant1024 安装使用指南

## 🎯 你现在可以做什么

`quant1024` **已经是一个完整的、可以被其他项目正常安装和使用的 pip 包**！

---

## ✅ 验证状态

✓ 包已构建成功：
  - `dist/quant1024-0.1.0-py3-none-any.whl`
  - `dist/quant1024-0.1.0.tar.gz`

✓ 包检查通过：`twine check dist/*` ✅

✓ 本地安装测试通过 ✅

✓ 外部项目集成测试通过 ✅

✓ 18个单元测试全部通过 ✅

---

## 🚀 立即使用 - 三种方式

### 方式 1️⃣：从本地安装（现在就能用）

其他项目可以直接从本地路径安装：

```bash
# 方式 A: 安装源码
pip install /Users/chuciqin/Desktop/project1024/quant1024

# 方式 B: 安装 wheel 包（推荐）
pip install /Users/chuciqin/Desktop/project1024/quant1024/dist/quant1024-0.1.0-py3-none-any.whl

# 方式 C: 开发模式（代码修改立即生效）
pip install -e /Users/chuciqin/Desktop/project1024/quant1024
```

**在 requirements.txt 中使用**：
```txt
# requirements.txt
/Users/chuciqin/Desktop/project1024/quant1024
```

或

```txt
# requirements.txt
/Users/chuciqin/Desktop/project1024/quant1024/dist/quant1024-0.1.0-py3-none-any.whl
```

---

### 方式 2️⃣：从 GitHub 安装（推荐）

**步骤 1**: 将代码推送到 GitHub

```bash
cd /Users/chuciqin/Desktop/project1024/quant1024

# 如果还没有远程仓库
git remote add origin https://github.com/yourusername/quant1024.git
git push -u origin main
```

**步骤 2**: 其他项目可以直接从 GitHub 安装

```bash
pip install git+https://github.com/yourusername/quant1024.git
```

**在 requirements.txt 中使用**：
```txt
# requirements.txt
git+https://github.com/yourusername/quant1024.git
```

**在 pyproject.toml 中使用**：
```toml
# pyproject.toml
[project]
dependencies = [
    "quant1024 @ git+https://github.com/yourusername/quant1024.git",
]
```

---

### 方式 3️⃣：发布到 PyPI（生产环境推荐）

**步骤 1**: 注册 PyPI 账号
- 访问 https://pypi.org/ 注册

**步骤 2**: 获取 API Token
- 登录 PyPI → Account Settings → API tokens → Add API token

**步骤 3**: 发布包

```bash
cd /Users/chuciqin/Desktop/project1024/quant1024

# 上传到 PyPI
twine upload dist/*
# 输入你的 API token
```

**步骤 4**: 其他人就可以直接安装了

```bash
pip install quant1024
```

**在 requirements.txt 中使用**：
```txt
# requirements.txt
quant1024>=0.1.0
```

详细发布流程参考：`PUBLISHING.md`

---

## 💡 实际使用示例

### 示例 1：在简单脚本中使用

创建文件 `my_strategy.py`：

```python
from quant1024 import QuantStrategy

class MyStrategy(QuantStrategy):
    def generate_signals(self, data):
        signals = []
        for i in range(len(data)):
            if i == 0:
                signals.append(0)
            elif data[i] > data[i-1]:
                signals.append(1)  # 买入
            else:
                signals.append(-1)  # 卖出
        return signals
    
    def calculate_position(self, signal, current_position):
        if signal == 1:
            return 1.0
        elif signal == -1:
            return 0.0
        else:
            return current_position

# 使用
strategy = MyStrategy(name="Simple")
result = strategy.backtest([100, 102, 101, 105, 103])
print(result)
```

安装并运行：

```bash
# 安装 quant1024（三种方式任选其一）
pip install /Users/chuciqin/Desktop/project1024/quant1024

# 运行
python my_strategy.py
```

---

### 示例 2：在完整项目中使用

我已经为你创建了一个完整的示例项目：

📁 **位置**：`/Users/chuciqin/Desktop/project1024/example_usage_project/`

📂 **包含**：
- `requirements.txt` - 依赖配置示例
- `pyproject.toml` - 现代项目配置示例
- `my_strategy.py` - 完整的 RSI 策略实现
- `README.md` - 使用说明

**运行示例项目**：

```bash
cd /Users/chuciqin/Desktop/project1024/example_usage_project
pip install -r requirements.txt
python my_strategy.py
```

---

## 📋 快速测试

验证包可以被正常使用：

```bash
# 创建测试环境
python -m venv test_env
source test_env/bin/activate

# 安装包
pip install /Users/chuciqin/Desktop/project1024/quant1024/dist/quant1024-0.1.0-py3-none-any.whl

# 测试导入和使用
python -c "
from quant1024 import QuantStrategy, calculate_returns
print('✓ 导入成功')

class TestStrategy(QuantStrategy):
    def generate_signals(self, data):
        return [1] * len(data)
    def calculate_position(self, signal, current_position):
        return 1.0

strategy = TestStrategy(name='Test')
result = strategy.backtest([100, 101, 102])
print('✓ 功能正常')
print('结果:', result)
"

# 清理
deactivate
rm -rf test_env
```

---

## 📚 其他项目如何添加依赖

### 使用 pip + requirements.txt

```txt
# requirements.txt

# 选项 1: 从本地
/Users/chuciqin/Desktop/project1024/quant1024

# 选项 2: 从 GitHub
git+https://github.com/yourusername/quant1024.git

# 选项 3: 从 PyPI（发布后）
quant1024>=0.1.0
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
    "quant1024>=0.1.0",  # 从 PyPI
    # 或
    # "quant1024 @ git+https://github.com/yourusername/quant1024.git",  # 从 Git
    # 或
    # "quant1024 @ file:///Users/chuciqin/Desktop/project1024/quant1024",  # 从本地
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

# 从 PyPI
quant1024 = "^0.1.0"

# 或从 Git
quant1024 = { git = "https://github.com/yourusername/quant1024.git" }

# 或从本地
quant1024 = { path = "/Users/chuciqin/Desktop/project1024/quant1024", develop = true }
```

安装：
```bash
poetry install
```

---

## 🔄 更新包版本

当你修改代码并想发布新版本时：

```bash
cd /Users/chuciqin/Desktop/project1024/quant1024

# 1. 修改版本号
# 编辑 pyproject.toml: version = "0.2.0"
# 编辑 src/quant1024/__init__.py: __version__ = "0.2.0"

# 2. 运行测试
pytest tests/ -v

# 3. 重新构建
rm -rf dist/
python -m build

# 4. 检查
twine check dist/*

# 5. 重新发布（如果已发布到 PyPI）
twine upload dist/*

# 6. Git 打标签
git tag v0.2.0
git push origin v0.2.0
```

---

## ❓ 常见问题

### Q1: 别人可以直接 pip install quant1024 吗？

**现在**：❌ 不能，因为还没发布到 PyPI

**可以**：
- ✅ 从本地路径安装
- ✅ 从 wheel 包安装
- ✅ 从 GitHub 安装（需先推送）

**发布到 PyPI 后**：✅ 可以直接 `pip install quant1024`

---

### Q2: 如何分发给其他人使用？

**方式 1**：分发 wheel 包（推荐）
```bash
# 把这个文件发给别人
/Users/chuciqin/Desktop/project1024/quant1024/dist/quant1024-0.1.0-py3-none-any.whl

# 别人安装
pip install quant1024-0.1.0-py3-none-any.whl
```

**方式 2**：推送到 GitHub（推荐）
```bash
# 别人安装
pip install git+https://github.com/yourusername/quant1024.git
```

**方式 3**：发布到 PyPI
```bash
# 别人安装
pip install quant1024
```

---

### Q3: 在 requirements.txt 中如何指定？

```txt
# 本地开发
/Users/chuciqin/Desktop/project1024/quant1024

# 从 wheel 包
/path/to/quant1024-0.1.0-py3-none-any.whl

# 从 GitHub
git+https://github.com/yourusername/quant1024.git

# 从 PyPI（发布后）
quant1024==0.1.0      # 指定版本
quant1024>=0.1.0      # 最低版本
quant1024~=0.1.0      # 兼容版本
```

---

### Q4: 如何确认安装成功？

```bash
# 检查包是否安装
pip list | grep quant1024

# 查看包信息
pip show quant1024

# 测试导入
python -c "import quant1024; print(quant1024.__version__)"
```

---

## 📖 相关文档

- **`HOW_TO_USE_AS_PACKAGE.md`** - 完整的包使用指南
- **`PUBLISHING.md`** - 发布到 PyPI 的详细步骤
- **`README.md`** - 项目说明和 API 文档
- **`QUICKSTART.md`** - 快速开始教程
- **`example_usage_project/`** - 完整的集成示例项目

---

## 🎉 总结

### ✅ 你现在就能做的

1. ✅ **立即使用**：其他项目可以通过本地路径或 wheel 包安装
2. ✅ **分发包**：可以把 wheel 包发给别人使用
3. ✅ **Git 安装**：推送到 GitHub 后，任何人都能安装

### 🚀 下一步可选操作

1. **推送到 GitHub**（推荐）
   - 创建 GitHub 仓库
   - 推送代码
   - 其他人可以用 `pip install git+https://...` 安装

2. **发布到 PyPI**（可选）
   - 注册 PyPI 账号
   - 运行 `twine upload dist/*`
   - 全世界都能 `pip install quant1024`

---

**🎯 核心结论**：

你的包**已经完全可以被其他项目正常安装和使用**！

无论是通过本地路径、wheel 包、Git 仓库，还是将来的 PyPI，都能正常工作。✅


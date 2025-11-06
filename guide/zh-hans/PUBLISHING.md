# 发布指南 - 将 quant1024 打包为 pip 包

本文档说明如何将 `quant1024` 打包并发布，使其可以通过 `pip install` 安装。

## 📋 目录

1. [本地安装和测试](#本地安装和测试)
2. [构建分发包](#构建分发包)
3. [发布到 PyPI](#发布到-pypi)
4. [在其他项目中使用](#在其他项目中使用)
5. [版本管理](#版本管理)

---

## 1. 本地安装和测试

### 方式 A: 可编辑模式安装（开发模式）

```bash
cd quant1024

# 使用 uv（推荐）
uv pip install -e .

# 或使用传统 pip
pip install -e .
```

这种方式安装后，代码修改会立即生效，适合开发阶段。

### 方式 B: 正常安装

```bash
# 安装到当前 Python 环境
pip install .
```

### 验证安装

```python
# 在任意目录的 Python 中测试
python -c "import quant1024; print(quant1024.__version__)"
```

---

## 2. 构建分发包

### 2.1 安装构建工具

```bash
# 使用 uv
uv pip install build twine

# 或使用 pip
pip install build twine
```

### 2.2 构建包

```bash
# 进入项目根目录
cd quant1024

# 清理旧的构建文件
rm -rf dist/ build/ *.egg-info

# 构建源码包和wheel包
python -m build
```

构建成功后，会在 `dist/` 目录下生成两个文件：
- `quant1024-0.1.0.tar.gz` (源码包)
- `quant1024-0.1.0-py3-none-any.whl` (wheel包)

### 2.3 检查包

```bash
# 检查构建的包是否符合规范
twine check dist/*
```

应该看到：
```
Checking dist/quant1024-0.1.0.tar.gz: PASSED
Checking dist/quant1024-0.1.0-py3-none-any.whl: PASSED
```

### 2.4 本地测试安装构建的包

```bash
# 创建测试环境
python -m venv test_env
source test_env/bin/activate  # Windows: test_env\Scripts\activate

# 从构建的包安装
pip install dist/quant1024-0.1.0-py3-none-any.whl

# 测试导入
python -c "from quant1024 import QuantStrategy; print('✓ 安装成功')"

# 退出测试环境
deactivate
rm -rf test_env
```

---

## 3. 发布到 PyPI

### 3.1 注册 PyPI 账号

1. 访问 [PyPI](https://pypi.org/) 注册账号
2. 访问 [TestPyPI](https://test.pypi.org/) 注册测试账号（推荐先在这里测试）

### 3.2 配置 API Token

1. 登录 PyPI，进入 Account Settings
2. 创建 API Token
3. 配置到本地：

```bash
# 创建 .pypirc 文件
cat > ~/.pypirc << EOF
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YourAPIToken

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YourTestAPIToken
EOF

# 设置权限
chmod 600 ~/.pypirc
```

### 3.3 先发布到 TestPyPI（推荐）

```bash
# 上传到 TestPyPI
twine upload --repository testpypi dist/*

# 从 TestPyPI 安装测试
pip install --index-url https://test.pypi.org/simple/ quant1024
```

### 3.4 发布到正式 PyPI

```bash
# 确认一切正常后，上传到正式 PyPI
twine upload dist/*
```

发布成功后，你的包会出现在：https://pypi.org/project/quant1024/

---

## 4. 在其他项目中使用

### 4.1 直接安装

```bash
# 从 PyPI 安装（发布后）
pip install quant1024

# 从 GitHub 安装（推荐在正式发布前）
pip install git+https://github.com/yourusername/quant1024.git

# 从本地路径安装
pip install /path/to/quant1024

# 安装特定版本
pip install quant1024==0.1.0
```

### 4.2 在 requirements.txt 中使用

```txt
# requirements.txt
quant1024>=0.1.0

# 或指定确切版本
quant1024==0.1.0

# 或从 Git 安装
git+https://github.com/yourusername/quant1024.git@main
```

### 4.3 在 pyproject.toml 中使用

```toml
[project]
dependencies = [
    "quant1024>=0.1.0",
]
```

### 4.4 在代码中使用

```python
# 其他项目中的代码
from quant1024 import QuantStrategy, calculate_returns, calculate_sharpe_ratio

class MyCustomStrategy(QuantStrategy):
    def generate_signals(self, data):
        # 你的策略逻辑
        return [1, -1, 0]
    
    def calculate_position(self, signal, current_position):
        return 1.0 if signal == 1 else 0.0

# 使用策略
strategy = MyCustomStrategy(name="Custom")
result = strategy.backtest([100, 101, 102])
```

---

## 5. 版本管理

### 5.1 更新版本号

编辑 `pyproject.toml` 和 `src/quant1024/__init__.py`：

```python
# src/quant1024/__init__.py
__version__ = "0.2.0"
```

```toml
# pyproject.toml
[project]
version = "0.2.0"
```

### 5.2 版本号规范（语义化版本）

- `0.1.0` → `0.1.1` - 补丁版本（bug修复）
- `0.1.0` → `0.2.0` - 次版本（新功能，向后兼容）
- `0.1.0` → `1.0.0` - 主版本（重大变更，可能不兼容）

### 5.3 发布新版本

```bash
# 1. 更新版本号
# 2. 更新 CHANGELOG.md（如果有）
# 3. 提交更改
git add .
git commit -m "Bump version to 0.2.0"
git tag v0.2.0
git push origin main --tags

# 4. 重新构建和发布
rm -rf dist/
python -m build
twine upload dist/*
```

---

## 📝 完整发布流程示例

```bash
# 1. 确保代码已提交
cd quant1024
git add .
git commit -m "Prepare for release 0.1.0"
git push origin main

# 2. 清理旧构建
rm -rf dist/ build/ src/*.egg-info

# 3. 运行测试
pytest tests/ -v

# 4. 构建包
python -m build

# 5. 检查包
twine check dist/*

# 6. 上传到 TestPyPI 测试
twine upload --repository testpypi dist/*

# 7. 测试安装
pip install --index-url https://test.pypi.org/simple/ quant1024

# 8. 确认无误后上传到正式 PyPI
twine upload dist/*

# 9. 打标签
git tag v0.1.0
git push origin v0.1.0

# 10. 创建 GitHub Release（可选）
```

---

## 🔍 故障排除

### 问题 1: ModuleNotFoundError

**原因**: 包结构不正确

**解决**:
```bash
# 确保结构如下：
src/
  quant1024/
    __init__.py
    core.py
```

### 问题 2: twine upload 失败

**原因**: API token 配置错误

**解决**:
```bash
# 检查 ~/.pypirc 文件
# 确保 token 正确且有效
```

### 问题 3: 导入时找不到模块

**原因**: 包未正确安装

**解决**:
```bash
# 重新安装
pip uninstall quant1024
pip install quant1024
```

---

## ✅ 发布前检查清单

- [ ] 所有测试通过 (`pytest tests/ -v`)
- [ ] 版本号已更新
- [ ] README.md 文档完整
- [ ] pyproject.toml 元数据正确
- [ ] LICENSE 文件存在
- [ ] 代码已提交到 Git
- [ ] 在 TestPyPI 测试成功
- [ ] 构建的包检查通过 (`twine check dist/*`)

---

## 📚 相关资源

- [Python 打包用户指南](https://packaging.python.org/)
- [PyPI 官方文档](https://pypi.org/help/)
- [Hatchling 文档](https://hatch.pypa.io/latest/)
- [语义化版本](https://semver.org/)


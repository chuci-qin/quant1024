# 📦 Installation Guide

## 🚀 Three Installation Methods

### Method 1️⃣: Install from PyPI (Recommended)

```bash
# Install from PyPI
pip install quant1024

# Install specific version
pip install quant1024==0.1.0

# Install minimum version requirement
pip install quant1024>=0.1.0
```

**Use in requirements.txt**:
```txt
quant1024>=0.1.0
```

**Use in pyproject.toml**:
```toml
[project]
dependencies = [
    "quant1024>=0.1.0",
]
```

---

### Method 2️⃣: Install from GitHub

```bash
# Install from GitHub
pip install git+https://github.com/yourusername/quant1024.git

# Specify branch
pip install git+https://github.com/yourusername/quant1024.git@main

# Specify tag
pip install git+https://github.com/yourusername/quant1024.git@v0.1.0
```

**Use in requirements.txt**:
```txt
git+https://github.com/yourusername/quant1024.git
```

**Use in pyproject.toml**:
```toml
[project]
dependencies = [
    "quant1024 @ git+https://github.com/yourusername/quant1024.git",
]
```

---

### Method 3️⃣: Install from Local Source

```bash
# After cloning or downloading the repository
cd quant1024

# Development mode installation (recommended for development)
pip install -e .

# Or normal installation
pip install .
```

---

## ✅ Verify Installation

```python
import quant1024
from quant1024 import QuantStrategy, calculate_returns, calculate_sharpe_ratio

# Check version
print(quant1024.__version__)  # Should output: 0.1.0

# Test creating a strategy
class TestStrategy(QuantStrategy):
    def generate_signals(self, data):
        return [1] * len(data)
    def calculate_position(self, signal, current_position):
        return 1.0

strategy = TestStrategy(name="Test")
result = strategy.backtest([100, 101, 102])
print(result)  # Should successfully output backtest results
```

---

## 💻 Use in Projects

### Using pip + requirements.txt

```txt
# requirements.txt

# From PyPI (recommended)
quant1024>=0.1.0

# Or from GitHub
git+https://github.com/yourusername/quant1024.git

# Or from local path
/path/to/quant1024
```

Install:
```bash
pip install -r requirements.txt
```

---

### Using uv + pyproject.toml

```toml
# pyproject.toml
[project]
name = "my-app"
version = "1.0.0"
dependencies = [
    "quant1024>=0.1.0",
]
```

Install:
```bash
uv pip install -e .
```

---

### Using Poetry

```toml
# pyproject.toml
[tool.poetry.dependencies]
python = "^3.8"
quant1024 = "^0.1.0"

# Or from Git
# quant1024 = { git = "https://github.com/yourusername/quant1024.git" }

# Or from local path
# quant1024 = { path = "/path/to/quant1024", develop = true }
```

Install:
```bash
poetry install
```

---

## 🔍 Troubleshooting

### Issue 1: Import Failed After Installation

```bash
# Check if package is installed
pip list | grep quant1024

# Uninstall and reinstall
pip uninstall quant1024
pip install quant1024
```

### Issue 2: Version Mismatch

```bash
# Check installed version
pip show quant1024

# Force reinstall
pip install --force-reinstall quant1024
```

### Issue 3: Development Mode Changes Not Taking Effect

```bash
# Ensure using -e flag
pip install -e /path/to/quant1024

# Restart Python interpreter
```

---

## 📚 Related Documentation

- [Quick Start](QUICKSTART.md) - 5-minute tutorial
- [Publishing Guide](PUBLISHING.md) - How to publish to PyPI
- [Usage Guide](USAGE.md) - Detailed usage instructions
- [API Documentation](../../README.md) - Complete API reference

---

## ❓ FAQ

### Q: How to confirm installation was successful?

```bash
# Check if package is installed
pip list | grep quant1024

# View package information
pip show quant1024

# Test import
python -c "import quant1024; print(quant1024.__version__)"
```

### Q: How to update to the latest version?

```bash
# Update to latest version
pip install --upgrade quant1024
```

### Q: How to uninstall?

```bash
pip uninstall quant1024
```


# Publishing Guide - Package quant1024 as a pip Package

This document explains how to package and publish `quant1024` so it can be installed via `pip install`.

## 📋 Table of Contents

1. [Local Installation and Testing](#local-installation-and-testing)
2. [Build Distribution Package](#build-distribution-package)
3. [Publish to PyPI](#publish-to-pypi)
4. [Use in Other Projects](#use-in-other-projects)
5. [Version Management](#version-management)

---

## 1. Local Installation and Testing

### Method A: Editable Mode Installation (Development Mode)

```bash
cd quant1024

# Using uv (recommended)
uv pip install -e .

# Or using traditional pip
pip install -e .
```

This installation method makes code changes take effect immediately, suitable for development.

### Method B: Normal Installation

```bash
# Install to current Python environment
pip install .
```

### Verify Installation

```python
# Test in Python from any directory
python -c "import quant1024; print(quant1024.__version__)"
```

---

## 2. Build Distribution Package

### 2.1 Install Build Tools

```bash
# Using uv
uv pip install build twine

# Or using pip
pip install build twine
```

### 2.2 Build Package

```bash
# Enter project root directory
cd quant1024

# Clean old build files
rm -rf dist/ build/ *.egg-info

# Build source package and wheel package
python -m build
```

After successful build, two files will be generated in the `dist/` directory:
- `quant1024-0.1.0.tar.gz` (source package)
- `quant1024-0.1.0-py3-none-any.whl` (wheel package)

### 2.3 Check Package

```bash
# Check if the built package complies with specifications
twine check dist/*
```

You should see:
```
Checking dist/quant1024-0.1.0.tar.gz: PASSED
Checking dist/quant1024-0.1.0-py3-none-any.whl: PASSED
```

### 2.4 Test Install Built Package Locally

```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate  # Windows: test_env\Scripts\activate

# Install from built package
pip install dist/quant1024-0.1.0-py3-none-any.whl

# Test import
python -c "from quant1024 import QuantStrategy; print('✓ Installation successful')"

# Exit test environment
deactivate
rm -rf test_env
```

---

## 3. Publish to PyPI

### 3.1 Register PyPI Account

1. Visit [PyPI](https://pypi.org/) to register an account
2. Visit [TestPyPI](https://test.pypi.org/) to register a test account (recommended to test here first)

### 3.2 Configure API Token

1. Log in to PyPI, go to Account Settings
2. Create API Token
3. Configure locally:

```bash
# Create .pypirc file
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

# Set permissions
chmod 600 ~/.pypirc
```

### 3.3 Publish to TestPyPI First (Recommended)

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ quant1024
```

### 3.4 Publish to Official PyPI

```bash
# After confirming everything is correct, upload to official PyPI
twine upload dist/*
```

After successful publication, your package will appear at: https://pypi.org/project/quant1024/

---

## 4. Use in Other Projects

### 4.1 Direct Installation

```bash
# Install from PyPI (after publication)
pip install quant1024

# Install from GitHub (recommended before official release)
pip install git+https://github.com/yourusername/quant1024.git

# Install from local path
pip install /path/to/quant1024

# Install specific version
pip install quant1024==0.1.0
```

### 4.2 Use in requirements.txt

```txt
# requirements.txt
quant1024>=0.1.0

# Or specify exact version
quant1024==0.1.0

# Or install from Git
git+https://github.com/yourusername/quant1024.git@main
```

### 4.3 Use in pyproject.toml

```toml
[project]
dependencies = [
    "quant1024>=0.1.0",
]
```

### 4.4 Use in Code

```python
# Code in other projects
from quant1024 import QuantStrategy, calculate_returns, calculate_sharpe_ratio

class MyCustomStrategy(QuantStrategy):
    def generate_signals(self, data):
        # Your strategy logic
        return [1, -1, 0]
    
    def calculate_position(self, signal, current_position):
        return 1.0 if signal == 1 else 0.0

# Use strategy
strategy = MyCustomStrategy(name="Custom")
result = strategy.backtest([100, 101, 102])
```

---

## 5. Version Management

### 5.1 Update Version Number

Edit `pyproject.toml` and `src/quant1024/__init__.py`:

```python
# src/quant1024/__init__.py
__version__ = "0.2.0"
```

```toml
# pyproject.toml
[project]
version = "0.2.0"
```

### 5.2 Version Number Convention (Semantic Versioning)

- `0.1.0` → `0.1.1` - Patch version (bug fixes)
- `0.1.0` → `0.2.0` - Minor version (new features, backward compatible)
- `0.1.0` → `1.0.0` - Major version (breaking changes, may not be compatible)

### 5.3 Release New Version

```bash
# 1. Update version number
# 2. Update CHANGELOG.md (if applicable)
# 3. Commit changes
git add .
git commit -m "Bump version to 0.2.0"
git tag v0.2.0
git push origin main --tags

# 4. Rebuild and publish
rm -rf dist/
python -m build
twine upload dist/*
```

---

## 📝 Complete Release Process Example

```bash
# 1. Ensure code is committed
cd quant1024
git add .
git commit -m "Prepare for release 0.1.0"
git push origin main

# 2. Clean old builds
rm -rf dist/ build/ src/*.egg-info

# 3. Run tests
pytest tests/ -v

# 4. Build package
python -m build

# 5. Check package
twine check dist/*

# 6. Upload to TestPyPI for testing
twine upload --repository testpypi dist/*

# 7. Test installation
pip install --index-url https://test.pypi.org/simple/ quant1024

# 8. Upload to official PyPI after confirmation
twine upload dist/*

# 9. Tag
git tag v0.1.0
git push origin v0.1.0

# 10. Create GitHub Release (optional)
```

---

## 🔍 Troubleshooting

### Issue 1: ModuleNotFoundError

**Cause**: Incorrect package structure

**Solution**:
```bash
# Ensure structure is as follows:
src/
  quant1024/
    __init__.py
    core.py
```

### Issue 2: twine upload Failed

**Cause**: API token configuration error

**Solution**:
```bash
# Check ~/.pypirc file
# Ensure token is correct and valid
```

### Issue 3: Module Not Found on Import

**Cause**: Package not installed correctly

**Solution**:
```bash
# Reinstall
pip uninstall quant1024
pip install quant1024
```

---

## ✅ Pre-Release Checklist

- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Version number updated
- [ ] README.md documentation complete
- [ ] pyproject.toml metadata correct
- [ ] LICENSE file exists
- [ ] Code committed to Git
- [ ] TestPyPI test successful
- [ ] Built package check passed (`twine check dist/*`)

---

## 📚 Related Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI Official Documentation](https://pypi.org/help/)
- [Hatchling Documentation](https://hatch.pypa.io/latest/)
- [Semantic Versioning](https://semver.org/)


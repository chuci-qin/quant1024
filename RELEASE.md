# 📦 quant1024 发布指南

## 🚀 自动化发布流程

本项目使用 **GitHub Actions + PyPI Trusted Publishing** 实现自动化发布。

---

## 📋 发布步骤

### 方式 1: 通过 GitHub Release 发布（推荐）

1. **确保版本号已更新**
   ```bash
   # 检查 pyproject.toml 中的版本号
   grep version pyproject.toml
   ```

2. **提交并推送所有更改**
   ```bash
   git add .
   git commit -m "chore: prepare for v0.2.0 release"
   git push origin main
   ```

3. **创建 Git Tag**
   ```bash
   git tag -a v0.2.0 -m "Release version 0.2.0"
   git push origin v0.2.0
   ```

4. **在 GitHub 创建 Release**
   - 访问: https://github.com/chuci-qin/quant1024/releases/new
   - 选择刚才创建的 tag: `v0.2.0`
   - 填写 Release 标题: `v0.2.0 - Add 1024ex Exchange Support`
   - 填写 Release 说明（可以从 CHANGELOG 复制）
   - 点击 "Publish release"

5. **GitHub Actions 自动执行**
   - ✅ 运行所有测试
   - ✅ 构建包
   - ✅ 发布到 PyPI

6. **验证发布**
   - 访问: https://pypi.org/project/quant1024/
   - 测试安装: `pip install quant1024==0.2.0`

---

### 方式 2: 通过 Git Tag 触发（快速方式）

如果只想快速发布，不需要写 Release Notes：

```bash
# 1. 更新版本号并提交
git add pyproject.toml
git commit -m "chore: bump version to 0.2.0"
git push

# 2. 创建并推送 tag
git tag v0.2.0
git push origin v0.2.0
```

GitHub Actions 会自动触发发布。

---

### 方式 3: 测试发布到 TestPyPI

如果想先测试：

```bash
# 使用特殊的 tag 格式
git tag test-v0.2.0
git push origin test-v0.2.0
```

这会发布到 TestPyPI 而不是正式 PyPI。

---

## 🔧 工作流程详解

### 自动化流程

```
推送 tag/创建 release
    ↓
GitHub Actions 触发
    ↓
运行测试 (101个测试)
    ↓
构建包 (.whl + .tar.gz)
    ↓
使用 Trusted Publishing 发布
    ↓
自动上传到 PyPI
    ↓
✅ 发布完成
```

### 安全性

- ✅ **无需 API Token** - 使用 OpenID Connect (OIDC)
- ✅ **临时凭证** - 每次发布生成新的临时凭证
- ✅ **权限最小化** - 只有 GitHub Actions 可以发布
- ✅ **审计日志** - 所有发布都有 GitHub Actions 日志

---

## 📝 版本号规范

遵循 [语义化版本](https://semver.org/lang/zh-CN/)：

- `v0.2.0` - 次版本号（新功能）
- `v0.2.1` - 修订号（bug 修复）
- `v1.0.0` - 主版本号（不兼容的 API 更改）

---

## ⚠️ 注意事项

1. **版本号不能重复**
   - PyPI 不允许覆盖已发布的版本
   - 如需修改，必须发布新版本（如 0.2.1）

2. **Tag 格式**
   - 正式发布: `v0.2.0`
   - 测试发布: `test-v0.2.0`

3. **环境配置**
   - 需要在 PyPI 配置 Trusted Publisher
   - 需要在 GitHub 仓库配置 Actions 权限

4. **首次发布**
   - 首次发布可能需要先手动上传一个版本
   - 然后再配置 Trusted Publisher

---

## 🔍 排查问题

### Actions 失败

检查 GitHub Actions 日志：
https://github.com/chuci-qin/quant1024/actions

常见问题：
- 测试失败 → 修复代码后重新提交
- 构建失败 → 检查 pyproject.toml 配置
- 发布失败 → 检查 PyPI Trusted Publisher 配置

### 手动发布（备用方案）

如果自动化失败，可以手动发布：

```bash
# 1. 运行测试
pytest tests/ -v

# 2. 构建包
python -m build

# 3. 手动上传
twine upload dist/*
```

---

## 📚 相关文档

- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions](https://docs.github.com/actions)
- [语义化版本](https://semver.org/)

---

**最后更新**: 2025-11-08


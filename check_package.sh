#!/bin/bash
#
# 检查构建的包内容
# Check the contents of the built package
#

set -e

echo "🔍 检查 quant1024 包内容 / Checking quant1024 package contents"
echo "================================================================"
echo ""

# 检查 dist 目录
if [ ! -d "dist" ]; then
    echo "❌ dist/ 目录不存在。请先运行: python -m build"
    echo "❌ dist/ directory not found. Please run: python -m build"
    exit 1
fi

# 查找最新的 wheel 和 tar.gz 文件
WHEEL_FILE=$(ls -t dist/*.whl 2>/dev/null | head -1)
TAR_FILE=$(ls -t dist/*.tar.gz 2>/dev/null | head -1)

if [ -z "$WHEEL_FILE" ]; then
    echo "❌ 未找到 wheel 文件"
    echo "❌ No wheel file found"
    exit 1
fi

echo "📦 检查文件:"
echo "   Wheel: $WHEEL_FILE"
echo "   Source: $TAR_FILE"
echo ""

echo "─────────────────────────────────────────────────────────────"
echo "✅ 应该包含 / Should Include:"
echo "─────────────────────────────────────────────────────────────"
echo ""

# 检查应该包含的文件
SHOULD_INCLUDE=(
    "README.md"
    "README_zh.md"
    "LICENSE"
    "quant1024/__init__.py"
    "quant1024/core.py"
    "examples/usage_example.py"
    "guide/README.md"
    "guide/en/QUICKSTART.md"
    "guide/zh-hans/QUICKSTART.md"
)

echo "检查 wheel 包..."
for file in "${SHOULD_INCLUDE[@]}"; do
    if unzip -l "$WHEEL_FILE" 2>/dev/null | grep -q "$file"; then
        echo "  ✅ $file"
    else
        echo "  ❌ 缺失: $file"
    fi
done

echo ""
echo "─────────────────────────────────────────────────────────────"
echo "❌ 不应该包含 / Should NOT Include:"
echo "─────────────────────────────────────────────────────────────"
echo ""

# 检查不应该包含的文件
SHOULD_NOT_INCLUDE=(
    "release_documents/"
    "SECURITY_GUIDE.md"
    "PUBLISHING_STEPS.md"
    "COLLABORATOR_GUIDE.md"
    "publish.sh"
    "check_package.sh"
    "setup.py"
    ".packageignore"
    "tests/"
    "test_"
)

echo "检查 wheel 包..."
for file in "${SHOULD_NOT_INCLUDE[@]}"; do
    if unzip -l "$WHEEL_FILE" 2>/dev/null | grep -q "$file"; then
        echo "  ⚠️  包含了不应该有的文件: $file"
    else
        echo "  ✅ 正确排除: $file"
    fi
done

echo ""
echo "─────────────────────────────────────────────────────────────"
echo "📋 完整文件列表 / Full File List:"
echo "─────────────────────────────────────────────────────────────"
echo ""
unzip -l "$WHEEL_FILE"

echo ""
echo "─────────────────────────────────────────────────────────────"
echo "📊 包大小统计 / Package Size:"
echo "─────────────────────────────────────────────────────────────"
echo ""
ls -lh "$WHEEL_FILE"
if [ -n "$TAR_FILE" ]; then
    ls -lh "$TAR_FILE"
fi

echo ""
echo "✅ 检查完成！"
echo "✅ Check completed!"


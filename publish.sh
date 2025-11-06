#!/bin/bash
# 
# quant1024 发布脚本 / Publishing Script for quant1024
# 
# 使用方法 / Usage:
#   ./publish.sh test     # 发布到 TestPyPI
#   ./publish.sh prod     # 发布到正式 PyPI
#

set -e  # 遇到错误立即退出

echo "🚀 quant1024 Publishing Script"
echo "=============================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查参数
if [ "$1" != "test" ] && [ "$1" != "prod" ]; then
    echo -e "${RED}错误: 请指定发布目标 'test' 或 'prod'${NC}"
    echo "用法: $0 [test|prod]"
    exit 1
fi

TARGET=$1

echo -e "${YELLOW}步骤 1/6: 运行测试...${NC}"
pytest tests/ -v
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 测试失败！请修复测试后再发布。${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 测试通过${NC}"
echo ""

echo -e "${YELLOW}步骤 2/6: 清理旧构建文件...${NC}"
rm -rf dist/ build/ *.egg-info src/*.egg-info
echo -e "${GREEN}✅ 清理完成${NC}"
echo ""

echo -e "${YELLOW}步骤 3/6: 安装构建工具...${NC}"
pip install --upgrade build twine
echo -e "${GREEN}✅ 工具就绪${NC}"
echo ""

echo -e "${YELLOW}步骤 4/6: 构建包...${NC}"
python -m build
echo -e "${GREEN}✅ 构建完成${NC}"
echo ""

echo -e "${YELLOW}步骤 5/6: 检查包...${NC}"
twine check dist/*
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 包检查失败！${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 包检查通过${NC}"
echo ""

echo -e "${YELLOW}步骤 6/6: 上传包...${NC}"
if [ "$TARGET" = "test" ]; then
    echo "上传到 TestPyPI..."
    twine upload --repository testpypi dist/*
    echo ""
    echo -e "${GREEN}✅ 发布到 TestPyPI 成功！${NC}"
    echo ""
    echo "测试安装："
    echo "  pip install --index-url https://test.pypi.org/simple/ quant1024"
    echo ""
    echo "确认无误后，运行以下命令发布到正式 PyPI："
    echo "  ./publish.sh prod"
elif [ "$TARGET" = "prod" ]; then
    echo -e "${YELLOW}⚠️  即将发布到正式 PyPI！${NC}"
    read -p "确认继续？(yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "已取消发布"
        exit 0
    fi
    
    twine upload dist/*
    echo ""
    echo -e "${GREEN}✅ 发布到 PyPI 成功！${NC}"
    echo ""
    echo "包已发布到: https://pypi.org/project/quant1024/"
    echo ""
    echo "用户可以通过以下命令安装："
    echo "  pip install quant1024"
fi

echo ""
echo "🎉 发布完成！"


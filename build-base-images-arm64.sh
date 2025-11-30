#!/bin/bash
#####################################################################
# ARM64 基础镜像构建脚本 - 在 Mac 本地执行
# 项目: 长春市社情民意分析平台
# 用途: 构建包含依赖的基础镜像（依赖变化时才执行）
#####################################################################

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo "构建 ARM64 基础镜像"
echo "⚠️  此脚本只在依赖变化时执行"
echo "========================================"
echo ""

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}错误: Docker未运行，请先启动Docker${NC}"
    exit 1
fi

# 检查当前架构
ARCH=$(uname -m)
echo -e "${BLUE}当前系统架构: $ARCH${NC}"
if [ "$ARCH" != "arm64" ]; then
    echo -e "${YELLOW}警告: 当前不是ARM64架构，将使用跨平台构建${NC}"
fi

# 镜像标签
REGISTRY="changchun"
VERSION="0.0.1"
WEB_BASE_IMAGE="${REGISTRY}/dvadmin3-base-web-arm64:${VERSION}"
BACKEND_BASE_IMAGE="${REGISTRY}/dvadmin3-base-backend-arm64:${VERSION}"



echo ""
echo "========================================"
echo "Step 2: 构建前端基础镜像"
echo "========================================"
echo -e "${YELLOW}正在构建: $WEB_BASE_IMAGE${NC}"
echo "包含: Node.js + yarn + 前端依赖包"
echo -e "${BLUE}预计耗时: 5-10分钟${NC}"
echo ""

docker build --platform linux/arm64 \
    -f ./docker_env/web/DockerfileBuild \
    -t $WEB_BASE_IMAGE \
    .

echo ""
echo -e "${GREEN}✓ 前端基础镜像构建完成${NC}"

echo ""
echo "========================================"
echo "Step 3: 构建后端基础镜像"
echo "========================================"
echo -e "${YELLOW}正在构建: $BACKEND_BASE_IMAGE${NC}"
echo "包含: Python + 系统依赖 + Python包"
echo -e "${BLUE}预计耗时: 10-15分钟${NC}"
echo ""

docker build --platform linux/arm64 \
    -f ./docker_env/django/DockerfileBuild \
    -t $BACKEND_BASE_IMAGE \
    .

echo ""
echo -e "${GREEN}✓ 后端基础镜像构建完成${NC}"

echo ""
echo "========================================"
echo "构建完成！基础镜像列表："
echo "========================================"
docker images | grep -E "${REGISTRY}.*base.*${VERSION}|REPOSITORY"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}基础镜像构建成功！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "镜像信息："
echo "  前端基础镜像: $WEB_BASE_IMAGE"
echo "  后端基础镜像: $BACKEND_BASE_IMAGE"
echo ""
echo -e "${YELLOW}注意事项：${NC}"
echo "  • 基础镜像只在依赖变化时需要重新构建"
echo "  • 日常开发只需运行 ./build-images-arm64.sh"
echo "  • 如果新增/修改了依赖包，需要重新运行本脚本"
echo ""
echo "下一步："
echo "  运行 ./build-images-arm64.sh 构建应用镜像"
echo ""

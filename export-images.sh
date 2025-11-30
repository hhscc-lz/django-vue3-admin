#!/bin/bash
#####################################################################
# ARM64 镜像导出脚本 - 在 Mac 本地执行
# 项目: 长春市社情民意分析平台
# 用途: 导出构建好的镜像为 tar 包，用于传输到服务器
#####################################################################

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================"
echo "导出 ARM64 镜像为 tar 包"
echo "========================================"
echo ""

# 镜像名称
VERSION="0.0.1"
WEB_IMAGE="changchun/dvadmin3-web-arm64:${VERSION}"
DJANGO_IMAGE="changchun/dvadmin3-django-arm64:${VERSION}"

# 输出目录
OUTPUT_DIR="./deploy-tar"
mkdir -p $OUTPUT_DIR

echo -e "${BLUE}输出目录: $OUTPUT_DIR${NC}"
echo -e "${BLUE}版本号: $VERSION${NC}"
echo ""

# 检查镜像是否存在
echo "检查镜像是否存在..."
if ! docker image inspect $WEB_IMAGE > /dev/null 2>&1; then
    echo -e "${RED}错误: 前端镜像不存在，请先运行 ./build-images-arm64.sh${NC}"
    exit 1
fi

if ! docker image inspect $DJANGO_IMAGE > /dev/null 2>&1; then
    echo -e "${RED}错误: 后端镜像不存在，请先运行 ./build-images-arm64.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 镜像检查通过${NC}"
echo ""

echo "========================================"
echo "Step 1: 导出前端镜像"
echo "========================================"
echo -e "${YELLOW}正在导出: $WEB_IMAGE${NC}"

docker save -o $OUTPUT_DIR/dvadmin3-web-arm64-${VERSION}.tar $WEB_IMAGE

# 获取文件大小
WEB_SIZE=$(du -h $OUTPUT_DIR/dvadmin3-web-arm64-${VERSION}.tar | cut -f1)
echo -e "${GREEN}✓ 前端镜像已导出${NC}"
echo "  文件: $OUTPUT_DIR/dvadmin3-web-arm64-${VERSION}.tar"
echo "  大小: $WEB_SIZE"
echo ""

echo "========================================"
echo "Step 2: 导出后端镜像"
echo "========================================"
echo -e "${YELLOW}正在导出: $DJANGO_IMAGE${NC}"

docker save -o $OUTPUT_DIR/dvadmin3-django-arm64-${VERSION}.tar $DJANGO_IMAGE

# 获取文件大小
DJANGO_SIZE=$(du -h $OUTPUT_DIR/dvadmin3-django-arm64-${VERSION}.tar | cut -f1)
echo -e "${GREEN}✓ 后端镜像已导出${NC}"
echo "  文件: $OUTPUT_DIR/dvadmin3-django-arm64-${VERSION}.tar"
echo "  大小: $DJANGO_SIZE"
echo ""

echo "========================================"
echo "Step 3: 复制配置文件"
echo "========================================"

# 复制前端配置
echo -e "${YELLOW}复制前端部署配置...${NC}"
cp docker-compose-frontend.yml $OUTPUT_DIR/
echo -e "${GREEN}✓ 已复制 docker-compose-frontend.yml${NC}"

# 复制后端配置
echo -e "${YELLOW}复制后端部署配置...${NC}"
cp docker-compose-backend.yml $OUTPUT_DIR/
echo -e "${GREEN}✓ 已复制 docker-compose-backend.yml${NC}"

echo ""

echo "========================================"
echo "导出完成！"
echo "========================================"
echo ""
echo "输出目录: $OUTPUT_DIR"
echo ""
echo "文件列表："
ls -lh $OUTPUT_DIR/
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}镜像已准备就绪！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

#!/bin/bash
#####################################################################
# ARM64 应用镜像构建脚本 - 在 Mac 本地执行
# 项目: 长春市社情民意分析平台
# 用途: 构建前后端应用镜像（代码变化时执行）
#####################################################################

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 参数解析
VERSION="0.0.1"
BASE_VERSION="0.0.1"
BUILD_FRONTEND=false
BUILD_BACKEND=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--version) 
            VERSION="$2"
            shift # past argument
            shift # past value
            ;;
        -f|--frontend) 
            BUILD_FRONTEND=true
            shift # past argument
            ;;
        -b|--backend) 
            BUILD_BACKEND=true
            shift # past argument
            ;;
        *) 
            echo "未知参数: $1"
            echo "使用方法: $0 [-v version] [-f] [-b]"
            exit 1
            ;;
    esac
done

# 如果没有指定 -f 或 -b，默认都构建
if [ "$BUILD_FRONTEND" = false ] && [ "$BUILD_BACKEND" = false ]; then
    BUILD_FRONTEND=true
    BUILD_BACKEND=true
fi

echo "========================================"
echo "构建 ARM64 应用镜像"
echo "应用版本: $VERSION"
echo "基础镜像版本: $BASE_VERSION"
echo "构建前端: $BUILD_FRONTEND"
echo "构建后端: $BUILD_BACKEND"
echo "========================================"
echo ""

# 镜像标签
REGISTRY="changchun"
WEB_BASE_IMAGE="${REGISTRY}/dvadmin3-base-web-arm64:${BASE_VERSION}"
BACKEND_BASE_IMAGE="${REGISTRY}/dvadmin3-base-backend-arm64:${BASE_VERSION}"
WEB_IMAGE="${REGISTRY}/dvadmin3-web-arm64:${VERSION}"
DJANGO_IMAGE="${REGISTRY}/dvadmin3-django-arm64:${VERSION}"

echo ""
echo "========================================"
echo "检查基础镜像"
echo "========================================"

# 检查前端基础镜像
if [ "$BUILD_FRONTEND" = true ]; then
    if ! docker image inspect $WEB_BASE_IMAGE > /dev/null 2>&1; then
        echo -e "${RED}错误: 前端基础镜像不存在: $WEB_BASE_IMAGE${NC}"
        echo -e "${YELLOW}请先运行: ./build-base-images-arm64.sh${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ 前端基础镜像存在: $WEB_BASE_IMAGE${NC}"
fi

# 检查后端基础镜像
if [ "$BUILD_BACKEND" = true ]; then
    if ! docker image inspect $BACKEND_BASE_IMAGE > /dev/null 2>&1; then
        echo -e "${RED}错误: 后端基础镜像不存在: $BACKEND_BASE_IMAGE${NC}"
        echo -e "${YELLOW}请先运行: ./build-base-images-arm64.sh${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ 后端基础镜像存在: $BACKEND_BASE_IMAGE${NC}"
fi


if [ "$BUILD_FRONTEND" = true ]; then
    echo ""
    echo "========================================"
    echo "Step 2: 构建前端应用镜像"
    echo "========================================"
    echo -e "${YELLOW}正在构建: $WEB_IMAGE${NC}"
    echo "包含: Vue3 编译产物 + Nginx 配置"
    echo -e "${BLUE}预计耗时: 1-3分钟${NC}"
    echo ""

    docker build --platform linux/arm64 \
        -f ./docker_env/web/Dockerfile \
        -t $WEB_IMAGE \
        .

    echo ""
    echo -e "${GREEN}✓ 前端应用镜像构建完成${NC}"
fi

if [ "$BUILD_BACKEND" = true ]; then
    echo ""
    echo "========================================"
    echo "Step 3: 构建后端应用镜像"
    echo "========================================"
    echo -e "${YELLOW}正在构建: $DJANGO_IMAGE${NC}"
    echo "包含: Django 代码 + 配置文件"
    echo -e "${BLUE}预计耗时: 30秒 - 1分钟${NC}"
    echo ""

    docker build --platform linux/arm64 \
        -f ./docker_env/django/Dockerfile \
        -t $DJANGO_IMAGE \
        .

    echo ""
    echo -e "${GREEN}✓ 后端应用镜像构建完成${NC}"
fi

echo ""
echo "========================================"
echo "构建完成！应用镜像列表："
echo "========================================"
docker images | grep -E "${REGISTRY}.*${VERSION}|REPOSITORY" | grep -v base

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}应用镜像构建成功！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "镜像信息："
if [ "$BUILD_FRONTEND" = true ]; then
    echo "  前端应用镜像: $WEB_IMAGE"
fi
if [ "$BUILD_BACKEND" = true ]; then
    echo "  后端应用镜像: $DJANGO_IMAGE"
fi
echo ""
echo "下一步："
echo "  运行 ./export-images.sh -v $VERSION 导出镜像为 tar 包"
echo ""
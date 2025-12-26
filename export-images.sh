#!/bin/bash
#####################################################################
# ARM64 镜像导出脚本
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

# 镜像仓库前缀
REGISTRY="changchun"

# 参数解析
VERSION="0.0.1"
EXPORT_FRONTEND=false
EXPORT_BACKEND=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--version)
            VERSION="$2"
            shift # past argument
            shift # past value
            ;;
        -f|--frontend)
            EXPORT_FRONTEND=true
            shift # past argument
            ;;
        -b|--backend)
            EXPORT_BACKEND=true
            shift # past argument
            ;;
        *)
            echo "未知参数: $1"
            echo "使用方法: $0 [-v version] [-f] [-b]"
            exit 1
            ;;
    esac
done

# 如果没有指定 -f 或 -b，默认都导出
if [ "$EXPORT_FRONTEND" = false ] && [ "$EXPORT_BACKEND" = false ]; then
    EXPORT_FRONTEND=true
    EXPORT_BACKEND=true
fi

echo "========================================"
echo "导出 ARM64 镜像为 tar 包"
echo "版本: $VERSION"
echo "导出前端: $EXPORT_FRONTEND"
echo "导出后端: $EXPORT_BACKEND"
echo "========================================"
echo ""

# 镜像名称
WEB_IMAGE="${REGISTRY}/dvadmin3-web-arm64:${VERSION}"
DJANGO_IMAGE="${REGISTRY}/dvadmin3-django-arm64:${VERSION}"

# 输出目录
OUTPUT_DIR="./deploy-tar"
mkdir -p $OUTPUT_DIR

echo -e "${BLUE}输出目录: $OUTPUT_DIR${NC}"
echo -e "${BLUE}版本号: $VERSION${NC}"
echo ""

# 检查镜像是否存在
echo "检查镜像是否存在..."

if [ "$EXPORT_FRONTEND" = true ]; then
    if ! docker image inspect $WEB_IMAGE > /dev/null 2>&1; then
        echo -e "${RED}错误: 前端镜像不存在，请先运行 ./build-images-arm64.sh -v $VERSION${NC}"
        exit 1
    fi
fi

if [ "$EXPORT_BACKEND" = true ]; then
    if ! docker image inspect $DJANGO_IMAGE > /dev/null 2>&1; then
        echo -e "${RED}错误: 后端镜像不存在，请先运行 ./build-images-arm64.sh -v $VERSION${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ 镜像检查通过${NC}"
echo ""

if [ "$EXPORT_FRONTEND" = true ]; then
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
fi

if [ "$EXPORT_BACKEND" = true ]; then
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
fi

echo "========================================"
echo "Step 3: 复制配置文件"
echo "========================================"

if [ "$EXPORT_FRONTEND" = true ]; then
    # 复制前端配置
    echo -e "${YELLOW}复制前端部署配置...${NC}"
    cp docker-compose-frontend.yml $OUTPUT_DIR/
    # 更新docker-compose文件中的镜像版本
    sed -i "s|${REGISTRY}/dvadmin3-web-arm64:.*|${REGISTRY}/dvadmin3-web-arm64:${VERSION}|g" $OUTPUT_DIR/docker-compose-frontend.yml
    echo -e "${GREEN}✓ 已复制并更新 docker-compose-frontend.yml${NC}"
fi

if [ "$EXPORT_BACKEND" = true ]; then
    # 复制后端配置
    echo -e "${YELLOW}复制后端部署配置...${NC}"
    cp docker-compose-backend.yml $OUTPUT_DIR/
    # 更新docker-compose文件中的镜像版本
    sed -i "s|${REGISTRY}/dvadmin3-django-arm64:.*|${REGISTRY}/dvadmin3-django-arm64:${VERSION}|g" $OUTPUT_DIR/docker-compose-backend.yml
    echo -e "${GREEN}✓ 已复制并更新 docker-compose-backend.yml${NC}"
fi

echo ""
echo "========================================"
echo "Step 4: 生成部署脚本"
echo "========================================"

cat > $OUTPUT_DIR/deploy.sh << 'DEPLOY_SCRIPT'
#!/bin/bash
#####################################################################
# 部署脚本 - 在目标服务器执行
# 项目: 长春市社情民意分析平台
# 用法: ./deploy.sh [命令]
#   命令:
#     (无)      - 完整部署（加载镜像+启动服务）
#     start     - 启动服务
#     stop      - 停止服务
#     restart   - 重启服务
#     status    - 查看服务状态
#     logs      - 查看日志
#     clean     - 清理旧镜像
#####################################################################

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

DEPLOY_SCRIPT

# 动态写入版本号
echo "VERSION=\"${VERSION}\"" >> $OUTPUT_DIR/deploy.sh

cat >> $OUTPUT_DIR/deploy.sh << 'DEPLOY_SCRIPT'

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查 Docker 是否运行
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}错误: Docker 未运行，请先启动 Docker${NC}"
        exit 1
    fi
}

# 加载镜像
load_images() {
    echo "========================================"
    echo "加载镜像"
    echo "========================================"

    if [ -f "dvadmin3-django-arm64-${VERSION}.tar" ]; then
        echo -e "${YELLOW}加载后端镜像...${NC}"
        docker load -i dvadmin3-django-arm64-${VERSION}.tar
        echo -e "${GREEN}✓ 后端镜像加载完成${NC}"
    fi

    if [ -f "dvadmin3-web-arm64-${VERSION}.tar" ]; then
        echo -e "${YELLOW}加载前端镜像...${NC}"
        docker load -i dvadmin3-web-arm64-${VERSION}.tar
        echo -e "${GREEN}✓ 前端镜像加载完成${NC}"
    fi
    echo ""
}

# 停止服务
stop_services() {
    echo "========================================"
    echo "停止服务"
    echo "========================================"

    if [ -f "docker-compose-backend.yml" ]; then
        docker-compose -f docker-compose-backend.yml down 2>/dev/null || true
    fi
    if [ -f "docker-compose-frontend.yml" ]; then
        docker-compose -f docker-compose-frontend.yml down 2>/dev/null || true
    fi
    echo -e "${GREEN}✓ 服务已停止${NC}"
    echo ""
}

# 启动服务
start_services() {
    echo "========================================"
    echo "启动服务"
    echo "========================================"

    if [ -f "docker-compose-backend.yml" ]; then
        echo -e "${YELLOW}启动后端服务...${NC}"
        docker-compose -f docker-compose-backend.yml up -d
        echo -e "${GREEN}✓ 后端服务已启动${NC}"
    fi

    if [ -f "docker-compose-frontend.yml" ]; then
        echo -e "${YELLOW}启动前端服务...${NC}"
        docker-compose -f docker-compose-frontend.yml up -d
        echo -e "${GREEN}✓ 前端服务已启动${NC}"
    fi
    echo ""
}

# 查看状态
show_status() {
    echo "========================================"
    echo "服务状态"
    echo "========================================"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "dvadmin3|NAMES" || echo "没有运行中的服务"
    echo ""

    # 获取本机IP
    LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "<服务器IP>")
    echo -e "${GREEN}访问地址:${NC}"
    echo "  前端: http://${LOCAL_IP}:8883"
    echo "  后端: http://${LOCAL_IP}:8882"
    echo ""
}

# 查看日志
show_logs() {
    echo "========================================"
    echo "服务日志 (Ctrl+C 退出)"
    echo "========================================"
    echo ""
    echo "1) 后端日志"
    echo "2) 前端日志"
    echo "3) 全部日志"
    read -p "请选择 [1-3]: " choice

    case $choice in
        1) docker logs -f dvadmin3-django 2>/dev/null || echo "后端容器未运行" ;;
        2) docker logs -f dvadmin3-web 2>/dev/null || echo "前端容器未运行" ;;
        3) docker-compose -f docker-compose-backend.yml -f docker-compose-frontend.yml logs -f 2>/dev/null ;;
        *) echo "无效选择" ;;
    esac
}

# 清理旧镜像
clean_images() {
    echo "========================================"
    echo "清理旧镜像"
    echo "========================================"

    echo -e "${YELLOW}清理未使用的镜像...${NC}"
    docker image prune -f
    echo -e "${GREEN}✓ 清理完成${NC}"
    echo ""
}

# 完整部署
full_deploy() {
    echo "========================================"
    echo "部署 ARM64 应用镜像"
    echo "版本: $VERSION"
    echo "========================================"
    echo ""

    check_docker
    load_images
    stop_services
    start_services
    show_status

    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}部署完成！${NC}"
    echo -e "${GREEN}========================================${NC}"
}

# 主逻辑
case "${1:-deploy}" in
    deploy|"")
        full_deploy
        ;;
    start)
        check_docker
        start_services
        show_status
        ;;
    stop)
        check_docker
        stop_services
        ;;
    restart)
        check_docker
        stop_services
        start_services
        show_status
        ;;
    status)
        check_docker
        show_status
        ;;
    logs)
        check_docker
        show_logs
        ;;
    clean)
        check_docker
        clean_images
        ;;
    *)
        echo "用法: $0 {deploy|start|stop|restart|status|logs|clean}"
        exit 1
        ;;
esac
DEPLOY_SCRIPT

chmod +x $OUTPUT_DIR/deploy.sh
echo -e "${GREEN}✓ 已生成部署脚本 deploy.sh${NC}"

echo ""
echo "========================================"
echo "Step 5: 打包部署文件"
echo "========================================"

PACKAGE_NAME="deploy-${VERSION}.tar.gz"
echo -e "${YELLOW}正在打包: $PACKAGE_NAME${NC}"

tar -czvf $PACKAGE_NAME $OUTPUT_DIR/

PACKAGE_SIZE=$(du -h $PACKAGE_NAME | cut -f1)
echo -e "${GREEN}✓ 打包完成${NC}"
echo "  文件: $PACKAGE_NAME"
echo "  大小: $PACKAGE_SIZE"

echo ""
echo "========================================"
echo "导出完成！"
echo "========================================"
echo ""
echo -e "${BLUE}生成的文件:${NC}"
ls -lh $PACKAGE_NAME
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}部署包已准备就绪！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}部署步骤:${NC}"
echo "  1. 上传 $PACKAGE_NAME 到目标服务器"
echo "  2. 解压: tar -xzvf $PACKAGE_NAME"
echo "  3. 部署: cd deploy-tar && chmod +x deploy.sh && ./deploy.sh"
echo ""
echo -e "${YELLOW}deploy.sh 支持的命令:${NC}"
echo "  ./deploy.sh          # 完整部署"
echo "  ./deploy.sh start    # 启动服务"
echo "  ./deploy.sh stop     # 停止服务"
echo "  ./deploy.sh restart  # 重启服务"
echo "  ./deploy.sh status   # 查看状态"
echo "  ./deploy.sh logs     # 查看日志"
echo "  ./deploy.sh clean    # 清理旧镜像"
echo ""

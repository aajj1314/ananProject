#!/usr/bin/env bash
# ============================================================
# 智慧养老鞋垫平台 - 卸载脚本
# 停止服务、删除容器和镜像，可选删除数据卷
# ============================================================

set -euo pipefail

# ---- 颜色定义 ----
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ---- 项目配置 ----
IMAGES=("elderly-care-backend:latest" "elderly-care-frontend:latest" "redis:7.2.4-alpine")

# ---- 获取脚本所在目录 ----
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ---- 工具函数 ----
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

ask_confirm() {
    local prompt=$1
    local default=${2:-n}

    if [ "$default" = "y" ]; then
        prompt="$prompt [Y/n] "
    else
        prompt="$prompt [y/N] "
    fi

    read -r -p "$(echo -e "$prompt")" answer
    answer=${answer:-$default}

    case "$answer" in
        [yY][eE][sS]|[yY]) return 0 ;;
        *) return 1 ;;
    esac
}

check_docker_compose() {
    if docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    elif command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        print_error "Docker Compose 未安装！"
        exit 1
    fi
}

# ---- 主流程 ----
echo -e "${CYAN}"
echo "============================================================"
echo "       智慧养老鞋垫平台 - 卸载工具"
echo "============================================================"
echo -e "${NC}"

# 检查是否有正在运行的服务
check_docker_compose

running_containers=$($COMPOSE_CMD --profile prod ps -q 2>/dev/null | wc -l)

if [ "$running_containers" -gt 0 ]; then
    print_info "检测到正在运行的服务容器"
    if ask_confirm "是否停止所有服务？" "y"; then
        print_info "停止所有服务..."
        $COMPOSE_CMD --profile prod down
        print_success "所有服务已停止"
    else
        print_warn "跳过停止服务"
    fi
else
    print_info "没有检测到正在运行的服务容器"
    # 尝试清理可能残留的容器
    $COMPOSE_CMD --profile prod down 2>/dev/null || true
fi

echo ""

# 删除数据卷
if ask_confirm "是否删除持久化数据？（包含数据库和缓存数据，删除后不可恢复）" "n"; then
    print_warn "删除数据卷..."
    $COMPOSE_CMD --profile prod down -v 2>/dev/null || true

    # 额外清理可能残留的数据卷
    for vol in deploy_backend_data deploy_redis_data; do
        if docker volume inspect "$vol" &> /dev/null; then
            docker volume rm "$vol" 2>/dev/null || true
        fi
    done
    print_success "数据卷已删除"
else
    print_info "保留数据卷"
    # 确保容器已删除但保留数据卷
    $COMPOSE_CMD --profile prod down 2>/dev/null || true
fi

echo ""

# 删除镜像
if ask_confirm "是否删除 Docker 镜像？" "y"; then
    print_info "删除项目镜像..."
    for image in "${IMAGES[@]}"; do
        if docker image inspect "$image" &> /dev/null; then
            docker rmi "$image" 2>/dev/null || true
            print_success "已删除镜像: $image"
        else
            print_info "镜像不存在，跳过: $image"
        fi
    done

    # 清理悬空镜像
    dangling=$(docker images -f "dangling=true" -q | wc -l)
    if [ "$dangling" -gt 0 ]; then
        print_info "清理 $dangling 个悬空镜像..."
        docker image prune -f &> /dev/null
    fi
    print_success "镜像清理完成"
else
    print_info "保留 Docker 镜像"
fi

echo ""

# 删除 .env 文件
if [ -f ".env" ]; then
    if ask_confirm "是否删除 .env 配置文件？" "n"; then
        rm -f .env
        print_success ".env 文件已删除"
    else
        print_info "保留 .env 文件"
    fi
fi

# 清理网络
print_info "清理 Docker 网络..."
$COMPOSE_CMD --profile prod down 2>/dev/null || true
docker network prune -f &> /dev/null

echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}  卸载完成！${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo -e "  如需重新部署，请运行: ${CYAN}./deploy.sh start${NC}"
echo ""

#!/usr/bin/env bash
# ============================================================
# 智慧养老鞋垫平台 - 一键部署脚本
# 支持: start / stop / restart / status / logs
# ============================================================

set -euo pipefail

# ---- 颜色定义 ----
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ---- 项目配置 ----
PROJECT_NAME="elderly-care"
COMPOSE_FILE="docker-compose.yml"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-8081}"
ADMIN_PHONE="${ADMIN_PHONE:-15577305913}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-passwor}"

# ---- 获取脚本所在目录 ----
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ---- 工具函数 ----
print_banner() {
    echo -e "${CYAN}"
    echo "============================================================"
    echo "       智慧养老鞋垫平台 - 一键部署工具"
    echo "============================================================"
    echo -e "${NC}"
}

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

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装！请先安装 Docker。"
        echo -e "  安装指南: https://docs.docker.com/engine/install/"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        print_error "Docker 服务未运行！请先启动 Docker。"
        echo -e "  启动命令: sudo systemctl start docker"
        exit 1
    fi

    print_success "Docker 已安装且运行正常 (版本: $(docker --version | awk '{print $3}' | tr -d ','))"
}

check_docker_compose() {
    if docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
        print_success "Docker Compose (V2) 已安装 (版本: $(docker compose version --short))"
    elif command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
        print_success "Docker Compose (V1) 已安装 (版本: $(docker-compose --version | awk '{print $3}' | tr -d ','))"
    else
        print_error "Docker Compose 未安装！请先安装 Docker Compose。"
        echo -e "  安装指南: https://docs.docker.com/compose/install/"
        exit 1
    fi
}

generate_jwt_secret() {
    # 如果环境变量已设置，则使用现有值
    if [ -n "${JWT_SECRET:-}" ]; then
        print_info "使用已有的 JWT_SECRET"
        return
    fi

    # 尝试从 .env 文件读取
    if [ -f ".env" ]; then
        existing_secret=$(grep -E "^JWT_SECRET=" .env 2>/dev/null | cut -d'=' -f2-)
        if [ -n "$existing_secret" ] && [ "$existing_secret" != "your-super-secret-random-key-change-this-in-production" ]; then
            export JWT_SECRET="$existing_secret"
            print_info "从 .env 文件读取 JWT_SECRET"
            return
        fi
    fi

    # 自动生成新的 JWT_SECRET
    if command -v openssl &> /dev/null; then
        JWT_SECRET=$(openssl rand -hex 32)
    elif command -v python3 &> /dev/null; then
        JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    else
        JWT_SECRET="elderly-care-jwt-$(date +%s)-$RANDOM$RANDOM$RANDOM"
    fi
    export JWT_SECRET
    print_success "已自动生成 JWT_SECRET: ${JWT_SECRET:0:8}...${JWT_SECRET: -8}"

    # 保存到 .env 文件以便下次使用
    if [ ! -f ".env" ] || ! grep -q "^JWT_SECRET=" .env; then
        echo "JWT_SECRET=$JWT_SECRET" >> .env
    else
        sed -i "s|^JWT_SECRET=.*|JWT_SECRET=$JWT_SECRET|" .env
    fi
    print_info "JWT_SECRET 已保存到 .env 文件"
}

wait_for_healthy() {
    local service=$1
    local max_attempts=${2:-30}
    local attempt=1

    print_info "等待 $service 服务健康检查通过..."

    while [ $attempt -le $max_attempts ]; do
        local status
        status=$($COMPOSE_CMD ps "$service" --format json 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('Health', data.get('Status', 'unknown')))
except:
    print('unknown')
" 2>/dev/null || echo "unknown")

        if echo "$status" | grep -qi "healthy"; then
            print_success "$service 服务已健康"
            return 0
        fi

        # 也检查容器是否正在运行
        local running
        running=$($COMPOSE_CMD ps "$service" --format "{{.Status}}" 2>/dev/null || echo "")
        if echo "$running" | grep -qi "Up"; then
            printf "\r${BLUE}[INFO]${NC} 等待 %s... (%d/%d) 状态: %s" "$service" "$attempt" "$max_attempts" "$running"
        else
            printf "\r${BLUE}[INFO]${NC} 等待 %s... (%d/%d)" "$service" "$attempt" "$max_attempts"
        fi

        attempt=$((attempt + 1))
        sleep 3
    done

    echo ""
    print_warn "$service 在 ${max_attempts} 次尝试后仍未健康，请检查日志"
    return 1
}

do_start() {
    print_banner
    print_info "开始部署智慧养老鞋垫平台..."

    # 检查环境
    check_docker
    check_docker_compose

    # 生成 JWT_SECRET
    generate_jwt_secret

    # 导出其他环境变量
    export BACKEND_PORT
    export FRONTEND_PORT
    export ADMIN_PHONE
    export ADMIN_PASSWORD

    # 构建并启动服务
    print_info "构建并启动 Docker 容器（首次可能需要几分钟）..."
    $COMPOSE_CMD --profile prod up -d --build

    # 等待 Redis
    print_info "等待 Redis 服务启动..."
    local redis_attempts=0
    while [ $redis_attempts -lt 20 ]; do
        if docker exec elderly-care-redis redis-cli ping &> /dev/null; then
            print_success "Redis 服务已就绪"
            break
        fi
        redis_attempts=$((redis_attempts + 1))
        sleep 2
    done

    # 等待后端
    print_info "等待后端服务启动（约需30秒初始化数据库）..."
    local backend_attempts=0
    while [ $backend_attempts -lt 40 ]; do
        if curl -sf "http://localhost:${BACKEND_PORT}/health" > /dev/null 2>&1; then
            print_success "后端服务已就绪"
            break
        fi
        backend_attempts=$((backend_attempts + 1))
        printf "\r${BLUE}[INFO]${NC} 等待后端服务... (%d/40)" "$backend_attempts"
        sleep 3
    done
    echo ""

    # 等待前端
    print_info "等待前端服务启动..."
    local frontend_attempts=0
    while [ $frontend_attempts -lt 20 ]; do
        if curl -sf "http://localhost:${FRONTEND_PORT}" > /dev/null 2>&1; then
            print_success "前端服务已就绪"
            break
        fi
        frontend_attempts=$((frontend_attempts + 1))
        sleep 2
    done

    # 输出部署信息
    echo ""
    echo -e "${GREEN}============================================================${NC}"
    echo -e "${GREEN}  部署成功！智慧养老鞋垫平台已启动${NC}"
    echo -e "${GREEN}============================================================${NC}"
    echo ""
    echo -e "  ${CYAN}前端地址:${NC}    http://localhost:${FRONTEND_PORT}"
    echo -e "  ${CYAN}后端API:${NC}     http://localhost:${BACKEND_PORT}"
    echo -e "  ${CYAN}API文档:${NC}     http://localhost:${BACKEND_PORT}/docs"
    echo -e "  ${CYAN}健康检查:${NC}    http://localhost:${BACKEND_PORT}/health"
    echo ""
    echo -e "  ${YELLOW}管理员账号:${NC}"
    echo -e "  ${YELLOW}  手机号:${NC}  ${ADMIN_PHONE}"
    echo -e "  ${YELLOW}  密码:${NC}    ${ADMIN_PASSWORD}"
    echo ""
    echo -e "  ${BLUE}常用命令:${NC}"
    echo -e "  ${BLUE}  查看状态:${NC}  $0 status"
    echo -e "  ${BLUE}  查看日志:${NC}  $0 logs"
    echo -e "  ${BLUE}  停止服务:${NC}  $0 stop"
    echo -e "  ${BLUE}  重启服务:${NC}  $0 restart"
    echo ""
    echo -e "  ${RED}安全提示: 生产环境请修改 JWT_SECRET 和管理员密码！${NC}"
    echo ""
}

do_stop() {
    print_info "停止智慧养老鞋垫平台..."
    check_docker_compose
    $COMPOSE_CMD --profile prod down
    print_success "所有服务已停止"
}

do_restart() {
    print_info "重启智慧养老鞋垫平台..."
    do_stop
    do_start
}

do_status() {
    check_docker_compose
    echo -e "${CYAN}服务状态:${NC}"
    $COMPOSE_CMD --profile prod ps
    echo ""
    echo -e "${CYAN}健康检查:${NC}"

    # 检查后端
    if curl -sf "http://localhost:${BACKEND_PORT}/health" > /dev/null 2>&1; then
        echo -e "  后端: ${GREEN}正常${NC}"
    else
        echo -e "  后端: ${RED}异常${NC}"
    fi

    # 检查前端
    if curl -sf "http://localhost:${FRONTEND_PORT}" > /dev/null 2>&1; then
        echo -e "  前端: ${GREEN}正常${NC}"
    else
        echo -e "  前端: ${RED}异常${NC}"
    fi

    # 检查Redis
    if docker exec elderly-care-redis redis-cli ping &> /dev/null; then
        echo -e "  Redis: ${GREEN}正常${NC}"
    else
        echo -e "  Redis: ${RED}异常${NC}"
    fi
}

do_logs() {
    check_docker_compose
    local service="${2:-}"
    if [ -n "$service" ]; then
        $COMPOSE_CMD logs -f "$service"
    else
        $COMPOSE_CMD logs -f
    fi
}

# ---- 主入口 ----
case "${1:-start}" in
    start)
        do_start
        ;;
    stop)
        do_stop
        ;;
    restart)
        do_restart
        ;;
    status)
        do_status
        ;;
    logs)
        do_logs "$@"
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|logs [service]}"
        echo ""
        echo "命令说明:"
        echo "  start    - 构建并启动所有服务（默认）"
        echo "  stop     - 停止所有服务"
        echo "  restart  - 重启所有服务"
        echo "  status   - 查看服务状态和健康检查"
        echo "  logs     - 查看服务日志（可选指定服务名: backend/frontend/redis）"
        exit 1
        ;;
esac

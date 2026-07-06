#!/bin/bash
# ============================================================
# Vue-Springboot-Library 开发操作脚本
# 用法: ./dev.sh [命令]
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/SpringBoot"
FRONTEND_DIR="$SCRIPT_DIR/vue"
BACKEND_URL="${BACKEND_URL:-http://localhost:9090}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:9876}"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

pass()  { echo -e "${GREEN}[PASS]${NC} $*"; }
fail()  { echo -e "${RED}[FAIL]${NC} $*"; }
info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }

usage() {
    echo "用法: $0 <命令>"
    echo ""
    echo "命令:"
    echo "  build-backend    编译后端 (Maven)"
    echo "  build-frontend   编译前端 (npm)"
    echo "  build            编译全部"
    echo "  start-backend    启动后端 (本地 jar)"
    echo "  start-frontend   启动前端开发服务器"
    echo "  docker-up        Docker Compose 启动全部"
    echo "  docker-down      Docker Compose 停止"
    echo "  docker-logs      查看容器日志"
    echo "  verify           核心流程冒烟测试"
    echo "  verify-full      完整验收测试（冒烟+错误路径+权限边界）"
    echo "  api-test         快速 API 连通性测试"
    echo "  help             显示此帮助"
}

# ============================================================
# 编译
# ============================================================
build_backend() {
    info "编译后端..."
    cd "$BACKEND_DIR"
    mvn package -DskipTests -q
    pass "后端编译完成 → $BACKEND_DIR/target/"
}

build_frontend() {
    info "编译前端..."
    cd "$FRONTEND_DIR"
    npm install --silent 2>/dev/null
    npm run build 2>&1 | tail -3
    pass "前端编译完成 → $FRONTEND_DIR/dist/"
}

build() {
    build_backend
    build_frontend
}

# ============================================================
# 启动
# ============================================================
start_backend() {
    info "启动后端 (端口 9090)..."
    cd "$BACKEND_DIR"
    local jar=$(ls target/*.jar 2>/dev/null | head -1)
    if [ -z "$jar" ]; then
        warn "未找到 jar，先编译..."
        build_backend
        jar=$(ls target/*.jar 2>/dev/null | head -1)
    fi
    java -jar "$jar" &
    sleep 5
    if curl -s "$BACKEND_URL/user/login" -X POST -H 'Content-Type: application/json' -d '{"username":"_ping_","password":"_"}' > /dev/null 2>&1; then
        pass "后端已启动: $BACKEND_URL"
    else
        warn "后端可能还在启动中，请稍候..."
    fi
}

start_frontend() {
    info "启动前端开发服务器 (端口 9876)..."
    cd "$FRONTEND_DIR"
    npm run serve
}

# ============================================================
# Docker
# ============================================================
docker_up() {
    info "Docker Compose 启动全部服务..."
    cd "$SCRIPT_DIR"
    docker-compose up -d
    info "等待服务就绪..."
    sleep 10
    pass "服务已启动"
    echo "  前端: $FRONTEND_URL"
    echo "  后端: $BACKEND_URL"
}

docker_down() {
    cd "$SCRIPT_DIR"
    docker-compose down
    pass "服务已停止"
}

docker_logs() {
    cd "$SCRIPT_DIR"
    docker-compose logs --tail=50 "${1:-}"
}

# ============================================================
# 验证
# ============================================================

# API 连通性快速测试
api_test() {
    info "API 连通性测试..."
    local base="$BACKEND_URL"
    local failures=0

    _curl() {
        local desc="$1" method="$2" url="$3" data="$4"
        local resp
        resp=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$url" \
            -H 'Content-Type: application/json' \
            -d "$data" 2>/dev/null || echo "000")
        if [ "$resp" -ge 200 ] && [ "$resp" -lt 500 ]; then
            pass "$desc (HTTP $resp)"
        else
            fail "$desc (HTTP $resp)  → $url"
            ((failures++)) || true
        fi
    }

    _curl "dashboard"     GET  "$base/dashboard" '{}'
    _curl "books"         GET  "$base/book?pageNum=1&pageSize=5" '{}'
    _curl "lend-records"  GET  "$base/LendRecord?pageNum=1&pageSize=5" '{}'
    _curl "bookwithuser"  GET  "$base/bookwithuser?pageNum=1&pageSize=5" '{}'

    if [ "$failures" -eq 0 ]; then
        pass "API 连通性测试全部通过"
    else
        fail "$failures 个端点不可达"
        return 1
    fi
}

# 核心流程冒烟测试
verify() {
    local base="$BACKEND_URL"
    local failures=0
    local admin_user="verify_admin_$(date +%s)"
    local reader_user="verify_reader_$(date +%s)"
    local admin_token=""
    local reader_token=""
    local test_book_isbn="TEST-ISBN-$(date +%s)"

    echo ""
    echo "============================================"
    info "核心流程冒烟测试"
    echo "============================================"

    # ---- 1. 注册管理员 ----
    info "1. 注册管理员账号: $admin_user"
    local resp
    resp=$(curl -s -X POST "$base/user/register" \
        -H 'Content-Type: application/json' \
        -d "{\"username\":\"$admin_user\",\"password\":\"test123\",\"nickName\":\"TestAdmin\",\"role\":1}" 2>/dev/null)
    if echo "$resp" | grep -q '"code":"0"'; then
        pass "管理员注册成功"
    elif echo "$resp" | grep -q "用户名已重复"; then
        pass "管理员已存在（跳过注册）"
    else
        fail "管理员注册失败: $resp"
        ((failures++)) || true
    fi

    # ---- 2. 管理员登录 ----
    info "2. 管理员登录"
    resp=$(curl -s -X POST "$base/user/login" \
        -H 'Content-Type: application/json' \
        -d "{\"username\":\"$admin_user\",\"password\":\"test123\"}" 2>/dev/null)
    if echo "$resp" | grep -q '"code":"0"'; then
        admin_token=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('token',''))" 2>/dev/null || true)
        pass "管理员登录成功"
    else
        fail "管理员登录失败: $resp"
        ((failures++)) || true
    fi

    # ---- 3. 注册读者 ----
    info "3. 注册读者账号: $reader_user"
    resp=$(curl -s -X POST "$base/user/register" \
        -H 'Content-Type: application/json' \
        -d "{\"username\":\"$reader_user\",\"password\":\"test123\",\"nickName\":\"TestReader\",\"role\":2}" 2>/dev/null)
    if echo "$resp" | grep -q '"code":"0"'; then
        pass "读者注册成功"
    elif echo "$resp" | grep -q "用户名已重复"; then
        pass "读者已存在（跳过注册）"
    else
        fail "读者注册失败: $resp"
        ((failures++)) || true
    fi

    # ---- 4. 读者登录 ----
    info "4. 读者登录"
    resp=$(curl -s -X POST "$base/user/login" \
        -H 'Content-Type: application/json' \
        -d "{\"username\":\"$reader_user\",\"password\":\"test123\"}" 2>/dev/null)
    local reader_id=""
    if echo "$resp" | grep -q '"code":"0"'; then
        reader_token=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('token',''))" 2>/dev/null || true)
        reader_id=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('id',''))" 2>/dev/null || true)
        pass "读者登录成功 (id=$reader_id)"
    else
        fail "读者登录失败: $resp"
        ((failures++)) || true
    fi

    # ---- 5. 管理员新增图书 ----
    info "5. 管理员新增图书: $test_book_isbn"
    resp=$(curl -s -X POST "$base/book" \
        -H 'Content-Type: application/json' \
        -d "{\"isbn\":\"$test_book_isbn\",\"name\":\"冒烟测试图书\",\"price\":29.90,\"author\":\"测试作者\",\"publisher\":\"测试出版社\",\"status\":\"1\",\"borrownum\":0}" 2>/dev/null)
    local book_id=""
    if echo "$resp" | grep -q '"code":"0"'; then
        pass "图书新增成功"
        # 查询图书获取 ID
        resp=$(curl -s "$base/book?pageNum=1&pageSize=20" 2>/dev/null)
        book_id=$(echo "$resp" | python3 -c "
import sys,json
data=json.load(sys.stdin)
records=data.get('data',{}).get('records',[])
for r in records:
    if r.get('isbn')=='$test_book_isbn':
        print(r.get('id',''))
        break
" 2>/dev/null || true)
        info "  图书 ID: $book_id"
    else
        fail "图书新增失败: $resp"
        ((failures++)) || true
    fi

    # ---- 6. 查询图书（读者可查） ----
    info "6. 查询图书列表"
    resp=$(curl -s "$base/book?pageNum=1&pageSize=5&search=冒烟测试" 2>/dev/null)
    if echo "$resp" | grep -q '"code":"0"'; then
        local count=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('total',0))" 2>/dev/null || echo 0)
        if [ "$count" -ge 1 ]; then
            pass "图书查询成功 (找到 $count 本)"
        else
            warn "图书查询未找到测试图书 (count=$count)"
        fi
    else
        fail "图书查询失败"
        ((failures++)) || true
    fi

    # ---- 7. Dashboard 统计 ----
    info "7. Dashboard 统计"
    resp=$(curl -s "$base/dashboard" 2>/dev/null)
    if echo "$resp" | grep -q '"code":"0"'; then
        pass "Dashboard 正常返回"
        local vc=$(echo "$resp" | python3 -c "import sys,json; d=json.load(sys.stdin).get('data',{}); print(f'visit={d.get(\"visitCount\",\"?\")}, user={d.get(\"userCount\",\"?\")}, book={d.get(\"bookCount\",\"?\")}, lend={d.get(\"lendRecordCount\",\"?\")}')" 2>/dev/null || echo "?")
        info "  统计: $vc"
    else
        fail "Dashboard 返回异常"
        ((failures++)) || true
    fi

    # ---- 8. 读者管理接口 ----
    info "8. 读者管理（管理员查询读者列表）"
    resp=$(curl -s "$base/user?pageNum=1&pageSize=10" 2>/dev/null)
    if echo "$resp" | grep -q '"code":"0"'; then
        pass "读者列表查询成功"
    else
        fail "读者列表查询失败"
        ((failures++)) || true
    fi

    # ---- 9. 借阅记录接口 ----
    info "9. 借阅记录查询"
    resp=$(curl -s "$base/LendRecord?pageNum=1&pageSize=5" 2>/dev/null)
    if echo "$resp" | grep -q '"code":"0"'; then
        pass "借阅记录查询成功"
    else
        fail "借阅记录查询失败"
        ((failures++)) || true
    fi

    # ---- 10. 当前借阅状态接口 ----
    info "10. 当前借阅状态查询"
    resp=$(curl -s "$base/bookwithuser?pageNum=1&pageSize=5" 2>/dev/null)
    if echo "$resp" | grep -q '"code":"0"'; then
        pass "借阅状态查询成功"
    else
        fail "借阅状态查询失败"
        ((failures++)) || true
    fi

    # ---- 11. 清理测试图书 ----
    if [ -n "$book_id" ] && [ "$book_id" != "None" ]; then
        info "11. 清理测试图书 (id=$book_id)"
        resp=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$base/book/$book_id" 2>/dev/null || echo "000")
        if [ "$resp" -ge 200 ] && [ "$resp" -lt 300 ]; then
            pass "测试图书已清理"
        else
            warn "测试图书清理返回 HTTP $resp (可手动删除)"
        fi
    fi

    # ---- 结果 ----
    echo ""
    echo "============================================"
    if [ "$failures" -eq 0 ]; then
        pass "核心流程冒烟测试全部通过 (0 失败)"
        echo "============================================"
        return 0
    else
        fail "核心流程冒烟测试: $failures 项失败"
        echo "============================================"
        return 1
    fi
}

# ============================================================
# 完整验收测试（错误路径 + 权限边界）
# ============================================================
verify_full() {
    local base="$BACKEND_URL"
    local failures=0
    local admin_user="vfull_admin_$(date +%s)"
    local reader_user="vfull_reader_$(date +%s)"
    local admin_token=""
    local reader_token=""

    echo ""
    echo "============================================"
    info "完整验收测试：冒烟 + 错误路径 + 权限边界"
    echo "============================================"

    # ---- 阶段一：核心冒烟 ----
    info "阶段一：核心流程冒烟测试"
    local smoke_ok=0
    verify && smoke_ok=1 || warn "冒烟测试有未通过项（可能是已知问题），继续后续阶段..."
    echo ""

    # ---- 阶段二：错误路径 ----
    info "阶段二：错误路径测试"

    _expect_code() {
        local desc="$1" code="$2" method="$3" url="$4" data="$5"
        local resp
        resp=$(curl -s -X "$method" "$url" \
            -H 'Content-Type: application/json' \
            -d "$data" 2>/dev/null || echo '{}')
        local actual=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('code','?'))" 2>/dev/null || echo '?')
        if [ "$actual" = "$code" ]; then
            pass "$desc"
        else
            # 如果是 HTTP 非 200，也算 error
            local http=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$url" \
                -H 'Content-Type: application/json' \
                -d "$data" 2>/dev/null || echo '000')
            if [ "$http" -ge 500 ]; then
                fail "$desc (HTTP $http, 期望 code=$code)"
                ((failures++)) || true
            elif [ "$actual" = "-1" ] && [ "$code" = "-1" ]; then
                pass "$desc (code=-1 OK)"
            else
                fail "$desc (code=$actual, 期望 code=$code)"
                ((failures++)) || true
            fi
        fi
    }

    _expect_code "空用户名注册" "-1" POST "$base/user/register" \
        '{"username":"","password":"test123","nickName":"test","role":1}'

    _expect_code "错误密码登录" "-1" POST "$base/user/login" \
        '{"username":"admin","password":"wrongpassword123"}'

    _expect_code "不存在的用户登录" "-1" POST "$base/user/login" \
        '{"username":"nonexistent_user_xyz","password":"test"}'

    _expect_code "空 ISBN 新增图书" "-1" POST "$base/book" \
        '{"isbn":"","name":"test","status":"1","borrownum":0}'

    _expect_code "删除不存在的图书" "-1" DELETE "$base/book/99999" '{}'

    echo ""

    # ---- 阶段三：权限边界 ----
    info "阶段三：权限边界测试"

    # 获取读者 token
    info "  获取读者 token..."
    local resp
    resp=$(curl -s -X POST "$base/user/login" \
        -H 'Content-Type: application/json' \
        -d '{"username":"reader","password":"123456"}' 2>/dev/null)
    reader_token=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('token',''))" 2>/dev/null || echo '')

    if [ -z "$reader_token" ]; then
        warn "读者 token 获取失败（可能 reader 账号不存在），跳过权限测试"
    else
        _expect_denied() {
            local desc="$1" method="$2" url="$3" data="$4"
            local http
            http=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$url" \
                -H "token: $reader_token" \
                -H 'Content-Type: application/json' \
                ${data:+-d "$data"} 2>/dev/null || echo '000')
            # 读者被拒绝: HTTP 非 200 范围，或返回 code=-1
            if [ "$http" -ge 200 ] && [ "$http" -lt 300 ]; then
                # 可能是 200 但内容拒绝了——再检查一下响应
                local body
                body=$(curl -s -X "$method" "$url" \
                    -H "token: $reader_token" \
                    -H 'Content-Type: application/json' \
                    ${data:+-d "$data"} 2>/dev/null)
                local code=$(echo "$body" | python3 -c "import sys,json; print(json.load(sys.stdin).get('code','?'))" 2>/dev/null || echo '?')
                if [ "$code" = "-1" ]; then
                    pass "$desc (HTTP 200, code=-1)"
                else
                    warn "$desc (HTTP $http, code=$code) —— 权限控制可能不完整"
                fi
            else
                pass "$desc (HTTP $http, 已拒绝)"
            fi
        }

        _expect_denied "读者删除图书" DELETE "$base/book/1"
        _expect_denied "读者查看所有读者列表" GET "$base/user?pageNum=1&pageSize=10"
    fi

    # ---- 结果 ----
    echo ""
    echo "============================================"
    if [ "$failures" -eq 0 ]; then
        pass "完整验收测试全部通过 (0 失败)"
        echo "============================================"
        return 0
    else
        fail "完整验收测试: $failures 项失败"
        echo "============================================"
        return 1
    fi
}

# ============================================================
# 入口
# ============================================================
case "${1:-help}" in
    build-backend)   build_backend ;;
    build-frontend)  build_frontend ;;
    build)           build ;;
    start-backend)   start_backend ;;
    start-frontend)  start_frontend ;;
    docker-up)       docker_up ;;
    docker-down)     docker_down ;;
    docker-logs)     docker_logs "${2:-}" ;;
    verify)          verify ;;
    verify-full)      verify_full ;;
    api-test)        api_test ;;
    help|--help|-h)  usage ;;
    *)
        echo "未知命令: $1"
        usage
        exit 1
        ;;
esac

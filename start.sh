#!/bin/bash
# 图书馆管理系统 - 启动脚本
# 用法: ./start.sh

PROJECT_DIR="/home/lijihao/Vue-Springboot-Library"
cd "$PROJECT_DIR"

echo "=== 启动后端 (端口 9090) ==="
java --add-opens java.base/java.lang.reflect=ALL-UNNAMED \
     --add-opens java.base/java.lang.invoke=ALL-UNNAMED \
     --add-opens java.base/java.lang=ALL-UNNAMED \
     --add-opens java.base/java.util=ALL-UNNAMED \
     -jar SpringBoot/target/demo-0.0.1-SNAPSHOT.jar &
BACKEND_PID=$!
sleep 5

if curl -s http://localhost:9090/dashboard > /dev/null 2>&1; then
    echo "后端启动成功: http://localhost:9090"
else
    echo "后端启动中，请稍候..."
fi

echo ""
echo "=== 启动前端 (端口 9876) ==="
cd vue
npm run serve &
FRONTEND_PID=$!
sleep 8

if curl -s http://localhost:9876 > /dev/null 2>&1; then
    echo "前端启动成功: http://localhost:9876"
else
    echo "前端启动中，请稍候..."
fi

echo ""
echo "=========================================="
echo "  访问地址: http://localhost:9876"
echo "  管理员: admin / admin"
echo "  后端PID: $BACKEND_PID  前端PID: $FRONTEND_PID"
echo "=========================================="

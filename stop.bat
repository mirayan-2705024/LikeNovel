@echo off
chcp 65001 >nul
echo ========================================
echo   LikeNovel 小说脉络分析系统
echo   停止脚本
echo ========================================
echo.

echo [1/2] 停止 Flask 后端服务...
taskkill /FI "WINDOWTITLE eq LikeNovel Backend*" /F >nul 2>&1
if errorlevel 1 (
    echo ⚠️  未找到运行中的 Flask 服务
) else (
    echo ✅ Flask 后端已停止
)

echo.
echo [2/2] 停止 Neo4j 数据库...
docker-compose down
if errorlevel 1 (
    echo ❌ Neo4j 停止失败
) else (
    echo ✅ Neo4j 已停止
)

echo.
echo ========================================
echo   ✅ 所有服务已停止
echo ========================================
echo.
pause

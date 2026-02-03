@echo off
chcp 65001 >nul
echo ========================================
echo   LikeNovel 小说脉络分析系统
echo   启动脚本
echo ========================================
echo.

REM 检查 Docker 是否运行
echo [1/4] 检查 Docker 服务...
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未运行，请先启动 Docker Desktop
    pause
    exit /b 1
)
echo ✅ Docker 服务正常

REM 启动 Neo4j
echo.
echo [2/4] 启动 Neo4j 数据库...
docker-compose up -d
if errorlevel 1 (
    echo ❌ Neo4j 启动失败
    pause
    exit /b 1
)
echo ✅ Neo4j 已启动

REM 等待 Neo4j 就绪
echo.
echo [3/4] 等待 Neo4j 就绪（约 10 秒）...
timeout /t 10 /nobreak >nul
echo ✅ Neo4j 就绪

REM 启动 Flask 后端
echo.
echo [4/4] 启动 Flask 后端服务...
start "LikeNovel Backend" cmd /k "python backend/app.py"
timeout /t 2 /nobreak >nul
echo ✅ Flask 后端已启动

echo.
echo ========================================
echo   🎉 启动完成！
echo ========================================
echo.
echo 📊 Neo4j 浏览器: http://localhost:7474
echo    用户名: neo4j
echo    密码: password
echo.
echo 🌐 Web 界面: http://localhost:5000
echo.
echo 💡 提示:
echo    - 在浏览器中打开 http://localhost:5000 使用 Web 界面
echo    - 上传 TXT 格式的小说文件进行分析
echo    - 关闭时请运行 stop.bat 停止服务
echo.
echo 按任意键打开 Web 界面...
pause >nul
start http://localhost:5000

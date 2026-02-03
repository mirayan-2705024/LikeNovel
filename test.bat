@echo off
chcp 65001 >nul
echo ========================================
echo   LikeNovel 系统测试
echo ========================================
echo.

echo [测试 1/5] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安装
    goto :end
) else (
    python --version
    echo ✅ Python 环境正常
)

echo.
echo [测试 2/5] 检查 Docker 服务...
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未运行
    goto :end
) else (
    echo ✅ Docker 服务正常
)

echo.
echo [测试 3/5] 检查项目文件...
if exist "backend\app.py" (
    echo ✅ backend\app.py 存在
) else (
    echo ❌ backend\app.py 不存在
)

if exist "frontend\index.html" (
    echo ✅ frontend\index.html 存在
) else (
    echo ❌ frontend\index.html 不存在
)

if exist "frontend\css\style.css" (
    echo ✅ frontend\css\style.css 存在
) else (
    echo ❌ frontend\css\style.css 不存在
)

if exist "frontend\js\app.js" (
    echo ✅ frontend\js\app.js 存在
) else (
    echo ❌ frontend\js\app.js 不存在
)

echo.
echo [测试 4/5] 检查 Neo4j 容器...
docker ps | findstr neo4j >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Neo4j 容器未运行
    echo    提示: 运行 docker-compose up -d 启动
) else (
    echo ✅ Neo4j 容器正在运行
)

echo.
echo [测试 5/5] 检查 Python 依赖...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo ❌ Flask 未安装
    echo    提示: 运行 pip install -r requirements.txt
) else (
    echo ✅ Flask 已安装
)

python -c "import neo4j" >nul 2>&1
if errorlevel 1 (
    echo ❌ neo4j 驱动未安装
) else (
    echo ✅ neo4j 驱动已安装
)

python -c "import jieba" >nul 2>&1
if errorlevel 1 (
    echo ❌ jieba 未安装
) else (
    echo ✅ jieba 已安装
)

echo.
echo ========================================
echo   测试完成
echo ========================================
echo.
echo 💡 下一步:
echo    1. 如果所有测试通过，运行 start.bat 启动服务
echo    2. 如果有测试失败，请根据提示修复问题
echo    3. 启动后访问 http://localhost:5000
echo.

:end
pause

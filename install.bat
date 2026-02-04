@echo off
chcp 65001 >nul
echo ========================================
echo   LikeNovel 依赖安装
echo ========================================
echo.

echo [1/2] 检查 Python 环境...
python --version
if errorlevel 1 (
    echo ❌ Python 未安装
    pause
    exit /b 1
)
echo ✅ Python 环境正常
echo.

echo [2/2] 安装 Python 依赖包...
echo 这可能需要几分钟，请耐心等待...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ❌ 依赖安装失败
    echo.
    echo 💡 可能的解决方法：
    echo    1. 检查网络连接
    echo    2. 尝试使用国内镜像源：
    echo       pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    echo    3. 升级 pip：python -m pip install --upgrade pip
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ✅ 依赖安装完成！
echo ========================================
echo.
echo 💡 下一步：
echo    运行 start.bat 启动服务
echo.
pause

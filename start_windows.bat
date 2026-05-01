@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   建筑物理 AI 世界模型 Demo
echo ========================================
echo.
echo [1] 正在检查环境...
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 安装依赖
echo [2] 正在安装依赖...
pip install -r requirements.txt -q

echo.
echo [3] 启动 Demo...
echo.
echo ========================================
echo   浏览器将自动打开
echo   地址: http://localhost:8501
echo ========================================
echo.

:: 启动 Streamlit
streamlit run app.py --server.port 8501 --browser.gatherUsageStats false

pause

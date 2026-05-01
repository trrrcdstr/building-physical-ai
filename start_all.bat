@echo off
chcp 65001 >nul 2>&1
title Physical AI - 建筑物理世界模型

echo ============================================
echo   Physical AI 世界模型 启动器 v2.0
echo ============================================
echo.

cd /d "%~dp0"
set ROOT=%CD%
set WEB=%ROOT%\web-app
set SRC=%ROOT%\src

echo [1/5] 终止旧服务...
for %%p in (3000 3001 3002 5000 5001 5002 5003 5004 8888) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%%p " ^| findstr "LISTENING"') do (
        echo   kill port %%p (PID %%a)
        taskkill /F /PID %%a >nul 2>&1
    )
)
echo   完成
echo.

echo [2/5] 启动后端服务...
:: 渲染图HTTP服务器 (8888)
start /min cmd /c "cd /d \"%SRC%\" ^&^& python -m http.server 8888 > nul 2>&1"
timeout /t 2 /nobreak >nul

:: NN推理服务 (5000)
start /min cmd /c "cd /d \"%SRC%\" ^&^& python neural_inference_server.py > nul 2>&1"
timeout /t 2 /nobreak >nul

:: 场景API服务 (5001)
start /min cmd /c "cd /d \"%SRC%\" ^&^& python four_layer_api.py > nul 2>&1"
timeout /t 2 /nobreak >nul

:: VLA指令分类 (5004)
start /min cmd /c "cd /d \"%SRC%\" ^&^& python vla_inference_server.py > nul 2>&1"
timeout /t 2 /nobreak >nul

echo   等待服务初始化...
timeout /t 5 /nobreak >nul

echo.
echo [3/5] 验证服务...
for %%p in (8888 5000 5001 5004) do (
    curl -s -o nul -w "  port %%p: %%{http_code}\n" http://127.0.0.1:%%p/ 2>nul
)
echo.

echo [4/5] 启动前端...
cd /d "%WEB%"
start cmd /k "npm run dev -- --port 3002"
timeout /t 5 /nobreak >nul

echo.
echo [5/5] 完成！
echo.
echo ============================================
echo   前端:    http://localhost:3002
echo   渲染图:  http://localhost:8888
echo   NN推理:  http://localhost:5000
echo   场景API: http://localhost:5001
echo   VLA:     http://localhost:5004
echo ============================================
echo.
echo 按任意键打开浏览器...
pause >nul
start http://localhost:3002
exit

# 一键启动脚本

Write-Host "🚀 启动建筑物理 AI 世界模型 Demo..." -ForegroundColor Green

# 启动后端
Write-Host "`n📡 启动 CAD 解析服务 (端口 8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$PSScriptRoot\cad-parser'; pip install -r requirements.txt; python -m uvicorn api.main:app --reload --port 8000"
)

# 等待后端启动
Start-Sleep -Seconds 3

# 启动前端
Write-Host "`n🎨 启动 Web 界面 (端口 3000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$PSScriptRoot\web-app'; npm install; npm run dev"
)

Write-Host @"

✅ 启动完成！

📱 访问地址:
   前端: http://localhost:3000
   后端: http://localhost:8000/docs

💡 提示: 两个终端窗口已打开，不要关闭

"@ -ForegroundColor Green

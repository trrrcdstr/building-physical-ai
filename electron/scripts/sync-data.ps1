# 同步桌面建筑数据到项目

$sourcePath = "$env:USERPROFILE\Desktop\建筑数据库"
$destPath = "$PSScriptRoot\..\data\raw"

Write-Host "同步建筑数据..." -ForegroundColor Green

# 创建目标目录
if (-not (Test-Path $destPath)) {
    New-Item -ItemType Directory -Path $destPath -Force | Out-Null
}

# 复制所有文件
Copy-Item -Path "$sourcePath\*" -Destination $destPath -Recurse -Force

Write-Host "✅ 数据同步完成！" -ForegroundColor Green
Write-Host "数据位置: $destPath" -ForegroundColor Yellow

# 显示文件统计
$fileCount = (Get-ChildItem -Path $destPath -Recurse -File).Count
Write-Host "共 $fileCount 个文件" -ForegroundColor Cyan

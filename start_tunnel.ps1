# -*- coding: utf-8 -*-
$cf = "$env:TEMP\cloudflared.exe"
$log = "$env:TEMP\cf_tunnel.log"
$urlfile = "$env:TEMP\cf_url.txt"

# 启动 cloudflared，输出写入日志文件
$proc = Start-Process -FilePath $cf -ArgumentList "tunnel","--url","http://localhost:3000" -PassThru -NoNewWindow -RedirectStandardOutput $log -RedirectStandardError $log
Write-Host "Cloudflared PID: $($proc.Id)"

# 等待URL出现
Start-Sleep 12

# 读取日志
$log_content = Get-Content $log -Raw -ErrorAction SilentlyContinue

# 提取URL
if ($log_content -match "https://[a-z0-9-]+\.trycloudflare\.com") {
    $pub_url = $Matches[0]
    Write-Host "URL: $pub_url"
    $pub_url | Out-File -FilePath $urlfile -Encoding utf8
    Write-Host "Saved to $urlfile"
} else {
    Write-Host "Log content:"
    Write-Host $log_content
}

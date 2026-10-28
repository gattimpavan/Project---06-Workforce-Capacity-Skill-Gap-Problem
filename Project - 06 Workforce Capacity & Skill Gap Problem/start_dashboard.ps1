# Launch Infosys Workforce Intelligence Dashboard
Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host "  INFOSYS WORKFORCE CAPACITY & SKILL GAP INTELLIGENCE SYSTEM" -ForegroundColor Yellow
Write-Host "  Project - 06: Autonomous Business Operations" -ForegroundColor Green
Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting Flask web server on port 5006..." -ForegroundColor White
Write-Host "Dashboard will be live at: http://localhost:5006" -ForegroundColor Green
Write-Host "Executive PDF Report available at: http://localhost:5006/api/download_report" -ForegroundColor Cyan
Write-Host ""

Set-Location -Path $PSScriptRoot
& "C:\Users\hp\AppData\Local\Programs\Orange\python.exe" app.py


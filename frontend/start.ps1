$ErrorActionPreference = 'Stop'

Write-Host "[Frontend] Installing dependencies" -ForegroundColor Cyan
npm install

Write-Host "[Frontend] Starting dev server on http://localhost:3000" -ForegroundColor Green
npm start

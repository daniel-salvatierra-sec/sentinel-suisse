# Fase 0 setup script
# Run: Set-ExecutionPolicy -Scope Process Bypass
#      .\scripts\setup-fase0.ps1

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "==> Sentinel Suisse - Fase 0 setup" -ForegroundColor Cyan

if (-not (Test-Path .git)) {
    git init -b main
}

git add -A
Write-Host ""
Write-Host "==> git status" -ForegroundColor Yellow
git status

$staged = git diff --cached --name-only
foreach ($file in $staged) {
    if ($file -eq ".env") {
        Write-Error ".env is staged - aborting. Check .gitignore."
    }
}

git commit -m "chore: Fase 0 - entorno seguro inicial"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Commit skipped (maybe nothing new or already committed)" -ForegroundColor DarkYellow
}

git branch -f feature/fase-0 2>$null

if (-not (Test-Path .venv)) {
    python -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\pip.exe install -r requirements-dev.txt
.\.venv\Scripts\pre-commit.exe install

Write-Host ""
Write-Host "==> Verification" -ForegroundColor Yellow
git check-ignore -v .env
Write-Host "ls-files .env (should be empty):"
git ls-files .env

if (Get-Command gh -ErrorAction SilentlyContinue) {
    gh --version
} else {
    Write-Host "gh CLI not found - create private repo manually on GitHub" -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "==> Fase 0 setup complete" -ForegroundColor Green

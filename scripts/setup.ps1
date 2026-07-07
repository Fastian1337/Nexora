# ============================================
# Nexora Platform — Initial Setup Script
# ============================================
# Usage: .\scripts\setup.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Nexora Platform — Initial Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "[1/6] Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found. Install Python 3.12+" -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  ✓ Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Node.js not found. Install Node.js 20+" -ForegroundColor Red
    exit 1
}

# Check Docker
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "  ✓ $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Docker not found. Install Docker Desktop" -ForegroundColor Red
    exit 1
}

# Setup backend
Write-Host ""
Write-Host "[2/6] Setting up backend..." -ForegroundColor Yellow

Push-Location backend

if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
}

& .venv\Scripts\Activate.ps1
pip install -r requirements/dev.txt -q
Write-Host "  ✓ Python dependencies installed" -ForegroundColor Green

Pop-Location

# Setup frontend
Write-Host ""
Write-Host "[3/6] Setting up frontend..." -ForegroundColor Yellow

Push-Location frontend
npm install --silent
Write-Host "  ✓ Node dependencies installed" -ForegroundColor Green
Pop-Location

# Copy environment files
Write-Host ""
Write-Host "[4/6] Setting up environment files..." -ForegroundColor Yellow

if (-not (Test-Path "backend\.env")) {
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "  ✓ backend/.env created from template" -ForegroundColor Green
} else {
    Write-Host "  - backend/.env already exists (skipped)" -ForegroundColor Gray
}

if (-not (Test-Path "frontend\.env")) {
    Copy-Item "frontend\.env.example" "frontend\.env"
    Write-Host "  ✓ frontend/.env created from template" -ForegroundColor Green
} else {
    Write-Host "  - frontend/.env already exists (skipped)" -ForegroundColor Gray
}

# Start Docker services
Write-Host ""
Write-Host "[5/6] Starting Docker services..." -ForegroundColor Yellow
docker compose -f docker/docker-compose.yml up -d postgres redis
Write-Host "  ✓ PostgreSQL and Redis started" -ForegroundColor Green

# Wait for services
Write-Host ""
Write-Host "[6/6] Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Edit backend/.env with your settings"
Write-Host "  2. Run: .\scripts\start-dev.ps1"
Write-Host ""

# ============================================
# Nexora Platform — Start Production environment
# ============================================
# Usage: .\scripts\start-prod.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Green
Write-Host "  Nexora Platform — Starting Prod Services" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if Docker is running
try {
    docker ps > $null
} catch {
    Write-Host "  ✗ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Verify environment configuration files
if (-not (Test-Path "backend\.env")) {
    Write-Host "  ✗ Production requires a valid backend\.env file." -ForegroundColor Red
    exit 1
}

Write-Host "Starting Docker containers in Production mode..." -ForegroundColor Yellow
docker compose -f docker/docker-compose.prod.yml up -d --build

Write-Host ""
Write-Host "✓ Production services started successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Endpoints:" -ForegroundColor Cyan
Write-Host "  - Public Access (Nginx): http://localhost (Port 80 / 443)"
Write-Host "  - n8n Automation:        http://localhost:5678"
Write-Host ""
Write-Host "Logs can be viewed with: docker compose -f docker/docker-compose.prod.yml logs -f" -ForegroundColor Gray
Write-Host ""

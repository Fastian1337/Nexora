# ============================================
# Nexora Platform — Start Development environment
# ============================================
# Usage: .\scripts\start-dev.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Nexora Platform — Starting Dev Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
try {
    docker ps > $null
} catch {
    Write-Host "  ✗ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Start local dependencies and application services via Compose
Write-Host "Starting Docker containers..." -ForegroundColor Yellow
docker compose -f docker/docker-compose.yml up -d

Write-Host ""
Write-Host "✓ Services started successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Endpoints:" -ForegroundColor Cyan
Write-Host "  - Frontend:         http://localhost:3000"
Write-Host "  - Backend API:      http://localhost:8000"
Write-Host "  - API Swagger UI:   http://localhost:8000/api/docs"
Write-Host "  - Nginx Reverse:    http://localhost:8080"
Write-Host "  - n8n Automation:   http://localhost:5678"
Write-Host ""
Write-Host "Logs can be viewed with: docker compose -f docker/docker-compose.yml logs -f" -ForegroundColor Gray
Write-Host ""

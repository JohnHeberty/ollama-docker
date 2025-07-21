#!/usr/bin/env pwsh

Write-Host "🚀 Iniciando Sistema Ollama OTIMIZADO..." -ForegroundColor Green

# Verificar recursos disponíveis
Write-Host "💻 Verificando recursos do sistema..." -ForegroundColor Cyan
$totalRAM = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
$cores = (Get-CimInstance Win32_ComputerSystem).NumberOfProcessors
Write-Host "   RAM Total: $totalRAM GB" -ForegroundColor Yellow
Write-Host "   CPU Cores: $cores" -ForegroundColor Yellow

# Configurar Docker para usar mais recursos
Write-Host "⚙️ Aplicando configurações de performance..." -ForegroundColor Cyan
$env:COMPOSE_DOCKER_CLI_BUILD = "1"
$env:DOCKER_BUILDKIT = "1"

# Parar containers antigos
Write-Host "🔄 Parando containers antigos..." -ForegroundColor Yellow
docker compose down --remove-orphans

# Rebuild com otimizações
Write-Host "🔨 Rebuilding com otimizações..." -ForegroundColor Yellow
docker compose build --no-cache

# Iniciar sistema otimizado
Write-Host "🚀 Iniciando sistema otimizado..." -ForegroundColor Green
docker compose up -d

# Aguardar inicialização
Write-Host "⏳ Aguardando sistema ficar pronto..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Verificar status
Write-Host "📊 Verificando performance..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
    Write-Host "✅ API funcionando: $($health.status)" -ForegroundColor Green
    
    $models = Invoke-RestMethod -Uri "http://localhost:8000/models" -Method GET  
    Write-Host "✅ Modelos disponíveis: $($models.models -join ', ')" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Sistema ainda inicializando..." -ForegroundColor Yellow
}

# Pre-carregar modelos para performance
Write-Host "🔥 Pre-carregando modelos para melhor performance..." -ForegroundColor Cyan
docker exec ollama-server ollama run tinyllama:latest "test" 2>$null
Write-Host "✅ TinyLLama pré-carregado" -ForegroundColor Green

Write-Host "`n🎉 Sistema OTIMIZADO iniciado!" -ForegroundColor Green
Write-Host "📍 FastAPI: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📊 Recursos alocados: 4 CPUs, 8GB RAM" -ForegroundColor Cyan
Write-Host "🛑 Parar: docker compose down" -ForegroundColor Cyan
#!/usr/bin/env pwsh
# Script para iniciar Ollama + FastAPI

Write-Host "🚀 Iniciando Sistema Ollama + FastAPI..." -ForegroundColor Green

# Verificar Docker
try {
    docker info | Out-Null
    Write-Host "✅ Docker está rodando" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker não está rodando" -ForegroundColor Red
    Write-Host "💡 Inicie o Docker Desktop primeiro" -ForegroundColor Yellow
    exit 1
}

# Subir containers
Write-Host "🔄 Iniciando containers..." -ForegroundColor Yellow
docker compose up -d

# Aguardar sistema ficar pronto
Write-Host "⏳ Aguardando sistema ficar pronto..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Verificar status
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 10
    if ($response.status -eq "saudavel") {
        Write-Host "✅ Sistema está pronto!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Sistema iniciado mas pode não estar totalmente pronto" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Sistema pode ainda estar inicializando..." -ForegroundColor Yellow
}

# Verificar se tem modelos
Write-Host "📋 Verificando modelos..." -ForegroundColor Cyan
try {
    $modelos = Invoke-RestMethod -Uri "http://localhost:8000/api/tags" -Method GET -TimeoutSec 10
    if ($modelos.models -and $modelos.models.Count -gt 0) {
        Write-Host "✅ Modelos encontrados:" -ForegroundColor Green
        foreach ($modelo in $modelos.models) {
            Write-Host "   - $($modelo.name)" -ForegroundColor White
        }
    } else {
        Write-Host "⚠️ Nenhum modelo encontrado" -ForegroundColor Yellow
        Write-Host "💡 Para instalar: docker exec ollama-server ollama pull tinyllama" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Não foi possível verificar modelos ainda" -ForegroundColor Yellow
}

Write-Host "`n🎉 Sistema iniciado!" -ForegroundColor Green
Write-Host "📍 FastAPI: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📍 Ollama: http://localhost:11434" -ForegroundColor Cyan
Write-Host "📚 Documentação: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🧪 Teste: docker exec -it fastapi-proxy python chat_client.py" -ForegroundColor Cyan
Write-Host "🛑 Parar: docker compose down" -ForegroundColor Cyan
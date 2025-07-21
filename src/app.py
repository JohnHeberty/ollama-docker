#!/usr/bin/env python3
"""
🔄 FastAPI Proxy para Ollama
Apenas transita informações entre cliente e modelo, sem interferir no prompt
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import requests
import logging
import os
import uvicorn

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração da aplicação
app = FastAPI(
    title="Ollama Proxy",
    description="Proxy transparente para comunicação com Ollama",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração do Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

# Modelos de entrada
class ChatRequest(BaseModel):
    modelo: str
    prompt: str
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.7
    top_k: Optional[int] = 40
    top_p: Optional[float] = 0.9
    max_tokens: Optional[int] = None
    timeout: Optional[int] = 300  # Novo parâmetro timeout (padrão 5 minutos)

class ChatResponse(BaseModel):
    sucesso: bool
    resposta: Optional[str] = None
    modelo_usado: str
    tempo_resposta: Optional[float] = None
    tokens_gerados: Optional[int] = None
    tokens_prompt: Optional[int] = None
    erro: Optional[str] = None

@app.get("/")
async def root():
    """Status da API proxy"""
    return {
        "status": "ativo",
        "servico": "Ollama Proxy",
        "versao": "1.0.1",  # Versão atualizada
        "ollama_url": OLLAMA_BASE_URL,
        "funcao": "Proxy transparente para Ollama com timeout configurável"
    }

@app.get("/health")
async def health_check():
    """Verifica se o Ollama está disponível"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            return {
                "status": "saudavel", 
                "ollama": "disponivel",
                "url": OLLAMA_BASE_URL
            }
        else:
            return {
                "status": "erro", 
                "ollama": "indisponivel",
                "codigo": response.status_code
            }
    except Exception as e:
        return {
            "status": "erro", 
            "ollama": "indisponivel", 
            "erro": str(e)
        }

@app.get("/models")
async def get_modelos_disponiveis():
    """Lista modelos disponíveis no Ollama"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            modelos = [model["name"] for model in data.get("models", [])]
            return {"modelos": modelos, "total": len(modelos)}
        else:
            return {"modelos": [], "erro": f"Status {response.status_code}"}
            
    except Exception as e:
        return {"modelos": [], "erro": str(e)}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Proxy direto para conversa com modelo
    Agora aceita timeout configurável
    """
    try:
        import time
        start_time = time.time()
        
        # Usar timeout do parâmetro ou padrão de 300s (5 min)
        timeout_value = request.timeout or 300
        
        logger.info(f"🤖 Repassando prompt para modelo: {request.modelo}")
        logger.info(f"📝 Prompt (primeiros 100 chars): {request.prompt[:100]}...")
        logger.info(f"⏱️ Timeout configurado: {timeout_value}s")
        
        # Preparar requisição exatamente como recebida
        ollama_request = {
            "model": request.modelo,
            "prompt": request.prompt,
            "stream": request.stream,
            "options": {
                "temperature": request.temperature,
                "top_k": request.top_k,
                "top_p": request.top_p
            }
        }
        
        # Adicionar max_tokens se especificado
        if request.max_tokens:
            ollama_request["options"]["num_predict"] = request.max_tokens
        
        # Enviar para Ollama usando timeout configurável
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=ollama_request,
            timeout=timeout_value  # Usar timeout do parâmetro
        )
        
        end_time = time.time()
        
        if response.status_code != 200:
            logger.error(f"❌ Erro do Ollama: {response.status_code}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Erro do Ollama: {response.text}"
            )
        
        # Processar resposta do Ollama
        ollama_response = response.json()
        
        return ChatResponse(
            sucesso=True,
            resposta=ollama_response.get("response", ""),
            modelo_usado=request.modelo,
            tempo_resposta=round(end_time - start_time, 2),
            tokens_gerados=ollama_response.get("eval_count", 0),
            tokens_prompt=ollama_response.get("prompt_eval_count", 0)
        )
        
    except requests.exceptions.Timeout:
        logger.error(f"⏱️ Timeout após {timeout_value}s na comunicação com Ollama")
        raise HTTPException(
            status_code=504,
            detail=f"Timeout: Modelo demorou mais que {timeout_value}s para responder"
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"🔌 Erro de conexão: {e}")
        raise HTTPException(
            status_code=503,
            detail="Erro de conexão com Ollama"
        )
    except Exception as e:
        logger.error(f"💥 Erro interno: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

@app.get("/modelos")
async def listar_modelos():
    """Lista modelos disponíveis (proxy direto)"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Erro ao listar modelos"
            )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Erro de conexão: {str(e)}"
        )

@app.post("/modelo/baixar")
async def baixar_modelo(modelo: dict):
    """Baixa um modelo (proxy direto)"""
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/pull",
            json=modelo,
            timeout=1800  # 30 minutos para download
        )
        if response.status_code == 200:
            return {"status": "sucesso", "modelo": modelo.get("name", "unknown")}
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Erro ao baixar modelo"
            )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Erro de conexão: {str(e)}"
        )

@app.api_route("/ollama/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_ollama(path: str, request: Request):
    """
    Proxy genérico para qualquer endpoint do Ollama
    Útil para funcionalidades futuras
    """
    try:
        # Pegar body da requisição
        body = await request.body()
        
        # Headers
        headers = dict(request.headers)
        headers.pop('host', None)  # Remove host para evitar conflitos
        
        # Fazer requisição proxy
        response = requests.request(
            method=request.method,
            url=f"{OLLAMA_BASE_URL}/api/{path}",
            data=body,
            headers=headers,
            timeout=300
        )
        
        return response.json() if response.content else {}
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Erro no proxy: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
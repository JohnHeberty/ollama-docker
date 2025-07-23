#!/usr/bin/env python3
"""
🔄 Cliente Python para comunicação com API Ollama
Versão atualizada com suporte a timeout configurável e configurações via .env
"""

import requests
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

# Carregar configurações do .env se existir
def load_env_config():
    """Carrega configurações do arquivo .env"""
    env_path = Path(__file__).parent / '.env'
    config = {}
    
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    
    return config

# Carregar configurações
ENV_CONFIG = load_env_config()

class ChatClient:
    
    def __init__(self, base_url: Optional[str] = None):
        # Usar URL do .env ou padrão
        self.base_url = (base_url or 
                        ENV_CONFIG.get('FASTAPI_URL', 'http://localhost:8000')).rstrip('/')
        
        self.session = requests.Session()
        
        # Desabilitar proxy para localhost
        self.session.proxies = {
            'http': None,
            'https': None
        }
        
        # Configurar trust_env para False para ignorar variáveis de ambiente de proxy
        self.session.trust_env = False
        
        # Debug info se habilitado
        if ENV_CONFIG.get('DEBUG', 'False').lower() == 'true':
            print(f"🔧 ChatClient inicializado com URL: {self.base_url}")
        
    def health_check(self) -> Dict[str, Any]:
        """Verifica status da API"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"erro": str(e)}
    
    def listar_modelos(self) -> list:
        """Lista modelos disponíveis"""
        try:
            response = self.session.get(f"{self.base_url}/models", timeout=15)
            response.raise_for_status()
            data = response.json()
            return data.get("modelos", [])
        except Exception as e:
            print(f"Erro ao listar modelos: {e}")
            return []
    
    def chat(self, mensagem: str, modelo: str = "tinyllama:latest", 
             stream: bool = False, timeout: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """
        Conversa com modelo - AGORA COM TIMEOUT CONFIGURÁVEL via .env
        
        Args:
            mensagem: Prompt para o modelo
            modelo: Nome do modelo a usar
            stream: Se usar streaming
            timeout: Timeout em segundos (usa DEFAULT_CHAT_TIMEOUT do .env se None)
            **kwargs: Parâmetros adicionais (temperature, top_p, etc.)
        """
        try:
            # Usar timeout do .env se não especificado
            if timeout is None:
                timeout = int(ENV_CONFIG.get('DEFAULT_CHAT_TIMEOUT', '300'))
            
            payload = {
                "modelo": modelo,
                "prompt": mensagem,
                "stream": stream,
                "timeout": timeout,
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
                "top_k": kwargs.get("top_k", 40),
                "max_tokens": kwargs.get("max_tokens")
            }
            
            # Usar timeout maior no cliente para acomodar o timeout do servidor
            client_timeout = timeout + 30  # 30s extra para comunicação
            
            response = self.session.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=client_timeout
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.Timeout:
            return {
                "erro": f"Timeout: Modelo não respondeu em {timeout}s",
                "codigo": "timeout"
            }
        except requests.exceptions.RequestException as e:
            return {
                "erro": f"Erro de conexão: {str(e)}",
                "codigo": "conexao"
            }
        except Exception as e:
            return {
                "erro": f"Erro inesperado: {str(e)}",
                "codigo": "interno"
            }
    
    def baixar_modelo(self, nome_modelo: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Baixa um modelo do repositório Ollama
        
        Args:
            nome_modelo: Nome do modelo (ex: 'qwen2:0.5b')
            timeout: Timeout para download (usa DEFAULT_DOWNLOAD_TIMEOUT do .env se None)
        """
        try:
            # Usar timeout do .env se não especificado
            if timeout is None:
                timeout = int(ENV_CONFIG.get('DEFAULT_DOWNLOAD_TIMEOUT', '1800'))
            
            print(f"🔄 Iniciando download do modelo: {nome_modelo}")
            print(f"⏱️ Timeout: {timeout}s ({timeout//60} min)")
            
            payload = {"name": nome_modelo}
            
            response = self.session.post(
                f"{self.base_url}/modelo/baixar",
                json=payload,
                timeout=timeout
            )
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Modelo {nome_modelo} baixado com sucesso!")
            return result
            
        except requests.exceptions.Timeout:
            return {
                "erro": f"Timeout no download após {timeout}s",
                "codigo": "timeout_download"
            }
        except Exception as e:
            return {
                "erro": f"Erro no download: {str(e)}",
                "codigo": "download_erro"
            }
    
    def listar_modelos_detalhado(self) -> Dict[str, Any]:
        """Lista modelos com detalhes completos"""
        try:
            response = self.session.get(f"{self.base_url}/modelos", timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"erro": str(e)}
    
    def get_ollama_info(self) -> Dict[str, Any]:
        """Informações diretas do servidor Ollama"""
        try:
            response = self.session.get(f"{self.base_url}/ollama/version", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"erro": str(e)}

# Função de conveniência para chat rápido
def chat_rapido(pergunta: str, modelo: str = "tinyllama:latest", 
                timeout: Optional[int] = None) -> str:
    """
    Função rápida para fazer uma pergunta
    
    Args:
        pergunta: Sua pergunta
        modelo: Modelo a usar
        timeout: Timeout em segundos (usa configuração do .env se None)
    
    Returns:
        Resposta como string simples
    """
    client = ChatClient()
    resultado = client.chat(pergunta, modelo=modelo, timeout=timeout)
    
    if "erro" in resultado:
        return f"ERRO: {resultado['erro']}"
    
    return resultado.get("resposta", "Sem resposta")

# Função para listar modelos recomendados do .env
def get_modelos_recomendados() -> list:
    """Retorna lista de modelos recomendados do .env"""
    modelos_str = ENV_CONFIG.get('RECOMMENDED_MODELS', 'tinyllama:latest')
    return [m.strip() for m in modelos_str.split(',')]

# # Exemplo de uso e demonstração
# if __name__ == "__main__":
#     print("🤖 Testando Cliente Ollama com Configurações .env")
#     print("=" * 60)
    
#     # Mostrar configurações carregadas
#     if ENV_CONFIG:
#         print("📋 Configurações carregadas do .env:")
#         for key, value in ENV_CONFIG.items():
#             if 'URL' in key or 'TIMEOUT' in key:
#                 print(f"   {key}: {value}")
    
#     # Criar cliente
#     client = ChatClient()
    
#     # Verificar status
#     print("\n1. Verificando status da API...")
#     status = client.health_check()
#     print(f"   Status: {status}")
    
#     # Listar modelos
#     print("\n2. Listando modelos disponíveis...")
#     modelos = client.listar_modelos()
#     print(f"   Modelos: {modelos}")
    
#     # Mostrar modelos recomendados
#     print("\n3. Modelos recomendados (.env):")
#     recomendados = get_modelos_recomendados()
#     for modelo in recomendados:
#         print(f"   - {modelo}")
    
#     if modelos:
#         # Teste rápido com configurações do .env
#         print("\n4. Teste rápido (usando timeout do .env)...")
#         resultado = client.chat(
#             "Responda em uma frase: o que é IA?", 
#             modelo=modelos[0]  # timeout vem do .env
#         )
        
#         if "erro" in resultado:
#             print(f"   ❌ {resultado['erro']}")
#         else:
#             print(f"   ✅ Resposta: {resultado.get('resposta', 'N/A')}")
#             print(f"   ⏱️ Tempo: {resultado.get('tempo_resposta', 'N/A')}s")
    
#     print("\n" + "=" * 60)
#     print("✅ Cliente pronto para uso com configurações .env!")

#!/usr/bin/env python3
"""
🔄 Cliente Python para comunicação com API Ollama
Versão atualizada com suporte a timeout configurável
"""

import requests
import json
from typing import Optional, Dict, Any

class ChatClient:
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        # Desabilitar proxy para localhost
        self.session.proxies = {
            'http': None,
            'https': None
        }
        
        # Configurar trust_env para False para ignorar variáveis de ambiente de proxy
        self.session.trust_env = False
        
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
             stream: bool = False, timeout: int = 300, **kwargs) -> Dict[str, Any]:
        """
        Conversa com modelo - AGORA COM TIMEOUT CONFIGURÁVEL
        
        Args:
            mensagem: Prompt para o modelo
            modelo: Nome do modelo a usar
            stream: Se usar streaming
            timeout: Timeout em segundos (padrão: 300s = 5min)
            **kwargs: Parâmetros adicionais (temperature, top_p, etc.)
        """
        try:
            payload = {
                "modelo": modelo,
                "prompt": mensagem,
                "stream": stream,
                "timeout": timeout,  # Novo parâmetro
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
    
    def baixar_modelo(self, nome_modelo: str, timeout: int = 1800) -> Dict[str, Any]:
        """
        Baixa um modelo do repositório Ollama
        
        Args:
            nome_modelo: Nome do modelo (ex: 'qwen2:0.5b')
            timeout: Timeout para download (padrão: 30min)
        """
        try:
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

# # Função de conveniência para chat rápido
# def chat_rapido(pergunta: str, modelo: str = "tinyllama:latest", 
#                 timeout: int = 120) -> str:
#     """
#     Função rápida para fazer uma pergunta
    
#     Args:
#         pergunta: Sua pergunta
#         modelo: Modelo a usar
#         timeout: Timeout em segundos (padrão: 2min)
    
#     Returns:
#         Resposta como string simples
#     """
#     client = ChatClient()
#     resultado = client.chat(pergunta, modelo=modelo, timeout=timeout)
    
#     if "erro" in resultado:
#         return f"ERRO: {resultado['erro']}"
    
#     return resultado.get("resposta", "Sem resposta")

# # Exemplo de uso e demonstração
# if __name__ == "__main__":
#     print("🤖 Testando Cliente Ollama com Timeout Configurável")
#     print("=" * 60)
    
#     # Criar cliente
#     client = ChatClient()
    
#     # Verificar status
#     print("1. Verificando status da API...")
#     status = client.health_check()
#     print(f"   Status: {status}")
    
#     # Listar modelos
#     print("\n2. Listando modelos disponíveis...")
#     modelos = client.listar_modelos()
#     print(f"   Modelos: {modelos}")
    
#     if modelos:
#         # Teste rápido com timeout curto
#         print("\n3. Teste rápido (timeout 60s)...")
#         resultado = client.chat(
#             "Responda em uma frase: o que é IA?", 
#             modelo=modelos[0],
#             timeout=60  # 1 minuto apenas
#         )
        
#         if "erro" in resultado:
#             print(f"   ❌ {resultado['erro']}")
#         else:
#             print(f"   ✅ Resposta: {resultado.get('resposta', 'N/A')}")
#             print(f"   ⏱️ Tempo: {resultado.get('tempo_resposta', 'N/A')}s")
    
#     print("\n" + "=" * 60)
#     print("✅ Cliente pronto para uso com timeout configurável!")


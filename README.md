# Ollama + FastAPI - Sistema LLM Local

Sistema para executar modelos de linguagem localmente usando Ollama em Docker com interface FastAPI, com
monitoramnto de desempenho e inicio automatico otimizado conforme hardware.

## Teste de Fogo

Os modelos recomendados neste `readme.md` foram testado em um notebook `tinkped` com `8Gb` de RAM sem placa de
video com suporte para `CUDA`, e seu o processador é um `Ryzen 5 7535U`.

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Seu Cliente   │───▶│  FastAPI Proxy  │───▶│     Ollama      │
│  (Prompts)      │    │  (Transparente) │    │   (Modelos)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
      ▲                           │                       │
      │                           │                       │
      └───────────────────────────┴───────────────────────┘
                    Resposta sem modificação
```

### Fluxo de Dados:
1. **Cliente** envia prompt personalizado
2. **FastAPI Proxy** repassa exatamente como recebido
3. **Ollama** processa com o modelo escolhido
4. **Resposta** retorna sem modificações
5. **Cliente** recebe resposta pura do modelo

## 📁 Estrutura

```
ollama-docker/
├── service/                    # 🐳 Serviço Docker
│   ├── app.py                  # FastAPI proxy para Ollama
│   ├── compose.yml             # Orquestração Docker
│   ├── Dockerfile              # Build da API
│   ├── entrypoint.sh           # Script de inicialização Ollama
│   ├── requirements.txt        # Dependências Python do serviço
│   ├── start.ps1               # Script básico PowerShell
│   └── start_V2.ps1            # Script otimizado PowerShell
│
├── src/                        # 📊 Ferramentas Externas
│   ├── chat_client.py          # Cliente Python para Jupyter
│   ├── example.ipynb           # Notebook com exemplos
│   ├── pdf_processor.py        # Processador de PDFs
│   └── data/                   # Dados do projeto
│       ├── external/           # PDFs originais
│       ├── interim/            # Dados processados
│       └── processed/          # Resultados finais
│
├── LICENSE                     # Licença MIT
└── README.md                   # Esta documentação
```

## 🎯 Funcionalidades

### 🐳 Serviço Docker (`/service/`)
- **Ollama Server**: Modelos LLM rodando em container isolado
- **FastAPI Proxy**: API RESTful para comunicação externa
- **Auto-configuração**: Scripts PowerShell para inicialização automática
- **Recursos Otimizados**: Configuração dinâmica baseada no hardware

### 📊 Ferramentas Externas (`/src/`)
- **Cliente Python**: Biblioteca para integração com Jupyter/Python
- **Processador PDF**: Extração de dados de documentos ferroviários
- **Notebook Interativo**: Exemplos práticos de uso
- **Gerenciamento de Dados**: Estrutura organizada para projetos

## 🚀 Setup Rápido

### Pré-requisitos
- Docker Desktop instalado e rodando
- Python 3.8+ (para usar ferramentas em `/src/`)
- PowerShell (para scripts automatizados)

#### ⚙️ Configuração .env (OBRIGATÓRIA)

O arquivo `src/.env` é **essencial** para o funcionamento correto:

```bash
# Configuração padrão (src/.env)
FASTAPI_URL=http://localhost:8000
OLLAMA_URL=http://localhost:11434
DEFAULT_CHAT_TIMEOUT=300
DEFAULT_DOWNLOAD_TIMEOUT=1800
RECOMMENDED_MODELS=tinyllama:latest,qwen2:1.5b,phi:latest
PDF_MAX_PAGES=100
PDF_TIMEOUT=600
DEBUG=True
VERBOSE_LOGGING=True
```

### 1. Configurar ferramentas Python
```bash
cd src
pip install -r requirements.txt
copy .env.example .env
```

### 2. Iniciar serviços Docker
```powershell
.\service\start_V2.ps1
```

### 3. Testar
```bash
curl http://localhost:8000/health
```

## 🌐 Endpoints da API (Porta 8000)
### Configurado no chat_client.py

| Método HTTP | Endpoint              | Descrição                                   |
|-------------|-----------------------|---------------------------------------------|
| `GET`       | `/`                   | Status geral da API                         |
| `GET`       | `/health`             | Verificação detalhada do sistema            |
| `GET`       | `/models`             | Lista modelos disponíveis (formato simplificado) |
| `GET`       | `/modelos`            | Lista modelos com detalhes completos        |
| `POST`      | `/chat`               | Conversa com contexto e timeout configurável |
| `POST`      | `/modelo/baixar`      | Download de novos modelos                   |
| `GET`       | `/docs`               | Documentação automática FastAPI             |
| `GET`       | `/ollama/{path}`      | Proxy genérico para qualquer endpoint Ollama |

### Modelos Recomendados (Baixo Consumo < 4GB RAM)
```bash
# Dentro do container Ollama
docker exec ollama-server ollama pull tinyllama:latest     # 637MB - Ultra rápido
docker exec ollama-server ollama pull tinydolphin:latest   # 637MB - Ultra rápido
docker exec ollama-server ollama pull qwen2:1.5b           # 934MB - Equilibrado  
docker exec ollama-server ollama pull deepcoder:1.5b       # 
docker exec ollama-server ollama pull qwen3:1.7b           # 1.6GB - Microsoft

# Via API (programaticamente)
client.baixar_modelo("tinyllama:latest")
client.baixar_modelo("tinydolphin:latest")
client.baixar_modelo("qwen2:1.5b")
client.baixar_modelo("deepcoder:1.5b")
client.baixar_modelo("qwen3:1.7b ")
```

### Escolha modelo por Caso de Uso:
- **Testes rápidos**: `tinyllama:latest`
- **Análises precisas**: `qwen2:1.5b` ou `qwen3:1.7b` 
- **Geração de código**: `deepcoder:1.5b`
- **Conversação**: `tinydolphin:latest`

### Métricas de Performance
```python
# Tempo de resposta e tokens
resultado = client.chat("Teste", timeout=60)
print(f"Tempo: {resultado['tempo_resposta']}s")
print(f"Tokens gerados: {resultado['tokens_gerados']}")
print(f"Tokens do prompt: {resultado['tokens_prompt']}")
```

## 💻 Como Usar

### No Jupyter Notebook
```python
import sys
sys.path.append('../src')
from chat_client import ChatClient

client = ChatClient()  # Usa configurações do .env automaticamente

# Chat simples
resposta = client.chat("Explique IA em uma frase")
print(resposta['resposta'])

# Listar modelos
modelos = client.listar_modelos()
print(modelos)

# Baixar modelo
client.baixar_modelo("tinyllama:latest")
```

### Processamento de PDFs
```python
from pdf_processor import PDFReader

pdf = PDFReader("data/external/documento.pdf")
texto = pdf.extract_text_optimized()

# Analisar com LLM
resultado = client.chat(f"Resuma este texto: {texto[:2000]}")
```

## ⚙️ Configuração (.env)

Arquivo `src/.env` com configurações principais:
```bash
FASTAPI_URL=http://localhost:8000
DEFAULT_CHAT_TIMEOUT=300
DEFAULT_DOWNLOAD_TIMEOUT=1800
RECOMMENDED_MODELS=tinyllama:latest,qwen2:1.5b
```

## ❓ Resolução de Problemas

### Container não inicia
```bash
# Verificar logs
docker-compose logs

# Recriar containers
docker-compose down --volumes
docker-compose up --build -d

# Verificar recursos
docker stats
```

### API não responde
```bash
# Verificar portas
netstat -an | findstr :8000
netstat -an | findstr :11434

# Testar conectividade
curl -v http://localhost:8000/health
curl -v http://localhost:11434/api/tags
```

### Modelo lento ou timeout
```python
# Aumentar timeout
client.chat("pergunta", timeout=600)  # 10 minutos

# Usar modelo mais leve
client.chat("pergunta", modelo="tinyllama:latest")

# Verificar recursos do sistema
docker stats ollama-server
```

## 🚦 Comandos Úteis

### Docker
```bash
# Parar tudo
docker-compose down

# Reiniciar serviços
docker-compose restart

# Ver recursos em tempo real
docker stats

# Limpar sistema
docker system prune -a
```

### Python/Jupyter
```python
# Recarregar módulo modificado
import importlib
importlib.reload(chat_client)

# Verificar versão das dependências  
import requests
print(requests.__version__)
```

## 🔧 Instalação de Modelos

```bash
# Via container direto (recomendado)
docker exec ollama-server ollama pull tinyllama

# Via API FastAPI (programaticamente)
curl -X POST http://localhost:8000/modelo/baixar \
  -H "Content-Type: application/json" \
  -d '{"name": "tinyllama:latest"}'

# Verificar modelos instalados
curl http://localhost:8000/models

# Modelos recomendados para baixo consumo
docker exec ollama-server ollama pull tinyllama:latest
docker exec ollama-server ollama pull qwen2:1.5b
docker exec ollama-server ollama pull deepcoder:1.5b
docker exec ollama-server ollama pull qwen3:1.7b
```

## 📊 Monitoramento

### Verificar Status do Sistema
```bash
# Status geral
curl http://localhost:8000/

# Status detalhado  
curl http://localhost:8000/health

# Modelos disponíveis
curl http://localhost:8000/models
```

### Logs dos Containers
```bash
# Logs do Ollama
docker logs ollama-server

# Logs do FastAPI
docker logs fastapi-proxy

# Logs em tempo real
docker compose logs -f
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📞 Suporte e Links

- **Documentação API**: http://localhost:8000/docs (quando rodando)
- **GitHub Issues**: Para reportar bugs e sugestões
- **Ollama Official**: https://ollama.ai/
- **FastAPI Docs**: https://fastapi.tiangolo.com/

## 📝 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.
---

## 🎉 Agradecimentos

- [Ollama](https://ollama.ai/) - Framework para LLMs locais
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [Docker](https://www.docker.com/) - Plataforma de containerização
resultado = client.baixar_modelo("qwen2:1.5b", timeout=1800)
print(resultado)

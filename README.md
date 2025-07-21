# Ollama + FastAPI - Sistema Simplificado

Sistema completo para rodar modelos LLM localmente com Ollama e FastAPI como proxy transparente.

## 🎯 Funcionalidades

- **Ollama**: Servidor LLM rodando em container
- **FastAPI Proxy**: API que atua como proxy transparente para o Ollama
- **Prompts Externos**: Controle total dos prompts fora da aplicação
- **Conversa Direta**: Comunicação direta com os modelos via API

## 🚀 Início Rápido

### Pré-requisitos
- Docker e Docker Compose
- Python 3.8+ (para o cliente)

### Uma única linha para subir tudo:
```bash
# Do diretório raiz
cd src && docker compose up -d

# Ou diretamente no diretório src
docker compose up -d
```

### Com script automático:
```powershell
# Windows PowerShell - Script básico
.\src\start.ps1

# Windows PowerShell - Script otimizado (recomendado)
.\src\start_V2.ps1
```

### Alternativa via diretório src:
```bash
cd src
docker compose up -d
```

## 📁 Estrutura do Projeto

```
ollama-docker/
├── src/
│   ├── Dockerfile              # Container da API FastAPI
│   ├── compose.yml             # Orquestração dos serviços Docker
│   ├── app.py                  # FastAPI Proxy (transparente)
│   ├── requirements.txt        # Dependências Python
│   ├── start.ps1               # Script básico de inicialização
│   ├── start_V2.ps1           # Script otimizado com recursos
│   └── test.json              # Arquivo para testes
├── chat_client.py              # Cliente Python para teste
├── example.ipynb              # Notebook Jupyter com exemplos
├── LICENSE                    # Licença MIT
├── .gitignore                 # Arquivos ignorados pelo Git
└── README.md                  # Este arquivo
```

## 🌐 Endpoints

### FastAPI Proxy (Porta 8000)
- `GET /` - Status geral da API
- `GET /health` - Status detalhado do sistema
- `GET /models` - Listar modelos disponíveis (formato simplificado)
- `GET /modelos` - Listar modelos disponíveis (formato completo)  
- `POST /chat` - Conversa com contexto e timeout configurável
- `POST /modelo/baixar` - Baixar novos modelos
- `GET /docs` - Documentação automática FastAPI
- `API /ollama/{path}` - Proxy genérico para qualquer endpoint Ollama

### Ollama Direto (Porta 11434)
- Acesso direto ao Ollama (opcional)

## 💻 Uso via Cliente Python

```python
from chat_client import ChatClient

# Inicializar cliente
client = ChatClient()

# Verificar status
status = client.health_check()
print(status)

# Listar modelos
modelos = client.listar_modelos()
print(modelos)

# Conversar com timeout configurável
resposta = client.chat(
    "Explique o que é transporte ferroviário",
    modelo="tinyllama:latest",
    timeout=300  # 5 minutos
)
print(resposta)

# Baixar um modelo
resultado = client.baixar_modelo("qwen2:1.5b", timeout=1800)
print(resultado)
```

## 🎨 Prompts Externos - Filosofia

O sistema foi projetado para **não ter lógica de prompts internos**. Toda a inteligência de prompt fica **fora** da aplicação:

```python
# Seus prompts personalizados
prompt_extracao = f"""
Você é um especialista em análise de dados de transporte.
Extraia TODOS os dados do texto: {texto}
Retorne em formato JSON estruturado.
"""

# Envio via proxy (sem modificação) com timeout
resultado = client.chat(
    mensagem=prompt_extracao,
    modelo="tinyllama:latest",
    temperature=0.1,
    timeout=600  # 10 minutos
)
```

### Vantagens:
- ✅ **Controle total** sobre prompts
- ✅ **Flexibilidade máxima** para diferentes casos de uso
- ✅ **FastAPI só transita** dados sem modificar
- ✅ **Facilidade de manutenção** e teste
- ✅ **Reutilização** de prompts em diferentes contextos
- ✅ **Timeout configurável** por requisição

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
docker exec ollama-server ollama pull stablelm2:1.6b
```

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

## ❓ Resolução de Problemas

### Container não inicia
```bash
# Verificar logs
cd src
docker compose logs

# Reiniciar sistema
docker compose down && docker compose up -d
```

### Modelo não responde ou timeout
```bash
# Verificar se modelo existe
curl http://localhost:8000/models

# Baixar modelo se necessário
docker exec ollama-server ollama pull tinyllama:latest

# Verificar recursos do sistema (use script otimizado)
.\src\start_V2.ps1
```

### API não responde
```bash
# Verificar se containers estão rodando
docker ps

# Verificar saúde da API
curl http://localhost:8000/health

# Verificar logs do FastAPI
docker logs fastapi-proxy
```

### Para parar tudo
```bash
cd src
docker compose down
```

### Otimização de Performance
```bash
# Use o script otimizado que aloca recursos adequadamente
.\src\start_V2.ps1

# Pre-carrega modelos em memória para melhor performance
# Configure variáveis de ambiente no compose.yml para sua máquina
```

## 🎯 Casos de Uso

### 1. Extração de Dados com Timeout
```python
prompt = f"Extraia dados técnicos do texto: {texto_ferroviario}"
dados = client.chat(
    mensagem=prompt, 
    modelo="tinyllama:latest", 
    temperature=0.1,
    timeout=300
)
```

### 2. Análise de Viabilidade
```python
prompt = f"Analise viabilidade financeira: {dados_projeto}"
analise = client.chat(
    mensagem=prompt, 
    modelo="qwen2:1.5b", 
    temperature=0.3,
    timeout=600
)
```

### 3. Geração de Relatórios
```python
prompt = f"Gere relatório executivo: {dados_completos}"
relatorio = client.chat(
    mensagem=prompt, 
    modelo="tinyllama:latest", 
    temperature=0.2,
    timeout=900
)
```

## 📓 Exemplo Interativo com Jupyter

O projeto inclui um notebook Jupyter (`example.ipynb`) com exemplos práticos:

- ✅ Configuração automática do cliente
- ✅ Verificação de modelos disponíveis  
- ✅ Download automático de modelos recomendados
- ✅ Exemplos de análise de transporte ferroviário
- ✅ Extração de dados estruturados para JSON
- ✅ Testes com diferentes modelos de IA

```bash
# Abrir o notebook
jupyter notebook example.ipynb
```

## ⚙️ Configurações Avançadas

### Otimização de Recursos
O arquivo `compose.yml` inclui configurações para otimizar uso de CPU e RAM:

```yaml
environment:
  - OLLAMA_NUM_PARALLEL=6          # 6 processos paralelos
  - OLLAMA_MAX_LOADED_MODELS=2     # 2 modelos em memória
  - OLLAMA_FLASH_ATTENTION=1       # Otimização de atenção
  - OLLAMA_NUM_THREAD=6            # 6 threads
```

### Scripts de Inicialização
- **start.ps1**: Script básico para inicialização
- **start_V2.ps1**: Script otimizado com verificação de recursos e pré-carregamento

### Cliente Python Avançado
O `chat_client.py` oferece:
- ✅ Timeout configurável por requisição
- ✅ Download automático de modelos
- ✅ Tratamento de erros robusto
- ✅ Informações detalhadas de performance

## 🤖 Modelos Recomendados

### Modelos de Baixo Consumo (< 3GB RAM)
```bash
# Ultra-leve e rápido (1.1B parâmetros)
docker exec ollama-server ollama pull tinyllama:latest

# Equilibrio entre velocidade e qualidade (1.5B parâmetros)  
docker exec ollama-server ollama pull qwen2:1.5b
docker exec ollama-server ollama pull qwen3:1.7b

# Especializado em código
docker exec ollama-server ollama pull deepcoder:1.5b

# Modelo estável
docker exec ollama-server ollama pull stablelm2:1.6b

# Modelo conversacional
docker exec ollama-server ollama pull tinydolphin:latest
```

### Escolha por Caso de Uso:
- **Testes rápidos**: `tinyllama:latest`
- **Análises precisas**: `qwen2:1.5b` ou `qwen3:1.7b` 
- **Geração de código**: `deepcoder:1.5b`
- **Conversação**: `tinydolphin:latest`

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

## 📝 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/JohnHeberty/ollama-docker/issues)
- **Documentação FastAPI**: http://localhost:8000/docs (quando rodando)
- **Ollama Official**: https://ollama.ai/

## 🎉 Agradecimentos

- [Ollama](https://ollama.ai/) - Framework para LLMs locais
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno e rápido
- [Docker](https://www.docker.com/) - Plataforma de containerização

FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema para performance
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivo de dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicação e scripts
COPY app.py .
COPY chat_client.py .
COPY exemplo_prompts_externos.py .

# Expor porta
EXPOSE 8000

# Comando otimizado para iniciar a aplicação
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
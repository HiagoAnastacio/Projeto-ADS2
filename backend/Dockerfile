# ---- Base Image ----
FROM python:3.10-slim

# ---- Setup Environment ----
# Evita que o Python gere arquivos .pyc
ENV PYTHONDONTWRITEBYTECODE 1
# Evita que o Python faça buffer do stdout/stderr (logs em tempo real)
ENV PYTHONUNBUFFERED 1

# Diretório de trabalho no container
WORKDIR /app

# ---- Dependencies ----
# Copia o arquivo de requisitos primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instala as dependências
# --no-cache-dir reduz o tamanho da imagem final
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copy Code ----
# Copia o restante do código para o workdir /app
COPY . .

# ---- Run ----
# Expõe a porta 8000 (apenas indicativo, quem publica é o docker-compose)
EXPOSE 8000

# Comando de inicialização
# "app.main:app" é o caminho para a instância do FastAPI
# "--host 0.0.0.0" permite acesso externo ao container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

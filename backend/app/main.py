# Ponto de entrada da aplicação FastAPI e Controller da arquitetura MVC.
from fastapi import FastAPI
from routes import base_data, stats_data, specific_stats

app = FastAPI()

# Inclui os roteadores das rotas, cada um responsável por um grupo de endpoints.
app.include_router(base_data.router, prefix="/api")      # Rotas de dados base (heróis, mapas, etc.)
app.include_router(stats_data.router, prefix="/api")      # Rotas de estatísticas gerais
app.include_router(specific_stats.router, prefix="/api")  # Rotas de estatísticas específicas

@app.get("/")
async def root():
    # Endpoint raiz retorna mensagem de status da API
    return {"message": "API de Análise de Metagame de Overwatch - Online"}
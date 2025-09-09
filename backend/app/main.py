# Ponto de entrada da aplicação FastAPI e Controller da arquitetura MVC.
from fastapi import FastAPI
from routes import specific_stats, stats_data, base_data
from routes import route_get, route_post, route_update, route_delete

app = FastAPI()

# Inclui os roteadores das rotas, cada um responsável por um grupo de endpoints.
app.include_router(base_data.router, prefix="/api")       # Rotas de dados base (heróis, mapas, etc.)
app.include_router(stats_data.router, prefix="/api")      # Rotas de estatísticas gerais
app.include_router(specific_stats.router, prefix="/api")  # Rotas de estatísticas específicas

app.include_router(route_get.router, prefix="/api")       # Rotas de consulta de dados
app.include_router(route_post.router, prefix="/api")      # Rotas de inserção de dados
app.include_router(route_update.router, prefix="/api")    # Rotas de atualização de dados
app.include_router(route_delete.router, prefix="/api")    # Rotas de exclusão de dados

@app.get("/")
async def STATUS():
    # Endpoint raiz retorna mensagem de status da API
    return {"message": "API de Análise de Metagame de Overwatch - Online"}
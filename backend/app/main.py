# Ponto de entrada da aplicação FastAPI e Controller da arquitetura MVC.
from fastapi import FastAPI
from routes import route_get, route_post, route_update, route_delete
from routes.docs import route_schema_models

app = FastAPI()

app.include_router(route_get.router, prefix="/api")            # Rotas de consulta de dados
app.include_router(route_post.router, prefix="/api")           # Rotas de inserção de dados
app.include_router(route_update.router, prefix="/api")         # Rotas de atualização de dados
app.include_router(route_delete.router, prefix="/api")         # Rotas de exclusão de dados

app.include_router(route_schema_models.router, prefix="/api")  # Rotas de documentação dos modelos

@app.get("/", tags=["Status of API"])
async def STATUS():
    # Endpoint raiz retorna mensagem de status da API
    return {"message": "API de Análise de Metagame de Overwatch - Online"}
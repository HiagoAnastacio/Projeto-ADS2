# FLUXO E A LÓGICA:
# 1. O arquivo principal inicializa o FastAPI.
# 2. As configurações de segurança (Lifespan para Redis/Rate Limit e CORS) foram importadas, mas estão DESATIVADAS no main.py.
# 3. Ele atua como um 'coletor' de rotas, incluindo todos os módulos CRUD (`route_*.py`) sob o prefixo `/api`, 
#    direcionando o tráfego e garantindo a modularidade da aplicação.

from fastapi import FastAPI # Importa o framework principal. Razão: Base da API.
from routes import route_get, route_post, route_update, route_delete # Importa as rotas CRUD. Razão: Modularidade do código.
from routes.docs import route_schema_models # Importa rota de documentação/exemplo. Razão: Utilidade para o Swagger/Testes.

# Importa a lógica de segurança do seu repositório (DESATIVADA no código abaixo)
from app.security.ratelimt_and_CORS_security import lifespan_security, configure_middlewares 

# 1. Inicialização do FastAPI:
# Variável 'app' (Escopo Global/Módulo): Instância principal do FastAPI, dura o ciclo de vida da aplicação.
# app = FastAPI(lifespan=lifespan_security)   # CÓDIGO ORIGINAL (COMENTADO)
# O parâmetro 'lifespan' (ciclo de vida) foi removido, DESATIVANDO o Rate Limiting e o CORS no arquivo 'main'.
app = FastAPI()                               

# 2. Configuração de Middlewares (DESATIVADA)
# A chamada a 'configure_middlewares(app)' foi removida, DESATIVANDO o CORS globalmente.
# configure_middlewares(app)     

# 3. Inclusão de Rotas Modulares
# As rotas são incluídas aqui. O tráfego para `/api/*` será direcionado aos módulos importados.
app.include_router(route_get.router, prefix="/api")            
app.include_router(route_post.router, prefix="/api")           
app.include_router(route_update.router, prefix="/api")         
app.include_router(route_delete.router, prefix="/api")  
       
app.include_router(route_schema_models.router, prefix="/api")
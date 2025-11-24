# =======================================================================================
# ARQUIVO PRINCIPAL DA APLICAÇÃO (PONTO DE ENTRADA) - REFATORADO (RESTful)
# =======================================================================================
# ARQUITETURA:
# 1. Adiciona um prefixo de versionamento `/api/v1` para todas as rotas de dados.
# 2. O resto da lógica de lifespan (agendador) permanece a mesma.
# =======================================================================================

from fastapi import FastAPI
import logging
from dotenv import load_dotenv

# --- Importações da Aplicação ---\
from routes import route_post, route_update, route_delete, routes_get
from routes.req_body_exemple_route import route_schema_models
from routes.analytic_routes import route_analysis
from app.security.ratelimt_and_CORS_security import configure_middlewares
from services.data_uploader import scheduler_lifespan

# Carrega as variáveis de ambiente (ex: DB_HOST) do .env
# Deve ser chamado antes de importar módulos que usam as variáveis (ex: db_manager)
load_dotenv()

# --- Configuração do Logger Principal ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Inicialização da Aplicação FastAPI com Lifespan ---
app = FastAPI(lifespan=scheduler_lifespan)
logger.info("Instância principal do FastAPI criada com lifespan do agendador.")

# --- Configuração de Middlewares ---
configure_middlewares(app)
logger.info("Middlewares configurados.")

# --- Inclusão de Roteadores (COM VERSIONAMENTO v1) ---
# Todas as rotas de dados agora respondem sob "/API/V1-DATA" 
API_PREFIX = "/API/V1-DATA" 

app.include_router(routes_get.router, prefix=API_PREFIX)
app.include_router(route_post.router, prefix=API_PREFIX)
app.include_router(route_update.router, prefix=API_PREFIX)
app.include_router(route_delete.router, prefix=API_PREFIX)

# A rota de documentação dos modelos (útil para o frontend)
app.include_router(route_schema_models.router, prefix=API_PREFIX)

logger.info(f"Roteadores de dados genéricos incluídos com prefixo: {API_PREFIX}")

# Registra o novo roteador de análise
app.include_router(route_analysis.router, prefix=API_PREFIX)
logger.info(f"Roteadores de Análise e Dimensão incluídos com prefixo: {API_PREFIX}")
# --- FIM DO REGISTRO ---

# --- Ponto de Entrada para Uvicorn ---
if __name__ == "__main__":
    import uvicorn
    # A porta 8000 é padrão do Uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
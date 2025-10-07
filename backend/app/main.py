from fastapi import FastAPI
from routes import route_get, route_post, route_update, route_delete
from routes.docs import route_schema_models
from app.security.ratelimt_and_CORS_security import lifespan_security, configure_middlewares
import logging # Importa o módulo de logging

# --- LOGGING ADICIONADO ---
# Configuração básica do logging para a aplicação.
# Define o nível mínimo de log (INFO) e o formato da mensagem.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
logger = logging.getLogger(__name__)


# 1. Inicialização do FastAPI
# O lifespan ainda está desativado, então o log do Rate Limiting não aparecerá.
app = FastAPI()

# 2. Configuração de Middlewares (ATIVADA)
# Esta chamada irá executar a lógica em `configure_middlewares` e, consequentemente, gerar o log do CORS.
configure_middlewares(app)
logger.info("Middlewares configurados.")

# 3. Inclusão de Rotas Modulares
app.include_router(route_get.router, prefix="/api")
app.include_router(route_post.router, prefix="/api")
app.include_router(route_update.router, prefix="/api")
app.include_router(route_delete.router, prefix="/api")
app.include_router(route_schema_models.router, prefix="/api")
logger.info("Todas as rotas foram incluídas.")
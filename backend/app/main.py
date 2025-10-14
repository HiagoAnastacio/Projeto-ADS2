# =======================================================================================
# ARQUIVO PRINCIPAL DA APLICAÇÃO (PONTO DE ENTRADA)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Cria a instância principal do FastAPI, definindo o `lifespan`.
# 2. O `lifespan` (`scheduler_lifespan`) é um gerenciador de contexto que é executado
#    na inicialização e no encerramento da API. Nós o usamos para iniciar o serviço
#    do `data_uploader` em uma tarefa de fundo assíncrona.
# 3. Inclui todos os roteadores dos módulos de rotas e configura os middlewares (CORS).
#
# RAZÃO DE EXISTIR: Ser o único ponto de partida para a aplicação. Ao rodar este
# arquivo com Uvicorn, tanto a API RESTful quanto o serviço de agendamento em
# segundo plano são iniciados e gerenciados juntos.
# =======================================================================================

from fastapi import FastAPI
import logging

# --- Importações da Aplicação ---
from routes import route_get, route_post, route_update, route_delete
from routes.docs import route_schema_models
from app.security.ratelimt_and_CORS_security import configure_middlewares
# Importa o gerenciador de ciclo de vida do nosso serviço de agendamento.
from services.data_uploader import scheduler_lifespan

# --- Configuração do Logger Principal ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Inicialização da Aplicação FastAPI com Lifespan ---
# O parâmetro `lifespan` instrui o FastAPI a executar o código dentro do
# `scheduler_lifespan` durante a inicialização e o encerramento da API.
app = FastAPI(lifespan=scheduler_lifespan)
logger.info("Instância principal do FastAPI criada com lifespan do agendador.")

# --- Configuração de Middlewares ---
configure_middlewares(app)
logger.info("Middlewares configurados.")

# --- Inclusão de Roteadores ---
app.include_router(route_get.router, prefix="/api")
app.include_router(route_post.router, prefix="/api")
app.include_router(route_update.router, prefix="/api")
app.include_router(route_delete.router, prefix="/api")
app.include_router(route_schema_models.router, prefix="/api")
logger.info("Todos os roteadores foram incluídos com o prefixo /api.")
# =======================================================================================
# ARQUIVO PRINCIPAL DA APLICAÇÃO (PONTO DE ENTRADA)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Este é o primeiro arquivo executado pelo servidor Uvicorn.
# 2. Ele cria a instância principal do FastAPI, que é a base de toda a API.
# 3. Importa e "inclui" os roteadores dos outros arquivos (`route_*.py`), agindo como um
#    centralizador que organiza todos os endpoints da aplicação sob o prefixo `/api`.
# 4. Chama as funções de configuração de segurança (como o CORS) durante a inicialização.
#
# RAZÃO DE EXISTIR: Orquestrar a montagem da aplicação FastAPI, unindo todas as
# partes (rotas, segurança, configuração) em um único objeto que pode ser servido.
# =======================================================================================

# Importa a classe principal do framework FastAPI.
from fastapi import FastAPI
# Importa os objetos 'router' de cada módulo de rotas para modularização.
from routes import route_get, route_post, route_update, route_delete
from routes.docs import route_schema_models
# Importa as funções de configuração de segurança.
from app.security.ratelimt_and_CORS_security import lifespan_security, configure_middlewares
# Importa o módulo de logging para registrar eventos da aplicação.
import logging

# --- Configuração do Logger Principal ---
# Razão: Garante que os logs de inicialização e de outros módulos sejam exibidos de forma consistente.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Inicialização da Aplicação FastAPI ---
# Variável 'app' (Escopo Global/Módulo): É a instância principal da aplicação.
# O Uvicorn a utiliza para receber e processar todas as requisições HTTP.
# O 'lifespan' está comentado, desativando o Rate Limiting por enquanto.
app = FastAPI()
logger.info("Instância principal do FastAPI criada.")

# --- Configuração de Middlewares ---
# Razão: Aplicar configurações de segurança que interceptam todas as requisições.
# Esta chamada executa a lógica em `configure_middlewares` para ativar o CORS.
configure_middlewares(app)

# --- Inclusão de Roteadores ---
# Razão: Manter o código organizado. Em vez de definir todas as rotas neste arquivo,
# nós as agrupamos em módulos e as incluímos aqui.
app.include_router(route_get.router, prefix="/api")
app.include_router(route_post.router, prefix="/api")
app.include_router(route_update.router, prefix="/api")
app.include_router(route_delete.router, prefix="/api")
app.include_router(route_schema_models.router, prefix="/api")
logger.info("Todos os roteadores foram incluídos com o prefixo /api.")
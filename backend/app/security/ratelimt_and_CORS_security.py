from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging # Importa o módulo de logging

# Cria uma instância do logger para este módulo.
logger = logging.getLogger(__name__)

# -----------------------------------------------------\
# 1. Gerenciamento do Ciclo de Vida (Lifespan)
# -----------------------------------------------------\

@asynccontextmanager
async def lifespan_security(app: FastAPI) -> AsyncGenerator[None, None]:
    """Função Lifespan que agora loga seu status de execução."""
    
    # --- LOGGING ADICIONADO ---
    # Informa que a função foi chamada e qual o status da funcionalidade.
    logger.info("Estágio de Segurança: Função Lifespan executada (Rate Limiting: DESATIVADO).")
    
    # O código de conexão com o Redis e FastAPILimiter.init() ficaria aqui.
    # Se fosse ativado, o log acima seria alterado para:
    # logger.info("Estágio de Segurança: Serviço de Rate Limiting inicializado com Redis.")
    
    yield
    
    # Código de encerramento iria aqui.

# -----------------------------------------------------\
# 2. Configuração de Middlewares (CORS)
# -----------------------------------------------------\

def configure_middlewares(app: FastAPI):
    """Aplica o Middleware de CORS e loga o status da configuração."""
    
    origins = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # --- LOGGING ADICIONADO ---
    # Informa que o CORS foi configurado e está ativo.
    logger.info("Estágio de Segurança: Middleware de CORS ATIVADO.")
    # Um log de nível DEBUG é útil para ver detalhes sem poluir a saída padrão.
    logger.debug(f"Origens permitidas para o CORS: {origins}")
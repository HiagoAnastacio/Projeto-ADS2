# =======================================================================================
# MÓDULO DE CONFIGURAÇÃO DE SEGURANÇA
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Define a função `configure_middlewares`, que aplica o middleware de CORS à aplicação.
#    Isto adiciona cabeçalhos HTTP às respostas do servidor, instruindo o navegador
#    a permitir requisições de origens específicas (ex: http://localhost:3000).
# 2. Define a função `lifespan_security`, um gerenciador de ciclo de vida que (quando ativado)
#    inicializaria e encerraria serviços como a conexão com o Redis para o Rate Limiting.
#
# RAZÃO DE EXISTIR: Centralizar toda a configuração de segurança da aplicação, como
# CORS e Rate Limiting, em um único local, seguindo o princípio de Separação de Responsabilidades.
# =======================================================================================

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

# Cria uma instância do logger para este módulo.
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------------
# 1. GERENCIAMENTO DO CICLO DE VIDA (LIFESPAN) - STATUS: DESATIVADO
# ----------------------------------------------------------------------------------
@asynccontextmanager
async def lifespan_security(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Função Lifespan que (quando ativada) gerencia o ciclo de vida de serviços
    de segurança, como o Rate Limiter.
    """
    # Log para indicar o status da funcionalidade.
    logger.info("Estágio de Segurança: Função Lifespan executada (Rate Limiting: DESATIVADO).")
    # O código de inicialização do Rate Limiter (conexão com Redis) iria aqui.
    
    yield # Ponto onde a aplicação FastAPI roda.
    
    # O código de encerramento (fechar conexão com Redis) iria no bloco finally.

# ----------------------------------------------------------------------------------
# 2. CONFIGURAÇÃO DE MIDDLEWARES (CORS) - STATUS: ATIVADO
# ----------------------------------------------------------------------------------
def configure_middlewares(app: FastAPI):
    """Aplica o Middleware de CORS à aplicação."""
    
    # Variável 'origins' (Escopo de Função): Lista de endereços (origens) que têm
    # permissão para fazer requisições à nossa API. Essencial para o desenvolvimento frontend.
    origins = [
        "http://localhost",
        "http://localhost:3000",  # Porta padrão do Create React App
        "http://localhost:5173",  # Porta padrão do Vite (React moderno)
        "http://localhost:8080",
    ]

    # Adiciona o middleware de CORS à instância principal do FastAPI.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,         # Permite apenas as origens da lista.
        allow_credentials=True,      # Permite o envio de cookies.
        allow_methods=["*"],         # Permite todos os métodos HTTP (GET, POST, etc.).
        allow_headers=["*"],         # Permite todos os cabeçalhos HTTP.
    )
    
    # Log para confirmar a ativação e configuração do CORS.
    logger.info("Estágio de Segurança: Middleware de CORS ATIVADO.")
    logger.debug(f"Origens permitidas para o CORS: {origins}")
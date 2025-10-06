# FLUXO E A LÓGICA:
# O arquivo define funções de segurança (Rate Limiting e CORS), essenciais para proteger a API de sobrecarga (DoS) e acessos não autorizados.
# Ambas as funções estão comentadas ou desativadas, o que significa que o Rate Limiting e o CORS não estão ativos na API atualmente.
# A razão de existir: Concentrar a lógica de infraestrutura e segurança em um único lugar (modularidade).

from fastapi import FastAPI # Razão: Necessário para tipagem e para aplicar o Middleware.
from starlette.middleware.cors import CORSMiddleware # Razão: Classe que implementa o CORS.
from contextlib import asynccontextmanager # Razão: Essencial para gerenciar o ciclo de vida (startup/shutdown).
# import redis.asyncio as redis # Razão: Driver assíncrono para o Redis (banco de dados em memória para o Rate Limiter).
# from fastapi_limiter import FastAPILimiter # Razão: Biblioteca que usa Redis para limitar requisições.
from typing import AsyncGenerator # Razão: Tipagem para a função lifespan.

# -----------------------------------------------------\
# 1. Gerenciamento do Ciclo de Vida (Lifespan)
#    STATUS: DESATIVADO
# -----------------------------------------------------\

@asynccontextmanager
async def lifespan_security(app: FastAPI) -> AsyncGenerator[None, None]:
    """Função Lifespan DESATIVADA temporariamente. Quando ativada, inicializa serviços como o Rate Limiter/Redis."""
    
    # O código de conexão com o Redis e FastAPILimiter.init() ficaria aqui (STARTUP).
    # Conecta ao Redis
    #     redis_connection = redis.from_url("redis://localhost:6379", encoding="utf-8", decode_responses=True)
    #     await FastAPILimiter.init(redis_connection)
    #     print("Serviço de Rate Limiting inicializado.")
    
    yield # Marca o ponto onde a aplicação principal é executada.

    # O código de FastAPILimiter.close() ficaria aqui (SHUTDOWN).
    # finally:
    #     # CÓDIGO DE SHUTDOWN (TEMPORARIAMENTE COMENTADO)
    #     await FastAPILimiter.close()
    #     print("Conexão com o Redis encerrada.")


# -----------------------------------------------------\
# 2. Configuração de Middlewares (CORS)
#    STATUS: DESATIVADO
# -----------------------------------------------------\

def configure_middlewares(app: FastAPI):
    """Aplica todos os Middlewares de segurança e utilidade à aplicação. O CORS está temporariamente DESATIVADO."""
    
    # O código que aplicaria o CORSMiddleware ficaria aqui.
      # CÓDIGO DO CORS (TEMPORARIAMENTE COMENTADO)
    # origins = ["*"] # ATENÇÃO: Em produção, substitua por domínios específicos.
    # app.add_middleware(
    #     CORSMiddleware,
    #     allow_origins=origins,
    #     allow_credentials=True,
    #     allow_methods=["*"],
    #     allow_headers=["*"],
    # )

    # Variáveis 'origins' (Escopo de Função): Define a lista de domínios permitidos, usada apenas durante a execução desta função.
    pass # Função vazia, pois o código de CORS está comentado.
# =======================================================================================
# MÓDULO GERENCIADOR DE CONEXÃO DA API (POOL)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Cria um Pool de Conexões MySQL (`db_pool`) quando a API é iniciada.
# 2. Define a dependência `get_db_connection` que o FastAPI usará para injetar
#    uma conexão do pool em cada rota.
# 3. Define a função `execute_api_query` que roda SQL usando a conexão injetada.
#
# RAZÃO DE EXISTIR: Otimizar a performance da API. As rotas não devem abrir/fechar
# conexões (como os scripts de ETL fazem). Elas devem "pegar emprestado" conexões
# já abertas do pool, o que é ordens de magnitude mais rápido.
# =======================================================================================

import mysql.connector.pooling
from mysql.connector import Error
from mysql.connector.connection import MySQLConnection
from fastapi import HTTPException, Depends
import logging
import os
from dotenv import load_dotenv

# --- NOVAS IMPORTAÇÕES PARA TYPE HINTING ---
from typing import Generator, Any

# Carrega variáveis de ambiente (necessário se rodado fora do main.py)
load_dotenv() 

# Pega o logger principal
logger = logging.getLogger(__name__)

# --- Criação do Pool de Conexões ---
try:
    db_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="api_pool",
        pool_size=10,  # Ajuste conforme necessário
        pool_reset_session=True,
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PSWD"),
        database=os.getenv("DB_NAME")
    )
    logger.info("Pool de conexões MySQL 'api_pool' criado com sucesso.")
except Error as e:
    logger.critical(f"FALHA CRÍTICA: Não foi possível criar o pool de conexões MySQL. Erro: {e}")
    # Se o pool falhar, a aplicação não pode continuar.
    raise e

# --- Dependência do FastAPI (COM TYPE HINT CORRIGIDO) ---
def get_db_connection() -> Generator[MySQLConnection, Any, None]:
    """
    Dependência do FastAPI que obtém uma conexão do pool.
    O 'yield' entrega a conexão para a rota e o 'finally' garante
    que ela seja devolvida ao pool, mesmo se a rota falhar.
    
    Type Hint: Generator[YieldType, SendType, ReturnType]
    - Yields: MySQLConnection
    - Receives (Send): Any
    - Returns: None
    """
    connection = None
    try:
        connection = db_pool.get_connection()
        yield connection
    except Error as e:
        logger.error(f"Erro ao obter conexão do pool: {e}")
        raise HTTPException(status_code=503, detail="Serviço indisponível. Não foi possível conectar ao banco de dados.")
    finally:
        if connection and connection.is_connected():
            connection.close()  # Devolve a conexão ao pool

# --- Executor de Query da API ---
def execute_api_query(connection: MySQLConnection, sql: str, params: tuple = None) -> list | int:
    """
    Executa uma query SQL usando uma conexão FORNECIDA (do pool).
    Não gerencia o ciclo de vida da conexão (connect/disconnect).
    """
    cursor = None # Define o cursor como None fora do try
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql, params)
        
        if sql.strip().lower().startswith("select"):
            result = cursor.fetchall()
            return result
        else:
            # Para INSERT, UPDATE, DELETE
            connection.commit()
            return cursor.lastrowid if sql.strip().lower().startswith("insert") else cursor.rowcount
            
    except Error as e:
        logger.error(f"Erro ao executar query da API: {e}")
        # Reverte a transação em caso de erro de escrita
        if not sql.strip().lower().startswith("select"):
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {e}")
    finally:
        if cursor:
            cursor.close()
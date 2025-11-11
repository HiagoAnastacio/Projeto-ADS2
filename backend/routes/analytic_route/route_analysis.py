# =======================================================================================
# MÓDULO DE ROTA - ANÁLISE GENÉRICA (v2)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Define um endpoint `POST /API/V1-DATA/analysis/query` que aceita um corpo JSON.
# 2. O corpo JSON (definido pelo modelo `AnalysisQuery`) permite ao frontend
#    especificar a tabela, filtros (igualdade, 'IN') e intervalo de datas.
# 3. (SEGURANÇA) Valida `table_name` contra a `ALLOWED_GET_TABLES`.
# 4. (SEGURANÇA) Constrói a query SQL dinamicamente, mas de forma SEGURA,
#    validando os nomes das colunas (chaves do dict de filtros) contra uma
#    lista de colunas seguras, prevenindo SQL Injection.
# 5. Executa a query e retorna os dados históricos ou filtrados.
#
# RAZÃO DE EXISTIR: Implementar a rota analítica genérica solicitada,
# de forma segura, performática e flexível.
# =======================================================================================

import logging
from fastapi import APIRouter, HTTPException, Depends, Body
from mysql.connector.connection import MySQLConnection
from typing import List, Dict, Any, Tuple
from datetime import datetime

# Importa o pool de conexões e o executor da API
from utils.db_manager import get_db_connection, execute_api_query
# Importa o modelo Pydantic para o corpo da requisição
from model.analytic_model import AnalysisQuery
# Importa as listas de segurança
from app.security.db_whitelist_security import ALLOWED_GET_TABLES, ALLOWED_FILTER_COLUMNS

logger = logging.getLogger(__name__)
router = APIRouter()

# --- COLUNAS SEGURAS PERMITIDAS PARA FILTRO ---
# (SEGURANÇA) Isso impede que o usuário tente filtrar por colunas
# não indexadas ou injetar SQL (ex: "1=1; --")

@router.post("/ANALYSIS/QUERY", tags=["Analysis & Dashboards"])
async def run_analysis_query(
    query: AnalysisQuery = Body(...), # Recebe o corpo JSON
    db_conn: MySQLConnection = Depends(get_db_connection)
) -> List[Dict[str, Any]]:
    """
    Executa uma consulta analítica genérica e segura em uma tabela de fato ou view.
    
    Permite filtrar por igualdade, listas ('IN') e intervalos de datas.
    """
    
    # 1. VALIDAÇÃO DE SEGURANÇA (NOME DA TABELA)
    if query.table_name not in ALLOWED_GET_TABLES:
        raise HTTPException(status_code=400, detail=f"O recurso '{query.table_name}' não é válido ou permitido para consulta.")
    
    # Lista para armazenar as cláusulas WHERE
    where_clauses: List[str] = []
    # Lista para armazenar os parâmetros (para prevenir SQL Injection)
    params: List[Any] = []

    # 2. CONSTRUÇÃO DINÂMICA DA QUERY (SEGURA)
    
    # --- Filtros de Igualdade (=) ---
    if query.filters_equal:
        for column, value in query.filters_equal.items():
            # (SEGURANÇA) Verifica se a coluna está na nossa whitelist
            if column not in ALLOWED_FILTER_COLUMNS:
                logger.warning(f"Tentativa de filtro em coluna não permitida: {column}")
                continue # Pula este filtro
            
            where_clauses.append(f"`{column}` = %s")
            params.append(value)

    # --- Filtros de Lista (IN) ---
    if query.filters_in:
        for column, value_list in query.filters_in.items():
            if column not in ALLOWED_FILTER_COLUMNS:
                logger.warning(f"Tentativa de filtro 'IN' em coluna não permitida: {column}")
                continue
            
            if not value_list: # Se a lista estiver vazia, pula
                continue

            # Cria os placeholders (%s, %s, %s)
            placeholders = ", ".join(["%s"] * len(value_list))
            where_clauses.append(f"`{column}` IN ({placeholders})")
            params.extend(value_list) # Adiciona todos os valores da lista aos parâmetros

    # --- Filtros de Data (BETWEEN) ---
    if query.start_date:
        where_clauses.append("`date_of_the_data` >= %s")
        params.append(query.start_date)
    if query.end_date:
        where_clauses.append("`date_of_the_data` <= %s")
        params.append(query.end_date)
        
    # --- Montagem da Query Final ---
    sql = f"SELECT * FROM `{query.table_name}`"
    
    if where_clauses:
        # Junta todas as condições com "AND"
        sql += " WHERE " + " AND ".join(where_clauses)
    
    # Adiciona ORDER BY (útil para histórico) e LIMIT (proteção)
    # Tenta ordenar pela data se existir, senão pelo ID da tabela
    id_column = f"{query.table_name}_id"
    sql += f" ORDER BY `date_of_the_data` DESC"
    sql += f" LIMIT %s"
    params.append(query.limit)

    logger.info(f"Executando Query Analítica: {sql}")
    
    # 3. EXECUÇÃO
    try:
        result = execute_api_query(db_conn, sql, tuple(params))
        
        if result is None:
            return []
            
        return result
        
    except Exception as e:
        logger.error(f"Erro ao executar query analítica: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar a consulta: {e}")
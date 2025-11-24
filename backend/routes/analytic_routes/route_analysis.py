# =======================================================================================
# MÓDULO DE ROTA - ANÁLISE GENÉRICA (v2.2 - Centralized Security)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Recebe o JSON (AnalysisQuery).
# 2. Valida tabela, filtros e ordenação usando as listas do 'db_whitelist_security'.
# 3. Constrói e executa a query SQL segura com ORDER BY dinâmico.
# =======================================================================================

import logging
from fastapi import APIRouter, HTTPException, Depends, Body
from mysql.connector.connection import MySQLConnection
from typing import List, Dict, Any

# Importa o pool de conexões e o executor da API
from utils.db_manager import get_db_connection, execute_api_query
# Importa o modelo Pydantic
from model.analytic_model import AnalysisQuery
# Importa as listas de segurança (AGORA INCLUINDO SORT)
from app.security.db_whitelist_security import (
    ALLOWED_GET_TABLES, 
    ALLOWED_FILTER_COLUMNS, 
    ALLOWED_SORT_COLUMNS
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/ANALYSIS/QUERY", tags=["Analysis & Dashboards"])
async def run_analysis_query(
    query: AnalysisQuery = Body(...), 
    db_conn: MySQLConnection = Depends(get_db_connection)
) -> List[Dict[str, Any]]:
    """
    Executa uma consulta analítica genérica.
    Suporta filtros (=, IN), Range de Datas e Ordenação Dinâmica.
    """
    
    # 1. VALIDAÇÃO DE SEGURANÇA (TABELA)
    if query.table_name not in ALLOWED_GET_TABLES:
        raise HTTPException(status_code=400, detail=f"O recurso '{query.table_name}' não é válido ou permitido para consulta.")
    
    where_clauses: List[str] = []
    params: List[Any] = []

    # 2. CONSTRUÇÃO DOS FILTROS (WHERE)
    
    # --- Filtros de Igualdade ---
    if query.filters_equal:
        for column, value in query.filters_equal.items():
            if column not in ALLOWED_FILTER_COLUMNS:
                logger.warning(f"Tentativa de filtro em coluna não permitida: {column}")
                continue 
            
            where_clauses.append(f"`{column}` = %s")
            params.append(value)

    # --- Filtros de Lista (IN) ---
    if query.filters_in:
        for column, value_list in query.filters_in.items():
            if column not in ALLOWED_FILTER_COLUMNS:
                logger.warning(f"Tentativa de filtro 'IN' em coluna não permitida: {column}")
                continue
            
            if not value_list: 
                continue

            placeholders = ", ".join(["%s"] * len(value_list))
            where_clauses.append(f"`{column}` IN ({placeholders})")
            params.extend(value_list)

    # --- Filtros de Data ---
    if query.start_date:
        where_clauses.append("`date_of_the_data` >= %s")
        params.append(query.start_date)
    if query.end_date:
        where_clauses.append("`date_of_the_data` <= %s")
        params.append(query.end_date)
        
    # --- Montagem Inicial do SQL ---
    sql = f"SELECT * FROM `{query.table_name}`"
    
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)
    
    # 3. ORDENAÇÃO DINÂMICA (Centralizada)
    sort_column = "date_of_the_data" # Padrão
    
    # Verifica se a coluna de ordenação está na Whitelist Central
    if query.order_by and query.order_by in ALLOWED_SORT_COLUMNS:
        sort_column = query.order_by
    elif query.order_by:
        logger.warning(f"Tentativa de ordenação inválida ignorada: {query.order_by}")

    sql += f" ORDER BY `{sort_column}` DESC"
    sql += f" LIMIT %s"
    params.append(query.limit)

    logger.info(f"Executando Query Analítica: {sql}")
    
    # 4. EXECUÇÃO
    try:
        result = execute_api_query(db_conn, sql, tuple(params))
        return result if result is not None else []
        
    except Exception as e:
        logger.error(f"Erro ao executar query analítica: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")
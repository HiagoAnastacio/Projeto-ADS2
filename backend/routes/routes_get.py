# =======================================================================================
# MÓDULO DE ROTA - GET (LEITURA) - REFATORADO (RESTful & Pool & Restrição de ID)
# =======================================================================================
# ARQUITETURA:
# ... (descrição anterior) ...
# 4. (NOVO) A rota `get_single_item` agora verifica se a tabela solicitada
#    pertence à lista de tabelas com ID simples (`EDITABLE_TABLES`), restringindo
#    seu uso para evitar erros com chaves compostas ou views.
# =======================================================================================

from fastapi import APIRouter, HTTPException, Path, Depends
from mysql.connector.connection import MySQLConnection
# --- Importa AMBAS as listas de segurança ---
from app.security.table_whitelist_security import ALLOWED_GET_TABLES, EDITABLE_TABLES
from utils.db_manager import get_db_connection, execute_api_query

router = APIRouter()

@router.get("/{table_name}", tags=["Resource List Retrieval"])
async def get_resource_list(
    table_name: str = Path(..., description="Nome do recurso (tabela ou view) para consulta"),
    db_conn: MySQLConnection = Depends(get_db_connection)
):
    """
    Busca uma lista de todos os registros de um recurso autorizado (tabela ou view).
    Funciona para todas as tabelas e views em ALLOWED_GET_TABLES.

    COMO USAR:
    ... (docstring anterior) ...
    """
    if table_name not in ALLOWED_GET_TABLES:
        raise HTTPException(status_code=400, detail=f"O recurso '{table_name}' não é válido ou permitido para consulta.")

    try:
        sql = f"SELECT * FROM `{table_name}`"
        result = execute_api_query(connection=db_conn, sql=sql)

        # Retorna lista vazia se não houver resultados, em vez de 404.
        return result if result is not None else []
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao buscar lista de '{table_name}': {e}")


@router.get("/{table_name}/{item_id}", tags=["Resource List Retrieval"])
async def get_single_item(
    table_name: str = Path(..., description="Nome do recurso (APENAS tabelas de dimensão simples)"),
    item_id: int = Path(..., description="ID do item a ser buscado (ex: hero_id, map_id)"),
    db_conn: MySQLConnection = Depends(get_db_connection)
):
    """
    Busca um único registro de um recurso pelo seu ID.

    **IMPORTANTE:** Esta rota funciona APENAS para tabelas de dimensão simples
    que possuem uma chave primária única no formato `{table_name}_id`
    (ex: hero, map, role, rank, game_mode).
    **NÃO FUNCIONA** para tabelas de fato (com chave composta) ou views complexas.

    COMO USAR:
    ... (docstring anterior) ...
    """

    # --- NOVA VERIFICAÇÃO ---
    # Verifica se a tabela está na lista de tabelas editáveis (que têm ID simples)
    if table_name not in EDITABLE_TABLES:
         raise HTTPException(
             status_code=400, # Bad Request, pois a operação não é suportada para esta tabela/view
             detail=f"A busca por ID único não é suportada para o recurso '{table_name}'. Use a rota de listagem ou uma rota específica, se disponível."
         )
    # --- FIM DA VERIFICAÇÃO ---

    # A verificação ALLOWED_GET_TABLES não é estritamente necessária aqui,
    # pois EDITABLE_TABLES é um subconjunto, mas mantê-la adiciona uma camada.
    if table_name not in ALLOWED_GET_TABLES:
         raise HTTPException(status_code=403, detail=f"Acesso negado para o recurso '{table_name}'.")

    id_column = f"{table_name}_id"

    # Validação simples do nome da coluna (já existente)
    if not id_column.replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="Nome de tabela inválido gerou nome de coluna inválido.")

    try:
        sql = f"SELECT * FROM `{table_name}` WHERE `{id_column}` = %s"
        result = execute_api_query(connection=db_conn, sql=sql, params=(item_id,))

        if not result:
            raise HTTPException(status_code=404, detail=f"Item com ID {item_id} não encontrado em '{table_name}'.")

        return result[0]
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao buscar item {item_id} de '{table_name}': {e}")
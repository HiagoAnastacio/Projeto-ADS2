# =======================================================================================
# MÓDULO DE ROTA - DELETE (EXCLUSÃO) - REFATORADO (RESTful & Pool)
# =======================================================================================
# ARQUITETURA:
# 1. Rota RESTful (ex: DELETE /{table_name}/{item_id}).
# 2. Usa `Depends(get_db_connection)` para injetar uma conexão do Pool.
# 3. Usa `execute_api_query` (do db_manager).
# =======================================================================================

from fastapi import APIRouter, HTTPException, Path, Depends
from mysql.connector.connection import MySQLConnection
from app.security.db_whitelist_security import ALLOWED_WRITE_TABLES
from utils.db_manager import get_db_connection, execute_api_query

router = APIRouter()

@router.delete("/{table_name}/{item_id}", tags=["Resource Exclusion"])
async def delete_resource(
    table_name: str = Path(..., description="Nome do recurso (tabela) para exclusão"),
    item_id: int = Path(..., description="ID do item a ser excluído"),
    db_conn: MySQLConnection = Depends(get_db_connection)
):
    """
    Exclui um registro existente de uma tabela autorizada pelo seu ID.

    COMO USAR:
    
    1.  **Endpoint:** `DELETE /api/v1/{table_name}/{item_id}`
        -   Ex: `DELETE /api/v1/hero/5` (Exclui o herói com hero_id = 5)
    
    2.  **Segurança e Validação:**
        -   A rota falhará com `403 Forbidden` se a tabela não estiver na `ALLOWED_WRITE_TABLES`.
        -   A rota assume que a coluna de ID segue o padrão `{table_name}_id`.

    3.  **Resposta (Sucesso 200):**
        -   Retorna uma mensagem de sucesso e o número de linhas afetadas.
    
    4.  **Resposta (Erro 404):**
        -   Retorna `404 Not Found` se o `item_id` não for encontrado (nenhuma linha afetada).
    """

    if table_name not in ALLOWED_WRITE_TABLES:
        raise HTTPException(status_code=403, detail=f"O recurso '{table_name}' não permite exclusão via API.")

    id_column = f"{table_name}_id"

    try:
        sql = f"DELETE FROM `{table_name}` WHERE `{id_column}` = %s"
        rows_affected = execute_api_query(connection=db_conn, sql=sql, params=(item_id,))

        if not rows_affected:
            raise HTTPException(status_code=404, detail=f"Item com ID {item_id} não encontrado em '{table_name}'.")

        return {"message": f"Item com ID {item_id} excluído com sucesso de '{table_name}'.",
                "rows_affected": rows_affected}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")
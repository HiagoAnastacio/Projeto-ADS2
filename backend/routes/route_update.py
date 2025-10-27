# =======================================================================================
# MÓDULO DE ROTA - UPDATE (ATUALIZAÇÃO) - REFATORADO (RESTful & Pool)
# =======================================================================================
# ARQUITETURA:
# 1. Rota RESTful (ex: UPDATE/{table_name}/{item_id}).
# 2. Usa `Depends(get_db_connection)` para injetar uma conexão do Pool.
# 3. Usa `execute_api_query` (do db_manager).
# =======================================================================================

from fastapi import APIRouter, HTTPException, Path, Depends, Body 
from typing import Dict, Any
from mysql.connector.connection import MySQLConnection
from utils.dependencies import validate_body
from app.security.table_whitelist_security import ALLOWED_WRITE_TABLES
from utils.db_manager import get_db_connection, execute_api_query

router = APIRouter()

@router.put("/{table_name}/{item_id}", tags=["Resource Update"])
async def update_resource(
    table_name: str = Path(..., description="Nome do recurso (tabela) para atualização."),
    item_id: int = Path(..., description="ID do item a ser atualizado."),
    request_body: Dict[str, Any] = Body(..., description="Corpo JSON com os dados para atualizar."),
    data_dict: Dict[str, Any] = Depends(validate_body),
    db_conn: MySQLConnection = Depends(get_db_connection)
):
    """
    Atualiza um registro existente em uma tabela autorizada (permite atualização parcial).

    COMO USAR:
    
    1.  **Endpoint:** `PUT /api/v1/{table_name}/{item_id}`
        -   Ex: `PUT /api/v1/hero/5` (Atualiza o herói com hero_id = 5)
    
    2.  **Corpo da Requisição (Body):**
        -   Deve ser um JSON contendo *apenas* os campos que você deseja alterar.
        -   Use a rota `GET /api/v1/models/{table_name}/example` para ver um exemplo de campos.
        -   Exemplo de Body para `hero` (atualizando apenas o ícone):
            ```json
            {
              "hero_icon_img_link": "[http://new-link.com/icon.png](http://new-link.com/icon.png)"
            }
            ```
            
    3.  **Segurança e Validação:**
        -   A rota falhará com `403 Forbidden` se a tabela não estiver na `ALLOWED_WRITE_TABLES`.
        -   A rota falhará com `422 Unprocessable Entity` se o JSON contiver campos inválidos.
    
    4.  **Resposta (Sucesso 200):**
        -   Retorna uma mensagem de sucesso e o número de linhas afetadas.
    
    5.  **Resposta (Erro 404):**
        -   Retorna `404 Not Found` se o `item_id` não existir ou se os dados enviados forem idênticos aos já existentes (nenhuma linha afetada).
    """

    if table_name not in ALLOWED_WRITE_TABLES:
        raise HTTPException(status_code=403, detail=f"O recurso '{table_name}' não permite atualização via API.")
    
    if not data_dict:
        raise HTTPException(status_code=400, detail="O corpo da requisição não pode estar vazio.")

    set_clause = ", ".join([f"`{key}` = %s" for key in data_dict.keys()])
    values = tuple(data_dict.values()) + (item_id,)
    id_column = f"{table_name}_id"

    try:
        sql = f"UPDATE `{table_name}` SET {set_clause} WHERE `{id_column}` = %s"
        rows_affected = execute_api_query(connection=db_conn, sql=sql, params=values)
        
        if not rows_affected:
            raise HTTPException(status_code=404, detail=f"Item com ID {item_id} não encontrado ou dados idênticos.")

        return {"message": f"Item com ID {item_id} atualizado com sucesso em '{table_name}'.", "rows_affected": rows_affected}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")
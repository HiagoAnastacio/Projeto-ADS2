# =======================================================================================
# MÓDULO DE ROTA - POST (CRIAÇÃO) - REFATORADO (RESTful & Pool)
# =======================================================================================
# ARQUITETURA:
# 1. Rota RESTful (ex: POST /{table_name}).
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

@router.post("/{table_name}", tags=["Resource Creation"])
async def create_resource(
    table_name: str = Path(..., description="Nome do recurso (tabela) para inserção."), 
    request_body: Dict[str, Any] = Body(..., description="Corpo JSON com os dados para inserir."),
    data_dict: Dict[str, Any] = Depends(validate_body),
    db_conn: MySQLConnection = Depends(get_db_connection)
):
    """
    Insere um novo registro em uma tabela autorizada.

    COMO USAR:
    
    1.  **Endpoint:** `POST /api/v1/{table_name}`
        -   Ex: `POST /api/v1/hero`
    
    2.  **Corpo da Requisição (Body):**
        -   Deve ser um JSON contendo os dados do novo registro.
        -   Os campos DEVEM corresponder ao schema Pydantic da tabela.
        -   Use a rota `GET /api/v1/models/{table_name}/example` para ver um exemplo.
        -   Exemplo de Body para `hero`:
            ```json
            {
              "hero_name": "Novo Heroi",
              "role_id": 1,
              "hero_icon_img_link": "[http://example.com/icon.png](http://example.com/icon.png)"
            }
            ```
            
    3.  **Segurança e Validação:**
        -   A rota falhará com `403 Forbidden` se a tabela não estiver na `ALLOWED_WRITE_TABLES`.
        -   A rota falhará com `422 Unprocessable Entity` se o JSON não passar na validação Pydantic (ex: campo faltando, tipo errado).
    
    4.  **Resposta (Sucesso 200):**
        -   Retorna uma mensagem de sucesso, o ID do novo item e os dados inseridos.
    """

    if table_name not in ALLOWED_WRITE_TABLES:
        raise HTTPException(status_code=403, detail=f"O recurso '{table_name}' não permite criação via API.")
    
    columns = ", ".join([f"`{col}`" for col in data_dict.keys()])
    placeholders = ", ".join(["%s"] * len(data_dict))
    values = tuple(data_dict.values())

    try:
        sql = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
        new_id = execute_api_query(connection=db_conn, sql=sql, params=values)
        
        if not new_id:
            raise HTTPException(status_code=500, detail="Falha ao criar o recurso, nenhum ID retornado.")

        return {"message": f"Recurso criado com sucesso em '{table_name}'.", "id": new_id, **data_dict}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")
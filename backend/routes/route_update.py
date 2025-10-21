# =======================================================================================
# MÓDULO DE ROTA - PUT (ATUALIZAÇÃO)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Define um endpoint genérico `PUT /api/update/{table_name}/{item_id}`.
# 2. Recebe 'table_name' e 'item_id' da URL.
# 3. (Segurança) Valida `table_name` contra a `ALLOWED_WRITE_TABLES`.
# 4. (Validação) Usa a dependência `validate_body` para validar o JSON.
# 5. Constrói a Query SQL `UPDATE` dinamicamente com base nos campos presentes
#    no JSON, permitindo atualizações parciais (similar a um PATCH).
# 6. Chama a função `execute` da camada DAO para rodar o comando.
#
# RAZÃO DE EXISTIR: Fornecer um endpoint seguro e validado para atualizar
# registros existentes em tabelas de dimensão autorizadas.
# =======================================================================================

from fastapi import APIRouter, HTTPException, Path, Depends, Body 
from typing import Dict, Any
from utils.function_execute import execute
from utils.dependencies import validate_body
# Importa a whitelist de segurança
from app.security.table_whitelist_security import ALLOWED_WRITE_TABLES 

# Variável 'router' (Escopo Global/Módulo).
router = APIRouter()

@router.put("/update/{table_name}/{item_id}", tags=["Generic Data Management"]) 
async def update_data(
    table_name: str = Path(..., description="Nome da tabela para atualização."), 
    item_id: int = Path(..., description="ID do item a ser atualizado."), 
    request_body: Dict[str, Any] = Body(..., description="Corpo JSON com os dados para atualizar."),
    data_dict: Dict[str, Any] = Depends(validate_body) 
):
    """
    Atualiza um registro existente em uma tabela autorizada, com base no ID.
    
    COMO USAR:
    
    1.  **Endpoint:** `PUT /api/update/{table_name}/{item_id}`
        -   Ex: `PUT /api/update/hero/10` (Atualiza o herói com ID 10)
    
    2.  **Corpo da Requisição (Body):**
        -   Deve ser um JSON contendo os dados a serem atualizados.
        -   **Permite atualização parcial:** Você só precisa enviar os campos que
          deseja alterar.
        -   Use a rota `GET /api/models/{table_name}/example` para ver um exemplo.
        -   Exemplo de Body para `hero`:
            ```json
            {
              "hero_name": "Nome Corrigido"
            }
            ```
            
    3.  **Segurança e Validação:**
        -   A rota falhará se a tabela não estiver na whitelist de escrita.
        -   A rota falhará se o JSON não passar na validação Pydantic.
    """

    # 1. Verificação de Segurança (Whitelist)
    if table_name not in ALLOWED_WRITE_TABLES:
        raise HTTPException(status_code=403, detail=f"A tabela '{table_name}' não permite atualização via API.")
    
    if not data_dict:
        raise HTTPException(status_code=400, detail="O corpo da requisição não pode estar vazio.")

    # Constrói a parte SET da query dinamicamente.
    set_clause = ", ".join([f"`{key}` = %s" for key in data_dict.keys()]) 
    values = tuple(data_dict.values()) + (item_id,) 

    try:
        # A coluna de ID é padronizada como `nome_da_tabela_id`.
        sql = f"UPDATE `{table_name}` SET {set_clause} WHERE `{table_name}_id` = %s"
        # Chama a camada DAO.
        rows_affected = execute(sql=sql, params=values)
        
        if not rows_affected:
            raise HTTPException(status_code=404, detail=f"Item com ID {item_id} não encontrado ou dados idênticos.")

        return {"message": f"Item com ID {item_id} atualizado com sucesso na tabela '{table_name}'.", "rows_affected": rows_affected}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {e}")
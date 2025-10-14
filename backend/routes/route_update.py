# =======================================================================================
# MÓDULO DE ROTA - PUT (ATUALIZAÇÃO)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Define um endpoint genérico `PUT /api/update/{table_name}/{item_id}`.
# 2. Recebe 'table_name' e 'item_id' da URL.
# 3. (NOVO) Realiza uma verificação de segurança para garantir que a tabela permite escrita.
# 4. Injeção de Dependência: Chama a dependência `validate_body` para validar, limpar
#    e retornar um dicionário (`data_dict`) com os dados seguros para atualização.
# 5. Constrói a Query SQL `UPDATE` dinamicamente com base nos campos presentes em `data_dict`,
#    permitindo atualizações parciais (semelhante a um PATCH).
# 6. Chama a função `execute` da camada DAO para rodar o comando SQL.
# 7. Verifica se alguma linha foi de fato alterada (`rows_affected`) e retorna um erro
#    404 se o ID não for encontrado ou se os dados enviados forem idênticos aos existentes.
#
# RAZÃO DE EXISTIR: Fornecer um endpoint genérico, seguro e padronizado para
# atualizar registros existentes em qualquer tabela autorizada.
# =======================================================================================

from fastapi import APIRouter, HTTPException, Path, Depends, Body 
from typing import Dict, Any
from utils.function_execute import execute
from utils.dependencies import validate_body
from app.security.table_whitelist_security import ALLOWED_WRITE_TABLES # <-- IMPORTAÇÃO CENTRALIZADA

# Variável 'router' (Escopo Global/Módulo).
router = APIRouter()

@router.put("/update/{table_name}/{item_id}", tags=["Generic Data Management"]) 
async def update_data(
    table_name: str = Path(..., description="Nome da tabela para atualização."), 
    item_id: int = Path(..., description="ID do item a ser atualizado."), 
    request_body: Dict[str, Any] = Body(..., description="Corpo JSON com os dados para atualizar."),
    data_dict: Dict[str, Any] = Depends(validate_body) 
):
    """Atualiza um item em uma tabela autorizada com base no ID."""

    # 1. Verificação de Segurança (Whitelist) - CORREÇÃO CRÍTICA
    if table_name not in ALLOWED_WRITE_TABLES:
        raise HTTPException(status_code=403, detail=f"A tabela '{table_name}' não permite atualização via API.")
    
    if not data_dict:
        raise HTTPException(status_code=400, detail="O corpo da requisição não pode estar vazio.")

    # Constrói a parte SET da query dinamicamente.
    set_clause = ", ".join([f"`{key}` = %s" for key in data_dict.keys()]) # Ex: `hero_name` = %s, `role_id` = %s
    values = tuple(data_dict.values()) + (item_id,) # Adiciona o item_id ao final da tupla de valores.

    try:
        # Monta a query final.
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
# =======================================================================================
# MÓDULO DE ROTA - POST (CRIAÇÃO)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Define um endpoint genérico `POST /api/insert/{table_name}`.
# 2. Recebe o `table_name` da URL e o corpo da requisição (JSON).
# 3. **Injeção de Dependência:** Antes de executar a lógica principal, o FastAPI chama
#    a dependência `validate_body`, que valida o JSON contra o schema Pydantic correto.
# 4. A rota recebe o dicionário já validado (`data_dict`) da dependência.
# 5. Constrói a query `INSERT INTO ...` dinamicamente com base nas chaves e valores
#    do dicionário validado.
# 6. Chama a função `execute` da camada DAO para inserir os dados.
# 7. Retorna uma mensagem de sucesso com o ID do novo registro.
#
# RAZÃO DE EXISTIR: Fornecer um ponto de entrada seguro e genérico para a criação de
# novos registros em qualquer tabela autorizada.
# =======================================================================================

from fastapi import APIRouter, HTTPException, Path, Depends, Body 
from typing import Dict, Any
from utils.function_execute import execute
from utils.dependencies import validate_body

# Variável 'router' (Escopo Global/Módulo).
router = APIRouter()

@router.post("/insert/{table_name}", tags=["Generic Data Management"])
async def insert_data(
    table_name: str = Path(..., description="Nome da tabela para inserção."), 
    
    # O `request_body` é usado pelo Swagger para documentação.
    request_body: Dict[str, Any] = Body(..., description="Corpo JSON com os dados para inserir."),
    
    # Variável 'data_dict' (Escopo de Requisição): Este não é um parâmetro normal.
    # Ele é o **resultado** da execução da dependência `validate_body`. O FastAPI injeta
    # o dicionário validado aqui.
    data_dict: Dict[str, Any] = Depends(validate_body) 
):
    """Insere um novo item em uma tabela autorizada."""
    
    # Constrói dinamicamente as partes da query SQL.
    columns = ", ".join([f"`{col}`" for col in data_dict.keys()]) # Ex: `hero_name`, `role_id`
    placeholders = ", ".join(["%s"] * len(data_dict)) # Ex: %s, %s
    values = tuple(data_dict.values()) # Tupla com os valores a serem inseridos.

    try:
        # Monta a query final.
        sql = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
        # Chama a camada DAO.
        new_id = execute(sql=sql, params=values)
        
        # `execute` retorna o lastrowid para INSERTs.
        if not new_id:
            raise HTTPException(status_code=500, detail="Não foi possível inserir os dados.")

        return {"message": f"Dados inseridos com sucesso na tabela '{table_name}'.", "new_id": new_id}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno na inserção: {e}")
# app/routes/route_update.py
from fastapi import APIRouter, HTTPException, Path, Depends
from typing import Dict, Any
from utils.function_execute import execute
import logging
from utils.dependencies import validate_body

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
router = APIRouter()

@router.put("/update/{table_name}/{item_id}", tags=["Generic Data Management"])
async def update_data(
    table_name: str = Path(..., description="Nome da tabela para atualização."),
    item_id: int = Path(..., description="ID do item a ser atualizado."),
    data_dict: Dict[str, Any] = Depends(validate_body)
):
    set_clauses = [f"{column} = %s" for column in data_dict.keys()]
    sql_set = ", ".join(set_clauses)
    values = tuple(list(data_dict.values()) + [item_id])

    try:
        sql = f"UPDATE {table_name} SET {sql_set} WHERE {table_name}_id = %s"
        rows_affected = execute(sql=sql, params=values)
        if not rows_affected:
            raise HTTPException(status_code=404, detail=f"Item com ID {item_id} não encontrado ou não houve alteração.")

        return {"message": f"Item com ID {item_id} atualizado com sucesso na tabela '{table_name}'."}
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        logging.error(f"Erro no banco de dados durante a atualização: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar dados: {e}")
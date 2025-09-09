from fastapi import APIRouter, HTTPException, Path, Depends
from pydantic import BaseModel
from utils.function_execute import execute
from model.db_model_for_tabel import get_model_for_table

router = APIRouter()

@router.put("/update/{table_name}/{item_id}", tags=["Generic Data Management"])
async def update_data(
    table_name: str = Path(..., description="Nome da tabela para atualização."),
    item_id: int = Path(..., description="ID do item a ser atualizado."),
    # Dependência que injeta o modelo Pydantic correspondente
    data: BaseModel = Depends(get_model_for_table)
):
    """
    Atualiza um item em uma tabela autorizada com base no ID e em um modelo Pydantic.
    """
    data_dict = data.model_dump()
    set_clauses = [f"{column} = %s" for column in data_dict.keys()]
    sql_set = ", ".join(set_clauses)
    values = tuple(list(data_dict.values()) + [item_id])

    try:
        sql = f"UPDATE {table_name} SET {sql_set} WHERE {table_name}_id = %s"
        rows_affected = execute(sql=sql, params=values)
        if not rows_affected:
            raise HTTPException(status_code=404, detail=f"Item com ID {item_id} não encontrado ou não houve alteração.")
        
        return {"message": f"Item com ID {item_id} atualizado com sucesso na tabela '{table_name}'."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
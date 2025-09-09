# app/routes/delete_data.py
from fastapi import APIRouter, HTTPException, Path
from utils.function_execute import execute

router = APIRouter()

# Lista de tabelas permitidas para exclusão
TABLES_WHITELIST = ["hero", "map", "role", "rank", "game_mode"]

@router.delete("/delete/{table_name}/{item_id}", tags=["Generic Data Management"])
async def delete_data(
    table_name: str = Path(..., description="Nome da tabela para exclusão"),
    item_id: int = Path(..., description="ID do item a ser excluído")
):
    """
    Exclui um item de uma tabela autorizada com base no ID.
    """
    if table_name not in TABLES_WHITELIST:
        raise HTTPException(status_code=400, detail=f"A tabela '{table_name}' não é válida para esta operação.")

    try:
        sql = f"DELETE FROM {table_name} WHERE {table_name}_id = %s"
        rows_affected = execute(sql=sql, params=(item_id,))
        if not rows_affected:
            raise HTTPException(status_code=404, detail=f"Item com ID {item_id} não encontrado.")
        
        return {"message": f"Item com ID {item_id} excluído com sucesso da tabela '{table_name}'."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
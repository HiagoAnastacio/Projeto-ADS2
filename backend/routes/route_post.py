# app/routes/route_post.py
from fastapi import APIRouter, HTTPException, Path, Depends
from typing import Dict, Any
from utils.function_execute import execute
import logging
from utils.dependencies import validate_body

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
router = APIRouter()

@router.post("/insert/{table_name}", tags=["Generic Data Management"])
async def insert_data(
    table_name: str = Path(..., description="Nome da tabela para inserção."),
    data_dict: Dict[str, Any] = Depends(validate_body)
):
    columns = ", ".join(data_dict.keys())
    placeholders = ", ".join(["%s"] * len(data_dict))
    values = tuple(data_dict.values())

    try:
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        new_id = execute(sql=sql, params=values)
        if not new_id:
            raise HTTPException(status_code=500, detail="Não foi possível inserir os dados.")

        return {"message": f"Dados inseridos com sucesso na tabela '{table_name}'. ID do novo item: {new_id}"}
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        logging.error(f"Erro no banco de dados durante a inserção: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao inserir dados: {e}")
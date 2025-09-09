from fastapi import APIRouter, HTTPException, Path, Depends
from pydantic import BaseModel
from utils.function_execute import execute
from model.db_model_for_tabel import get_model_for_table

router = APIRouter()

# O parâmetro de rota para a tabela agora determina o modelo Pydantic
@router.post("/insert/{table_name}", tags=["Generic Data Management"])
async def insert_data(
    table_name: str = Path(..., description="Nome da tabela para inserção."),
    # Dependência que injeta o modelo Pydantic correspondente
    # A validação do corpo da requisição é feita automaticamente aqui
    data: BaseModel = Depends(get_model_for_table)
):
    """
    Insere um novo item em uma tabela autorizada com base em um modelo Pydantic.
    """
    # Converter o modelo Pydantic para um dicionário para a consulta SQL
    data_dict = data.model_dump()
    columns = ", ".join(data_dict.keys())
    placeholders = ", ".join(["%s"] * len(data_dict))
    values = tuple(data_dict.values())

    try:
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        new_id = execute(sql=sql, params=values)
        if not new_id:
            raise HTTPException(status_code=500, detail="Não foi possível inserir os dados.")
        
        return {"message": f"Dados inseridos com sucesso na tabela '{table_name}'.", "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
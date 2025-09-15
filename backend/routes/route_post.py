from fastapi import APIRouter, HTTPException, Path, Request
from pydantic import BaseModel, ValidationError
from utils.function_execute import execute
from model.model_resolver import get_model_for_table
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
router = APIRouter()

@router.post("/insert/{table_name}", tags=["Generic Data Management"])
async def insert_data(
    table_name: str = Path(..., description="Nome da tabela para inserção."),
    request = Request
):
    """
    Insere um novo item em uma tabela autorizada com base em um modelo Pydantic.
    """
    try:
        # Tenta obter o modelo Pydantic em tempo de execução
        model: BaseModel = get_model_for_table(table_name)
    except HTTPException as e:
        # Se não houver modelo, retorna erro 400
        raise e

    try:
        # Lê o corpo da requisição como JSON
        json_data = await request.json()
        # Valida manualmente os dados contra o modelo Pydantic
        validated_data = model.model_validate(json_data)
        data_dict = validated_data.model_dump()
    except ValidationError as e:
        # Em caso de erro de validação do Pydantic, retorna 422
        logging.error(f"Erro de validação Pydantic: {e.errors()}")
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        # Outros erros de leitura do JSON
        logging.error(f"Erro ao processar o corpo da requisição: {e}")
        raise HTTPException(status_code=400, detail="Corpo da requisição inválido.")
    
    # Converte o modelo Pydantic validado para um dicionário para a consulta SQL
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
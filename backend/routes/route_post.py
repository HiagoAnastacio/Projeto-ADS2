from fastapi import APIRouter, HTTPException, Path, Body
from pydantic import BaseModel, ValidationError, HttpUrl
from typing import Dict, Any
from utils.function_execute import execute
from model.model_resolver import get_model_for_table
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
router = APIRouter()

@router.post("/insert/{table_name}", tags=["Generic Data Management"])
async def insert_data(
    table_name: str = Path(..., description="Nome da tabela para inserção."),
    # Deixe o FastAPI cuidar da leitura e validação do corpo da requisição
    request_body: Dict[str, Any] = Body(
        ...,
        description="Corpo JSON com os dados para inserir. O schema depende da tabela."
    )
):
    """
    Insere um novo item em uma tabela autorizada com base em um modelo Pydantic.
    """
    try:
        # Tenta obter o modelo Pydantic em tempo de execução
        model: BaseModel = get_model_for_table(table_name)
    except ValueError as e:
        # Se não houver modelo, retorna erro 400
        raise HTTPException(status_code=400, detail=str(e))
    
    try:
        # Valida manualmente os dados contra o modelo Pydantic obtido
        validated_data = model.model_validate(request_body)
        
        # Converte o modelo Pydantic validado para um dicionário
        data_dict = validated_data.model_dump(exclude_none=True)
        
    except ValidationError as e:
        # Em caso de erro de validação do Pydantic, retorna 422
        logging.error(f"Erro de validação Pydantic: {e.errors()}")
        
        # Esta é a mudança mais importante:
        # Retorna o erro detalhado do Pydantic diretamente.
        raise HTTPException(
            status_code=422, 
            detail=[{"loc": err["loc"], "msg": err["msg"], "type": err["type"]} for err in e.errors()]
        )
    
    except Exception as e:
        # Outros erros de processamento
        logging.error(f"Erro ao processar o corpo da requisição: {e}")
        raise HTTPException(status_code=400, detail="Corpo da requisição inválido.")

    # Converte explicitamente HttpUrl para string, por segurança.
    converted_values = []
    for value in data_dict.values():
        if isinstance(value, HttpUrl):
            converted_values.append(str(value))
        else:
            converted_values.append(value)
            
    columns = ", ".join(data_dict.keys())
    placeholders = ", ".join(["%s"] * len(data_dict))
    values = tuple(converted_values)

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
        raise HTTPException(status_code=500, detail=str(e))
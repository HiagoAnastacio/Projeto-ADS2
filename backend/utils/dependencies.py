# Dependência para validar o corpo da requisição com base no modelo Pydantic da tabela.
from fastapi import HTTPException, Request
from pydantic import BaseModel, ValidationError
from typing import Dict, Any
from model.model_resolver import get_model_for_table

async def validate_body(table_name: str, request: Request) -> Dict[str, Any]:
    """
    Dependência que valida o corpo da requisição JSON com base no modelo Pydantic da tabela.
    """
    try:
        model: BaseModel = get_model_for_table(table_name)
    except HTTPException as e:
        raise e

    try:
        json_data = await request.json()
        validated_data = model.model_validate(json_data)
        data_dict = validated_data.model_dump()
        return data_dict
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Corpo da requisição inválido. Erro: {e}')
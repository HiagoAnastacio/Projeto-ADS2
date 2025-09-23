# app/utils/dependencies.py
from fastapi import HTTPException, Request, Path, Depends
from pydantic import BaseModel, ValidationError
from typing import Dict, Any
from model.model_resolver import get_model_for_table

async def validate_body(
    request: Request,
    table_name: str = Path(...)
) -> Dict[str, Any]:
    """
    Dependência que valida o corpo da requisição JSON com base no modelo Pydantic da tabela.
    """
    try:
        model: BaseModel = get_model_for_table(table_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    try:
        json_data = await request.json()
        validated_data = model.model_validate(json_data)
        data_dict = validated_data.model_dump(exclude_none=True)
        return data_dict
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        raise HTTPException(status_code=400, detail="Corpo da requisição inválido.")
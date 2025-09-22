# app/routes/docs/route_schema_models.py
from fastapi import APIRouter
from typing import Dict, Any
from model.model_resolver import TABLE_MODEL_MAPPING

router = APIRouter()

@router.get("/models", tags=["API Documentation"])
def get_model_schemas() -> Dict[str, Any]:
    """
    Retorna um dicionário com os schemas JSON de todos os modelos mapeados.
    """
    model_schemas = {}
    for table_name, model in TABLE_MODEL_MAPPING.items():
        model_schemas[table_name] = model.model_json_schema()
    
    return model_schemas
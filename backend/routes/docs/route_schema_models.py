# app/routes/docs/route_schema_models.py
from fastapi import APIRouter, HTTPException, Path
from typing import Dict, Any, Type
from pydantic import BaseModel, Field, HttpUrl

from model.model_resolver import get_model_for_table, TABLE_MODEL_MAPPING

router = APIRouter()

def create_example_json(model: Type[BaseModel]) -> Dict[str, Any]:
    """
    Cria um dicionário de exemplo a partir de um modelo Pydantic.
    """
    schema = model.model_json_schema()
    example_json = {}
    for prop_name, prop_data in schema.get("properties", {}).items():
        # Verificando se há um exemplo específico
        if "examples" in prop_data and prop_data["examples"]:
            example_json[prop_name] = prop_data["examples"][0]
        # Verificando se há um valor padrão
        elif "default" in prop_data:
            example_json[prop_name] = prop_data["default"]
        else:
            # Gerando placeholders genéricos baseados no tipo do campo
            prop_type = prop_data.get("type", None)
            if prop_type == "string":
                # Verifica se é uma URL a partir do formato
                if prop_data.get("format") == "uri":
                    example_json[prop_name] = "URL"
                else:
                    example_json[prop_name] = "STRING"
            elif prop_type == "integer":
                example_json[prop_name] = 0
            elif prop_type == "number":
                example_json[prop_name] = 0.0
            else:
                example_json[prop_name] = None
    return example_json

# Mantendo apenas a rota para o exemplo
@router.get("/models/{table_name}/example", tags=["API Documentation"])
def get_model_example(
    table_name: str = Path(..., description="Nome da tabela para obter o exemplo de JSON.")
) -> Dict[str, Any]:
    """
    Retorna um exemplo de JSON para um modelo Pydantic, útil para testes.
    """
    try:
        model = get_model_for_table(table_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return create_example_json(model)
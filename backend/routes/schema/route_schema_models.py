# =======================================================================================
# MÓDULO DE ROTA - DOCUMENTAÇÃO (EXEMPLOS DE MODELO)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Define um endpoint de utilidade `GET /api/models/{table_name}/example`.
# 2. Recebe o `table_name` da URL.
# 3. (Segurança) Valida se a tabela solicitada está na `ALLOWED_GET_TABLES`.
# 4. Usa a função `get_model_for_table` do resolvedor de modelos para obter a
#    classe Pydantic correta.
# 5. Gera um dicionário de exemplo a partir do schema Pydantic.
# 6. Retorna o JSON de exemplo gerado.
#
# RAZÃO DE EXISTIR: Oferecer uma rota de utilidade para a documentação e para
# desenvolvedores do frontend, permitindo que descubram qual o formato JSON
# esperado pelas rotas POST e PUT para uma determinada tabela.
# =======================================================================================

from fastapi import APIRouter, HTTPException, Path
from typing import Dict, Any, Type
from pydantic import BaseModel, HttpUrl
from model.model_resolver import get_model_for_table
# Importa a whitelist de segurança
from app.security.table_whitelist_security import ALLOWED_GET_TABLES 

# Variável 'router' (Escopo Global/Módulo).
router = APIRouter()

def create_example_json(model_schema: Dict[str, Any]) -> Dict[str, Any]:
    """Cria um JSON de exemplo a partir de um schema Pydantic."""
    example_json = {}
    properties = model_schema.get("properties", {})
    for prop_name, prop_data in properties.items():
        if "examples" in prop_data and prop_data["examples"]:
            example_json[prop_name] = prop_data["examples"][0]
        elif "default" in prop_data:
            example_json[prop_name] = prop_data["default"]
        else:
            prop_type = prop_data.get("type")
            if prop_type == "string": example_json[prop_name] = "string"
            elif prop_type == "integer": example_json[prop_name] = 0
            elif prop_type == "number": example_json[prop_name] = 0.0
            else: example_json[prop_name] = None
    return example_json

@router.get("/models/{table_name}/example", tags=["API Documentation"])
def get_model_example(
    table_name: str = Path(..., description="Nome da tabela para obter o exemplo de JSON.")
) -> Dict[str, Any]:
    """
    Retorna um exemplo de corpo JSON para uma tabela específica.
    
    COMO USAR:
    
    1.  **Endpoint:** `GET /api/models/{table_name}/example`
        -   Ex: `GET /api/models/hero/example`
            
    2.  **Propósito:** Esta rota é uma ferramenta de documentação. Ela mostra
        o formato JSON que as rotas `POST /insert/{table_name}` e
        `PUT /update/{table_name}` esperam receber no corpo da requisição.
    """
    
    # 1. Verificação de Segurança (Whitelist)
    if table_name not in ALLOWED_GET_TABLES:
        raise HTTPException(status_code=400, detail=f"A tabela '{table_name}' não é válida para esta consulta.")
        
    try:
        model = get_model_for_table(table_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    # Gera o schema JSON do modelo Pydantic
    model_schema = model.model_json_schema()
    
    # Cria e retorna o exemplo de JSON
    example_payload = create_example_json(model_schema)
    return example_payload
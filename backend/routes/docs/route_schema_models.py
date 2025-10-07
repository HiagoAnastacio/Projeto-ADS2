# =======================================================================================
# MÓDULO DE ROTA - DOCUMENTAÇÃO (EXEMPLOS DE MODELO)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Define um endpoint de utilidade `GET /api/models/{table_name}/example`.
# 2. Recebe o `table_name` da URL.
# 3. Usa a função `get_model_for_table` do resolvedor de modelos para obter a classe Pydantic
#    correspondente à tabela.
# 4. Chama a função `create_example_json`, que inspeciona o schema do modelo Pydantic.
# 5. A função `create_example_json` gera um dicionário JSON de exemplo, usando os valores
#    definidos nos `examples` dos campos do modelo ou placeholders genéricos.
# 6. Retorna o JSON de exemplo gerado.
#
# RAZÃO DE EXISTIR: Oferecer uma rota de utilidade para a documentação e desenvolvimento.
# Permite que um desenvolvedor frontend (ou qualquer cliente da API) descubra rapidamente
# o formato JSON exato esperado para uma operação POST/PUT em uma determinada tabela.
# =======================================================================================

from fastapi import APIRouter, HTTPException, Path
from typing import Dict, Any, Type
from pydantic import BaseModel
from model.model_resolver import get_model_for_table

# Variável 'router' (Escopo Global/Módulo).
router = APIRouter()

def create_example_json(model: Type[BaseModel]) -> Dict[str, Any]:
    """Cria um dicionário de exemplo a partir de um modelo Pydantic."""
    # `schema` (Escopo de Função): Obtém a estrutura do modelo em formato JSON Schema.
    schema = model.model_json_schema() 
    # `example_json` (Escopo de Função): O dicionário que será construído e retornado.
    example_json = {}
    
    # Itera sobre todas as propriedades (campos) definidas no schema do modelo.
    for prop_name, prop_data in schema.get("properties", {}).items():
        # Verifica se o campo tem um exemplo definido no `Field(..., examples=[...])`.
        if "examples" in prop_data and prop_data["examples"]:
            example_json[prop_name] = prop_data["examples"][0]
        # Se não houver exemplo, usa o valor padrão, se existir.
        elif "default" in prop_data:
            example_json[prop_name] = prop_data["default"]
        # Se não, gera um placeholder genérico com base no tipo do campo.
        else:
            prop_type = prop_data.get("type")
            if prop_type == "string":
                example_json[prop_name] = "string"
            elif prop_type == "integer":
                example_json[prop_name] = 0
            elif prop_type == "number":
                example_json[prop_name] = 0.0
            else:
                example_json[prop_name] = None
    return example_json

@router.get("/models/{table_name}/example", tags=["API Documentation"])
def get_model_example(
    # `table_name` (Escopo de Requisição): Capturado da URL.
    table_name: str = Path(..., description="Nome da tabela para obter o exemplo de JSON.")
) -> Dict[str, Any]:
    """Retorna um exemplo de corpo JSON para uma tabela específica."""
    try:
        # `model` (Escopo de Requisição): A classe Pydantic (ex: HeroBase) retornada pelo resolvedor.
        model = get_model_for_table(table_name)
    except ValueError as e:
        # Retorna 404 se a tabela não estiver mapeada no `model_resolver`.
        raise HTTPException(status_code=404, detail=str(e))
        
    # Chama a função auxiliar e retorna seu resultado.
    return create_example_json(model)
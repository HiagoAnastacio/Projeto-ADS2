# FLUXO E A LÓGICA:
# 1. Recebe `table_name` da URL (Escopo de Requisição).
# 2. Usa `get_model_for_table` para resolver a classe Pydantic (Escopo de Requisição).
# 3. Chama a função utilitária `create_example_json` com a classe do modelo.
# 4. Retorna o JSON de exemplo gerado.
# A razão de existir: Oferecer uma rota de utilidade para a documentação da API, permitindo que o cliente 
# descubra o formato JSON esperado para cada tabela.

from fastapi import APIRouter, HTTPException, Path # Razão: Roteamento, tratamento de erros e parâmetros.
from typing import Dict, Any, Type # Razão: Tipagem para dicionários, tipos genéricos e classes.
from pydantic import BaseModel, HttpUrl # Razão: BaseModel para tipagem de modelos e HttpUrl para lógica de exemplo.
from model.model_resolver import get_model_for_table # Razão: Função CRÍTICA para buscar o modelo Pydantic pelo nome.

# Variável 'router' (Escopo Global/Módulo).
router = APIRouter()

def create_example_json(model: Type[BaseModel]) -> Dict[str, Any]:
    """Cria um dicionário de exemplo a partir de um modelo Pydantic, usando 'examples' ou placeholders."""
    # Variável 'schema' (Escopo de Função/Requisição): Dicionário contendo o JSON Schema do modelo.
    schema = model.model_json_schema() 
    # Variável 'example_json' (Escopo de Função/Requisição): Dicionário que será retornado.
    example_json = {}
    
    # Itera sobre todas as propriedades (campos) definidas no modelo
    for prop_name, prop_data in schema.get("properties", {}).items():
        # A lógica interna usa `examples` ou `default` (se existirem) ou gera placeholders (STRING/0).
        # É uma lógica pura de Python, Escopo de Função.
        if "examples" in prop_data and prop_data["examples"]:
            example_json[prop_name] = prop_data["examples"][0]
        # ... [Restante da lógica de geração de exemplo, omitida aqui por brevidade] ...
        else:
            prop_type = prop_data.get("type", None)
            if prop_type == "string":
                if prop_data.get("format") == "uri":
                    example_json[prop_name] = "URL"
                else:
                    example_json[prop_name] = "STRING"
            elif prop_type == "integer":
                example_json[prop_name] = 0
            # ...
    return example_json

@router.get("/models/{table_name}/example", tags=["API Documentation"]) # Rota para obter exemplo de JSON
def get_model_example(
    # Variável 'table_name' (Escopo de Requisição).
    table_name: str = Path(..., description="Nome da tabela para obter o exemplo de JSON.")
) -> Dict[str, Any]:
    """Retorna um exemplo de JSON para um modelo Pydantic, útil para testes."""
    try:
        # Variável 'model' (Escopo de Requisição): Classe Pydantic resolvida.
        model = get_model_for_table(table_name)
    except ValueError as e:
        # Erro 404 se o modelo não for mapeado em model_resolver.py.
        raise HTTPException(status_code=404, detail=str(e))
        
    return create_example_json(model) # Retorna o JSON de exemplo gerado.
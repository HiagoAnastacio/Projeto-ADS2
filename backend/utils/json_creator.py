from typing import Dict, Any, Type
from pydantic import BaseModel, HttpUrl
# Importa o resolvedor de modelos de tabela


def create_example_json(model: Type[BaseModel]) -> Dict[str, Any]:
    """Gera um JSON de exemplo a partir de um schema Pydantic."""
    example_json = {}
    # Linha 31: Pega as propriedades do schema do modelo.
    properties = model.model_json_schema().get("properties", {})
    # Linha 33: Itera sobre cada propriedade.
    for prop_name, prop_data in properties.items():
        # Linha 34: Usa o primeiro exemplo definido no Field(), se existir.
        if "examples" in prop_data and prop_data["examples"]:
            example_json[prop_name] = prop_data["examples"][0]
        # Linha 37: Senão, usa o valor default, se existir.
        elif "default" in prop_data:
            example_json[prop_name] = prop_data["default"]
        # Linha 40: Senão, gera um placeholder com base no tipo.
        else:
            prop_type = prop_data.get("type")
            if prop_type == "string": example_json[prop_name] = "string"
            elif prop_type == "integer": example_json[prop_name] = 0
            elif prop_type == "number": example_json[prop_name] = 0.0
            else: example_json[prop_name] = None
    # Linha 48: Retorna o dicionário de exemplo.
    return example_json
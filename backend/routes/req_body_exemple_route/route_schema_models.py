# =======================================================================================
# MÓDULO DE ROTA - DOCUMENTAÇÃO (EXEMPLOS DE MODELO) (v0.8.1)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Define endpoints de utilidade para a documentação da API.
# 2. (Rota 1) `GET /models/{table_name}/example`: Retorna um exemplo de DADOS para
#    uma tabela específica (ex: como um JSON de Herói deve parecer).
# 3. (MUDANÇA v0.8.1) (Rota 2) `GET /models/analysis_query/example`: Nova rota que
#    retorna um exemplo do CORPO DE CONSULTA esperado pela rota analítica genérica.
#
# RAZÃO DE EXISTIR: Oferecer rotas de utilidade seguras para a documentação, permitindo
# que um cliente da API (como o frontend) descubra os formatos JSON esperados.
# =======================================================================================

from fastapi import APIRouter, HTTPException, Path
from typing import Dict, Any, Type
from pydantic import BaseModel, HttpUrl
# Importa o resolvedor de modelos de tabela
from model.model_resolver import get_model_for_table
# (NOVO) Importa o modelo da consulta analítica do models.py
from model.analytic_model import AnalysisQuery
# Importa a whitelist
from app.security.db_whitelist_security import EVERTHING_READ_ONLY

# Variável 'router' (Escopo Global/Módulo).
router = APIRouter()

# --- Função Auxiliar (sem alterações) ---
# Linha 28: Função que gera um exemplo a partir de um modelo Pydantic.
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

# --- Rota 1 (Existente): Exemplo de DADOS da Tabela ---
# Linha 51: Define a rota GET para exemplos de dados de tabela.
@router.get("/MODELS/{table_name}/EXEMPLE", tags=["API Documentation"])
def get_model_example(
    table_name: str = Path(..., description="Nome da tabela para obter o exemplo de JSON.")
) -> Dict[str, Any]:
    """Retorna um exemplo de corpo JSON de DADOS para uma tabela específica."""
    
    # Linha 59: 1. Verificação de Segurança (Whitelist)
    if table_name not in EVERTHING_READ_ONLY:
        # Linha 61: Rejeita se a tabela não estiver na lista.
        raise HTTPException(status_code=400, detail=f"A tabela '{table_name}' não é válida para esta consulta.")
        
    try:
        # Linha 65: 2. Resolução do Modelo (chama o model_resolver).
        model = get_model_for_table(table_name)
    except ValueError as e:
        # Linha 68: Erro 404 se o modelo não for encontrado no mapeamento.
        raise HTTPException(status_code=404, detail=str(e))
    
    # Linha 71: 3. Geração do Exemplo.
    return create_example_json(model)

@router.get("/MODELS/Analysis_Query/EXEMPLE", tags=["API Documentation"])
def get_analysis_query_example() -> Dict[str, Any]:
    """
    Retorna um exemplo do corpo JSON esperado pela
    rota analítica genérica `POST /API/V1-DATA/ANALYSIS/QUERY`.
    """
    try:
        # Linha 83: 1. Obtém o modelo `AnalysisQuery` (importado de analytic_model.py).
        model = AnalysisQuery
        # Linha 85: 2. Gera um exemplo dele usando a mesma função auxiliar `create_example_json`.
        return create_example_json(model)
    except Exception as e:
        # Linha 88: Captura erro genérico.
        raise HTTPException(status_code=500, detail=f"Erro ao gerar exemplo para AnalysisQuery: {e}")
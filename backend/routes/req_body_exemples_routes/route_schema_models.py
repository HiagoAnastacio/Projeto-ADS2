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
# Importa a whitelist
from app.security.db_whitelist_security import EVERTHING_READ_ONLY
from utils.json_creator import create_example_json

# Variável 'router' (Escopo Global/Módulo).
router = APIRouter()

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
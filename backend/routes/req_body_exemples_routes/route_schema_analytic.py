from fastapi import APIRouter, HTTPException, Path
from typing import Dict, Any, Type
from pydantic import BaseModel, HttpUrl
# (NOVO) Importa o modelo da consulta analítica do models.py
from model.analytic_model import AnalysisQuery
from utils.json_creator import create_example_json

router = APIRouter()

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
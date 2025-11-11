# =======================================================================================
# Modelos para Rotas Analíticas
# =======================================================================================
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class AnalysisQuery(BaseModel):
    # O nome da tabela/view que queremos consultar (ex: "vw_hero_rank_win_latest")
    table_name: str = Field(..., description="A tabela ou view de fato a ser consultada.")
    
    # Filtros exatos (ex: {"hero_id": 5, "rank_id": 3})
    filters_equal: Optional[Dict[str, Any]] = Field(None, description="Filtros de igualdade (ex: {'hero_id': 5}).")
    
    # Filtros de lista (ex: {"hero_id": [1, 5, 10], "rank_id": [3, 4]})
    filters_in: Optional[Dict[str, List[Any]]] = Field(None, description="Filtros 'IN' (ex: {'hero_id': [1, 5]}).")
    
    # Filtros de data (para consultar o histórico)
    start_date: Optional[datetime] = Field(None, description="Data de início (inclusive) para filtrar snapshots.")
    end_date: Optional[datetime] = Field(None, description="Data de fim (inclusive) para filtrar snapshots.")
    
    # Limite de resultados
    limit: int = Field(1000, description="Limite de linhas a serem retornadas.")
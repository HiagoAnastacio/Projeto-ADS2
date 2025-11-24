from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

class AnalysisQuery(BaseModel):
    table_name: str = Field(..., description="Nome da tabela ou view a ser consultada (ex: hero_stats_view)")
    
    filters_equal: Optional[Dict[str, Any]] = Field(
        None, 
        description="Dicionário de filtros de igualdade. Ex: {'hero_id': 1, 'rank_id': 3}"
    )
    
    filters_in: Optional[Dict[str, List[Any]]] = Field(
        None, 
        description="Dicionário de filtros de lista (IN). Ex: {'hero_id': [1, 2, 3]}"
    )
    
    start_date: Optional[str] = Field(None, description="Data de início (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="Data de fim (YYYY-MM-DD)")
    
    limit: int = Field(100, description="Limite de registros retornados")

    # --- NOVO CAMPO ---
    order_by: Optional[str] = Field(
        "date_of_the_data", 
        description="Coluna para ordenação. Padrão: 'date_of_the_data'. Opções seguras: 'win_rate', 'pick_rate', etc."
    )
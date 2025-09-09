# app/utils/model_resolver.p
from fastapi import HTTPException
from typing import Type
from pydantic import BaseModel
from model.models import (
    HeroBase, MapBase, RoleBase, RankBase, GameModeBase,
    HeroWinData, HeroPickData, HeroMapWinData, HeroMapPickData,
    HeroRankWinData, HeroRankPickData
)

# Mapeia nomes de tabelas para seus respectivos modelos Pydantic
TABLE_MODEL_MAPPING: dict[str, Type[BaseModel]] = {
    "hero": HeroBase,
    "map": MapBase,
    "role": RoleBase,
    "rank": RankBase,
    "game_mode": GameModeBase,
    "herowindata": HeroWinData,
    "heropickdata": HeroPickData,
    "heromapwindata": HeroMapWinData,
    "heromappickdata": HeroMapPickData,
    "herorankwindata": HeroRankWinData,
    "herorankpickdata": HeroRankPickData,
}

def get_model_for_table(table_name: str) -> Type[BaseModel]:
    """
    Retorna a classe do modelo Pydantic correspondente a uma tabela.
    Levanta um erro se a tabela não for encontrada.
    """
    model = TABLE_MODEL_MAPPING.get(table_name.lower())
    if not model:
        raise HTTPException(status_code=400, detail=f"A tabela '{table_name}' não é válida para esta operação.")
    return model
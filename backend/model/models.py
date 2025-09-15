# Arquivo de modelo para garantir que a tipagem dos dados seja consistente em toda a aplicação.
# É uma das partes do model da arquitetura MVC, pois molda a um dos aspectos com a interação com os dados.
# app/model/models.py
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional

# 1. Modelos de Entidades Principais

class HeroBase(BaseModel):
    hero_name: str = Field(..., examples=["Reinhardt"])
    hero_icon_img_link: Optional[HttpUrl] = Field(None, examples=["https://overwatch.com/hero/reinhardt.png"])

class MapBase(BaseModel):
    map_name: str = Field(..., examples=["Eichenwalde"])

class GameModeBase(BaseModel):
    game_mode_name: str = Field(..., examples=["Push"])

class RoleBase(BaseModel):
    role: str = Field(..., examples=["Tank"])

class RankBase(BaseModel):
    rank_name: str = Field(..., examples=["Grandmaster"])

# 2. Modelos para Inserção de Estatísticas

# Dados de taxa de vitória e escolha (geral)
class HeroWinData(BaseModel):
    hero_id: int = Field(..., examples=[1])
    win_total: float = Field(..., examples=[55.6])

class HeroPickData(BaseModel):
    hero_id: int = Field(..., examples=[1])
    pick_rate: float = Field(..., examples=[12.3])

# Dados de estatísticas por Herói e Mapa
class HeroMapWinData(BaseModel):
    hero_id: int = Field(..., examples=[1])
    map_id: int = Field(..., examples=[1])
    win_rate: float = Field(..., examples=[57.1])

class HeroMapPickData(BaseModel):
    hero_id: int = Field(..., examples=[1])
    map_id: int = Field(..., examples=[1])
    pick_rate: float = Field(..., examples=[15.8])

# Dados de estatísticas por Herói e Rank
class HeroRankWinData(BaseModel):
    hero_id: int = Field(..., examples=[1])
    rank_id: int = Field(..., examples=[1])
    win_rate: float = Field(..., examples=[52.9])

class HeroRankPickData(BaseModel):
    hero_id: int = Field(..., examples=[1])
    rank_id: int = Field(..., examples=[1])
    pick_rate: float = Field(..., examples=[10.1])

# Dados de estatísticas por Herói, Rank e Mapa
class HeroRankMapWinData(BaseModel):
    hero_id: int = Field(..., examples=[1])
    map_id: int = Field(..., examples=[1])
    rank_id: int = Field(..., examples=[1])
    win_rate: float = Field(..., examples=[58.4])

class HeroRankMapPickData(BaseModel):
    hero_id: int = Field(..., examples=[1])
    map_id: int = Field(..., examples=[1])
    rank_id: int = Field(..., examples=[1])
    pick_rate: float = Field(..., examples=[11.2])
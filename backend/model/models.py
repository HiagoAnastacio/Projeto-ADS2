# Arquivo de modelo para garantir que a tipagem dos dados seja consistente em toda a aplicação.
# É uma das partes do model da arquitetura MVC, pois molda a um dos aspectos com a interação com os dados.
from pydantic import BaseModel, HttpUrl
from typing import Optional

# 1. Modelos de Entidades Principais

class HeroBase(BaseModel):
    hero_name: str
    hero_icon_img_link: Optional[HttpUrl] = None

class MapBase(BaseModel):
    map_name: str

class GameModeBase(BaseModel):
    game_mode_name: str

class RoleBase(BaseModel):
    role: str

class RankBase(BaseModel):
    rank_name: str

# 2. Modelos para Inserção de Estatísticas

# Dados de taxa de vitória e escolha (geral)
class HeroWinData(BaseModel):
    hero_id: int
    win_total: float

class HeroPickData(BaseModel):
    hero_id: int
    pick_rate: float

# Dados de estatísticas por Herói e Mapa
class HeroMapWinData(BaseModel):
    hero_id: int
    map_id: int
    win_rate: float

class HeroMapPickData(BaseModel):
    hero_id: int
    map_id: int
    pick_rate: float

# Dados de estatísticas por Herói e Rank
class HeroRankWinData(BaseModel):
    hero_id: int
    rank_id: int
    win_rate: float

class HeroRankPickData(BaseModel):
    hero_id: int
    rank_id: int
    pick_rate: float

# Dados de estatísticas por Herói, Rank e Mapa
class HeroRankMapWinData(BaseModel):
    hero_id: int
    map_id: int
    rank_id: int
    win_rate: float

class HeroRankMapPickData(BaseModel):
    hero_id: int
    map_id: int
    rank_id: int
    pick_rate: float
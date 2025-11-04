# =======================================================================================
# MÓDULO DE SCHEMAS DE DADOS (PYDANTIC) (v0.5.0)
# =======================================================================================
# Define a "forma" dos dados para validação da API e documentação Swagger,
# refletindo a estrutura das tabelas do banco de dados v0.5.0.
# =======================================================================================

from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime # Usar datetime para timestamps

# ----------------------------------------------------------------------------------
# 1. Modelos de Dimensões (Geralmente usados para POST/PUT em EDITABLE_TABLES)
#    Adicionamos campos de ID e data/timestamp opcionais para refletir a leitura (GET)
# ----------------------------------------------------------------------------------

class RoleBase(BaseModel):
    role: str = Field(..., examples=["Tank"], description="Nome da função.")

class Role(RoleBase): # Modelo completo para leitura
    role_id: int
    creation_date: datetime

class RankBase(BaseModel):
    rank_name: str = Field(..., examples=["Gold"], description="Nome do rank.")

class Rank(RankBase):
    rank_id: int
    creation_date: datetime

class GameModeBase(BaseModel):
    game_mode_name: str = Field(..., examples=["Control"], description="Nome do modo de jogo.")

class GameMode(GameModeBase):
    game_mode_id: int
    creation_date: datetime

class HeroBase(BaseModel):
    hero_name: str = Field(..., examples=["Reinhardt"], description="Nome do herói.")
    role_id: int = Field(..., examples=[3], description="ID da função (FK para Role).")
    hero_icon_img_link: Optional[HttpUrl] = Field(None, examples=["http://...png"], description="URL do ícone do herói.")

class Hero(HeroBase):
    hero_id: int
    creation_date: datetime

class MapBase(BaseModel):
    map_name: str = Field(..., examples=["King's Row"], description="Nome do mapa.")
    game_mode_id: int = Field(..., examples=[4], description="ID do modo de jogo (FK para GameMode).")

class Map(MapBase):
    map_id: int
    creation_date: datetime


# ----------------------------------------------------------------------------------
# 2. Modelos das Novas Tabelas de Fato (Geralmente READ_ONLY_TABLES)
#    Representam os dados lidos dessas tabelas. Incluem o ID PK e a data.
# ----------------------------------------------------------------------------------

# --- Agregação por Herói ---
class HeroWinData(BaseModel):
    hero_win_id: int
    hero_id: int
    win_rate: Optional[float] = None
    date_of_the_data: datetime # Renomeado de last_updated para consistência

class HeroPickData(BaseModel):
    hero_pick_id: int
    hero_id: int
    pick_rate: Optional[float] = None
    date_of_the_data: datetime

# --- Agregação por Herói e Rank ---
class HeroRankWinData(BaseModel):
    hero_rank_win_id: int
    hero_id: int
    rank_id: int
    win_rate: Optional[float] = None
    date_of_the_data: datetime

class HeroRankPickData(BaseModel):
    hero_rank_pick_id: int
    hero_id: int
    rank_id: int
    pick_rate: Optional[float] = None
    date_of_the_data: datetime

# --- Agregação por Herói e Mapa ---
class HeroMapWinData(BaseModel):
    hero_map_win_id: int
    hero_id: int
    map_id: int
    win_rate: Optional[float] = None
    date_of_the_data: datetime

class HeroMapPickData(BaseModel):
    hero_map_pick_id: int
    hero_id: int
    map_id: int
    pick_rate: Optional[float] = None
    date_of_the_data: datetime

# --- Agregação por Herói e Modo de Jogo ---
class HeroGameModeWinData(BaseModel):
    hero_gamemode_win_id: int
    hero_id: int
    game_mode_id: int
    win_rate: Optional[float] = None
    date_of_the_data: datetime

class HeroGameModePickData(BaseModel):
    hero_gamemode_pick_id: int
    hero_id: int
    game_mode_id: int
    pick_rate: Optional[float] = None
    date_of_the_data: datetime

# --- Tabela Granular (Herói, Rank, Mapa) ---
class HeroRankMapWinData(BaseModel):
    hero_rank_map_win_id: int
    hero_id: int
    rank_id: int
    map_id: int
    win_rate: float # Assumindo que esta sempre terá valor
    date_of_the_data: datetime

class HeroRankMapPickData(BaseModel):
    hero_rank_map_pick_id: int
    hero_id: int
    rank_id: int
    map_id: int
    pick_rate: float # Assumindo que esta sempre terá valor
    date_of_the_data: datetime

# ----------------------------------------------------------------------------------
# 3. Modelos para as Views "_latest" (Geralmente READ_ONLY_TABLES)
#    São idênticos aos modelos das tabelas de fato correspondentes, pois as views
#    apenas selecionam as colunas dessas tabelas. O campo 'rn' (ROW_NUMBER) não é incluído.
# ----------------------------------------------------------------------------------

VWHeroWinLatest = HeroWinData
VWHeroPickLatest = HeroPickData
VWHeroRankWinLatest = HeroRankWinData
VWHeroRankPickLatest = HeroRankPickData
VWHeroMapWinLatest = HeroMapWinData
VWHeroMapPickLatest = HeroMapPickData
VWHeroGameModeWinLatest = HeroGameModeWinData
VWHeroGameModePickLatest = HeroGameModePickData
VWHeroRankMapWinLatest = HeroRankMapWinData
VWHeroRankMapPickLatest = HeroRankMapPickData
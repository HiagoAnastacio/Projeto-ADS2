# Arquivo de modelo para garantir que a tipagem dos dados seja consistente em toda a aplicação.
# É uma das partes do model da arquitetura MVC, pois molda a um dos aspectos com a interação com os dados.
# app/model/models.py
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional

# 1. Modelos de Entidades Principais

class HeroBase(BaseModel):
    hero_name: str = Field(..., examples=["Reinhardt"])
    hero_icon_img_link: Optional[HttpUrl] = Field(None, examples=["https://overwatch.com/hero/reinhardt.png"])
    # Chave estrangeira para a tabela de 'role'
    role_id: int = Field(..., examples=[1], description="ID da função (role) do herói.")

class MapBase(BaseModel):
    map_name: str = Field(..., examples=["Eichenwalde"])
    # Chave estrangeira para a tabela de 'game_mode'
    game_mode_id: int = Field(..., examples=[1], description="ID do modo de jogo do mapa.")

class GameModeBase(BaseModel):
    game_mode_name: str = Field(..., examples=["Push"])

class RoleBase(BaseModel):
    role: str = Field(..., examples=["Tank"])

class RankBase(BaseModel):
    rank_name: str = Field(..., examples=["Grandmaster"])

# 2. Modelos para Inserção de Estatísticas (Tabelas Associativas)

# Dados de taxa de vitória e escolha (geral)
class HeroWinData(BaseModel):
    # Chave estrangeira para 'hero'
    hero_id: int = Field(..., examples=[1], description="ID do herói.")
    win_total: float = Field(..., examples=[55.6])

class HeroPickData(BaseModel):
    # Chave estrangeira para 'hero'
    hero_id: int = Field(..., examples=[1], description="ID do herói.")
    pick_rate: float = Field(..., examples=[12.3])

# Dados de estatísticas por Herói e Mapa
class HeroMapWinData(BaseModel):
    # Chaves estrangeiras para 'hero' e 'map'
    hero_id: int = Field(..., examples=[1], description="ID do herói.")
    map_id: int = Field(..., examples=[1], description="ID do mapa.")
    win_rate: float = Field(..., examples=[57.1])

class HeroMapPickData(BaseModel):
    # Chaves estrangeiras para 'hero' e 'map'
    hero_id: int = Field(..., examples=[1], description="ID do herói.")
    map_id: int = Field(..., examples=[1], description="ID do mapa.")
    pick_rate: float = Field(..., examples=[15.8])

# Dados de estatísticas por Herói e Rank
class HeroRankWinData(BaseModel):
    # Chaves estrangeiras para 'hero' e 'rank'
    hero_id: int = Field(..., examples=[1], description="ID do herói.")
    rank_id: int = Field(..., examples=[1], description="ID do rank.")
    win_rate: float = Field(..., examples=[52.9])

class HeroRankPickData(BaseModel):
    # Chaves estrangeiras para 'hero' e 'rank'
    hero_id: int = Field(..., examples=[1], description="ID do herói.")
    rank_id: int = Field(..., examples=[1], description="ID do rank.")
    pick_rate: float = Field(..., examples=[10.1])

# Dados de estatísticas por Herói, Rank e Mapa
class HeroRankMapWinData(BaseModel):
    # Chaves estrangeiras para 'hero', 'rank' e 'map'
    hero_id: int = Field(..., examples=[1], description="ID do herói.")
    rank_id: int = Field(..., examples=[1], description="ID do rank.")
    map_id: int = Field(..., examples=[1], description="ID do mapa.")
    win_rate: float = Field(..., examples=[54.3])

class HeroRankMapPickData(BaseModel):
    # Chaves estrangeiras para 'hero', 'rank' e 'map'
    hero_id: int = Field(..., examples=[1], description="ID do herói.")
    rank_id: int = Field(..., examples=[1], description="ID do rank.")
    map_id: int = Field(..., examples=[1], description="ID do mapa.")
    pick_rate: float = Field(..., examples=[11.7])
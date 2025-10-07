# =======================================================================================
# MÓDULO DE SCHEMAS DE DADOS (PYDANTIC)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Este módulo define a "forma" dos dados que a API espera receber ou enviar.
# 2. Cada classe (ex: `HeroBase`) representa o schema de uma tabela do banco.
# 3. O FastAPI usa essas classes para:
#    a. Validar automaticamente o corpo (body) das requisições POST e PUT.
#    b. Gerar a documentação do Swagger UI, mostrando o formato JSON esperado.
#
# RAZÃO DE EXISTIR: Atuar como a camada de **Validação e Contrato de Dados**. Garante que
# nenhum dado malformado ou com tipos incorretos chegue à lógica de negócio ou ao
# banco de dados, prevenindo erros e vulnerabilidades.
# =======================================================================================

from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import date

# ----------------------------------------------------------------------------------
# 1. Modelos de Entidades Principais (Tabelas de Dimensão)
# ----------------------------------------------------------------------------------

class HeroBase(BaseModel):
    # Schema para a tabela 'hero'.
    # Variável `hero_name` (Escopo de Definição): Campo obrigatório do tipo string.
    hero_name: str = Field(..., examples=["Reinhardt"], description="Nome do herói.")
    # Variável `role_id` (Escopo de Definição): Chave estrangeira para a tabela 'role'.
    role_id: int = Field(..., examples=[1], description="ID da role do herói.")
    # Variável `hero_icon_img_link` (Escopo de Definição): Campo opcional que valida se o valor é uma URL.
    hero_icon_img_link: Optional[HttpUrl] = Field(None, examples=["https://..."], description="Link para o ícone do herói.")
    
class MapBase(BaseModel):
    # Schema para a tabela 'map'.
    game_mode_id: int = Field(..., examples=[1], description="ID do modo de jogo do mapa.")
    map_name: str = Field(..., examples=["King's Row"], description="Nome do mapa.")

class RoleBase(BaseModel):
    # Schema para a tabela 'role'. Renomeado para 'role' para consistência.
    role: str = Field(..., examples=["Tank"], description="Nome da função (Tank, Damage, Support).")

class RankBase(BaseModel):
    # Schema para a tabela 'skill_rank' (anteriormente 'rank').
    rank_name: str = Field(..., examples=["Gold"], description="Nome do nível de habilidade.")

class GameModeBase(BaseModel):
    # Schema para a tabela 'game_mode'.
    game_mode_name: str = Field(..., examples=["Hybrid"], description="Nome do modo de jogo.")


# ----------------------------------------------------------------------------------
# 2. Modelos de Estatísticas (Tabelas de Fato)
# ----------------------------------------------------------------------------------
# A razão de existir para estas classes é validar os dados para as tabelas de
# junção que armazenam as estatísticas.

class HeroWinData(BaseModel):
    # Define o Schema para a tabela 'hero_win' (Taxa de Vitória por Herói).
    hero_id: int = Field(..., examples=[1], description="ID do herói (Chave Estrangeira para 'hero').") # Variável (Escopo de Definição): Tipo int, representa a FK para a tabela 'hero'.
    win_rate: float = Field(..., examples=[50.55], description="Taxa de vitória (float).") # Variável (Escopo de Definição): Tipo float.

class HeroPickData(BaseModel):
    # Define o Schema para a tabela 'hero_pick' (Taxa de Escolha por Herói).
    hero_id: int = Field(..., examples=[1], description="ID do herói.") # Variável (Escopo de Definição): Tipo int, FK.
    pick_rate: float = Field(..., examples=[10.1], description="Taxa de escolha (float).") # Variável (Escopo de Definição): Tipo float.
    
class HeroMapWinData(BaseModel):
    # Define o Schema para a tabela 'hero_map_win' (Taxa de Vitória por Herói e Mapa).
    hero_id: int = Field(..., examples=[1], description="ID do herói.") # Variável (Escopo de Definição): Tipo int, FK.
    map_id: int = Field(..., examples=[1], description="ID do mapa.") # Variável (Escopo de Definição): Tipo int, FK.
    win_rate: float = Field(..., examples=[55.0], description="Taxa de vitória (float).") # Variável (Escopo de Definição): Tipo float.

class HeroMapPickData(BaseModel):
    # Define o Schema para a tabela 'hero_map_pick' (Taxa de Escolha por Herói e Mapa).
    hero_id: int = Field(..., examples=[1], description="ID do herói.") # Variável (Escopo de Definição): Tipo int, FK.
    map_id: int = Field(..., examples=[1], description="ID do mapa.") # Variável (Escopo de Definição): Tipo int, FK.
    pick_rate: float = Field(..., examples=[8.2], description="Taxa de escolha (float).") # Variável (Escopo de Definição): Tipo float.

class HeroRankWinData(BaseModel):
    # Define o Schema para a tabela 'hero_rank_win' (Taxa de Vitória por Herói e Rank).
    hero_id: int = Field(..., examples=[1], description="ID do herói.") # Variável (Escopo de Definição): Tipo int, FK.
    rank_id: int = Field(..., examples=[1], description="ID do rank.") # Variável (Escopo de Definição): Tipo int, FK.
    win_rate: float = Field(..., examples=[52.9], description="Taxa de vitória (float).") # Variável (Escopo de Definição): Tipo float.

class HeroRankPickData(BaseModel):
    # Define o Schema para a tabela 'hero_rank_pick' (Taxa de Escolha por Herói e Rank).
    hero_id: int = Field(..., examples=[1], description="ID do herói.") # Variável (Escopo de Definição): Tipo int, FK.
    rank_id: int = Field(..., examples=[1], description="ID do rank.") # Variável (Escopo de Definição): Tipo int, FK.
    pick_rate: float = Field(..., examples=[10.1], description="Taxa de escolha (float).") # Variável (Escopo de Definição): Tipo float.

class HeroRankMapWinData(BaseModel):
    # Define o Schema para a tabela 'hero_rank_map_win' (Taxa de Vitória por Herói, Rank e Mapa).
    hero_id: int = Field(..., examples=[1], description="ID do herói.") # Variável (Escopo de Definição): Tipo int, FK.
    rank_id: int = Field(..., examples=[1], description="ID do rank.") # Variável (Escopo de Definição): Tipo int, FK.
    map_id: int = Field(..., examples=[1], description="ID do mapa.") # Variável (Escopo de Definição): Tipo int, FK.
    win_rate: float = Field(..., examples=[54.3], description="Taxa de vitória (float).") # Variável (Escopo de Definição): Tipo float.

class HeroRankMapPickData(BaseModel):
    # Define o Schema para a tabela 'hero_rank_map_pick' (Taxa de Escolha por Herói, Rank e Mapa).
    hero_id: int = Field(..., examples=[1], description="ID do herói.") # Variável (Escopo de Definição): Tipo int, FK.
    rank_id: int = Field(..., examples=[1], description="ID do rank.") # Variável (Escopo de Definição): Tipo int, FK.
    map_id: int = Field(..., examples=[1], description="ID do mapa.") # Variável (Escopo de Definição): Tipo int, FK.
    pick_rate: float = Field(..., examples=[12.5], description="Taxa de escolha (float).") # Variável (Escopo de Definição): Tipo float.

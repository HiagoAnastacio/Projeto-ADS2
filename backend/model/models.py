# FLUXO E A LÓGICA:
# 1. Este módulo define as estruturas de dados (Schemas) para toda a API.
# 2. As classes são importadas no **model_resolver.py** (Escopo Global/Módulo).
# 3. Uma classe específica (ex: HeroBase) é enviada para **validate_body** em tempo de requisição.
# 4. O Pydantic usa esta classe para comparar o JSON recebido com a estrutura definida aqui, garantindo tipos e campos corretos.
# RAZÃO DE EXISTIR: É a camada **Model/Schema Validation**. Garante a **integridade e tipagem** dos dados, protegendo a camada DAO (SQL) de dados malformados.

from pydantic import BaseModel, HttpUrl, Field # Razão de Existir: BaseModel (base de validação), HttpUrl (validação de URLs), Field (metadados, obrigatoriedade e exemplos).
from typing import Optional # Razão de Existir: Tipagem para campos que não são obrigatórios (permite None), útil para o UPDATE parcial.

# -----------------------------------------------------\
# 1. Modelos de Entidades Principais (Tabelas de Cadastro)
# -----------------------------------------------------\

class HeroBase(BaseModel):
    # Define o Schema base para a tabela 'hero'.
    hero_name: str = Field(..., examples=["Reinhardt"], description="Nome do herói (obrigatório).") # Variável (Escopo de Definição): Tipo str, obrigatório (Field(...)), corresponde à coluna 'hero_name'.
    hero_icon_img_link: Optional[HttpUrl] = Field(None, examples=["https://overwatch.com/hero/reinhardt.png"], description="Link opcional para o ícone do herói.") # Variável (Escopo de Definição): Tipo HttpUrl, opcional (Optional). Razão: O Pydantic valida se o valor é uma URL válida.
    
class MapBase(BaseModel):
    # Define o Schema base para a tabela 'map'.
    map_name: str = Field(..., examples=["King's Row"], description="Nome do mapa.") # Variável (Escopo de Definição): Tipo str, corresponde à coluna 'map_name'.

class RoleBase(BaseModel):
    # Define o Schema base para a tabela 'role'.
    role_name: str = Field(..., examples=["Tank"], description="Nome da função do herói (ex: Tank, DPS, Support).") # Variável (Escopo de Definição): Tipo str, corresponde à coluna 'role_name'.

class RankBase(BaseModel):
    # Define o Schema base para a tabela 'rank'.
    rank_name: str = Field(..., examples=["Grandmaster"], description="Nome do nível de habilidade/rank.") # Variável (Escopo de Definição): Tipo str, corresponde à coluna 'rank_name'.

class GameModeBase(BaseModel):
    # Define o Schema base para a tabela 'game_mode'.
    game_mode_name: str = Field(..., examples=["Competitive"], description="Nome do modo de jogo.") # Variável (Escopo de Definição): Tipo str, corresponde à coluna 'game_mode_name'.

# -----------------------------------------------------\
# 2. Modelos de Estatísticas (Tabelas de Fatos/Relacionamentos)
# -----------------------------------------------------\

class HeroWinData(BaseModel):
    # Define o Schema para a tabela 'hero_win' (Taxa de Vitória por Herói).
    hero_id: int = Field(..., examples=[1], description="ID do herói (Chave Estrangeira para 'hero').") # Variável (Escopo de Definição): Tipo int, representa a FK para a tabela 'hero'.
    win_rate: float = Field(..., examples=[50.5], description="Taxa de vitória (float).") # Variável (Escopo de Definição): Tipo float.

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
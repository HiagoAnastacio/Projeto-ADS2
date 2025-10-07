# =======================================================================================
# MÓDULO RESOLVEDOR DE MODELOS
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. O dicionário `TABLE_MODEL_MAPPING` é criado quando a aplicação inicia, mapeando
#    nomes de tabelas (strings) para suas classes Pydantic correspondentes.
# 2. A função `get_model_for_table` é chamada pela dependência `validate_body` durante
#    uma requisição. Ela recebe o nome da tabela da URL.
# 3. A função busca a classe Pydantic no dicionário e a retorna.
# 4. Se a tabela não estiver mapeada, um erro é levantado, resultando em um HTTP 400.
#
# RAZÃO DE EXISTIR: É o "tradutor" que conecta o mundo das URLs (strings) ao mundo
# da validação de dados (classes Pydantic). É a peça-chave que permite que nossas
# rotas CRUD sejam genéricas e dinâmicas.
# =======================================================================================

from typing import Type
from pydantic import BaseModel
# Importa todas as classes de schema Pydantic que serão mapeadas.
from model.models import (
    HeroBase, MapBase, RoleBase, RankBase, GameModeBase, 
    HeroMapPickData, HeroMapWinData,  HeroPickData, HeroWinData, HeroRankPickData, HeroRankWinData,
    HeroWinData, HeroPickData, HeroRankMapWinData, HeroRankMapPickData
)

# Variável 'TABLE_MODEL_MAPPING' (Escopo Global/Módulo): O dicionário de mapeamento.
# Chave: nome da tabela (string). Valor: Classe Pydantic correspondente.
TABLE_MODEL_MAPPING: dict[str, Type[BaseModel]] = {
    "hero": HeroBase,
    "map": MapBase,
    "role": RoleBase,
    "rank": RankBase,
    "game_mode": GameModeBase,
    "hero_win": HeroWinData,
    "hero_pick": HeroPickData,
    "hero_map_win": HeroMapWinData,
    "hero_map_pick": HeroMapPickData,
    "hero_rank_win": HeroRankWinData,
    "hero_rank_pick": HeroRankPickData,
    "hero_rank_map_win": HeroRankMapWinData,
    "hero_rank_map_pick": HeroRankMapPickData,
}

def get_model_for_table(table_name: str) -> Type[BaseModel]:
    """
    Retorna a classe do modelo Pydantic correspondente a uma tabela.
    """
    # Variável 'model' (Escopo de Requisição): Tenta buscar o modelo no dicionário.
    model = TABLE_MODEL_MAPPING.get(table_name.lower())
    
    # Se o nome da tabela não estiver no mapeamento, levanta um erro.
    if not model:
        raise ValueError(f"A tabela '{table_name}' não é válida ou não está mapeada para esta operação.")
        
    # Retorna a CLASSE Pydantic para a dependência `validate_body`.
    return model

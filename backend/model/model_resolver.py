# =======================================================================================
# MÓDULO RESOLVEDOR DE MODELOS (v0.5.0)
# =======================================================================================
# Mapeia nomes de tabelas/views (strings) para suas classes Pydantic correspondentes,
# permitindo que as rotas genéricas e a validação funcionem com a nova estrutura.
# =======================================================================================

from typing import Type
from pydantic import BaseModel
# Importa todos os modelos Pydantic definidos em models.py
from model.models import (
    # Dimensões (usar modelos Base para validação de escrita)
    HeroBase, MapBase, RoleBase, RankBase, GameModeBase,
    # Dimensões (usar modelos completos para leitura, se necessário mapear)
    # Hero, Map, Role, Rank, GameMode,

    # Novas Tabelas de Fato
    HeroWinData, HeroPickData,
    HeroRankWinData, HeroRankPickData,
    HeroMapWinData, HeroMapPickData,
    HeroGameModeWinData, HeroGameModePickData,
    HeroRankMapWinData, HeroRankMapPickData,
    # Novas Views _latest
    VWHeroWinLatest, VWHeroPickLatest,
    VWHeroRankWinLatest, VWHeroRankPickLatest,
    VWHeroMapWinLatest, VWHeroMapPickLatest,
    VWHeroGameModeWinLatest, VWHeroGameModePickLatest,
    VWHeroRankMapWinLatest, VWHeroRankMapPickLatest
)

# Mapeamento: Chave (nome da tabela/view string) -> Valor (Classe Pydantic)
# Usamos os modelos 'Base' para tabelas editáveis (para validação de POST/PUT)
# Usamos os modelos completos de dados/views para tabelas/views read-only
TABLE_MODEL_MAPPING: dict[str, Type[BaseModel]] = {
    # Tabelas de Dimensão (Editáveis - usar Base para validação de escrita)
    "hero": HeroBase,
    "map": MapBase,
    "role": RoleBase,
    "rank": RankBase,
    "game_mode": GameModeBase,

    # Novas Tabelas de Fato (Read-Only - mapear para modelos de dados completos)
    "hero_win": HeroWinData,
    "hero_pick": HeroPickData,
    "hero_rank_win": HeroRankWinData,
    "hero_rank_pick": HeroRankPickData,
    "hero_map_win": HeroMapWinData,
    "hero_map_pick": HeroMapPickData,
    "hero_game_mode_win": HeroGameModeWinData,
    "hero_game_mode_pick": HeroGameModePickData,
    "hero_rank_map_win": HeroRankMapWinData, # Granular mantida
    "hero_rank_map_pick": HeroRankMapPickData, # Granular mantida

    # Novas Views _latest (Read-Only)
    "vw_hero_win_latest": VWHeroWinLatest,
    "vw_hero_pick_latest": VWHeroPickLatest,
    "vw_hero_rank_win_latest": VWHeroRankWinLatest,
    "vw_hero_rank_pick_latest": VWHeroRankPickLatest,
    "vw_hero_map_win_latest": VWHeroMapWinLatest,
    "vw_hero_map_pick_latest": VWHeroMapPickLatest,
    "vw_hero_game_mode_win_latest": VWHeroGameModeWinLatest,
    "vw_hero_game_mode_pick_latest": VWHeroGameModePickLatest,
    "vw_hero_rank_map_win_latest": VWHeroRankMapWinLatest, # Granular mantida
    "vw_hero_rank_map_pick_latest": VWHeroRankMapPickLatest # Granular mantida
}

def get_model_for_table(table_name: str) -> Type[BaseModel]:
    """
    Retorna a classe do modelo Pydantic correspondente a uma tabela ou view.
    Levanta ValueError se o nome não for encontrado no mapeamento.
    """
    model = TABLE_MODEL_MAPPING.get(table_name)
    if model is None:
        raise ValueError(f"Modelo Pydantic não definido para a tabela/view: '{table_name}'")
    return model

# Nota: A função `create_example_json` (usada em `route_schema_models.py`)
# pode precisar de ajustes se os modelos Base não tiverem todos os campos
# esperados para um exemplo completo, mas deve funcionar razoavelmente bem.
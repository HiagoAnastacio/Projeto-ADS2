# =======================================================================================
# MÓDULO DE CONFIGURAÇÃO CENTRAL DE PERMISSÕES (v0.5.0)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Define quais tabelas/views podem ser lidas e quais podem ser escritas pela API.
# 2. As listas são importadas pelas rotas e dependências para validação.
# RAZÃO DE EXISTIR: Centralizar a gestão de segurança de acesso aos dados.
# =======================================================================================

# --- NÍVEIS DE PERMISSÃO ---

# Tabelas/Views que a API pode LER, mas NÃO modificar.
# Inclui as novas tabelas de fato (que são populadas pelo ETL)
# e as novas views _latest.
from re import A


READ_ONLY_TABLES = [
    # Novas Tabelas de Fato (Agregadas/Históricas)
    "hero_win",
    "hero_pick",
    "hero_rank_win",
    "hero_rank_pick",
    "hero_map_win",
    "hero_map_pick",
    "hero_game_mode_win",
    "hero_game_mode_pick",
    "hero_rank_map_win", # Tabela granular mantida
    "hero_rank_map_pick", # Tabela granular mantida

    # Novas Views _latest
    "vw_hero_win_latest",
    "vw_hero_pick_latest",
    "vw_hero_rank_win_latest",
    "vw_hero_rank_pick_latest",
    "vw_hero_map_win_latest",
    "vw_hero_map_pick_latest",
    "vw_hero_game_mode_win_latest",
    "vw_hero_game_mode_pick_latest",
    "vw_hero_rank_map_win_latest", # View _latest para a granular mantida
    "vw_hero_rank_map_pick_latest" # View _latest para a granular mantida
]

# Tabelas que a API pode LER E TAMBÉM modificar (criar, atualizar, deletar).
# Apenas as tabelas de dimensão.
EDITABLE_TABLES = [
    "hero",
    "map",
    "role",
    "rank",
    "game_mode"
    # Note: As tabelas de fato NÃO estão aqui, garantindo que só o ETL as popule.
]
ALLOWED_FILTER_COLUMNS = [
    "hero_id",
    "rank_id",
    "map_id",
    "game_mode_id",
    "role_id",
    "date_of_the_data" # Embora seja tratado separadamente
]

ALLOWED_FILTER_ANALYTIC_ROUTES = [
    "Analysis_Query"
]
# --- LISTAS CONSOLIDADAS PARA AS ROTAS ---

# Lista completa de tabelas/views e rotas analiticas que podem ser lidas via GET pela rota de schemas.
EVERTHING_READ_ONLY = READ_ONLY_TABLES + EDITABLE_TABLES + ALLOWED_FILTER_ANALYTIC_ROUTES + ALLOWED_FILTER_COLUMNS

# Lista completa de tabelas/views que podem ser lidas via GET (genérico ou por ID, se aplicável).
ALLOWED_GET_TABLES = READ_ONLY_TABLES + EDITABLE_TABLES

# Lista de tabelas que permitem operações de escrita (POST, PUT, DELETE).
ALLOWED_WRITE_TABLES = EDITABLE_TABLES

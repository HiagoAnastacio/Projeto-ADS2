# =======================================================================================
# MÓDULO DE CONFIGURAÇÃO CENTRAL DE PERMISSÕES
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Este arquivo define quais tabelas podem ser acessadas pela API e com qual nível
#    de permissão (apenas leitura ou escrita completa).
# 2. As listas aqui definidas são importadas pelos módulos de rotas (CRUD) para
#    validar se uma operação solicitada em uma tabela é permitida.
#
# RAZÃO DE EXISTIR: Centralizar a gestão de segurança de acesso às tabelas em um
# único local. Isso evita a duplicação de whitelists, reduz o risco de erros e
# facilita a manutenção ao adicionar ou remover tabelas da API. É a nossa "fonte
# única da verdade" para permissões de CRUD.
# =======================================================================================

# --- NÍVEIS DE PERMISSÃO ---

# Tabelas que a API pode ler, mas NUNCA modificar (criar, atualizar ou deletar).
# Inclui tabelas de fatos e views que são populadas exclusivamente pelo pipeline de ETL.
READ_ONLY_TABLES = [
    "vw_hero_win",
    "vw_hero_pick",
    "vw_hero_map_win",
    "vw_hero_map_pick",
    "vw_hero_rank_win",
    "vw_hero_rank_pick",
    "hero_rank_map_win",
    "hero_rank_map_pick"
]

# Tabelas que a API pode ler E TAMBÉM modificar (criar, atualizar, deletar).
# Geralmente são as tabelas de dimensão que podem necessitar de correção manual.
EDITABLE_TABLES = [
    "hero",
    "map",
    "role",
    "rank",
    "game_mode"
]

# --- LISTAS CONSOLIDADAS PARA AS ROTAS ---

# Lista completa de tabelas que podem ser lidas pela API (GET).
# Usada por: route_get.py, route_schema_models.py
ALLOWED_GET_TABLES = READ_ONLY_TABLES + EDITABLE_TABLES

# Lista completa de tabelas que podem ser modificadas pela API (POST, PUT, DELETE).
# Usada por: route_post.py, route_update.py, route_delete.py
ALLOWED_WRITE_TABLES = EDITABLE_TABLES
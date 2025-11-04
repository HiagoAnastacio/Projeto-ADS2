# =======================================================================================
# SCRIPT ORQUESTRADOR - PIPELINE DE FATOS (NÍVEL 3) (Refatorado SoC)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Este script orquestra a população de TODAS as 12 tabelas de fato.
# 2. A função `run_stats_pipeline` (antiga main_populate_facts) orquestra o processo:
#    a. LÊ todas as dimensões (`hero`, `rank`, `map`, `game_mode`) do DB.
#    b. Define as 3 lógicas de loop de extração (Rank+AllMaps, Rank+Maps, Rank+game_modes).
#    c. Em cada loop, chama o `info_lvl3_extractor.fetch_stats_data` (Extrator).
#    d. Chama o `stats_lvl3_loader.load_fact_data` (Loader) com o SQL e os dados corretos.
#
# RAZÃO DE EXISTIR: Isolar a lógica de *Orquestração* da população de fatos.
# Define o "fluxo" da Etapa 3, sem se preocupar com "como"
# os dados são extraídos ou carregados.
# =======================================================================================

import sys
import logging
import argparse
from typing import Dict, Any, List
from slugify import slugify
from types import SimpleNamespace
import datetime

# --- Configuração de Logger ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

# --- Importações da Aplicação ---
try:
    # Importa o executor de SQL (para buscar dimensões)
    from utils.function_execute import execute
    # Importa as funções de "Como Fazer" dos módulos especializados
    from services.extractors.info_stats_lvl3_extractor import fetch_stats_data, TIER_ALL
    from services.loaders.stats_lvl3_loader import load_fact_data
except ImportError:
    logger.error("Erro: Não foi possível importar módulos. Execute 'pip install -e .' na pasta 'backend'.")
    sys.exit(1)

# =======================================================================================
# FUNÇÃO PRINCIPAL (ORQUESTRADOR DE TAREFA)
# =======================================================================================

def run_stats_pipeline(args):
    """
    Função principal que orquestra a busca e carga de dados de fato.
    (Lógica `main` movida de populate_lvl3.py v0.7.0)
    """
    logger.info("--- Iniciando Etapa 3: População de Fatos (v0.7.0 - SoC Refactor) ---")
    
    # 1. CARREGAR DIMENSÕES
    logger.info("Carregando dimensões (heróis, ranks, mapas, modos de jogo)...")
    try:
        dims = {
            "heroes": {item['hero_name']: item['hero_id'] for item in execute("SELECT `hero_id`, `hero_name` FROM `hero`")},
            "ranks": {item['rank_name']: item['rank_id'] for item in execute("SELECT `rank_id`, `rank_name` FROM `rank`")},
            "maps": {item['map_name']: item['map_id'] for item in execute("SELECT `map_id`, `map_name` FROM `map`")},
            "game_modes": {item['game_mode_name']: item['game_mode_id'] for item in execute("SELECT `game_mode_id`, `game_mode_name` FROM `game_mode`")}
        }
        if not all([dims["heroes"], dims["ranks"], dims["maps"], dims["game_modes"]]):
             raise Exception("Tabelas de dimensão (hero, rank, map, game_mode) estão vazias.")
        logger.info(f"Dimensões carregadas: {len(dims['heroes'])} heróis, {len(dims['ranks'])} ranks, {len(dims['maps'])} mapas, {len(dims['game_modes'])} modos.")
    except Exception as e:
        logger.critical(f"Falha CRÍTICA ao carregar dimensões: {e}. Abortando.", exc_info=True)
        raise e

    # 2. DEFINIR LISTAS DE ITERAÇÃO
    ranks_to_iterate = [(rank_name, slugify(rank_name), rank_id) for rank_name, rank_id in dims["ranks"].items()]
    ranks_to_iterate.append(("All Ranks", TIER_ALL, None)) # (Nome, Slug, ID=None)

    maps_to_iterate = [(map_name, slugify(map_name), map_id) for map_name, map_id in dims["maps"].items()]
    maps_to_iterate.append(("All Maps", "all-maps", None)) # (Nome, Slug, ID=None)
    
    game_modes_to_iterate = [(gm_name, slugify(gm_name), gm_id) for gm_name, gm_id in dims["game_modes"].items()]

    limit_value = getattr(args, 'limit', 0)
    if limit_value > 0:
        ranks_to_iterate = ranks_to_iterate[:limit_value]
        maps_to_iterate = maps_to_iterate[:limit_value]
        game_modes_to_iterate = game_modes_to_iterate[:limit_value]
        logger.warning(f"Execução limitada a {limit_value} item(ns) por dimensão.")
    
    execution_timestamp = datetime.datetime.now().replace(microsecond=0)
    
    
    # 3. EXECUTAR OS LOOPS DE ETL (API)
    # Cada loop chama o Extrator e o Carregador apropriados.

    # --- LOOP 1: Popula `hero_win`/`pick` e `hero_rank_win`/`pick` ---
    logger.info("="*30)
    logger.info("Iniciando Loop 1: Agregados por Rank (map=all-maps)")
    logger.info("="*30)
    total_requests_loop1 = len(ranks_to_iterate)
    for i, (rank_name, rank_slug, rank_id) in enumerate(ranks_to_iterate):
        
        logger.info(f"Processando Loop 1 ({i+1}/{total_requests_loop1}): Rank='{rank_name}', Mapa='All Maps'")
        
        # Chama o Extrator
        data_list = fetch_stats_data(rank_slug=rank_slug, map_slug="all-maps")
        if not data_list: 
            continue

        try:
            context = {}
            if rank_name == "All Ranks": # tier=all, map=all-maps
                # Popula `hero_win` e `hero_pick` (Combinação 1)
                sql_win = "INSERT INTO `hero_win` (hero_id, win_rate, date_of_the_data) VALUES (%s, %s, %s)"
                sql_pick = "INSERT INTO `hero_pick` (hero_id, pick_rate, date_of_the_data) VALUES (%s, %s, %s)"
                # Chama o Carregador
                load_fact_data(sql_win, data_list, dims["heroes"], context, execution_timestamp)
                load_fact_data(sql_pick, data_list, dims["heroes"], context, execution_timestamp)
            else: # tier={slug}, map=all-maps
                # Popula `hero_rank_win` e `hero_rank_pick` (Combinação 4)
                context['rank_id'] = rank_id
                sql_win = "INSERT INTO `hero_rank_win` (hero_id, rank_id, win_rate, date_of_the_data) VALUES (%s, %s, %s, %s)"
                sql_pick = "INSERT INTO `hero_rank_pick` (hero_id, rank_id, pick_rate, date_of_the_data) VALUES (%s, %s, %s, %s)"
                load_fact_data(sql_win, data_list, dims["heroes"], context, execution_timestamp)
                load_fact_data(sql_pick, data_list, dims["heroes"], context, execution_timestamp)
        except Exception as e:
            logger.error(f"Erro ao carregar dados (Rank='{rank_name}', Mapa='All Maps'): {e}", exc_info=True)


    # --- LOOP 2: Popula `hero_map_win`/`pick` e `hero_rank_map_win`/`pick` ---
    logger.info("="*30)
    logger.info("Iniciando Loop 2: Agregados por Rank e Mapa (map={slug})")
    logger.info("="*30)
    maps_specific_iterate = [m for m in maps_to_iterate if m[1] != 'all-maps']
    total_requests_loop2 = len(ranks_to_iterate) * len(maps_specific_iterate)
    loop2_count = 0
    
    for rank_name, rank_slug, rank_id in ranks_to_iterate:
        for map_name, map_slug, map_id in maps_specific_iterate:
            
            loop2_count += 1
            logger.info(f"Processando Loop 2 ({loop2_count}/{total_requests_loop2}): Rank='{rank_name}', Mapa='{map_name}'")

            # Chama o Extrator
            data_list = fetch_stats_data(rank_slug=rank_slug, map_slug=map_slug)
            if not data_list: 
                continue
            
            try:
                context = {}
                if rank_name == "All Ranks": # tier=all, map={slug}
                    # Popula `hero_map_win` e `hero_map_pick` (Combinação 2)
                    context['map_id'] = map_id
                    sql_win = "INSERT INTO `hero_map_win` (hero_id, map_id, win_rate, date_of_the_data) VALUES (%s, %s, %s, %s)"
                    sql_pick = "INSERT INTO `hero_map_pick` (hero_id, map_id, pick_rate, date_of_the_data) VALUES (%s, %s, %s, %s)"
                    load_fact_data(sql_win, data_list, dims["heroes"], context, execution_timestamp)
                    load_fact_data(sql_pick, data_list, dims["heroes"], context, execution_timestamp)
                else: # tier={slug}, map={slug}
                    # Popula `hero_rank_map_win` e `hero_rank_map_pick` (Combinação 3)
                    context['rank_id'] = rank_id
                    context['map_id'] = map_id
                    sql_win = "INSERT INTO `hero_rank_map_win` (hero_id, rank_id, map_id, win_rate, date_of_the_data) VALUES (%s, %s, %s, %s, %s)"
                    sql_pick = "INSERT INTO `hero_rank_map_pick` (hero_id, rank_id, map_id, pick_rate, date_of_the_data) VALUES (%s, %s, %s, %s, %s)"
                    load_fact_data(sql_win, data_list, dims["heroes"], context, execution_timestamp)
                    load_fact_data(sql_pick, data_list, dims["heroes"], context, execution_timestamp)
            except Exception as e:
                logger.error(f"Erro ao carregar dados (Rank='{rank_name}', Mapa='{map_name}'): {e}", exc_info=True)


    # --- LOOP 3: Popula `hero_game_mode_win`/`pick` e `hero_game_mode_rank_win`/`pick` ---
    logger.info("="*30)
    logger.info("Iniciando Loop 3: Agregados por Rank e Modo de Jogo (map={game_mode_slug})")
    logger.info("="*30)
    total_requests_loop3 = len(ranks_to_iterate) * len(game_modes_to_iterate)
    loop3_count = 0
    
    for rank_name, rank_slug, rank_id in ranks_to_iterate:
        for gm_name, gm_slug, gm_id in game_modes_to_iterate:
            
            loop3_count += 1
            logger.info(f"Processando Loop 3 ({loop3_count}/{total_requests_loop3}): Rank='{rank_name}', Modo='{gm_name}'")

            # Chama o Extrator
            data_list = fetch_stats_data(rank_slug=rank_slug, map_slug=gm_slug)
            if not data_list: 
                continue
            
            try:
                context = {}
                if rank_name == "All Ranks": # tier=all, map={game_mode_slug}
                    # Popula `hero_game_mode_win` e `hero_game_mode_pick` (Combinação 6)
                    context['game_mode_id'] = gm_id
                    sql_win = "INSERT INTO `hero_game_mode_win` (hero_id, game_mode_id, win_rate, date_of_the_data) VALUES (%s, %s, %s, %s)"
                    sql_pick = "INSERT INTO `hero_game_mode_pick` (hero_id, game_mode_id, pick_rate, date_of_the_data) VALUES (%s, %s, %s, %s)"
                    load_fact_data(sql_win, data_list, dims["heroes"], context, execution_timestamp)
                    load_fact_data(sql_pick, data_list, dims["heroes"], context, execution_timestamp)
                else: # tier={slug}, map={game_mode_slug}
                    # Popula `hero_game_mode_rank_win` e `hero_game_mode_rank_pick` (Combinação 5)
                    context['rank_id'] = rank_id
                    context['game_mode_id'] = gm_id
                    sql_win = "INSERT INTO `hero_game_mode_rank_win` (hero_id, rank_id, game_mode_id, win_rate, date_of_the_data) VALUES (%s, %s, %s, %s, %s)"
                    sql_pick = "INSERT INTO `hero_game_mode_rank_pick` (hero_id, rank_id, game_mode_id, pick_rate, date_of_the_data) VALUES (%s, %s, %s, %s, %s)"
                    load_fact_data(sql_win, data_list, dims["heroes"], context, execution_timestamp)
                    load_fact_data(sql_pick, data_list, dims["heroes"], context, execution_timestamp)
            except Exception as e:
                logger.error(f"Erro ao carregar dados (Rank='{rank_name}', Modo='{gm_name}'): {e}", exc_info=True)

    
    # 4. REMOVIDA A ETAPA DE DERIVAÇÃO
    logger.info("Coleta da API e população de fatos concluída. Nenhuma derivação SQL foi necessária.")
    logger.info("Execução do script de população de fatos (Etapa 3) concluída.")


# --- Ponto de Entrada (se executado diretamente com argparse) ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Popula TODAS as tabelas de fato (v0.7.0) de Overwatch.")
    parser.add_argument("-l", "--limit", type=int, default=0, help="Limita o número de ranks, mapas e modos de jogo processados (para testes).")
    script_args = parser.parse_args()
    
    limit_msg = f"com limite de {script_args.limit}" if script_args.limit > 0 else "sem limite"
    logger.info(f"Executando 'run_stats_pipeline.py' (v0.7.0 - Refatorado) diretamente {limit_msg}.")
    try:
        run_stats_pipeline(script_args)
        logger.info("Execução direta concluída com sucesso.")
    except Exception as e:
        logger.critical(f"Falha crítica na execução direta: {e}", exc_info=True)
        sys.exit(1)
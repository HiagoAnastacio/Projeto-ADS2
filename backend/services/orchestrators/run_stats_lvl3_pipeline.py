# =======================================================================================
# SCRIPT ORQUESTRADOR - PIPELINE DE FATOS (NÍVEL 3) (v0.8.x - Fix Rank Slug + Derivação)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Este script orquestra a população de TODAS as 12 tabelas de fato.
# 2. (MUDANÇA v0.8.3) A Etapa 2 (Definir Listas) foi corrigida para usar o
#    `rank_name` capitalizado como o `rank_slug`, pois a API (ex: tier=Bronze)
#    é case-sensitive e não aceita slugs minúsculos.
# 3. A Etapa 3 (Coleta da API) busca os dados que a API fornece diretamente:
#    - Loop 1 (Rank + "all-maps"): Popula `hero_win` e `hero_rank_win`.
#    - Loop 2 (Rank + Mapas): Popula `hero_map_win` e `hero_rank_map_win`.
# 4. (MUDANÇA v0.8.0) A Etapa 4 (Derivação SQL) é REINTRODUZIDA para calcular
#    corretamente as tabelas `hero_game_mode_*` e `hero_game_mode_rank_*` a partir
#    dos dados coletados na Etapa 3, usando `GROUP BY` e `AVG()`.
#
# RAZÃO DE EXISTIR: Isolar a lógica de *Orquestração* da população de fatos.
# =======================================================================================

import sys
import logging
import argparse
from typing import Dict, Any, List
from slugify import slugify # Ainda necessário para mapas e modos de jogo
from types import SimpleNamespace
import datetime

# --- Configuração de Logger ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

# --- Importações da Aplicação ---
try:
    # Importa o executor de SQL (para buscar dimensões e carregar derivações)
    from utils.function_execute import execute
    # Importa o Extrator de stats e o Loader de stats
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
    (v0.8.3 - Corrigido bug do slug de rank e reintroduzida a derivação)
    """
    logger.info("--- Iniciando Etapa 3: População de Fatos (v0.8.3 - Fix Rank Slug + Derivação) ---")
    
    # 1. CARREGAR DIMENSÕES
    logger.info("Carregando dimensões (heróis, ranks, mapas, map_to_game_mode)...")
    try:
        dims = {
            "heroes": {item['hero_name']: item['hero_id'] for item in execute("SELECT `hero_id`, `hero_name` FROM `hero`")},
            "ranks": {item['rank_name']: item['rank_id'] for item in execute("SELECT `rank_id`, `rank_name` FROM `rank`")},
            "maps": {item['map_name']: item['map_id'] for item in execute("SELECT `map_id`, `map_name` FROM `map`")},
            # Necessário para a Etapa 4 de Derivação
            "map_to_game_mode": {item['map_id']: item['game_mode_id'] for item in execute("SELECT m.map_id, m.game_mode_id FROM `map` m")}
        }
        if not all([dims["heroes"], dims["ranks"], dims["maps"]]):
             raise Exception("Tabelas de dimensão (hero, rank, map) estão vazias.")
        logger.info(f"Dimensões carregadas: {len(dims['heroes'])} heróis, {len(dims['ranks'])} ranks, {len(dims['maps'])} mapas.")
    except Exception as e:
        logger.critical(f"Falha CRÍTICA ao carregar dimensões: {e}. Abortando.", exc_info=True)
        raise e

    # 2. DEFINIR LISTAS DE ITERAÇÃO
    
    # --- (CORREÇÃO v0.8.3) ---
    # Linha 81: Não usamos `slugify(rank_name)`. Usamos `rank_name` diretamente,
    #         pois a API espera o nome capitalizado (ex: "Bronze").
    ranks_to_iterate = [(rank_name, rank_name, rank_id) for rank_name, rank_id in dims["ranks"].items()]
    # --- FIM DA CORREÇÃO ---
    
    ranks_to_iterate.append(("All Ranks", TIER_ALL, None)) # (Nome, Slug, ID=None)

    # `slugify` ainda é correto para mapas (ex: "colosseo")
    maps_to_iterate = [(map_name, slugify(map_name), map_id) for map_name, map_id in dims["maps"].items()]
    maps_to_iterate.append(("All Maps", "all-maps", None)) # (Nome, Slug, ID=None)
    
    # (Loop 3 (game_modes_to_iterate) foi removido pois será derivado)

    # Limite de teste (se --limit foi passado)
    limit_value = getattr(args, 'limit', 0)
    if limit_value > 0:
        ranks_to_iterate = ranks_to_iterate[:limit_value]
        maps_to_iterate = maps_to_iterate[:limit_value]
        logger.warning(f"Execução limitada a {limit_value} item(ns) por dimensão.")
    
    # Gera um timestamp "naive" e sem microssegundos (essencial para a Etapa 4).
    execution_timestamp = datetime.datetime.now().replace(microsecond=0)
    
    
    # 3. EXECUTAR OS LOOPS DE ETL (API)

    # --- LOOP 1: Popula `hero_win`/`pick` e `hero_rank_win`/`pick` ---
    # (Itera sobre Ranks, usando map=all-maps)
    logger.info("="*30)
    logger.info("Iniciando Loop 1: Agregados por Rank (map=all-maps)")
    logger.info("="*30)
    total_requests_loop1 = len(ranks_to_iterate)
    for i, (rank_name, rank_slug, rank_id) in enumerate(ranks_to_iterate):
        
        # Agora `rank_slug` será "Bronze", "Silver", etc. (ou "all")
        logger.info(f"Processando Loop 1 ({i+1}/{total_requests_loop1}): Rank='{rank_name}', Mapa='All Maps'")
        
        # Chama o Extrator
        data_list = fetch_stats_data(rank_slug=rank_slug, map_slug="all-maps")
        if not data_list: continue

        try:
            context = {}
            if rank_name == "All Ranks": # tier=all, map=all-maps
                # Popula `hero_win` e `hero_pick` (Combinação 1)
                sql_win = "INSERT INTO `hero_win` (hero_id, win_rate, date_of_the_data) VALUES (%s, %s, %s)"
                sql_pick = "INSERT INTO `hero_pick` (hero_id, pick_rate, date_of_the_data) VALUES (%s, %s, %s)"
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
    # (Itera sobre Ranks E Mapas (exceto "all-maps"))
    logger.info("="*30)
    logger.info("Iniciando Loop 2: Agregados por Rank e Mapa (map={slug})")
    logger.info("="*30)
    maps_specific_iterate = [m for m in maps_to_iterate if m[1] != 'all-maps']
    total_requests_loop2 = len(ranks_to_iterate) * len(maps_specific_iterate)
    loop2_count = 0
    
    for rank_name, rank_slug, rank_id in ranks_to_iterate:
        for map_name, map_slug, map_id in maps_specific_iterate:
            
            loop2_count += 1
            # Agora `rank_slug` será "Bronze", "Silver", etc. (ou "all")
            logger.info(f"Processando Loop 2 ({loop2_count}/{total_requests_loop2}): Rank='{rank_name}', Mapa='{map_name}'")

            # Chama o Extrator
            data_list = fetch_stats_data(rank_slug=rank_slug, map_slug=map_slug)
            if not data_list: continue
            
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

    
    # --- ETAPA 4: EXECUTAR QUERIES DE DERIVAÇÃO (Para game_mode) ---
    #    (Restaurada e Corrigida)
    
    logger.info(f"Coleta da API concluída. Iniciando derivação de agregados (game_mode) para o timestamp: {execution_timestamp}...")
    try:
        # 4a. Popular `hero_game_mode_win` e `hero_game_mode_pick` (derivado de hero_map_win/pick)
        logger.info("Calculando `hero_game_mode_win` (derivado de hero_map_win)...")
        # Query: Calcula a média de 'hero_map_win' agrupando por 'game_mode_id'
        sql_derive_hgw = """
            INSERT INTO `hero_game_mode_win` (hero_id, game_mode_id, win_rate, date_of_the_data)
            SELECT
                hmw.hero_id,
                m.game_mode_id,
                AVG(hmw.win_rate) as avg_win_rate,
                %s
            FROM `hero_map_win` hmw
            JOIN `map` m ON hmw.map_id = m.map_id
            WHERE hmw.date_of_the_data = %s
            GROUP BY hmw.hero_id, m.game_mode_id;
        """
        execute(sql_derive_hgw, (execution_timestamp, execution_timestamp))
        
        logger.info("Calculando `hero_game_mode_pick` (derivado de hero_map_pick)...")
        sql_derive_hgp = """
            INSERT INTO `hero_game_mode_pick` (hero_id, game_mode_id, pick_rate, date_of_the_data)
            SELECT
                hmp.hero_id,
                m.game_mode_id,
                AVG(hmp.pick_rate) as avg_pick_rate,
                %s
            FROM `hero_map_pick` hmp
            JOIN `map` m ON hmp.map_id = m.map_id
            WHERE hmp.date_of_the_data = %s
            GROUP BY hmp.hero_id, m.game_mode_id;
        """
        execute(sql_derive_hgp, (execution_timestamp, execution_timestamp))

        # 4b. Popular `hero_game_mode_rank_win` e `hero_game_mode_rank_pick` (derivado de hero_rank_map_win/pick)
        logger.info("Calculando `hero_game_mode_rank_win` (derivado de hero_rank_map_win)...")
        # Query: Calcula a média de 'hero_rank_map_win' agrupando por 'game_mode_id' E 'rank_id'
        sql_derive_hgrw = """
            INSERT INTO `hero_game_mode_rank_win` (hero_id, game_mode_id, rank_id, win_rate, date_of_the_data)
            SELECT
                hrmw.hero_id,
                m.game_mode_id,
                hrmw.rank_id,
                AVG(hrmw.win_rate) as avg_win_rate,
                %s
            FROM `hero_rank_map_win` hrmw
            JOIN `map` m ON hrmw.map_id = m.map_id
            WHERE hrmw.date_of_the_data = %s
            GROUP BY hrmw.hero_id, m.game_mode_id, hrmw.rank_id;
        """
        execute(sql_derive_hgrw, (execution_timestamp, execution_timestamp))

        logger.info("Calculando `hero_game_mode_rank_pick` (derivado de hero_rank_map_pick)...")
        sql_derive_hgrp = """
            INSERT INTO `hero_game_mode_rank_pick` (hero_id, game_mode_id, rank_id, pick_rate, date_of_the_data)
            SELECT
                hrmp.hero_id,
                m.game_mode_id,
                hrmp.rank_id,
                AVG(hrmp.pick_rate) as avg_pick_rate,
                %s
            FROM `hero_rank_map_pick` hrmp
            JOIN `map` m ON hrmp.map_id = m.map_id
            WHERE hrmp.date_of_the_data = %s
            GROUP BY hrmp.hero_id, m.game_mode_id, hrmp.rank_id;
        """
        execute(sql_derive_hgrp, (execution_timestamp, execution_timestamp))
        
        logger.info("Derivação de agregados (Game_mode e Game_modeRank) concluída com sucesso.")

    except Exception as e:
        logger.error(f"Falha CRÍTICA durante a derivação de agregados: {e}", exc_info=True)
        # Tenta reverter dados da API
        try:
            logger.warning(f"Tentando reverter inserções parciais da API para o timestamp: {execution_timestamp}")
            tables_to_delete = [
                'hero_win', 'hero_pick', 'hero_rank_win', 'hero_rank_pick', 
                'hero_map_win', 'hero_map_pick',
                'hero_rank_map_win', 'hero_rank_map_pick'
                # Não deleta as tabelas de derivação, pois elas falharam ou não rodaram
            ]
            for table in tables_to_delete:
                execute(f"DELETE FROM `{table}` WHERE date_of_the_data = %s", (execution_timestamp,))
            logger.info("Reversão de dados parciais (API) concluída.")
        except Exception as del_e:
            logger.error(f"Falha CRÍTICA ao reverter dados parciais: {del_e}")
            
        raise e # Para o pipeline

    logger.info("Execução do script de população de fatos (Etapa 3) concluída.")


# --- Ponto de Entrada (se executado diretamente com argparse) ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Popula TODAS as tabelas de fato (v0.8.3) de Overwatch.")
    parser.add_argument("-l", "--limit", type=int, default=0, help="Limita o número de ranks e mapas processados (para testes).")
    script_args = parser.parse_args()
    
    limit_msg = f"com limite de {script_args.limit}" if script_args.limit > 0 else "sem limite"
    logger.info(f"Executando 'run_stats_pipeline.py' (v0.8.3) diretamente {limit_msg}.")
    try:
        run_stats_pipeline(script_args)
        logger.info("Execução direta concluída com sucesso.")
    except Exception as e:
        logger.critical(f"Falha crítica na execução direta: {e}", exc_info=True)
        sys.exit(1)
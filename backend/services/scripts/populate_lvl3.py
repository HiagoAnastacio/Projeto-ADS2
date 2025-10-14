# =======================================================================================
# SCRIPT ORQUESTRADOR - POPULAÇÃO DE TABELAS DE FATO (NÍVEL 3)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. É o "coletor" principal, responsável por buscar as estatísticas dinâmicas.
# 2. A função `main_populate_facts` orquestra o processo:
#    a. LÊ todas as tabelas de dimensão (`hero`, `rank`, `map`) para a memória.
#    b. Entra em um loop aninhado, iterando sobre cada `rank` e cada `map`.
#    c. CHAMA o helper `fetch_api_data` para cada combinação, buscando os dados granulares.
#    d. CHAMA a função local `load_stats_to_db` para inserir os dados nas tabelas de fato.
#
# RAZÃO DE EXISTIR: Orquestrar a busca massiva de dados estatísticos, assumindo que
# todas as dimensões já foram populadas. É a etapa final e mais demorada do pipeline.
# =======================================================================================

import sys
import logging
import argparse
from typing import Dict, Any, List
from slugify import slugify

# --- Configuração de Logger ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

# --- Importações da Aplicação ---
from utils.function_execute import execute
from utils.extraction_helpers import fetch_api_data

# --- LÓGICA DE CARGA (LOAD) ---
def load_stats_to_db(records: Dict[str, Dict[str, float]], rank_id: int, map_id: int, hero_map: Dict[str, int]):
    """Carrega as estatísticas transformadas para as tabelas de fato."""
    sql_win = """
        INSERT INTO `hero_rank_map_win` (`hero_id`, `rank_id`, `map_id`, `win_rate`)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE win_rate = VALUES(win_rate), date_of_the_data = CURRENT_TIMESTAMP;
    """
    sql_pick = """
        INSERT INTO `hero_rank_map_pick` (`hero_id`, `rank_id`, `map_id`, `pick_rate`)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE pick_rate = VALUES(pick_rate), date_of_the_data = CURRENT_TIMESTAMP;
    """
    for hero_name, stats in records.items():
        hero_id = hero_map.get(hero_name)
        if hero_id:
            execute(sql_win, (hero_id, rank_id, map_id, stats.get("win_rate", 0)))
            execute(sql_pick, (hero_id, rank_id, map_id, stats.get("pick_rate", 0)))

# --- ORQUESTRAÇÃO ---
def main_populate_facts(args):
    """Função principal que orquestra a busca e carga das estatísticas."""
    logger.info("--- LENDO DIMENSÕES DO BANCO DE DADOS ---")
    dims = {
        "heroes": {h['hero_name']: h['hero_id'] for h in execute("SELECT hero_id, hero_name FROM hero")},
        "ranks": {r['rank_name']: r['rank_id'] for r in execute("SELECT rank_id, rank_name FROM `rank`")},
        "maps": {m['map_name']: m['map_id'] for m in execute("SELECT map_id, map_name FROM map")}
    }
    
    logger.info("--- INICIANDO BUSCA E CARGA DE DADOS DE FATO (WIN/PICK RATE) ---")
    base_url = "https://overwatch.blizzard.com/pt-br/rates/data?"
    
    ranks_to_process = list(dims["ranks"].items())
    if args.limit > 0:
        ranks_to_process = ranks_to_process[:args.limit]
        logger.warning(f"Execução limitada a {args.limit} rank(s).")
    
    for rank_name, rank_id in ranks_to_process:
        logger.info(f"== Processando Rank: {rank_name} ==")
        for map_name, map_id in dims["maps"].items():
            params = f"platform=pc&gamemode=competitive&rank={slugify(rank_name)}&map={slugify(map_name)}"
            api_url = f"{base_url}{params}"
            raw_data = fetch_api_data(api_url)
            if raw_data:
                # A API já retorna os dados transformados, prontos para carga.
                load_stats_to_db(raw_data, rank_id, map_id, dims["heroes"])
            else:
                logger.warning(f"Não foram encontrados dados para Rank: '{rank_name}', Mapa: '{map_name}'")
                
    logger.info("Execução do script de população de fatos concluída.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script para popular as tabelas de fato com estatísticas.")
    parser.add_argument("--limit", type=int, default=0, help="Limita a execução a um número X de ranks para testes.")
    args = parser.parse_args()
    main_populate_facts(args)
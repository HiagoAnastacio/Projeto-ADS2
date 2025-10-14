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
from os.path import abspath, dirname
from typing import Dict, Any, List

# --- Configuração de Path e Logger ---
project_root = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(project_root)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

# --- Importações ---
try:
    from utils.function_execute import execute
    from utils.extraction_helpers import fetch_api_data
except ImportError as e:
    logger.error(f"Erro ao importar módulos. {e}")
    sys.exit(1)

# --- LÓGICA DE CARGA (LOAD) ESPECÍFICA DESTE SCRIPT ---
def load_stats_to_db(records: List[Dict[str, Any]], rank_id: int, map_id: int, hero_map: Dict[str, int]):
    """Insere ou atualiza um lote de estatísticas nas tabelas de fato."""
    if not records:
        return
    sql_win = "INSERT INTO `hero_rank_map_win` (`hero_id`, `rank_id`, `map_id`, `win_rate`) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE `win_rate`=VALUES(`win_rate`);"
    sql_pick = "INSERT INTO `hero_rank_map_pick` (`hero_id`, `rank_id`, `map_id`, `pick_rate`) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE `pick_rate`=VALUES(`pick_rate`);"

    for record in records:
        hero_id = hero_map.get(record["hero_name"])
        if hero_id:
            execute(sql_win, (hero_id, rank_id, map_id, record["win_rate"]))
            execute(sql_pick, (hero_id, rank_id, map_id, record["pick_rate"]))

# --- FUNÇÕES AUXILIARES E ORQUESTRAÇÃO ---
def load_all_dimensions_from_db() -> Dict[str, Dict[str, int]]:
    """Carrega todas as dimensões do DB para mapas de consulta rápida em memória."""
    logger.info("Carregando todas as dimensões (heroes, ranks, maps) do DB para a memória...")
    try:
        heroes = execute("SELECT `hero_id`, `hero_name` FROM `hero`")
        ranks = execute("SELECT `rank_id`, `rank_name` FROM `rank`")
        maps = execute("SELECT `map_id`, `map_name` FROM `map`")
        if not all([heroes, ranks, maps]):
            logger.error("Tabelas de dimensão estão vazias. Execute os scripts de população de Nível 1 e 2 primeiro.")
            sys.exit(1)
        dimensions = {
            "heroes": {item['hero_name']: item['hero_id'] for item in heroes},
            "ranks": {item['rank_name']: item['rank_id'] for item in ranks},
            "maps": {item['map_name']: item['map_id'] for item in maps}
        }
        logger.info("Dimensões carregadas com sucesso.")
        return dimensions
    except Exception as e:
        logger.error(f"Falha ao carregar dimensões do banco de dados: {e}", exc_info=True)
        sys.exit(1)

def transform_stats_data(raw_data: dict) -> list:
    """Transforma a resposta JSON da API em uma lista de dicionários limpos."""
    records = []
    for hero_data in raw_data.get("rates", []):
        details = hero_data.get("hero", {})
        stats = hero_data.get("cells", {})
        if details.get("name") and stats.get("winrate") is not None and stats.get("pickrate") is not None:
            records.append({ "hero_name": details["name"], "win_rate": stats["winrate"], "pick_rate": stats["pickrate"] })
    return records
    
def slugify(text: str) -> str:
    """Converte nomes para o formato de URL."""
    return text.lower().replace("'", "").replace(" ", "-").replace(":", "")

def main_populate_facts(args=None):
    """Orquestra a população das tabelas de fato (estatísticas)."""
    if args is None:
        class Args:
            limit = 0; verbose = False
        args = Args()

    if args.verbose: logger.setLevel(logging.DEBUG)

    dimensions = load_all_dimensions_from_db()
    logger.info("--- Iniciando população das tabelas de fato (Nível 3) ---")
    base_url = "https://overwatch.blizzard.com/pt-br/rates/data?"
    
    ranks_to_process = list(dimensions["ranks"].items())
    if args.limit > 0:
        ranks_to_process = ranks_to_process[:args.limit]
        logger.warning(f"Execução limitada a {args.limit} rank(s).")
    
    for rank_name, rank_id in ranks_to_process:
        logger.info(f"== Processando Rank: {rank_name} ==")
        for map_name, map_id in dimensions["maps"].items():
            params = f"platform=pc&gamemode=competitive&rank={slugify(rank_name)}&map={slugify(map_name)}"
            api_url = f"{base_url}{params}"
            raw_data = fetch_api_data(api_url)
            if raw_data:
                transformed_records = transform_stats_data(raw_data)
                load_stats_to_db(transformed_records, rank_id, map_id, dimensions["heroes"])
            else:
                logger.warning(f"Não foram encontrados dados para Rank: '{rank_name}', Mapa: '{map_name}'")
                
    logger.info("Execução do script de população de fatos concluída.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script para popular as tabelas de fato com estatísticas.")
    parser.add_argument("-l", "--limit", type=int, default=0, help="Limita o número de ranks a serem processados.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Aumenta a verbosidade.")
    cli_args = parser.parse_args()
    main_populate_facts(cli_args)
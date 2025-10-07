import sys
import logging
import argparse
from os.path import abspath, dirname
from typing import Dict, Any, List

# --- AJUSTE CRÍTICO DE PATH ---
# Razão: Mesmo motivo do populate_lvl2.py, precisamos alcançar a pasta 'backend'.
project_root = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(project_root)

# Configuração de Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

# Importações da Aplicação e dos Helpers
try:
    from utils.function_execute import execute
    from utils.data_populate_help import fetch_api_data, load_stats_to_db
except ImportError as e:
    logger.error(f"Erro ao importar módulos. {e}")
    sys.exit(1)

# Funções auxiliares específicas deste script
def load_all_dimensions_from_db() -> Dict[str, Dict[str, int]]:
    """Carrega todas as dimensões do DB para mapas de consulta rápida em memória."""
    logger.info("Carregando todas as dimensões (heroes, ranks, maps) do DB para a memória...")
    try:
        heroes = execute("SELECT `hero_id`, `hero_name` FROM `hero`")
        ranks = execute("SELECT `rank_id`, `rank_name` FROM `rank`")
        maps = execute("SELECT `map_id`, `map_name` FROM `map`")
        
        if not all([heroes, ranks, maps]):
            logger.error("Uma ou mais tabelas de dimensão estão vazias. Execute os scripts de 'seed' e de população de dimensões primeiro.")
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

# Função principal encapsulada para ser importável.
def main_populate_facts(args=None):
    """Orquestra a população das tabelas de fato (estatísticas)."""
    if args is None:
        # Se nenhum argumento for passado (ex: chamado pelo scheduler), usa valores padrão.
        class Args:
            limit = 0
            verbose = False
        args = Args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # 1. Preparação: Carrega dimensões
    dimensions = load_all_dimensions_from_db()
    
    logger.info("--- Iniciando população das tabelas de fato (Nível 3) ---")
    base_url = "https://overwatch.blizzard.com/pt-br/rates/data?"
    
    ranks_to_process = list(dimensions["ranks"].items())
    if args.limit > 0:
        ranks_to_process = ranks_to_process[:args.limit]
        logger.warning(f"Execução limitada a {args.limit} rank(s).")
    
    # 2. Orquestração: O grande loop que define QUAIS dados buscar
    for rank_name, rank_id in ranks_to_process:
        logger.info(f"== Processando Rank: {rank_name} ==")
        for map_name, map_id in dimensions["maps"].items():
            
            params = f"platform=pc&gamemode=competitive&rank={slugify(rank_name)}&map={slugify(map_name)}"
            api_url = f"{base_url}{params}"

            # 3. Execução: Chama os helpers para fazer o trabalho
            raw_data = fetch_api_data(api_url)
            if raw_data:
                transformed_records = transform_stats_data(raw_data)
                load_stats_to_db(transformed_records, execute, rank_id, map_id, dimensions["heroes"])
            else:
                logger.warning(f"Não foram encontrados dados para Rank: '{rank_name}', Mapa: '{map_name}'")
                
    logger.info("Execução do script de população de fatos concluída.")

# Ponto de Entrada para permitir execução manual do script.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script para popular as tabelas de fato com estatísticas.")
    parser.add_argument("-l", "--limit", type=int, default=0, help="Limita o número de ranks a serem processados (para testes).")
    parser.add_argument("-v", "--verbose", action="store_true", help="Aumenta a verbosidade.")
    cli_args = parser.parse_args()
    main_populate_facts(cli_args)
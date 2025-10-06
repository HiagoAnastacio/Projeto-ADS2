import requests, sys, logging, argparse, json
from os.path import abspath, dirname
from typing import Dict, Any, List

project_root = dirname(dirname(abspath(__file__)))
sys.path.append(project_root)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

try:
    from utils.function_execute import execute
except ImportError as e:
    logger.error(f"Erro ao importar módulos: {e}")
    sys.exit(1)

def load_all_dimensions_from_db() -> Dict[str, Dict[str, int]]:
    """Carrega as tabelas de dimensão do DB para mapas de consulta rápida em memória."""
    logger.info("Carregando todas as dimensões (heroes, ranks, maps) do DB para a memória...")
    try:
        heroes = execute("SELECT hero_id, hero_name FROM hero")
        
        # AJUSTE: Adicionadas crases (`) para proteger o nome da tabela `rank`.
        ranks = execute("SELECT rank_id, rank_name FROM `rank`")
        
        maps = execute("SELECT map_id, map_name FROM map")
        
        if not all([heroes, ranks, maps]):
            logger.error("Uma ou mais tabelas de dimensão estão vazias. Execute os scripts 'seed' e 'populate_dimensions' primeiro.")
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

def fetch_stats_from_api(api_url: str) -> dict | None:
    """Faz uma chamada à API para obter dados estatísticos."""
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    headers = {'User-Agent': user_agent}
    logger.debug(f"Buscando estatísticas de: {api_url}")
    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except json.JSONDecodeError:
        logger.warning(f"Resposta não é um JSON válido para a URL: {api_url}")
        logger.debug(f"Conteúdo recebido (início): {response.text[:200]}")
        return None
    except requests.exceptions.RequestException as e:
        logger.warning(f"Erro na requisição para {api_url}: {e}")
        return None

def transform_stats_data(raw_data: dict) -> list:
    """Transforma a resposta JSON da API em uma lista de dicionários limpos."""
    records = []
    for hero_data in raw_data.get("rates", []):
        hero_details = hero_data.get("hero", {})
        hero_stats = hero_data.get("cells", {})
        if hero_details.get("name") and hero_stats.get("winrate") is not None and hero_stats.get("pickrate") is not None:
            records.append({
                "hero_name": hero_details["name"],
                "win_rate": hero_stats["winrate"],
                "pick_rate": hero_stats["pickrate"]
            })
    return records
    
def load_stats_to_db(records: List[Dict[str, Any]], rank_id: int, map_id: int, hero_map: Dict[str, int]):
    """Insere um lote de estatísticas nas tabelas de fato."""
    if not records:
        return

    sql_win = "INSERT INTO hero_rank_map_win (hero_id, rank_id, map_id, win_rate) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE win_rate=VALUES(win_rate);"
    sql_pick = "INSERT INTO hero_rank_map_pick (hero_id, rank_id, map_id, pick_rate) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE pick_rate=VALUES(pick_rate);"

    for record in records:
        hero_id = hero_map.get(record["hero_name"])
        if hero_id:
            execute(sql_win, (hero_id, rank_id, map_id, record["win_rate"]))
            execute(sql_pick, (hero_id, rank_id, map_id, record["pick_rate"]))

def slugify(text: str) -> str:
    """Converte nomes para o formato de URL."""
    return text.lower().replace("'", "").replace(" ", "-").replace(":", "")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script para popular as tabelas de fato com estatísticas do Overwatch.")
    parser.add_argument("-p", "--platform", type=str, default="pc", help="Plataforma (pc, console).")
    parser.add_argument("-gm", "--gamemode", type=str, default="competitive", help="Modo de jogo (competitive, quickplay).")
    parser.add_argument("-l", "--limit", type=int, default=0, help="Limita o número de ranks a serem processados (para testes).")
    parser.add_argument("-v", "--verbose", action="store_true", help="Aumenta a verbosidade para nível DEBUG.")
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    dimensions = load_all_dimensions_from_db()
    
    logger.info("--- Iniciando população das tabelas de fato (Nível 3) ---")
    base_url = "https://overwatch.blizzard.com/pt-br/rates/data?"
    
    ranks_to_process = list(dimensions["ranks"].items())
    if args.limit > 0:
        ranks_to_process = ranks_to_process[:args.limit]
        logger.warning(f"Execução limitada a {args.limit} rank(s).")

    maps_to_process = list(dimensions["maps"].items())
    
    for rank_name, rank_id in ranks_to_process:
        logger.info(f"== Processando Rank: {rank_name} ==")
        for map_name, map_id in maps_to_process:
            
            params = f"platform={args.platform}&gamemode={args.gamemode}&rank={slugify(rank_name)}&map={slugify(map_name)}"
            api_url = f"{base_url}{params}"

            raw_data = fetch_stats_from_api(api_url)
            if raw_data:
                transformed_records = transform_stats_data(raw_data)
                load_stats_to_db(transformed_records, rank_id, map_id, dimensions["heroes"])
            else:
                logger.warning(f"Não foram encontrados dados para Rank: '{rank_name}', Mapa: '{map_name}'")
                
    logger.info("Execução do script de população de fatos concluída.")
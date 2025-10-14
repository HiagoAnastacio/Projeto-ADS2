# =======================================================================================
# SCRIPT DE WEB SCRAPING - EXTRAÇÃO E CARGA DE MAPAS
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Este script é responsável por se conectar à página de estatísticas da Blizzard.
# 2. Usa a biblioteca BeautifulSoup para analisar o HTML da página (Extração).
# 3. Identifica o menu dropdown de mapas e extrai os nomes dos mapas e seus
#    respectivos modos de jogo a partir das tags <optgroup> e <option>.
# 4. Insere ou atualiza esses dados na tabela 'map', resolvendo a FK com a tabela 'game_mode' (Carga).
#
# RAZÃO DE EXISTIR: Isolar a lógica de Web Scraping, que é inerentemente frágil,
# em um único script com uma responsabilidade clara e autossuficiente.
# =======================================================================================

import sys
import logging
import requests
from bs4 import BeautifulSoup
from os.path import abspath, dirname
from typing import List, Tuple, Dict

# --- Configuração de Path e Logger ---
project_root = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(project_root)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

# --- Importações da Aplicação ---
try:
    from utils.function_execute import execute
except ImportError as e:
    logger.error(f"Erro ao importar módulos: {e}")
    sys.exit(1)

def fetch_map_list_from_blizzard() -> List[Tuple[str, str]]:
    """Extrai a lista de mapas e seus modos de jogo via Web Scraping da página de estatísticas."""
    logger.info("--- Extraindo lista de mapas via Web Scraping do site da Blizzard (EN-US) ---")
    
    # --- CORREÇÃO AQUI ---
    # A URL agora aponta para a versão em inglês (en-us) para corresponder aos dados de seed.
    stats_url = "https://overwatch.blizzard.com/en-us/rates/"
    
    map_list = []

    try:
        response = requests.get(stats_url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Lógica de scraping para encontrar o menu de seleção de mapas.
        map_select = soup.find('select', {'id': 'filter-map-select'})

        if not map_select:
            logger.error("Não foi possível encontrar o menu de seleção de mapas no HTML da página. A estrutura do site pode ter mudado.")
            return []

        # Itera sobre cada <optgroup>, que representa um modo de jogo.
        for optgroup in map_select.find_all('optgroup'):
            game_mode_name = optgroup.get('label')
            
            # Itera sobre cada <option> dentro do grupo, que é um mapa.
            for option in optgroup.find_all('option'):
                map_name = option.text.strip()
                
                if map_name and game_mode_name:
                    map_list.append((map_name, game_mode_name.strip()))

        logger.info(f"Extração concluída. {len(map_list)} mapas encontrados.")
        return map_list

    except requests.exceptions.RequestException as e:
        logger.error(f"Falha ao buscar a página de estatísticas: {e}")
        return []

def load_maps_to_db(maps_to_insert: List[Tuple[str, str]], game_mode_map: Dict[str, int]):
    """Insere ou atualiza registros na tabela 'map'."""
    sql = "INSERT INTO `map` (`map_name`, `game_mode_id`) VALUES (%s, %s) ON DUPLICATE KEY UPDATE `map_name`=VALUES(`map_name`);"
    count = 0
    for map_name, game_mode_name in maps_to_insert:
        # A correspondência agora funcionará (ex: 'Control' == 'Control').
        game_mode_id = game_mode_map.get(game_mode_name)
        if game_mode_id:
            rows_affected = execute(sql, (map_name, game_mode_id))
            if rows_affected > 0: count += 1
        else:
            logger.warning(f"Modo de jogo '{game_mode_name}' para o mapa '{map_name}' não encontrado no banco. Verifique se os nomes correspondem.")
    logger.info(f"{count} novo(s) mapa(s) inserido(s).")

def main_scrape_and_populate_maps():
    """Função principal que orquestra a extração e carga dos mapas."""
    logger.info("Iniciando processo de população da dimensão 'map'...")
    game_modes_from_db = execute("SELECT `game_mode_id`, `game_mode_name` FROM `game_mode`")
    if not game_modes_from_db:
        logger.error("A tabela 'game_mode' está vazia. Execute o script SQL de 'seed' primeiro.")
        return
    game_mode_map = {item['game_mode_name']: item['game_mode_id'] for item in game_modes_from_db}
    
    dynamic_map_list = fetch_map_list_from_blizzard()
    
    if not dynamic_map_list:
        logger.error("Nenhum mapa foi extraído. O pipeline não pode continuar sem mapas.")
        return

    load_maps_to_db(dynamic_map_list, game_mode_map)
    logger.info("\nPopulação da dimensão 'map' concluída.")

if __name__ == "__main__":
    main_scrape_and_populate_maps()
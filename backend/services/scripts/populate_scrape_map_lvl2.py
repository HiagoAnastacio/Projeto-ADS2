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
from typing import List, Tuple, Dict

# --- Configuração de Logger ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

# --- Importações da Aplicação ---
from utils.function_execute import execute

# --- LÓGICA DE EXTRAÇÃO (EXTRACT) ---
def fetch_and_parse_maps_from_web() -> List[Tuple[str, str]]:
    """Busca e analisa o HTML para extrair a lista de mapas e seus modos de jogo."""
    url = "https://overwatch.blizzard.com/pt-br/stats/pc/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        maps_list = []
        map_dropdown = soup.find('select', {'data-js': 'filter-map'})
        if not map_dropdown:
            logger.error("Dropdown de mapas não encontrado na página. A estrutura do site pode ter mudado.")
            return []

        for optgroup in map_dropdown.find_all('optgroup'):
            game_mode = optgroup['label']
            for option in optgroup.find_all('option'):
                map_name = option.text
                if map_name != "All Maps":
                    maps_list.append((map_name, game_mode))
        return maps_list
    except requests.RequestException as e:
        logger.error(f"Erro ao buscar a página de estatísticas: {e}")
        return []

# --- LÓGICA DE CARGA (LOAD) ---
def load_maps_to_db(maps_to_insert: List[Tuple[str, str]], game_mode_map: Dict[str, int]):
    """Insere os mapas extraídos no banco de dados."""
    if not maps_to_insert:
        logger.warning("Nenhuma lista de mapas para carregar.")
        return
        
    sql = "INSERT INTO `map` (`map_name`, `game_mode_id`) VALUES (%s, %s) ON DUPLICATE KEY UPDATE `map_name`=VALUES(`map_name`);"
    count = 0
    for map_name, game_mode_name in maps_to_insert:
        game_mode_id = game_mode_map.get(game_mode_name)
        if game_mode_id:
            rows_affected = execute(sql, (map_name, game_mode_id))
            if rows_affected > 0: count += 1
        else:
            logger.warning(f"Modo de jogo '{game_mode_name}' para o mapa '{map_name}' não encontrado no banco.")
    logger.info(f"{count} novo(s) mapa(s) inserido(s).")

# --- ORQUESTRAÇÃO ---
def main_scrape_and_populate_maps():
    """Função principal que orquestra a extração e carga dos mapas."""
    logger.info("Iniciando processo de população da dimensão 'map'...")
    game_modes_from_db = execute("SELECT `game_mode_id`, `game_mode_name` FROM `game_mode`")
    if not game_modes_from_db:
        logger.error("A tabela 'game_mode' está vazia. Execute o script SQL de 'seed' primeiro.")
        return
    game_mode_map = {item['game_mode_name']: item['game_mode_id'] for item in game_modes_from_db}
    
    dynamic_map_list = fetch_and_parse_maps_from_web()
    if dynamic_map_list:
        load_maps_to_db(dynamic_map_list, game_mode_map)
    else:
        logger.error("Falha ao extrair a lista de mapas da web.")
    logger.info("Processo de população de mapas concluído.")

if __name__ == "__main__":
    main_scrape_and_populate_maps()
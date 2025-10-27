# =======================================================================================
# SCRIPT DE WEB SCRAPING - EXTRAÇÃO E CARGA DE MAPAS (REFATORADO)
# =======================================================================================
# ARQUITETURA (Mudança):
# 1. A função 'main' agora levanta uma exceção (raise Exception) se qualquer
#    etapa crítica (extração ou carga) falhar.
# 2. Isso garante que o orquestrador (data_uploader.py) possa capturar a falha
#    e abortar o pipeline corretamente, evitando "falsos positivos".
# =======================================================================================

import sys
import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Tuple, Dict
from utils.function_execute import execute
from requests.exceptions import RequestException

# Configuração de Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

# --- LÓGICA DE EXTRAÇÃO (EXTRACT) ---
def fetch_and_parse_maps_from_web() -> List[Tuple[str, str]]:
    """
    Busca e analisa o HTML da página de estatísticas para extrair mapas e modos de jogo.
    Levanta RequestException em caso de falha de rede (ex: 404).
    """
    
    # NOTA: Esta URL está quebrada (404). Você precisará fornecer a nova.
    url = "https://overwatch.blizzard.com/en-us/rates/?"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'}
    
    maps_data = []
    try:
        logger.info(f"Buscando URL de mapas: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() # Levanta exceção para erros HTTP (4xx, 5xx)

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Encontra todos os <optgroup> que representam os modos de jogo
        for optgroup in soup.find_all('optgroup'):
            game_mode = optgroup.get('label')
            if game_mode:
                # Encontra todos os <option> dentro deste grupo
                for option in optgroup.find_all('option'):
                    map_name = option.text
                    maps_data.append((map_name, game_mode))
        
        if not maps_data:
            logger.warning("Nenhum mapa encontrado no HTML. A estrutura do site pode ter mudado.")
            
        return maps_data

    except RequestException as e:
        logger.error(f"Erro ao buscar a página de estatísticas: {e}")
        # Re-levanta a exceção para que a 'main' possa capturá-la
        raise e 
    except Exception as e:
        logger.error(f"Erro inesperado ao analisar HTML: {e}")
        raise e

# --- LÓGICA DE CARGA (LOAD) ---
def load_maps_to_db(maps_to_insert: List[Tuple[str, str]], game_mode_map: Dict[str, int]):
    """Carrega a lista de mapas no banco de dados."""
    
    if not maps_to_insert:
        logger.warning("Nenhum mapa para inserir.")
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
    
    try:
        game_modes_from_db = execute("SELECT `game_mode_id`, `game_mode_name` FROM `game_mode`")
        if not game_modes_from_db:
            logger.error("A tabela 'game_mode' está vazia. Execute o script SQL de 'seed' primeiro.")
            # Levanta exceção para parar o pipeline
            raise Exception("Dependência 'game_mode' não populada.")
            
        game_mode_map = {item['game_mode_name']: item['game_mode_id'] for item in game_modes_from_db}
        
        # ETAPA DE EXTRAÇÃO
        try:
            extracted_maps = fetch_and_parse_maps_from_web()
        except Exception as e:
            logger.error("Falha ao extrair a lista de mapas da web.")
            # Propaga o erro para o orquestrador (data_uploader)
            raise Exception(f"Falha na extração de mapas: {e}")

        # ETAPA DE CARGA
        if extracted_maps:
            load_maps_to_db(extracted_maps, game_mode_map)
        else:
            logger.warning("Nenhum mapa foi extraído, etapa de carga pulada.")
            
        logger.info("Processo de população de mapas concluído.")

    except Exception as e:
        # Garante que qualquer falha na orquestração local seja logada
        logger.error(f"Falha no 'main_scrape_and_populate_maps': {e}")
        # E propaga a falha para o data_uploader
        raise e
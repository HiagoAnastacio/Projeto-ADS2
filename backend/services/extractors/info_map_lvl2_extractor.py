# =======================================================================================
# MÓDULO EXTRATOR - DIMENSÃO DE MAPAS (E do ETL)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Contém a lógica de Web Scraping para extrair dados de mapas.
# 2. Define a função `fetch_and_parse_maps_from_web` que realiza a requisição HTTP
#    (simulando um navegador) e parseia o HTML com BeautifulSoup.
#
# RAZÃO DE EXISTIR: Isolar a lógica de *Extração* (o "E") da dimensão de mapas.
# Se a estrutura do site da Blizzard mudar, este é o único arquivo que precisa
# ser atualizado para a Etapa 1 do ETL.
# =======================================================================================

import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Tuple
from requests.exceptions import RequestException

# Configuração de Logger
logger = logging.getLogger(__name__)

# --- LÓGICA DE EXTRAÇÃO (EXTRACT) ---

def fetch_and_parse_maps_from_web() -> List[Tuple[str, str]]:
    """
    Busca e analisa o HTML da página de estatísticas para extrair mapas e modos de jogo.
    (Lógica movida de populate_scrape_map_lvl2.py)
    Levanta RequestException em caso de falha de rede (ex: 404).
    """
    
    # ATENÇÃO: Esta URL provavelmente ainda está quebrada e precisa de atualização.
    url = "https://overwatch.blizzard.com/en-us/rates/?"
    # Simula um navegador, conforme a lógica do extraction_helpers
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'}
    
    maps_data = []
    try:
        logger.debug(f"Iniciando scraping de mapas de: {url}")
        # Usa 'requests' diretamente para scraping de HTML
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
            logger.warning("Nenhum mapa encontrado no scraping. A estrutura do site pode ter mudado.")
            
        return maps_data

    except RequestException as e:
        logger.error(f"Erro de rede ao buscar a página de mapas: {e}")
        # Propaga o erro para o orquestrador
        raise Exception(f"Falha na extração de mapas (rede): {e}")
    except Exception as e:
        logger.error(f"Erro inesperado ao analisar HTML dos mapas: {e}")
        raise e # Propaga o erro
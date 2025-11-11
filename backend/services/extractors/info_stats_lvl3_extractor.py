# =======================================================================================
# MÓDULO EXTRATOR - FATOS DE ESTATÍSTICAS (E do ETL)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Contém a lógica para extrair dados de estatísticas (fatos).
# 2. Define as constantes da API (URLs, parâmetros fixos).
# 3. Define a função `fetch_stats_data` que constrói a URL com parâmetros
#    dinâmicos (rank_slug, map_slug) e chama o helper `fetch_api_data`.
# 4. Valida a estrutura da resposta JSON.
#
# RAZÃO DE EXISTIR: Isolar a lógica de *Extração* (o "E") das tabelas de fato.
# Se a API de stats mudar (URL, parâmetros, formato de resposta), este
# é o único arquivo que precisa ser atualizado para a Etapa 3 do ETL.
# =======================================================================================

import logging
from typing import List, Any, Optional, Dict

# Importa o auxiliar de requisição HTTP (conforme solicitado)
from utils.extraction_helpers import fetch_api_data

logger = logging.getLogger(__name__)

# --- Constantes da API de Estatísticas (Movidas de populate_lvl3.py) ---
BASE_URL = "https://overwatch.blizzard.com/en-us/rates/data/?"
PLATFORM = "PC"
ROLE = "All"
QUEUE = "1" # Ranked
REGION = "Americas" # Filtro fixo para consistência
TIER_ALL = "All" # Parâmetro fixo para rank "All"

# --- Extrator 3: Fatos de Estatísticas ---

def fetch_stats_data(rank_slug: str, map_slug: str) -> Optional[List[Any]]:
    """
    Busca dados de estatísticas para uma combinação específica de rank e mapa.
    (Lógica de construção de URL e extração movida de populate_lvl3.py v0.7.0)
    """
    # Constrói os parâmetros da API
    params = f"input={PLATFORM}&map={map_slug}&region={REGION}&role={ROLE}&rq={QUEUE}&tier={rank_slug}"
    api_url = f"{BASE_URL}{params}"

    # Loga a URL exata que está sendo acessada.
    logger.info(f"Acessando API: {api_url}")
    # --- FIM DA ADIÇÃO ---

    # Chama o helper genérico
    raw_data = fetch_api_data(api_url)

    # Validação da Resposta
    if not raw_data:
        logger.warning(f"Dados não obtidos (timeout ou erro) para Rank='{rank_slug}', Mapa='{map_slug}'")
        return None
        
    data_list = None
    if isinstance(raw_data, list): 
        data_list = raw_data
    elif isinstance(raw_data, dict) and 'rates' in raw_data and isinstance(raw_data.get('rates'), list): 
        data_list = raw_data['rates']

    if data_list is None:
        logger.warning(f"Formato de dados inesperado para Rank='{rank_slug}', Mapa='{map_slug}'. Dados: {str(raw_data)[:100]}...")
        return None
    if not data_list:
        logger.debug(f"API retornou lista vazia para Rank='{rank_slug}', Mapa='{map_slug}'.")
        return None
        
    return data_list
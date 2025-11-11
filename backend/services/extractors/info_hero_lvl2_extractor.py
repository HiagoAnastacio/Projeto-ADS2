# =======================================================================================
# MÓDULO EXTRATOR - DIMENSÃO DE HERÓIS (E do ETL)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Contém a lógica para extrair os dados da dimensão de heróis.
# 2. Define a URL da API específica para os dados de heróis.
# 3. CHAMA o `extraction_helpers.fetch_api_data` para executar a requisição.
# 4. Valida a estrutura da resposta JSON (esperando um dict com a chave 'rates').
#
# RAZÃO DE EXISTIR: Isolar a lógica de *Extração* (o "E") da dimensão de heróis.
# =======================================================================================

import logging
from typing import List, Any, Optional

# Importa o auxiliar de requisição HTTP (conforme solicitado)
from utils.extraction_helpers import fetch_api_data

logger = logging.getLogger(__name__)

# --- Extrator 2: Dimensão de Heróis ---

def fetch_hero_dimension_data() -> Optional[List[Any]]:
    """
    Busca os dados da dimensão de heróis (para populate_hero_lvl2).
    (Lógica movida de populate_hero_lvl2.py)
    """
    # ATENÇÃO: Esta URL pode precisar de verificação.
    api_url = "https://overwatch.blizzard.com/en-us/rates/data/?"
    
    logger.debug(f"Buscando dados da dimensão de heróis de: {api_url}")
    # Usa o helper genérico para simular navegador e tratar erros/timeout
    api_response_data = fetch_api_data(api_url)
    
    # Validação da estrutura da resposta
    if not api_response_data:
        logger.error("Nenhum dado de herói foi retornado pela API.")
        raise Exception("API de Heróis não retornou dados.")

    if not isinstance(api_response_data, dict):
        logger.error(f"Falha na API de Heróis. Formato inesperado. Esperado: 'dict', Recebido: '{type(api_response_data).__name__}'")
        raise TypeError("A API de Heróis não retornou um dicionário.")
    
    hero_list = api_response_data.get('rates')
    
    if not isinstance(hero_list, list):
        logger.error(f"Falha na API de Heróis. Chave 'rates' ausente ou não é uma lista. Recebido: '{type(hero_list).__name__}'")
        raise TypeError("A API de Heróis retornou um dicionário, mas a chave 'rates' não contém uma lista.")
        
    return hero_list
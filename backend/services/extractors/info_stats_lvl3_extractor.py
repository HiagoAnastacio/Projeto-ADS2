# =======================================================================================
# MÓDULO EXTRATOR - FATOS DE ESTATÍSTICAS (E do ETL) (v1.3.0 - Resiliente)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. (v1.3.0) Implementa a solução "Teste A/B" em tempo real para
#    validar a resposta da API contra "falhas silenciosas".
# 2. (v1.3.0) Define uma LISTA DE FALLBACK (QUEUE_FALLBACKS) para o parâmetro 'rq'
#    para lidar com a instabilidade da API (às vezes é '2', '1' ou '').
# 3. `fetch_stats_data` agora:
#    a. Tenta um 'rq' (ex: "2").
#    b. (Requisição A) Busca dados para o mapa específico (ex: 'gibraltar').
#    c. (Requisição B) Busca dados para 'all-maps' (o controle).
#    d. Se (A == B), a API falhou silenciosamente (ignorou o 'map_slug').
#       Tenta o próximo 'rq'.
#    e. Se (A != B) e A não for nulo, A é válido.
#
# RAZÃO DE EXISTIR: Isolar a lógica de Extração e torná-la 100% RESILIENTE
# contra falhas silenciosas, sem NENHUM risco de coincidência.
# =======================================================================================

import logging
from typing import List, Any, Optional, Dict

# Importa o auxiliar de requisição HTTP (conforme solicitado)
from utils.extraction_helpers import fetch_api_data

logger = logging.getLogger(__name__)

# --- Constantes da API de Estatísticas (Baseadas no arquivo original) ---
BASE_URL = "https://overwatch.blizzard.com/en-us/rates/data/?"
PLATFORM = "PC" #
ROLE = "All"
REGION = "Americas"
TIER_ALL = "All"
MAP_ALL = "all-maps"

# (v1.3.0) Lista de Fallbacks para o parâmetro 'rq' (Fila Competitiva)
QUEUE_FALLBACKS = ["2", "1", ""]

# --- Helpers Internos de Extração (DRY) ---

def _get_api_data_list(raw_data: Any) -> Optional[List[Any]]:
    """
    Helper Padrão (DRY) para extrair a lista 'rates' da resposta da API.
    Retorna None se a resposta for nula, vazia ou de estrutura inválida.
    """
    if not raw_data:
        return None
    
    data_list = None
    if isinstance(raw_data, list): 
        data_list = raw_data
    elif isinstance(raw_data, dict) and 'rates' in raw_data and isinstance(raw_data.get('rates'), list):
        data_list = raw_data.get('rates')
    
    if data_list: # Verifica se a lista não é vazia
        return data_list
    return None # Retorna None para listas vazias ou estruturas inválidas

def _fetch_data_internal(
    rank_slug: str, 
    map_slug: str, 
    queue_value: str
) -> Optional[List[Any]]:
    """
    Função de baixo nível (DRY) que apenas constrói a URL e busca os dados.
    Usa 'input=' conforme o arquivo original.
    """
    # Constrói os parâmetros da API
    params = f"input={PLATFORM}&map={map_slug}&region={REGION}&role={ROLE}&rq={queue_value}&tier={rank_slug}"
    api_url = f"{BASE_URL}{params}"
    
    logger.info(f"Acessando API: {api_url}")
    
    raw_data = fetch_api_data(api_url)
    return _get_api_data_list(raw_data)


# --- Extrator 3: Fatos de Estatísticas ---

def fetch_stats_data(rank_slug: str, map_slug: str) -> Optional[List[Any]]:
    """
    Busca dados de estatísticas, validando contra falhas silenciosas da API
    usando o método "Teste A/B" (comparação com 'all-maps').
    """
    
    # Se a requisição for para 'all-maps', não precisamos do Teste A/B.
    # Apenas buscamos e retornamos (se falhar, 'None' é o esperado).
    if map_slug == MAP_ALL:
        logger.debug(f"Buscando dados para 'all-maps' (Rank: {rank_slug}).")
        # Usamos o primeiro 'rq' da lista (ex: "2")
        return _fetch_data_internal(rank_slug, MAP_ALL, QUEUE_FALLBACKS[0])

    # --- Loop de Fallback (para 'rq=2', 'rq=1', etc.) ---
    for queue_value in QUEUE_FALLBACKS:
        
        logger.debug(f"Teste A/B: Iniciando para rq='{queue_value}' (Rank: {rank_slug}, Mapa: {map_slug})")

        # (Requisição A) Busca os dados do mapa específico
        data_a = _fetch_data_internal(rank_slug, map_slug, queue_value)
        
        # (Requisição B) Busca os dados de 'all-maps' (o Controle)
        # Usamos o *mesmo* rank e *mesmo* rq para isolar a variável 'map_slug'
        data_b_control = _fetch_data_internal(rank_slug, MAP_ALL, queue_value)

        # --- Lógica de Validação ---

        # Check 1: A Requisição A falhou (nula ou vazia)?
        if not data_a:
            logger.warning(f"Teste A/B (rq='{queue_value}'): Requisição A (mapa) falhou (dados nulos).")
            continue # Tenta o próximo valor de 'rq'

        # Check 2: A Requisição B (Controle) falhou?
        # Se o controle falhar, não podemos comparar. Algo está errado.
        if not data_b_control:
            logger.error(f"Teste A/B (rq='{queue_value}'): Requisição B (Controle 'all-maps') falhou. Não é possível validar.")
            # Se o controle falha, pulamos para o próximo 'rq'
            continue 

        # Check 3 (O Teste A/B): Os dados são idênticos?
        if data_a == data_b_control:
            logger.warning(f"Teste A/B (rq='{queue_value}'): FALHA. API retornou dados 'all-maps' para '{map_slug}'.")
            continue # Tenta o próximo valor de 'rq'

        # --- Sucesso ---
        # Se A não é nulo, B não é nulo, e A != B,
        # então 'data_a' são dados válidos e específicos do mapa.
        logger.info(f"Teste A/B (rq='{queue_value}'): SUCESSO! Dados VÁLIDOS obtidos para '{map_slug}'.")
        return data_a   
        
    # (Fim do Loop)
    logger.error(f"FALHA TOTAL. Nenhuma tentativa de 'rq' retornou dados VÁLIDOS para Rank='{rank_slug}', Mapa='{map_slug}'.")
    return None
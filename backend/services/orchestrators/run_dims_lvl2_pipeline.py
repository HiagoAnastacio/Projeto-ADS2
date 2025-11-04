# =======================================================================================
# SCRIPT ORQUESTRADOR - PIPELINE DE DIMENSÕES (NÍVEL 2)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Contém os orquestradores de tarefa para as dimensões (Mapas e Heróis).
# 2. As funções `run_map_pipeline` e `run_hero_pipeline` (pontos de entrada)
#    orquestram o processo:
#    a. LÊem as dependências (dimensões Nível 1) do DB.
#    b. CHAMAM os Extratores (`services.extractors.*`) para buscar dados brutos.
#    c. CHAMAM os Carregadores (`services.loaders.dime_lvl2_loader`) para salvar os dados.
#
# RAZÃO DE EXISTIR: Isolar a lógica de *Orquestração* do ETL das dimensões.
# Define o "fluxo" de população das dimensões de Nível 2.
# =======================================================================================

import sys
import logging
from typing import Dict, List, Any

# --- Importações da Aplicação ---
# Importa o executor de SQL (usado para buscar dependências)
from utils.function_execute import execute
# Importa as funções de "Como Fazer" dos módulos especializados
from services.extractors.info_map_lvl2_extractor import fetch_and_parse_maps_from_web
from services.extractors.info_hero_lvl2_extractor import fetch_hero_dimension_data
from services.loaders.dims_lvl2_loader import load_maps_to_db, load_heroes_to_db


# --- Configuração de Logger ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

# --- ORQUESTRADOR 1: MAPAS ---
def run_map_pipeline():
    """
    Função principal que orquestra a extração e carga dos mapas.
    (Lógica `main` movida de populate_scrape_map_lvl2.py)
    """
    logger.info("Iniciando processo de população da dimensão 'map'...")
    
    try:
        # 1. Buscar Dependências (Dimensão GameMode)
        game_modes_from_db = execute("SELECT `game_mode_id`, `game_mode_name` FROM `game_mode`")
        if not game_modes_from_db:
            logger.error("A tabela 'game_mode' está vazia. Execute o script SQL de 'seed' primeiro.")
            raise Exception("Dependência 'game_mode' não populada.")
            
        game_mode_map = {item['game_mode_name']: item['game_mode_id'] for item in game_modes_from_db}
        
        # 2. Extrair Dados (Chama o Extrator)
        extracted_maps = fetch_and_parse_maps_from_web()

        # 3. Carregar Dados (Chama o Loader)
        if extracted_maps:
            load_maps_to_db(extracted_maps, game_mode_map)
        else:
            logger.warning("Nenhum mapa foi extraído, etapa de carga pulada.")
            
        logger.info("Processo de população de mapas concluído.")

    except Exception as e:
        logger.error(f"Falha no 'run_map_pipeline': {e}")
        raise e # Propaga a falha para o data_uploader

# --- ORQUESTRADOR 2: HERÓIS ---
def run_hero_pipeline():
    """
    Função principal que orquestra todo o fluxo de população de heróis.
    (Lógica `main` movida de populate_hero_lvl2.py)
    """
    logger.info("Iniciando processo de população da dimensão 'hero'...")
    
    try:
        # 1. Buscar Dependências (Dimensão Role)
        roles_from_db = execute("SELECT `role_id`, `role` FROM `role`")
        if not roles_from_db:
            logger.error("A tabela 'role' está vazia. Execute o script SQL de 'seed' primeiro.")
            raise Exception("Dependência 'role' não populada.")
            
        role_map = {item['role']: item['role_id'] for item in roles_from_db}
        
        # 2. Extrair Dados (Chama o Extrator)
        hero_list = fetch_hero_dimension_data()
        
        # 3. Carregar Dados (Chama o Loader)
        if not hero_list:
             logger.warning("A API retornou uma lista vazia de heróis. Nenhum herói será carregado.")
        else:
            load_heroes_to_db(hero_list, role_map)
        
        logger.info("Processo de população de 'hero' concluído.")

    except Exception as e:
        logger.error(f"Falha no 'run_hero_pipeline': {e}")
        raise e # Propaga a falha para o data_uploader
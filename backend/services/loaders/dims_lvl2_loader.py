# =======================================================================================
# MÓDULO DE CARREGADOR - DIMENSÕES NÍVEL 2 (L do ETL)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Contém as funções `load_heroes_to_db` e `load_maps_to_db`.
# 2. Encapsula as strings SQL (INSERT ... ON DUPLICATE KEY UPDATE) e a lógica
#    de iteração para carregar os dados de dimensão no banco de dados.
# 3. Utiliza o `utils.function_execute.execute` (conforme solicitado) para a 
#    execução real da query.
#
# RAZÃO DE EXISTIR: Isolar a lógica de *Carga* (o "L") das dimensões de Nível 2.
# =======================================================================================

import logging
from typing import Dict, Any, List, Tuple

# Importa o executor de SQL do ETL (conforme solicitado)
from utils.function_execute import execute

logger = logging.getLogger(__name__)

# --- Carregador 1: Dimensão de Mapas ---

def load_maps_to_db(maps_to_insert: List[Tuple[str, str]], game_mode_map: Dict[str, int]):
    """
    Carrega a lista de mapas no banco de dados.
    (Lógica movida de populate_scrape_map_lvl2.py)
    """
    # Define a query SQL de carga
    sql = "INSERT INTO `map` (`map_name`, `game_mode_id`) VALUES (%s, %s) ON DUPLICATE KEY UPDATE `game_mode_id`=VALUES(`game_mode_id`);"
    
    count = 0
    # Itera sobre os dados extraídos
    for map_name, game_mode_name in maps_to_insert:
        # Mapeia o nome do modo de jogo para seu ID
        game_mode_id = game_mode_map.get(game_mode_name)
        if game_mode_id:
            try:
                # Executa a query
                rows_affected = execute(sql, (map_name, game_mode_id))
                if rows_affected == 1: # 1 = INSERT (nova linha)
                    count += 1
            except Exception as e:
                logger.error(f"Erro ao carregar mapa '{map_name}': {e}")
        else:
            logger.warning(f"Modo de jogo '{game_mode_name}' para o mapa '{map_name}' não encontrado no banco.")
    logger.info(f"{count} novo(s) mapa(s) inserido(s).")

# --- Carregador 2: Dimensão de Heróis ---

def load_heroes_to_db(records: List[Dict[str, Any]], role_map: Dict[str, int]):
    """
    Processa os registros de heróis e os insere/atualiza no banco de dados.
    (Lógica movida de populate_hero_lvl2.py)
    """
    # Define a query SQL de carga
    sql = """INSERT INTO `hero` (`hero_name`, `role_id`, `hero_icon_img_link`) 
             VALUES (%s, %s, %s) 
             ON DUPLICATE KEY UPDATE `role_id`=VALUES(`role_id`), `hero_icon_img_link`=VALUES(`hero_icon_img_link`);"""
    
    inserted_count = 0
    updated_count = 0
    skipped_count = 0
    
    # Itera sobre os dados extraídos
    for hero_entry in records:
        hero_details = hero_entry.get("hero") 
        if not isinstance(hero_details, dict):
            logger.warning(f"Estrutura inesperada para entrada de herói, faltando chave 'hero': {hero_entry}")
            skipped_count += 1
            continue

        # Extrai dados do herói
        hero_name = hero_details.get("name")
        hero_role_name = hero_details.get("role")
        hero_portrait = hero_details.get("portrait")
        
        # Mapeia o nome da role para seu ID
        role_id = role_map.get(hero_role_name)
        
        if hero_name and role_id:
            params = (hero_name, role_id, hero_portrait)
            try:
                # Executa a query
                rows_affected = execute(sql, params)
                if rows_affected == 1: 
                    inserted_count += 1 # 1 = INSERT
                elif rows_affected == 2: 
                    updated_count += 1 # 2 = UPDATE
            except Exception as e:
                logger.error(f"Erro ao carregar herói '{hero_name}': {e}")
                skipped_count += 1
        else:
            # Loga se faltar nome ou role_id
            if not hero_name: 
                logger.warning(f"Nome do herói ausente em: {hero_details}")
            if not role_id: 
                logger.warning(f"Role '{hero_role_name}' para '{hero_name}' não encontrada no DB.")
            skipped_count += 1
                
    logger.info(f"{inserted_count} novo(s) herói(s) inserido(s).")
    logger.info(f"{updated_count} herói(s) existente(s) atualizado(s).")
    if skipped_count > 0:
        logger.warning(f"{skipped_count} herói(s) pulado(s) devido a dados ausentes ou erros.")
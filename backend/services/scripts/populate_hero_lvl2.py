# =======================================================================================
# SCRIPT ORQUESTRADOR - POPULAÇÃO DE DIMENSÕES (NÍVEL 2 - HERO)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Este script é o responsável único por popular a tabela 'hero'.
# 2. A função `main_populate_heroes` orquestra o processo:
#    a. LÊ da tabela `role` (dependência de Nível 1).
#    b. CHAMA o helper `fetch_api_data` para obter a lista de heróis.
#    c. CHAMA a função de carga local `load_heroes_to_db` para salvar os dados.
#
# RAZÃO DE EXISTIR: Isolar a lógica de população da dimensão 'hero', que é
# dinâmica e depende da API, separando-a da população de mapas (scraping) e fatos.
# =======================================================================================

import sys
import logging
from typing import Dict, List, Any

# --- Configuração de Logger ---
# O logger é configurado para fornecer feedback claro sobre a execução do script.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

# --- Importações da Aplicação ---
# Graças ao `pyproject.toml` e `pip install -e .`, o Python encontra
# esses módulos sem a necessidade de manipular o sys.path.
from utils.function_execute import execute
from utils.extraction_helpers import fetch_api_data

# --- LÓGICA DE CARGA (LOAD) ---
def load_heroes_to_db(records: List[Dict[str, Any]], role_map: Dict[str, int]):
    """Insere ou atualiza os heróis no banco de dados."""
    if not records:
        logger.warning("Nenhum registro de herói para carregar.")
        return

    # Query SQL com ON DUPLICATE KEY UPDATE para ser idempotente.
    sql = """
        INSERT INTO `hero` (`hero_name`, `role_id`, `hero_icon_img_link`)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
        `role_id`=VALUES(`role_id`), `hero_icon_img_link`=VALUES(`hero_icon_img_link`);"""
    inserted_count = 0
    for hero_data in records:
        details = hero_data.get("hero", {})
        role_id = role_map.get(details.get("role"))
        if details.get("name") and role_id:
            params = (details["name"], role_id, details.get("portrait"))
            rows_affected = execute(sql, params)
            if rows_affected == 1: # `1` para INSERT, `2` para UPDATE
                inserted_count += 1
    logger.info(f"{inserted_count} novo(s) herói(s) inserido(s).")

# --- ORQUESTRAÇÃO ---
def main_populate_heroes():
    """Função principal que orquestra todo o fluxo de população de heróis."""
    logger.info("Iniciando processo de população da dimensão 'hero'...")
    
    roles_from_db = execute("SELECT `role_id`, `role` FROM `role`")
    if not roles_from_db:
        logger.error("A tabela 'role' está vazia. Execute o script SQL de 'seed' primeiro.")
        return
    role_map = {item['role']: item['role_id'] for item in roles_from_db}
    
    hero_raw_data = fetch_api_data("https://overwatch.blizzard.com/pt-br/rates/data?platform=pc&gamemode=competitive&rank=grandmaster&map=all-maps")
    
    if hero_raw_data:
        load_heroes_to_db(hero_raw_data, role_map)
    else:
        logger.error("Falha ao buscar dados da API de heróis.")
    logger.info("Processo de população de heróis concluído.")

if __name__ == "__main__":
    main_populate_heroes()
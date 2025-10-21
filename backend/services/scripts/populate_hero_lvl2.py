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
# (Assumindo que o projeto foi instalado com `pip install -e .`,
# o bloco de manipulação de sys.path não é mais necessário)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

# --- Importações ---
try:
    from utils.function_execute import execute
    from utils.extraction_helpers import fetch_api_data
except ImportError:
    logger.critical("Erro fatal: Não foi possível importar os módulos `utils`. "
                    "Certifique-se de que o projeto foi instalado com `pip install -e .`", exc_info=True)
    sys.exit(1)


# --- LÓGICA DE CARGA (LOAD) ---

def load_heroes_to_db(records: List[Dict[str, Any]], role_map: Dict[str, int]): #
    """
    Insere ou atualiza os heróis no banco de dados.
    Utiliza 'ON DUPLICATE KEY UPDATE' para ser idempotente.
    """
    if not records:
        logger.warning("Nenhum registro de herói para carregar.")
        return

    # ESTA É A QUERY CORRETA. Ela não deve ter 'LIMIT' ou 'OFFSET'.
    sql = """
        INSERT INTO `hero` (`hero_name`, `role_id`, `hero_icon_img_link`)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
        `role_id`=VALUES(`role_id`), `hero_icon_img_link`=VALUES(`hero_icon_img_link`);""" #
    
    inserted_count = 0
    updated_count = 0
    
    for hero_data in records:
        details = hero_data.get("hero", {})
        
        # Resolve o role_id a partir do nome do 'role' (em minúsculas)
        # A API da Blizzard retorna "tank", "damage", "support" em minúsculas
        role_id = role_map.get(details.get("role"))
        
        if details.get("name") and role_id:
            params = (details["name"], role_id, details.get("portrait"))
            
            try:
                # A função 'execute' retorna o 'rows_affected'
                # Esta é a linha 42 (aproximadamente) que causa o erro no seu PC
                rows_affected = execute(sql, params) #
                
                if rows_affected == 1:
                    inserted_count += 1
                elif rows_affected == 2: # 2 indica que um UPDATE ocorreu
                    updated_count += 1
                    
            except Exception as e:
                logger.error(f"Falha ao inserir/atualizar herói {details.get('name')}. Erro: {e}")
        else:
            logger.warning(f"Herói {details.get('name')} ignorado. 'role' ou 'name' ausente ou 'role' inválido: {details.get('role')}")

    logger.info(f"{inserted_count} novo(s) herói(s) inserido(s). {updated_count} herói(s) atualizado(s).")


# --- ORQUESTRAÇÃO ---

def main_populate_heroes(): #
    """Função principal que orquestra todo o fluxo de população de heróis."""
    logger.info("Iniciando processo de população da dimensão 'hero'...")
    
    try:
        # 1. LER a dimensão de Nível 1 (role)
        roles_from_db = execute("SELECT `role_id`, `role` FROM `role`")
        if not roles_from_db:
            logger.error("A tabela 'role' está vazia. Execute o script SQL de 'seed' primeiro.")
            return
        
        # Cria um mapa de 'Role Name' -> 'role_id' para tradução
        # (Converte as chaves do mapa para minúsculas para corresponder à API)
        role_map = {item['role'].lower(): item['role_id'] for item in roles_from_db}
        
        # 2. EXTRAIR/TRANSFORMAR dados da API
        # A função fetch_api_data já retorna os dados transformados
        hero_raw_data = fetch_api_data("https://overwatch.blizzard.com/en-us/rates/data?") #
        
        if hero_raw_data:
            # 3. CARREGAR dados no banco
            load_heroes_to_db(hero_raw_data, role_map) #
        else:
            logger.error("Falha ao buscar dados da API de heróis.")
            
    except Exception as e:
        logger.critical(f"Falha fatal no script populate_hero_lvl2. Erro: {e}", exc_info=True)
        
    logger.info("Processo de população de heróis concluído.")


if __name__ == "__main__":
    main_populate_heroes() #
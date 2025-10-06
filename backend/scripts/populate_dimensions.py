import requests
import sys
import json
import logging
from os.path import abspath, dirname
from typing import Dict

# -- Configuração de Path e Logger --
project_root = dirname(dirname(abspath(__file__)))
sys.path.append(project_root)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

# -- Importação dos Módulos da Aplicação --
try:
    from utils.function_execute import execute
except ImportError as e:
    logger.error(f"Erro ao importar módulos. {e}")
    sys.exit(1)

# -- Funções de Lógica --

def fetch_hero_list(api_url: str) -> dict | None:
    """
    Função: Faz uma única chamada à API para obter a lista completa de heróis.
    Razão de Existência: Isolar a lógica de requisição HTTP para esta responsabilidade específica.
    """
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    headers = {'User-Agent': user_agent}
    
    logger.info(f"Buscando lista de heróis de: {api_url}")
    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        logger.error(f"Falha ao buscar ou decodificar lista de heróis: {e}", exc_info=True)
        return None

def populate_heroes_table(role_map: Dict[str, int]):
    """
    Função: Itera sobre os dados da API e insere/atualiza os heróis na tabela 'hero'.
    Razão de Existência: Orquestrar a população da tabela 'hero', resolvendo a FK `role_id`.
    """
    logger.info("--- Iniciando população da tabela 'hero' ---")
    # URL genérica que retorna todos os heróis.
    api_url = "https://overwatch.blizzard.com/pt-br/rates/data?platform=pc&gamemode=competitive"
    
    raw_data = fetch_hero_list(api_url)
    if not raw_data or "rates" not in raw_data:
        logger.error("Não foi possível obter a lista de heróis da API. Abortando.")
        return
        
    # Query idempotente para inserir ou atualizar heróis.
    # Requer uma chave UNIQUE na coluna `hero_name`.
    sql = "INSERT INTO hero (hero_name, role_id, hero_icon_img_link) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE role_id=VALUES(role_id), hero_icon_img_link=VALUES(hero_icon_img_link);"
    
    inserted_count = 0
    # Itera sobre os dados de cada herói.
    for hero_data in raw_data["rates"]:
        details = hero_data.get("hero", {})
        # Obtém o `role_id` usando o mapa carregado da memória.
        role_id = role_map.get(details.get("role"))
        
        # Valida se os dados essenciais existem.
        if details.get("name") and role_id:
            params = (details["name"], role_id, details.get("portrait"))
            rows_affected = execute(sql, params)
            if rows_affected == 1:
                inserted_count += 1

    logger.info(f"{inserted_count} novo(s) herói(s) inserido(s) ou atualizado(s).")

# -- Ponto de Entrada do Script --
if __name__ == "__main__":
    logger.info("Iniciando processo de população de dimensões dinâmicas...")
    
    # Carrega a dimensão 'role' para resolver a FK.
    roles_from_db = execute("SELECT role_id, role FROM role")
    if not roles_from_db:
        logger.error("A tabela 'role' está vazia. Execute o script 'seed_dimensions.py' primeiro.")
        sys.exit(1)
        
    role_map = {item['role']: item['role_id'] for item in roles_from_db}

    # Executa a função principal de população de heróis.
    populate_heroes_table(role_map)
    
    logger.info("\nPopulação de dimensões dinâmicas concluída.")
import sys
import logging
from os.path import abspath, dirname
from typing import Dict

# --- AJUSTE CRÍTICO DE PATH ---
# Razão: Como o script agora está em backend/services/scripts/, precisamos
# subir três níveis (scripts -> services -> backend) para chegar à raiz do módulo 'backend'.
project_root = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(project_root)

# Configuração de Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

# Importações da Aplicação e dos Helpers
try:
    from utils.function_execute import execute
    # O nome do arquivo de helpers é 'data_populate_help.py' conforme enviado
    from utils.data_populate_help import fetch_api_data, load_heroes_to_db
except ImportError as e:
    logger.error(f"Erro ao importar módulos: {e}")
    sys.exit(1)

def run_hero_population():
    """Orquestra a população da tabela 'hero'."""
    logger.info("--- Iniciando população da tabela 'hero' ---")
    
    # Busca a dependência (tabela 'role') do banco de dados.
    roles_from_db = execute("SELECT `role_id`, `role` FROM `role`")
    if not roles_from_db:
        logger.error("A tabela 'role' está vazia. Execute o script SQL de 'seed' primeiro.")
        return
    # Cria o mapa de nome -> id para consulta rápida.
    role_map = {item['role']: item['role_id'] for item in roles_from_db}

    # Define a URL genérica para buscar a lista de todos os heróis.
    api_url = "https://overwatch.blizzard.com/pt-br/rates/data?platform=pc&gamemode=competitive"
    raw_data = fetch_api_data(api_url)
    
    # Valida a resposta da API.
    if not raw_data or "rates" not in raw_data:
        logger.error("Não foi possível obter a lista de heróis da API. Abortando.")
        return

    # Chama a função helper para carregar os dados no banco.
    load_heroes_to_db(raw_data["rates"], execute, role_map)

# Função principal encapsulada para ser importável.
def main_populate_dimensions():
    logger.info("Iniciando processo de população de dimensões dinâmicas (Nível 2)...")
    run_hero_population()
    logger.info("\nPopulação de dimensões dinâmicas concluída.")

# Ponto de Entrada para permitir execução manual do script.
if __name__ == "__main__":
    main_populate_dimensions()
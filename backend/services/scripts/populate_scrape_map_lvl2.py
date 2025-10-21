# =======================================================================================
# SCRIPT DE WEB SCRAPING - EXTRAÇÃO E CARGA DE MAPAS
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Este script é responsável por se conectar à página de estatísticas da Blizzard.
# 2. Usa a biblioteca BeautifulSoup para analisar o HTML da página (Extração).
# 3. Identifica o menu dropdown de mapas e extrai os nomes dos mapas e seus
#    respectivos modos de jogo a partir das tags <optgroup> e <option>.
# 4. Insere ou atualiza esses dados na tabela 'map', resolvendo a FK com a tabela 'game_mode' (Carga).
#
# RAZÃO DE EXISTIR: Isolar a lógica de Web Scraping, que é inerentemente frágil,
# em um único script com uma responsabilidade clara e autossuficiente.
# =======================================================================================

import sys
import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Tuple, Dict, Optional

# --- Configuração de Logger ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

# --- Importações da Aplicação ---
try:
    from utils.function_execute import execute
except ImportError:
    logger.critical("Erro fatal: Não foi possível importar os módulos `utils`. "
                    "Verifique se o projeto foi instalado com `pip install -e .`.", exc_info=True)
    sys.exit(1)


# --- LÓGICA DE EXTRAÇÃO (EXTRACT) ---

# ALTERAÇÃO: A função agora retorna 'None' em caso de erro, o que será tratado.
def fetch_and_parse_maps_from_web() -> Optional[List[Tuple[str, str]]]:
    """Busca e analisa o HTML para extrair a lista de mapas e seus modos de jogo."""
    url = "https://overwatch.blizzard.com/en-us/rates/data?"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        maps_list = []
        
        # ==========================================================================
        # ALTERAÇÃO PRINCIPAL DO SCRAPER
        # O site da Blizzard não usa mais <select>.
        # Agora ele usa uma <ul> com a classe 'map-dropdown-options'.
        # ==========================================================================
        map_dropdown = soup.find('ul', {'class': 'map-dropdown-options'})
        
        if not map_dropdown:
            logger.error("Dropdown de mapas não encontrado (seletor 'ul.map-dropdown-options'). A estrutura do site pode ter mudado.")
            return None # Retorna None em caso de falha no scraping

        # A lógica de iterar por <optgroup> e <option> ainda é válida,
        # pois elas estão dentro da <ul>
        for optgroup in map_dropdown.find_all('optgroup'):
            game_mode = optgroup.get('label')
            if not game_mode:
                continue
                
            for option in optgroup.find_all('option'):
                map_name = option.text
                # Ignora a opção "Todos os mapas" que está em uma <li> separada
                if map_name and map_name.lower() != "all maps":
                    maps_list.append((map_name, game_mode))
                    
        if not maps_list:
            logger.warning("Scraping teve sucesso, mas nenhuma lista de mapas foi extraída.")
            return None
            
        return maps_list
        
    except requests.RequestException as e:
        logger.error(f"Erro ao buscar a página de estatísticas: {e}")
        return None # Retorna None em caso de falha de rede

# --- LÓGICA DE CARGA (LOAD) ---

# ALTERAÇÃO: Adicionado 'if not maps_to_insert:' para prevenir o 'TypeError'
def load_maps_to_db(maps_to_insert: List[Tuple[str, str]], game_mode_map: Dict[str, int]): #
    """Insere os mapas extraídos no banco de dados."""
    
    # Esta verificação previne o erro 'TypeError: 'NoneType' object is not iterable'
    # que foi visto na captura de tela.
    if not maps_to_insert:
        logger.warning("Nenhuma lista de mapas foi fornecida para carga (maps_to_insert é None ou vazio).")
        return
        
    sql = "INSERT INTO `map` (`map_name`, `game_mode_id`) VALUES (%s, %s) ON DUPLICATE KEY UPDATE `map_name`=VALUES(`map_name`);"
    count = 0
    
    for map_name, game_mode_name in maps_to_insert:
        # Busca o ID do modo de jogo
        game_mode_id = game_mode_map.get(game_mode_name)
        
        if game_mode_id:
            try:
                rows_affected = execute(sql, (map_name, game_mode_id))
                if rows_affected > 0: 
                    count += 1
            except Exception as e:
                logger.error(f"Falha ao inserir mapa '{map_name}'. Erro: {e}")
        else:
            logger.warning(f"Modo de jogo '{game_mode_name}' para o mapa '{map_name}' não encontrado no banco. Mapa ignorado.")
            
    logger.info(f"{count} novo(s) mapa(s) inserido(s) ou atualizado(s).")

# --- ORQUESTRAÇÃO ---

def main_scrape_and_populate_maps(): #
    """Função principal que orquestra a extração e carga dos mapas."""
    logger.info("Iniciando processo de população da dimensão 'map'...")
    
    try:
        # 1. LER dimensão de Nível 1 (game_mode)
        game_modes_from_db = execute("SELECT `game_mode_id`, `game_mode_name` FROM `game_mode`")
        if not game_modes_from_db:
            logger.error("A tabela 'game_mode' está vazia. Execute o script SQL de 'seed' primeiro.")
            return
        
        # Cria um mapa de 'Nome do Modo' -> 'game_mode_id' para tradução
        game_mode_map = {item['game_mode_name']: item['game_mode_id'] for item in game_modes_from_db}
        
        # 2. EXTRAIR/TRANSFORMAR
        dynamic_map_list = fetch_and_parse_maps_from_web() #
        
        # ==========================================================================
        # ALTERAÇÃO DE LÓGICA (Correção do Erro)
        # Adicionada uma verificação para garantir que 'dynamic_map_list'
        # não seja 'None' antes de passá-la para 'load_maps_to_db'.
        # Isso impede o 'TypeError' visto na captura de tela.
        # ==========================================================================
        if dynamic_map_list:
            # 3. CARREGAR
            load_maps_to_db(dynamic_map_list, game_mode_map) #
        else:
            logger.error("Falha ao extrair a lista de mapas da web. A etapa de carga (LOAD) será ignorada.")
            
    except Exception as e:
        logger.critical(f"Falha fatal no script populate_scrape_map_lvl2. Erro: {e}", exc_info=True)

    logger.info("Processo de população de mapas concluído.")

if __name__ == "__main__":
    main_scrape_and_populate_maps() #
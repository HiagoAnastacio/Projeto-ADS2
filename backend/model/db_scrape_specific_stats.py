# import requests
# from bs4 import BeautifulSoup
# from typing import Optional
# from model.db_operations_id import get_or_insert_id
# from utils.function_execute import execute
# import logging

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# def scrape_and_insert_stats_by_filters(hero_name: str, map_name: Optional[str] = None, rank_name: Optional[str] = None):
#     """
#     Realiza o scraping de dados de pick e win rate para um herói,
#     com filtros opcionais de mapa e rank, e insere no banco de dados.
#     """
#     logging.info(f"Iniciando scraping para o herói '{hero_name}' com filtros: Mapa='{map_name}', Rank='{rank_name}'")

#     hero_id = get_or_insert_id(table_name='hero', column_name='hero_name', item_name=hero_name)
#     if not hero_id:
#         logging.error(f"Herói '{hero_name}' não encontrado no banco de dados.")
#         raise ValueError(f"Herói '{hero_name}' não encontrado.")

#     map_id = None
#     if map_name:
#         map_id = get_or_insert_id(table_name='map', column_name='map_name', item_name=map_name)
#         if not map_id:
#             logging.error(f"Mapa '{map_name}' não encontrado no banco de dados.")
#             raise ValueError(f"Mapa '{map_name}' não encontrado.")

#     rank_id = None
#     if rank_name:
#         rank_id = get_or_insert_id(table_name='rank', column_name='rank_name', item_name=rank_name)
#         if not rank_id:
#             logging.error(f"Rank '{rank_name}' não encontrado no banco de dados.")
#             raise ValueError(f"Rank '{rank_name}' não encontrado.")
    
#     base_url = "https://overwatch.blizzard.com/en-us/rates/"
#     params = {
#         'input': 'PC',
#         'hero': hero_name.lower(),
#         'map': 'all-maps' if not map_name else map_name.lower().replace(' ', '-'),
#         'region': 'Americas',
#         'role': 'All',
#         'tier': 'All' if not rank_name else rank_name.lower()
#     }
    
#     try:
#         response = requests.get(base_url, params=params)
#         response.raise_for_status()
#         logging.info("Requisição HTTP para estatísticas específicas bem-sucedida.")
#         soup = BeautifulSoup(response.content, 'html.parser')
        
#         pick_rate_elem = soup.find('div', class_='pick-rate-value')
#         win_rate_elem = soup.find('div', class_='win-rate-value')
        
#         if not pick_rate_elem or not win_rate_elem:
#             logging.warning("Não foi possível encontrar os dados de pick/win rate na página. Verifique os seletores.")
#             raise ValueError("Não foi possível encontrar os dados de pick/win rate na página.")

#         pick_rate = float(pick_rate_elem.text.strip().replace('%', '')) / 100
#         win_rate = float(win_rate_elem.text.strip().replace('%', '')) / 100
        
#         logging.info(f"Dados extraídos: Pick Rate={pick_rate}, Win Rate={win_rate}.")

#         if map_name and rank_name:
#             sql = "INSERT INTO hero_rank_map_stats (hero_id, map_id, rank_id, pick_rate, win_rate) VALUES (%s, %s, %s, %s, %s)"
#             execute(sql, (hero_id, map_id, rank_id, pick_rate, win_rate))
#             logging.info("Dados de herói, mapa e rank inseridos com sucesso.")
#         elif map_name:
#             sql = "INSERT INTO hero_map_stats (hero_id, map_id, pick_rate, win_rate) VALUES (%s, %s, %s, %s)"
#             execute(sql, (hero_id, map_id, pick_rate, win_rate))
#             logging.info("Dados de herói e mapa inseridos com sucesso.")
#         elif rank_name:
#             sql = "INSERT INTO hero_rank_stats (hero_id, rank_id, pick_rate, win_rate) VALUES (%s, %s, %s, %s)"
#             execute(sql, (hero_id, rank_id, pick_rate, win_rate))
#             logging.info("Dados de herói e rank inseridos com sucesso.")
#         else:
#             sql = "INSERT INTO hero_general_stats (hero_id, pick_rate, win_rate) VALUES (%s, %s, %s)"
#             execute(sql, (hero_id, pick_rate, win_rate))
#             logging.info("Dados gerais de herói inseridos com sucesso.")

#     except requests.exceptions.RequestException as e:
#         logging.critical(f"Erro na requisição: {e}")
#         raise
#     except Exception as e:
#         logging.critical(f"Ocorreu um erro durante o scraping: {e}")
#         raise
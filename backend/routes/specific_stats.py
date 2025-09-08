# app/utils/function_scrape_base_tables.py
import requests
from bs4 import BeautifulSoup
from model.function_get_or_insert_id import get_or_insert_id  # Importação da nova função
from utils.function_execute import execute


def function_scrape_base_tables():
    """
    Roda o web scraping inicial para popular as tabelas de referência.
    Inclui lógica para heróis, mapas, roles, ranks e modos de jogo.
    """
    URL = "https://overwatch.blizzard.com/en-us/rates/?input=PC&map=all-maps&region=Americas&role=All&rq=0&tier=All"
    
    try:
        response = requests.get(URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Lógica para extrair os nomes das roles
        role_elements = soup.find_all('option', class_='role-selector-option') 
        for role_elem in role_elements:
            role_name = role_elem.get('value').strip()
            get_or_insert_id(table_name='role', column_name='role', item_name=role_name)

        # Lógica para extrair os nomes dos mapas
        map_elements = soup.find_all('option', class_='map-selector-option')
        for map_elem in map_elements:
            map_name = map_elem.get('value').strip()
            get_or_insert_id(table_name='map', column_name='map_name', item_name=map_name)

        # Lógica para extrair os nomes dos ranks
        rank_elements = soup.find_all('option', class_='tier-selector-option')
        for rank_elem in rank_elements:
            rank_name = rank_elem.get('value').strip()
            get_or_insert_id(table_name='rank', column_name='rank_name', item_name=rank_name)

        # Lógica para extrair os nomes dos modos de jogo
        game_mode_elements = soup.find_all('option', class_='game-mode-selector-option')
        for mode_elem in game_mode_elements:
            game_mode_name = mode_elem.get('value').strip()
            get_or_insert_id(table_name='game_mode', column_name='game_mode_name', item_name=game_mode_name)

        # Lógica para extrair e inserir heróis
        hero_elements = soup.find_all('div', class_='hero-portrait')
        for hero_elem in hero_elements:
            hero_name = hero_elem.get('data-hero-name').strip()
            # A lógica para extrair a role do herói a partir do HTML
            role_name = "tank" # Este é um exemplo, precisa ser extraído do HTML
            
            role_id = get_or_insert_id(table_name='role', column_name='role', item_name=role_name)
            
            # Insere o herói com o ID da role, evitando duplicatas
            sql = "INSERT INTO hero (hero_name, role_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE hero_name=hero_name"
            execute(sql=sql, params=(hero_name, role_id))

        print("Tabelas base (incluindo ranks e game modes) populadas com sucesso.")

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
    except Exception as e:
        print(f"Erro durante o scraping inicial: {e}")
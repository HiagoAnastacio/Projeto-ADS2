# app/utils/function_insert_stats_data.py

from fastapi import FastAPI
from model.db import Database
import requests
from bs4 import BeautifulSoup
from function_get_or_insert_id import get_or_insert_id  # Importação da nova função
from utils.function_execute import execute


app = FastAPI()
db = Database()

def function_insert_stats_data():
    """
    Roda o web scraping para dados de estatísticas e os insere no banco.
    """
    URL = "https://overwatch.blizzard.com/en-us/rates/?input=PC&map=all-maps&region=Americas&role=All&rq=0&tier=All"
    
    try:
        response = requests.get(URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # EXEMPLO: Lógica para pegar as taxas de pick de todos os heróis
        hero_stats_elements = soup.find_all('div', class_='hero-stats-row')
        for stat_elem in hero_stats_elements:
            hero_name = stat_elem.find('h3', class_='hero-name').text.strip()
            pick_rate = float(stat_elem.find('span', class_='pick-rate').text.strip('%')) / 100
            
            # 1. Busca o ID do herói (usando a nova função)
            hero_id = get_or_insert_id(table_name='hero', column_name='hero_name', item_name=hero_name)
            
            if hero_id:
                # 2. Insere na tabela de estatísticas (sem verificar duplicatas, pois é histórico)
                sql_insert = "INSERT INTO hero_pick (hero_id, pick_rate) VALUES (%s, %s)"
                execute(sql=sql_insert, params=(hero_id, pick_rate))
                print(f"Inserido novo dado de pick rate para o herói '{hero_name}'.")
            else:
                print(f"Herói '{hero_name}' não encontrado. Ignorando a inserção de dados.")

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
    except Exception as e:
        print(f"Ocorreu um erro no scraping: {e}")
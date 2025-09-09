# # app/utils/function_insert_stats_data.py

# from fastapi import FastAPI
# from model.db import Database
# import requests
# from model.db_operations_id import get_or_insert_id
# from utils.function_execute import execute
# import logging

# app = FastAPI()
# db = Database()


# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # app/model/db_insert_stats.py (Código corrigido - Exemplo)
# ...
# def function_insert_stats_data():
#     URL = "https://overwatch.blizzard.com/en-us/rates/data/?input=PC&map=all-maps&region=Americas&role=All&rq=0&tier=All"
#     logging.info(f"Iniciando coleta de dados da API: {URL}")

#     try:
#         response = requests.get(URL)
#         response.raise_for_status() # Verifica se a requisição foi bem sucedida
        
#         # A API retorna JSON, não HTML.
#         dados_json = response.json()
#         logging.info("Dados JSON recebidos com sucesso. Processando...")

#         # O JSON retornado contém uma chave 'heroes' com a lista de heróis
#         for heroi in dados_json.get('heroes', []):
#             hero_name = heroi.get('name')
#             pick_rate = heroi.get('pick_rate')
#             win_rate = heroi.get('win_rate')
            
#             if hero_name and pick_rate is not None and win_rate is not None:
#                 hero_id = get_or_insert_id(table_name='hero', column_name='hero_name', item_name=hero_name)
                
#                 # Inserir os dados na sua tabela de estatísticas
#                 sql_insert = "INSERT INTO hero_general_stats (hero_id, pick_rate, win_rate) VALUES (%s, %s, %s)"
#                 execute(sql=sql_insert, params=(hero_id, pick_rate, win_rate))
                
#                 logging.info(f"Estatísticas para '{hero_name}' inseridas com sucesso.")
    
#     except requests.exceptions.RequestException as e:
#         logging.error(f"Erro na requisição para a API: {e}")
#         raise e
#     except Exception as e:
#         logging.error(f"Erro durante a inserção de dados de estatísticas: {e}")
#         raise e
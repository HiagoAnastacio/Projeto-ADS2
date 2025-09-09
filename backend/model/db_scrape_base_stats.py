# # db_scrape_base_tables.py (código corrigido)
# import requests
# from bs4 import BeautifulSoup
# from model.db_operations_id import get_or_insert_id
# from utils.function_execute import execute
# import logging

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# def function_scrape_base_tables():
#     URL = "https://overwatch.blizzard.com/en-us/rates/?input=PC&map=all-maps&region=Americas&role=All&rq=0&tier=All"
#     logging.info(f"Iniciando scraping da URL: {URL}")

#     try:
#         response = requests.get(URL)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.content, 'html.parser')

#         # Lógica para extrair as roles
#         logging.info("Scraping de roles...")
#         role_elements = soup.find_all('option', class_='role-selector-option')
#         for role_elem in role_elements:
#             role_name = role_elem.get('value').strip()
#             get_or_insert_id(table_name='role', column_name='role', item_name=role_name)
        
#         # ... (Restante do seu código para mapas, ranks e game_modes está correto)
#         logging.info("Scraping de mapas, ranks e game modes concluído.")

#         # Lógica corrigida para extrair e inserir heróis
#         logging.info("Iniciando scraping de heróis...")
#         hero_elements = soup.find_all('div', class_='hero-portrait')
#         for hero_elem in hero_elements:
#             hero_name = hero_elem.get('data-hero-name').strip()
            
#             # Extrair a role do herói. Exemplo: <div data-hero-role="tank">
#             role_name = hero_elem.get('data-hero-role').strip()

#             # Obtém o ID da role, garantindo que ela exista
#             role_id = get_or_insert_id(table_name='role', column_name='role', item_name=role_name)
            
#             # Insere o herói na tabela 'hero' e obtém seu ID.
#             # A função get_or_insert_id já trata de duplicatas.
#             hero_id = get_or_insert_id(table_name='hero', column_name='hero_name', item_name=hero_name)
            
#             # Agora, você precisa atualizar a role do herói, se ela não foi definida na primeira inserção.
#             sql = "UPDATE hero SET role_id = %s WHERE hero_id = %s"
#             execute(sql=sql, params=(role_id, hero_id))
#             logging.info(f"Herói '{hero_name}' (ID: {hero_id}) com role '{role_name}' atualizado/inserido.")

#     except Exception as e:
#         logging.error(f"Erro durante o scraping das tabelas base: {e}")
#         raise
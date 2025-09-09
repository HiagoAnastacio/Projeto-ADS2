# # app/routes/base_data.py
# from fastapi import APIRouter, HTTPException
# from model.db_scrape_base_stats import function_scrape_base_tables
# import logging

# # Configuração básica de logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# router = APIRouter()

# @router.post("/base-data", tags=["Base Data"])
# async def update_base_data():
#     """
#     Roda o script para popular ou atualizar as tabelas base (heróis, mapas, roles, etc.).
#     """
#     logging.info("Endpoint '/base-data' chamado. Iniciando o scraping das tabelas base.")
#     try:
#         function_scrape_base_tables()
#         logging.info("Scraping das tabelas base finalizado com sucesso.")
#         return {"message": "Tabelas base atualizadas com sucesso."}
#     except Exception as e:
#         logging.error(f"Erro durante a atualização das tabelas base: {e}")
#         raise HTTPException(status_code=500, detail=f"Erro ao atualizar tabelas base: {e}")
# # app/routes/stats_data.py
# from fastapi import APIRouter, HTTPException
# from model.db_insert_stats import function_insert_stats_data

# router = APIRouter()

# @router.post("/stats-data", tags=["Stats Data"])
# async def insert_stats_data():
#     """
#     Roda o script de web scraping para coletar e inserir novas estatísticas no banco de dados.
#     """
#     try:
#         function_insert_stats_data()
#         return {"message": "Dados de estatísticas inseridos com sucesso."}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erro ao inserir dados de estatísticas: {e}")
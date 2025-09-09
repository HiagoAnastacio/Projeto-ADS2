# # app/routes/specific_stats.py

# from fastapi import APIRouter, HTTPException, Query
# from typing import Optional
# from model.db_scrape_specific_stats import scrape_and_insert_stats_by_filters # Importação da nova função

# router = APIRouter()

# @router.post("/update/hero/{hero_name}", tags=["Specific Stats"])
# async def update_hero_stats(
#     hero_name: str, 
#     map_name: Optional[str] = Query(None, description="Nome do mapa para filtrar os dados"),
#     rank_name: Optional[str] = Query(None, description="Nome do rank para filtrar os dados")
# ):
#     """
#     Roda o script para atualizar as estatísticas de um herói, com filtros opcionais de mapa e rank.
#     """
#     try:
#         scrape_and_insert_stats_by_filters(hero_name, map_name, rank_name)
#         return {"message": f"Estatísticas para o herói '{hero_name}' (filtro de mapa: {map_name}, rank: {rank_name}) inseridas com sucesso."}
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {e}")
# app/routes/base_data.py
from fastapi import APIRouter, HTTPException
from model.function_scrape_base_tables import function_scrape_base_tables

router = APIRouter()

@router.post("/base-data", tags=["Base Data"])
async def update_base_data():
    """
    Roda o script para popular ou atualizar as tabelas base (heróis, mapas, roles, etc.).
    """
    try:
        function_scrape_base_tables()
        return {"message": "Tabelas base atualizadas com sucesso."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar tabelas base: {e}")
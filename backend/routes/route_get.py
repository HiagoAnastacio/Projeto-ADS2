from fastapi import APIRouter, HTTPException, Path
from utils.function_execute import execute

router = APIRouter()

# Lista de tabelas que podem ser consultadas pela API
TABLES_WHITELIST = ["hero", "map", "role", "rank", "game_mode", "hero_win", "hero_pick",
                    "hero_map_win", "hero_map_pick", "hero_rank_win", "hero_rank_pick",]

@router.get("/get/{table_name}", tags=["Generic Data Management"])
async def get_tabela(table_name: str = Path(..., description="Nome da tabela para consulta")):
    """
    Consulta genérica e segura para tabelas autorizadas.
    O nome da tabela é validado antes de ser usado.
    """
    if table_name not in TABLES_WHITELIST:
        raise HTTPException(status_code=400, detail=f"A tabela '{table_name}' não é válida para esta consulta.")
    
    try:
        # A consulta agora é segura, pois 'table_name' vem de uma lista interna, não da URL.
        sql = f"SELECT * FROM {table_name}"
        result = execute(sql=sql)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados na tabela {table_name}: {e}")
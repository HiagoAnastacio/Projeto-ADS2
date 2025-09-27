# FLUXO E A LÓGICA:
# 1. Recebe 'table_name' e 'item_id' da URL (Escopo de Requisição).
# 2. Executa a dependência de Rate Limiting (Segurança).
# 3. Valida se 'table_name' está na Whitelist (Segurança Crítica).
# 4. Constrói a Query SQL DELETE dinâmica: DELETE FROM {table_name} WHERE {table_name}_id = %s.
# 5. Chama `execute` (DAO).
# 6. Verifica o número de linhas afetadas (`rows_affected`) para confirmar a exclusão e retorna 404 se nada for encontrado.
# A razão de existir: Fornecer um endpoint DELETE genérico e seguro.

from fastapi import APIRouter, HTTPException, Path, Depends # Razão: Roteamento, tratamento de erros, parâmetros e dependências.
from utils.function_execute import execute # Razão: Importa a função DAO para acesso ao DB.
from fastapi_limiter.depends import RateLimiter # Razão: Importa o limitador de taxa (Camada de Segurança).

# Variável 'router' (Escopo Global/Módulo): Objeto APIRouter para agrupar rotas.
router = APIRouter()

# Variável 'TABLES_WHITELIST' (Escopo Global/Módulo): Lista de tabelas permitidas para exclusão.
# Razão: SEGURANÇA. Impede exclusão em tabelas sensíveis que não devem ser expostas (ex: 'users').
TABLES_WHITELIST = ["hero", "map", "role", "rank", "game_mode", "hero_win", "hero_pick",
                    "hero_map_win", "hero_map_pick", "hero_rank_win", "hero_rank_pick",]

@router.delete("/delete/{table_name}/{item_id}", tags=["Generic Data Management"],
               # Rate Limiting ATIVADO (Essencial para rotas que alteram dados)
               dependencies=[Depends(RateLimiter(times=10, seconds=60))]) 
async def delete_data(
    # Variável 'table_name' (Escopo de Requisição): Nome da tabela.
    table_name: str = Path(..., description="Nome da tabela para exclusão"),
    # Variável 'item_id' (Escopo de Requisição): ID da linha a ser excluída.
    item_id: int = Path(..., description="ID do item a ser excluído")
):
    """Exclui um item de uma tabela autorizada com base no ID."""
    
    # 1. Verificação de Segurança (Whitelist)
    if table_name not in TABLES_WHITELIST:
        raise HTTPException(status_code=400, detail=f"A tabela '{table_name}' não é válida para esta operação.")

    try:
        # A chave primária é assumida como '{table_name}_id' (ex: hero_id, map_id).
        sql = f"DELETE FROM {table_name} WHERE {table_name}_id = %s"
        # Variável 'rows_affected' (Escopo de Requisição): Número de linhas alteradas (0 ou 1).
        rows_affected = execute(sql=sql, params=(item_id,)) # Envia para a camada DAO.
        
        # 2. Verificação de Resultado
        if not rows_affected:
            # Retorna 404 se o DB não excluiu nada (ID não existe).
            raise HTTPException(status_code=404, detail=f"Item com ID {item_id} não encontrado ou não houve exclusão.")

        return {"message": f"Item com ID {item_id} excluído com sucesso da tabela '{table_name}'."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar a exclusão: {e}")
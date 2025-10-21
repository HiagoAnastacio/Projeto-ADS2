# =======================================================================================
# MÓDULO DE ROTA - DELETE (EXCLUSÃO)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Define um endpoint genérico `DELETE /api/delete/{table_name}/{item_id}`.
# 2. Recebe 'table_name' e 'item_id' da URL.
# 3. (Segurança) Valida `table_name` contra a `ALLOWED_WRITE_TABLES`.
# 4. Constrói a Query SQL `DELETE` dinâmica e segura.
# 5. Chama a função `execute` da camada DAO para executar o comando.
# 6. Verifica se uma linha foi de fato afetada e retorna 404 se o ID não existir.
#
# RAZÃO DE EXISTIR: Fornecer um ponto de entrada seguro para a exclusão de
# registros em tabelas de dimensão autorizadas.
# =======================================================================================

from fastapi import APIRouter, HTTPException, Path
from utils.function_execute import execute
# Importa a whitelist de segurança
from app.security.table_whitelist_security import ALLOWED_WRITE_TABLES

# Variável 'router' (Escopo Global/Módulo).
router = APIRouter()

@router.delete("/delete/{table_name}/{item_id}", tags=["Generic Data Management"])
async def delete_data(
    table_name: str = Path(..., description="Nome da tabela para exclusão"),
    item_id: int = Path(..., description="ID do item a ser excluído")
):
    """
    Exclui um registro de uma tabela autorizada, com base no ID.
    
    COMO USAR:
    
    1.  **Endpoint:** `DELETE /api/delete/{table_name}/{item_id}`
        -   Ex: `DELETE /api/delete/hero/10` (Exclui o herói com ID 10)
            
    2.  **Segurança:**
        -   A rota falhará se a tabela não estiver na whitelist de escrita.
        -   A rota falhará (404) se o item_id não for encontrado.
    """

    # 1. Verificação de Segurança (Whitelist)
    if table_name not in ALLOWED_WRITE_TABLES:
        raise HTTPException(status_code=403, detail=f"A tabela '{table_name}' não permite exclusão via API.")

    try:
        # Constrói a query SQL, usando crases para segurança.
        # A coluna de ID é padronizada como `nome_da_tabela_id`.
        sql = f"DELETE FROM `{table_name}` WHERE `{table_name}_id` = %s"
        
        rows_affected = execute(sql=sql, params=(item_id,))

        # 2. Verificação de Resultado
        if not rows_affected:
            # Se nenhuma linha foi afetada, o ID não foi encontrado.
            raise HTTPException(status_code=404, detail=f"Item com ID {item_id} não encontrado na tabela '{table_name}'.")

        return {"message": f"Item com ID {item_id} excluído com sucesso da tabela '{table_name}'.",
                "rows_affected": rows_affected}

    except HTTPException as e:
        # Re-levanta exceções HTTP já tratadas.
        raise e
    except Exception as e:
        # Captura qualquer outro erro inesperado.
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {e}")
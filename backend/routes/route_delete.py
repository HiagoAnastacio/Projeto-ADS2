# =======================================================================================
# MÓDULO DE ROTA - DELETE (EXCLUSÃO)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Define um endpoint genérico `DELETE /api/delete/{table_name}/{item_id}`.
# 2. Recebe 'table_name' e 'item_id' da URL.
# 3. Realiza uma verificação de segurança CRÍTICA, validando se o `table_name`
#    está na `ALLOWED_WRITE_TABLES` (importada do config.py).
# 4. Constrói a Query SQL `DELETE` dinâmica.
# 5. Chama a função `execute` da camada DAO para executar o comando.
# 6. Verifica se uma linha foi de fato afetada e retorna 404 se o ID não existir.
#
# RAZÃO DE EXISTIR: Fornecer um ponto de entrada seguro e genérico para a exclusão de
# registros em tabelas autorizadas, protegido por uma lista branca (whitelist).
# =======================================================================================

from fastapi import APIRouter, HTTPException, Path
from utils.function_execute import execute
from app.security.table_whitelist_security import ALLOWED_WRITE_TABLES # <-- IMPORTAÇÃO CENTRALIZADA

# Variável 'router' (Escopo Global/Módulo).
router = APIRouter()

@router.delete("/delete/{table_name}/{item_id}", tags=["Generic Data Management"])
async def delete_data(
    table_name: str = Path(..., description="Nome da tabela para exclusão"),
    item_id: int = Path(..., description="ID do item a ser excluído")
):
    """Exclui um item de uma tabela autorizada com base no ID."""

    # 1. Verificação de Segurança (Whitelist)
    if table_name not in ALLOWED_WRITE_TABLES: # <-- USA A LISTA CENTRALIZADA
        raise HTTPException(status_code=403, detail=f"A tabela '{table_name}' não permite exclusão via API.")

    try:
        # Constrói a query SQL, usando crases para segurança.
        # A coluna de ID é padronizada como `nome_da_tabela_id`.
        sql = f"DELETE FROM `{table_name}` WHERE `{table_name}_id` = %s"

        # Chama a camada DAO para executar a exclusão.
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
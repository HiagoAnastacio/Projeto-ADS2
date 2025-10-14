# =======================================================================================
# MÓDULO DE ROTA - GET (LEITURA)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Define um endpoint genérico `GET /api/get/{table_name}`.
# 2. Recebe o nome da tabela (`table_name`) a partir do parâmetro da URL.
# 3. Realiza uma verificação de segurança CRÍTICA, garantindo que o `table_name`
#    esteja na `ALLOWED_GET_TABLES` (importada do config.py). Isso previne que um usuário
#    tente acessar tabelas sensíveis ou internas.
# 4. Constrói a query SQL `SELECT * FROM ...` dinamicamente.
# 5. Chama a função `execute` da camada DAO para buscar os dados no banco.
# 6. Retorna os resultados como uma resposta JSON ou um erro HTTP 404 se nada for encontrado.
#
# RAZÃO DE EXISTIR: Fornecer um ponto de entrada único e seguro para todas as operações
# de leitura de dados completos de uma tabela.
# =======================================================================================

from fastapi import APIRouter, HTTPException, Path
from utils.function_execute import execute
from app.security.table_whitelist_security import ALLOWED_GET_TABLES # <-- IMPORTAÇÃO CENTRALIZADA

# Variável 'router' (Escopo Global/Módulo): Instância do roteador para este módulo.
router = APIRouter()

@router.get("/get/{table_name}", tags=["Generic Data Management"])
async def get_tabela(
    # Variável 'table_name' (Escopo de Requisição): Capturada da URL.
    table_name: str = Path(..., description="Nome da tabela para consulta")
):
    """Consulta genérica e segura para tabelas autorizadas."""
    
    # 1. Verificação de Segurança (Whitelist)
    if table_name not in ALLOWED_GET_TABLES:  # <-- USA A LISTA CENTRALIZADA
        # Se a tabela não for permitida, levanta um erro 400 (Bad Request).
        raise HTTPException(status_code=400, detail=f"A tabela '{table_name}' não é válida para esta consulta.")
    
    try:
        # Constrói a query SQL usando crases para proteger contra palavras reservadas.
        sql = f"SELECT * FROM `{table_name}`"
        
        # Chama a camada DAO para executar a query.
        result = execute(sql=sql)
        
        # Verifica se a consulta retornou algum resultado.
        if result is None or len(result) == 0:
            # Se não, levanta um erro 404 (Not Found).
            raise HTTPException(status_code=404, detail=f"Nenhum dado encontrado para a tabela '{table_name}'.")

        # Retorna os dados para o cliente.
        return result
    except HTTPException as e:
        # Re-levanta exceções HTTP já tratadas (como o 500 do DAO) para o FastAPI.
        raise e
    except Exception as e:
        # Captura qualquer outro erro inesperado.
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {e}")
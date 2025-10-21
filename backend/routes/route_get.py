# =======================================================================================
# MÓDULO DE ROTA - GET (LEITURA)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Define um endpoint genérico `GET /api/get/{table_name}`.
# 2. Recebe o nome da tabela (`table_name`) a partir do parâmetro da URL.
# 3. (ALTERAÇÃO) Realiza uma verificação de segurança CRÍTICA, importando a
#    lista `ALLOWED_GET_TABLES` do módulo de segurança 'table_whitelist_security'
#    e garantindo que o `table_name` esteja nela.
# 4. Constrói a query SQL `SELECT * FROM ...` dinamicamente.
# 5. Chama a função `execute` da camada DAO para buscar os dados no banco.
# 6. Retorna os resultados como uma resposta JSON ou um erro HTTP 404 se nada for encontrado.
#
# RAZÃO DE EXISTIR: Fornecer um ponto de entrada único e seguro para todas as operações
# de leitura de dados completos de uma tabela.
# =======================================================================================

from fastapi import APIRouter, HTTPException, Path
from utils.function_execute import execute
# ALTERAÇÃO: Importa a whitelist centralizada do arquivo de segurança
from app.security.table_whitelist_security import ALLOWED_GET_TABLES

# Variável 'router' (Escopo Global/Módulo): Instância do roteador para este módulo.
router = APIRouter()

# ALTERAÇÃO: A 'TABLES_WHITELIST' local foi removida para usar a importada.

@router.get("/get/{table_name}", tags=["Generic Data Management"])
async def get_tabela(
    # Variável 'table_name' (Escopo de Requisição): Capturada da URL.
    table_name: str = Path(..., description="Nome da tabela para consulta")
):
    """
    Consulta genérica e segura para tabelas e views autorizadas.
    
    Retorna todos os registros da tabela ou view especificada.
    
    COMO USAR:
    
    1.  **Endpoint:** `GET /api/get/{table_name}`
        -   Exemplo (Tabela): `GET /api/get/hero`
        -   Exemplo (View): `GET /api/get/vw_hero_win`
    
    2.  **Parâmetros (Path):**
        -   `table_name`: O nome exato da tabela ou view que você deseja consultar.
            
    3.  **Resposta (Response):**
        -   Retorna um array JSON com todos os registros encontrados.
        -   Exemplo de Resposta para `GET /api/get/hero`:
            ```json
            [
              {
                "hero_id": 1,
                "hero_name": "Ana",
                "role_id": 3,
                "hero_icon_img_link": "[http://example.com/icon.png](http://example.com/icon.png)"
              },
              {
                "hero_id": 2,
                "hero_name": "Ashe",
                "role_id": 2,
                "hero_icon_img_link": "[http://example.com/icon2.png](http://example.com/icon2.png)"
              }
            ]
            ```
            
    4.  **Segurança e Validação:**
        -   A rota falhará (400 Bad Request) se a `table_name` não estiver na `ALLOWED_GET_TABLES`.
        -   A rota falhará (404 Not Found) se a tabela for válida, mas estiver vazia.
    """
    
    # 1. Verificação de Segurança (Whitelist)
    # ALTERAÇÃO: Usa a lista 'ALLOWED_GET_TABLES' importada
    if table_name not in ALLOWED_GET_TABLES:
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
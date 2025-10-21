# =======================================================================================
# MÓDULO DE ROTA - POST (CRIAÇÃO)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Define um endpoint genérico `POST /api/insert/{table_name}`.
# 2. Recebe o `table_name` da URL e o corpo da requisição (JSON).
# 3. (Segurança) Valida `table_name` contra a `ALLOWED_WRITE_TABLES`.
# 4. (Validação) Usa a dependência `validate_body` para garantir que o JSON
#    enviado corresponda ao schema Pydantic daquela tabela.
# 5. A rota recebe o dicionário já validado (`data_dict`) da dependência.
# 6. Constrói a query `INSERT INTO ...` dinamicamente e de forma segura.
# 7. Chama a função `execute` da camada DAO para inserir os dados.
#
# RAZÃO DE EXISTIR: Fornecer um ponto de entrada seguro e validado para a criação
# de novos registros em tabelas de dimensão autorizadas.
# =======================================================================================

from fastapi import APIRouter, HTTPException, Path, Depends, Body 
from typing import Dict, Any
from utils.function_execute import execute
from utils.dependencies import validate_body
# Importa a whitelist de segurança
from app.security.table_whitelist_security import ALLOWED_WRITE_TABLES 

# Variável 'router' (Escopo Global/Módulo).
router = APIRouter()

@router.post("/insert/{table_name}", tags=["Generic Data Management"])
async def insert_data(
    table_name: str = Path(..., description="Nome da tabela para inserção."), 
    request_body: Dict[str, Any] = Body(..., description="Corpo JSON com os dados para inserir."),
    data_dict: Dict[str, Any] = Depends(validate_body) 
):
    """
    Insere um novo registro em uma tabela autorizada.
    
    COMO USAR:
    
    1.  **Endpoint:** `POST /api/insert/{table_name}`
        -   Ex: `POST /api/insert/hero`
    
    2.  **Corpo da Requisição (Body):**
        -   Deve ser um JSON contendo os dados do novo registro.
        -   Os campos DEVEM corresponder ao schema Pydantic da tabela.
        -   Use a rota `GET /api/models/{table_name}/example` para ver um exemplo.
        -   Exemplo de Body para `hero`:
            ```json
            {
              "hero_name": "Novo Heroi",
              "role_id": 1,
              "hero_icon_img_link": "[http://example.com/icon.png](http://example.com/icon.png)"
            }
            ```
            
    3.  **Segurança e Validação:**
        -   A rota falhará se a tabela não estiver na whitelist de escrita.
        -   A rota falhará se o JSON não passar na validação Pydantic (ex: campo faltando, tipo errado).
    """

    # 1. Verificação de Segurança (Whitelist)
    if table_name not in ALLOWED_WRITE_TABLES:
        raise HTTPException(status_code=403, detail=f"A tabela '{table_name}' não permite inserção via API.")
    
    # Constrói dinamicamente as partes da query SQL.
    columns = ", ".join([f"`{col}`" for col in data_dict.keys()]) 
    placeholders = ", ".join(["%s"] * len(data_dict)) 
    values = tuple(data_dict.values()) 

    try:
        # Monta a query final.
        sql = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
        # Chama a camada DAO.
        new_id = execute(sql=sql, params=values)
        
        # `execute` retorna o lastrowid para INSERTs.
        if not new_id:
            raise HTTPException(status_code=500, detail="Não foi possível inserir os dados.")

        return {"message": f"Dados inseridos com sucesso na tabela '{table_name}'.", "new_id": new_id}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {e}")
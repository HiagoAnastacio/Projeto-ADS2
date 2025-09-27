# FLUXO E A LÓGICA:
# 1. Recebe 'table_name' da URL e o corpo via `request_body` (Escopo de Requisição).
# 2. Chama `validate_body` (Dependência) para obter o dicionário seguro `data_dict`.
# 3. Constrói a *query* SQL `INSERT` dinamicamente usando as chaves e valores de `data_dict`.
# 4. Chama `execute` (DAO) para rodar o comando SQL.
# A razão de existir: Ponto de entrada para a operação de escrita (POST) de forma GENÉRICA.

from fastapi import APIRouter, HTTPException, Path, Depends, Body # Razão: Roteamento, tratamento de erros, parâmetros, dependências e leitura do corpo.
from typing import Dict, Any # Razão: Tipagem.
from utils.function_execute import execute # Razão: Importa a função DAO para acesso ao DB.
import logging # Razão: Logging (embora não esteja sendo usado ativamente na rota).
from utils.dependencies import validate_body # Razão: Importa a dependência de validação (Camada de Lógica).
from fastapi_limiter.depends import RateLimiter # Razão: Importa o limitador de taxa (Camada de Segurança).

# Variável 'router' (Escopo Global/Módulo): Objeto APIRouter para agrupar rotas.
router = APIRouter()

# Rota para inserir dados genéricos: /insert/{table_name}
@router.post("/insert/{table_name}", tags=["Generic Data Management"], 
            # dependencies=[Depends(RateLimiter(times=5, seconds=30))] # Rate Limiter DESATIVADO (Risco de DoS)
) 
async def insert_data(
    # Variável 'table_name' (Escopo de Requisição): Nome da tabela (ex: hero).
    table_name: str = Path(..., description="Nome da tabela para inserção."), 
    
    # Variável 'request_body' (Escopo de Requisição): Recebe o corpo bruto (para documentação Swagger).
    request_body: Dict[str, Any] = Body(
        ..., description="Corpo JSON com os dados para inserir."
    ),
    
    # Variável 'data_dict' (Escopo de Requisição): Resultado da Injeção de Dependência. Contém os dados VALIDADOS.
    data_dict: Dict[str, Any] = Depends(validate_body) # Chamada CRÍTICA de validação.
):
    """Insere um novo item em uma tabela autorizada com base em um modelo Pydantic."""
    
    # Construção Dinâmica da Query SQL (Usando apenas os dados validados de data_dict)
    columns = ", ".join(data_dict.keys()) # Ex: "hero_name, hero_icon_img_link"
    placeholders = ", ".join(["%s"] * len(data_dict)) # Ex: "%s, %s"
    values = tuple(data_dict.values()) # Valores que serão passados de forma segura (prevenindo SQL Injection).

    try:
        # A query é construída dinamicamente.
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        # Variável 'new_id' (Escopo de Requisição): O ID do registro inserido (retornado pelo db.py).
        new_id = execute(sql=sql, params=values) # Envia para a camada DAO.
        
        if not new_id:
            raise HTTPException(status_code=500, detail="Não foi possível inserir os dados.")

        return {"message": f"Dados inseridos com sucesso na tabela '{table_name}'.", "new_id": new_id}
    except HTTPException as e:
        raise e
    except Exception as e:
        # Trata erros não capturados, mas o execute.py já deve ter tratado a maioria dos erros DB.
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar a inserção: {e}")
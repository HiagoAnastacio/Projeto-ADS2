# FLUXO E A LÓGICA:
# 1. Recebe 'table_name' e 'item_id' da URL e `request_body` (Escopo de Requisição).
# 2. Chama `validate_body` (Dependência CRÍTICA) para obter `data_dict` (dados seguros e limpos).
# 3. Constrói a Query SQL UPDATE dinâmica (SET {coluna} = %s).
# 4. A tupla de valores (`values`) é construída com os dados de `data_dict` + `item_id` (para o WHERE).
# 5. Chama `execute` (DAO).
# 6. Retorna 404 se o ID não for encontrado ou se o UPDATE não alterar nenhuma linha.
# A razão de existir: Fornecer um endpoint PUT genérico, seguro e capaz de fazer atualizações parciais (PATCH-like).

from fastapi import APIRouter, HTTPException, Path, Depends, Body # Razão: Roteamento, tratamento de erros, parâmetros, dependências e leitura do corpo.
from typing import Dict, Any # Razão: Tipagem.
from utils.function_execute import execute # Razão: Importa a função DAO para acesso ao DB.
from utils.dependencies import validate_body # Razão: Importa a dependência de validação (CRÍTICA).
from fastapi_limiter.depends import RateLimiter # Razão: Importa o limitador de taxa (Camada de Segurança).

# Variável 'router' (Escopo Global/Módulo).
router = APIRouter()

@router.put("/update/{table_name}/{item_id}", tags=["Generic Data Management"],
            # Rate Limiter DESATIVADO (Risco de DoS, mas mantido assim por sua configuração original)
            # dependencies=[Depends(RateLimiter(times=5, seconds=30))] 
) 
async def update_data(
    # Variável 'table_name' (Escopo de Requisição): Nome da tabela.
    table_name: str = Path(..., description="Nome da tabela para atualização."), 
    # Variável 'item_id' (Escopo de Requisição): ID da linha a ser atualizada.
    item_id: int = Path(..., description="ID do item a ser atualizado."), 
    
    # Variável 'request_body' (Escopo de Requisição): Corpo bruto (para documentação Swagger).
    request_body: Dict[str, Any] = Body(..., description="Corpo JSON com os dados para atualizar."),
    
    # Variável 'data_dict' (Escopo de Requisição): Resultado da validação Pydantic (dados seguros).
    data_dict: Dict[str, Any] = Depends(validate_body) # CRÍTICO: Injeta os dados validados.
):
    """Atualiza um item em uma tabela autorizada com base no ID e em um modelo Pydantic."""
    
    if not data_dict:
        # Erro 400 se o corpo estiver vazio (Pydantic deve impedir isso, mas é uma verificação defensiva).
        raise HTTPException(status_code=400, detail="Corpo da requisição não pode ser vazio.")
    
    # 1. Construção Dinâmica da Query SQL de UPDATE
    # Variável 'set_clauses' (Escopo de Requisição): Cria a parte "coluna = %s" para cada campo presente em data_dict.
    set_clauses = [f"{column} = %s" for column in data_dict.keys()]
    sql_set = ", ".join(set_clauses)
    
    # Variável 'values' (Escopo de Requisição): Tupla de valores para o SQL, incluindo o ID no final para o WHERE.
    values = tuple(list(data_dict.values()) + [item_id])

    try:
        # A query é construída dinamicamente.
        sql = f"UPDATE {table_name} SET {sql_set} WHERE {table_name}_id = %s"
        # Variável 'rows_affected' (Escopo de Requisição): Número de linhas alteradas.
        rows_affected = execute(sql=sql, params=values) # Envia para a camada DAO.
        
        # 2. Verificação de Resultado
        if not rows_affected:
            # Retorna 404 se o ID não existe ou se não houve alteração.
            raise HTTPException(status_code=404, detail=f"Item com ID {item_id} não encontrado ou não houve alteração.")

        return {"message": f"Item com ID {item_id} atualizado com sucesso na tabela '{table_name}'."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar a atualização: {e}")
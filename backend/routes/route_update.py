# =======================================================================================
# MÓDULO DE ROTA - PUT (ATUALIZAÇÃO)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Define um endpoint genérico `PUT /api/update/{table_name}/{item_id}`.
# 2. Recebe 'table_name' e 'item_id' da URL.
# 3. Injeção de Dependência: Chama a dependência `validate_body` para validar, limpar
#    e retornar um dicionário (`data_dict`) com os dados seguros para atualização.
# 4. Constrói a Query SQL `UPDATE` dinamicamente com base nos campos presentes em `data_dict`,
#    permitindo atualizações parciais (semelhante a um PATCH).
# 5. Chama a função `execute` da camada DAO para rodar o comando SQL.
# 6. Verifica se alguma linha foi de fato alterada (`rows_affected`) e retorna um erro
#    404 se o ID não for encontrado ou se os dados enviados forem idênticos aos existentes.
#
# RAZÃO DE EXISTIR: Fornecer um endpoint genérico, seguro e padronizado para
# atualizar registros existentes em qualquer tabela autorizada.
# =======================================================================================

from fastapi import APIRouter, HTTPException, Path, Depends, Body 
from typing import Dict, Any
from utils.function_execute import execute # Importa a função DAO.
from utils.dependencies import validate_body # Importa a dependência de validação.
import logging

# Variável 'router' (Escopo Global/Módulo).
router = APIRouter()
# Configuração básica do logger para este módulo.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@router.put("/update/{table_name}/{item_id}", tags=["Generic Data Management"]) 
async def update_data(
    # Parâmetro da URL para o nome da tabela.
    table_name: str = Path(..., description="Nome da tabela para atualização."), 
    # Parâmetro da URL para o ID do item a ser atualizado.
    item_id: int = Path(..., description="ID do item a ser atualizado."), 
    
    # Parâmetro do corpo da requisição, usado para documentação no Swagger.
    request_body: Dict[str, Any] = Body(..., description="Corpo JSON com os dados para atualizar."),
    
    # Dependência: O resultado da execução de `validate_body` é injetado aqui.
    # `data_dict` contém apenas os dados validados e seguros.
    data_dict: Dict[str, Any] = Depends(validate_body) 
):
    """Atualiza um item em uma tabela autorizada com base no ID."""
    
    # Verificação defensiva para garantir que o corpo validado não esteja vazio.
    if not data_dict:
        raise HTTPException(status_code=400, detail="Corpo da requisição com dados para atualização não pode ser vazio.")
    
    # 1. Construção Dinâmica da Query SQL de UPDATE
    # Cria uma lista de strings no formato "`coluna` = %s" para cada chave no dicionário.
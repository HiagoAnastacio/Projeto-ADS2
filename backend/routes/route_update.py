from fastapi import APIRouter, HTTPException, Path, Request
from pydantic import BaseModel, ValidationError
from utils.function_execute import execute
from model.model_resolver import get_model_for_table
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

router = APIRouter()

@router.put("/update/{table_name}/{item_id}", tags=["Generic Data Management"])
async def update_data(
    table_name: str = Path(..., description="Nome da tabela para atualização."),
    item_id: int = Path(..., description="ID do item a ser atualizado."),
    request: Request = None  # Recebe o objeto de requisição completo
):
    """
    Atualiza um item em uma tabela autorizada com base no ID e em um modelo Pydantic.
    """
    try:
        # Tenta obter o modelo Pydantic em tempo de execução
        model: BaseModel = get_model_for_table(table_name)
    except ValueError as e:
        # Se não houver modelo, retorna erro 400
        raise HTTPException(status_code=400, detail=str(e))

    try:
        # Lê o corpo da requisição como JSON
        json_data = await request.json()
        # Valida manualmente os dados contra o modelo Pydantic
        validated_data = model.model_validate(json_data)
        data_dict = validated_data.model_dump()
    except ValidationError as e:
        # Em caso de erro de validação do Pydantic, retorna 422
        logging.error(f"Erro de validação Pydantic: {e.errors()}")
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        # Outros erros de leitura do JSON
        logging.error(f"Erro ao processar o corpo da requisição: {e}")
        raise HTTPException(status_code=400, detail="Corpo da requisição inválido.")

    # Converte o modelo Pydantic validado para um dicionário para a consulta SQL
    set_clauses = [f"{column} = %s" for column in data_dict.keys()]
    sql_set = ", ".join(set_clauses)
    values = tuple(list(data_dict.values()) + [item_id])

    try:
        sql = f"UPDATE {table_name} SET {sql_set} WHERE {table_name}_id = %s"
        rows_affected = execute(sql=sql, params=values)
        if not rows_affected:
            raise HTTPException(status_code=404, detail=f"Item com ID {item_id} não encontrado ou não houve alteração.")

        return {"message": f"Item com ID {item_id} atualizado com sucesso na tabela '{table_name}'."}
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        logging.error(f"Erro no banco de dados durante a atualização: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar dados: {e}")
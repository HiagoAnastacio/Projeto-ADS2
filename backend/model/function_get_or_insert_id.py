# app/utils/db_functions.py
from typing import Optional, Union, Any

from utils.function_execute import execute  # Sua função que executa comandos SQL

def get_or_insert_id(table_name: str, column_name: str, item_name: str) -> Optional[Union[int, Any]]:
    """
    Busca o ID de um item pelo nome. Se não existir, insere um novo item
    e retorna o ID (existente ou recém-criado).
    """
    # 1. Tenta encontrar o item primeiro
    sql_select = f"SELECT {table_name}_id FROM {table_name} WHERE {column_name} = %s"
    result = execute(sql=sql_select, params=(item_name,))
    
    if result and len(result) > 0:
        return result[0][f'{table_name}_id']
    else:
        # 2. Se não encontrou, insere o novo item e retorna o ID da nova linha
        sql_insert = f"INSERT INTO {table_name} ({column_name}) VALUES (%s)"
        new_id = execute(sql=sql_insert, params=(item_name,))
        return new_id
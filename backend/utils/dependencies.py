# FLUXO E A LÓGICA:
# 1. Recebe dados brutos (`request_body`) e o nome da tabela (`table_name`) injetados pela rota (Escopo de Requisição).
# 2. Usa `table_name` para buscar o Schema Pydantic correspondente via `get_model_for_table`.
# 3. O Pydantic valida o `request_body`, transformando-o em `validated_data`.
# 4. Tipos complexos (como `HttpUrl`) são convertidos para `str` (formato aceito pelo MySQL).
# 5. Retorna o dicionário `data_dict` limpo e seguro para a rota.
# A razão de existir: Camada de Validação Centralizada. Garante que qualquer requisição de escrita (POST/PUT) só chegue ao banco de dados com dados íntegros e corretos (segurança de dados).

from fastapi import HTTPException, Path # Razão: Tratamento de erros (400, 422) e definição de parâmetros de rota.
from pydantic import BaseModel, ValidationError, HttpUrl # Razão: Classes para validação (BaseModel), tratamento de erros de validação e tipo HttpUrl.
from typing import Dict, Any # Razão: Tipagem (dicionários e tipos genéricos).
from model.model_resolver import get_model_for_table # Razão: Função crítica para buscar dinamicamente o modelo Pydantic da tabela.

async def validate_body( 
    # Variável 'request_body' (Escopo de Requisição): Contém o JSON bruto. Enviada da rota via Body.
    request_body: Dict[str, Any], 
    # Variável 'table_name' (Escopo de Requisição): Contém o nome da tabela. Enviada da rota via Path.
    table_name: str = Path(...) 
) -> Dict[str, Any]:
    """Dependência que valida o corpo da requisição JSON com base no modelo Pydantic da tabela."""
    
    # 1. Resolução do Modelo
    try:
        # Variável 'model' (Escopo de Requisição): A classe Pydantic (ex: HeroBase).
        model: BaseModel = get_model_for_table(table_name) # Obtém o modelo dinamicamente.
    except ValueError as e:
        # Retorna erro 400 se o nome da tabela for inválido ou não mapeado em model_resolver.py.
        raise HTTPException(status_code=400, detail=str(e))
    
    # 2. Validação Pydantic
    try:
        # Variável 'validated_data' (Escopo de Requisição): Objeto Pydantic validado.
        validated_data = model.model_validate(request_body) 
        # Variável 'data_dict' (Escopo de Requisição): Dicionário Python limpo (sem nulos).
        # É enviado para o route_post/route_update.
        data_dict = validated_data.model_dump(exclude_none=True)
        
        # 3. Conversão de Tipos Complexos (HttpUrl para str)
        # Variável 'converted_data_dict' (Escopo de Requisição): Dicionário final pronto para o MySQL.
        converted_data_dict = {}
        for key, value in data_dict.items():
            if isinstance(value, HttpUrl): 
                converted_data_dict[key] = str(value) # HttpUrl é convertido para a string do link.
            else:
                converted_data_dict[key] = value 
                
        return converted_data_dict # Retorna o dicionário final para a rota (data_dict no route_post/update).
        
    # 4. Tratamento de Exceções
    except ValidationError as e:
        # Erro 422 (Unprocessable Entity) se os dados não baterem com o Schema Pydantic.
        raise HTTPException(status_code=422, detail="Erro de validação de dados: " + str(e))
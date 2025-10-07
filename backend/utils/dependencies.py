# =======================================================================================
# MÓDULO DE DEPENDÊNCIAS DO FASTAPI
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. A função `validate_body` é uma "Dependência" do FastAPI. Ela é executada
#    automaticamente antes da lógica principal de uma rota (como `insert_data`).
# 2. Ela recebe o `table_name` da URL e o `request_body` (JSON bruto).
# 3. Usa o `model_resolver` para obter o schema Pydantic correto para a tabela.
# 4. Tenta validar o JSON bruto contra o schema. Se a validação falhar, levanta um erro
#    HTTP 422 (Unprocessable Entity) com detalhes sobre os campos incorretos.
# 5. Se a validação for bem-sucedida, converte tipos especiais (como HttpUrl) para
#    strings e retorna um dicionário Python limpo e seguro para a rota.
#
# RAZÃO DE EXISTIR: Centralizar a lógica de validação do corpo da requisição.
# Ao usar a Injeção de Dependência do FastAPI, garantimos que esta validação
# seja executada para todas as rotas de escrita (POST/PUT) de forma consistente e automática.
# =======================================================================================

from fastapi import HTTPException, Path
from pydantic import BaseModel, ValidationError, HttpUrl
from typing import Dict, Any
from model.model_resolver import get_model_for_table

async def validate_body( 
    # Variável 'request_body' (Escopo de Requisição): Contém o JSON bruto da requisição.
    request_body: Dict[str, Any], 
    # Variável 'table_name' (Escopo de Requisição): Contém o nome da tabela da URL.
    table_name: str = Path(...) 
) -> Dict[str, Any]:
    """Dependência que valida o corpo da requisição com base no modelo Pydantic da tabela."""
    
    # 1. Resolução do Modelo
    try:
        # Variável 'model' (Escopo de Requisição): A classe Pydantic (ex: HeroBase).
        model: BaseModel = get_model_for_table(table_name)
    except ValueError as e:
        # Retorna erro 400 se a tabela for inválida.
        raise HTTPException(status_code=400, detail=str(e))
    
    # 2. Validação Pydantic
    try:
        # Tenta validar o JSON bruto. Se falhar, levanta `ValidationError`.
        validated_data = model.model_validate(request_body) 
        # Converte o objeto Pydantic validado de volta para um dicionário.
        data_dict = validated_data.model_dump(exclude_none=True)
        
        # 3. Conversão de Tipos
        # Razão: O driver do MySQL não entende tipos Pydantic como HttpUrl.
        converted_data_dict = {}
        for key, value in data_dict.items():
            if isinstance(value, HttpUrl): 
                converted_data_dict[key] = str(value)
            else:
                converted_data_dict[key] = value 
                
        # Retorna o dicionário final, limpo e seguro, para a rota.
        return converted_data_dict
        
    except ValidationError as e:
        # Erro 422 se os dados não corresponderem ao schema.
        raise HTTPException(status_code=422, detail="Erro de validação de dados: " + str(e))
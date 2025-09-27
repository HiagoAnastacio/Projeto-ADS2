# FLUXO E A LÓGICA:
# 1. O **TABLE_MODEL_MAPPING** (Escopo Global/Módulo) é criado no startup da aplicação, mapeando estaticamente todas as tabelas aos seus Schemas.
# 2. A função **`get_model_for_table`** é chamada pela dependência `validate_body` (em dependencies.py) em tempo de requisição.
# 3. Ela recebe a string `table_name` (Escopo de Requisição) e faz a busca no dicionário global.
# 4. Retorna a **Classe Pydantic** (ex: HeroBase) correspondente para o chamador.
# 5. Se a tabela não for mapeada, lança um erro, que é capturado e transformado em HTTP 400 Bad Request.
# RAZÃO DE EXISTIR: É o serviço de **mapeamento centralizado**. Permite que o CRUD seja **genérico** ao conectar dinamicamente o Path Parameter (`table_name`) com o Schema de validação correto (Pydantic).

from fastapi import HTTPException # Razão de Existir: Para levantar erros padronizados caso a tabela não exista/não seja mapeada.
from typing import Type # Razão de Existir: Tipagem para indicar que a função retorna uma **Classe** (`Type[BaseModel]`).
from pydantic import BaseModel # Razão de Existir: Classe base do Pydantic para tipagem.
from model.models import ( # Razão de Existir: Importa TODAS as classes de Schemas Pydantic definidas.
    HeroBase, MapBase, RoleBase, RankBase, GameModeBase,
    HeroWinData, HeroPickData, HeroMapWinData, HeroMapPickData,
    HeroRankWinData, HeroRankPickData, HeroRankMapWinData, HeroRankMapPickData
)

# Variável 'TABLE_MODEL_MAPPING' (Escopo Global/Módulo): Dicionário estático.
# Razão: O coração da genericidade. Mapeia a string da URL/DB para a classe de validação (Pydantic).
TABLE_MODEL_MAPPING: dict[str, Type[BaseModel]] = {
    "hero": HeroBase,
    "map": MapBase,
    "role": RoleBase,
    "rank": RankBase,
    "game_mode": GameModeBase,
    "hero_win": HeroWinData,
    "hero_pick": HeroPickData,
    "hero_map_win": HeroMapWinData,
    "hero_map_pick": HeroMapPickData,
    "hero_rank_win": HeroRankWinData,
    "hero_rank_pick": HeroRankPickData,
    "hero_rank_map_win": HeroRankMapWinData,
    "hero_rank_map_pick": HeroRankMapPickData,
}

def get_model_for_table(table_name: str) -> Type[BaseModel]:
    """
    Retorna a classe do modelo Pydantic correspondente a uma tabela.
    Levanta um erro se a tabela não for encontrada.
    """
    # Variável 'model' (Escopo de Requisição): Tenta buscar o modelo no dicionário global (TABLE_MODEL_MAPPING).
    model = TABLE_MODEL_MAPPING.get(table_name.lower())
    
    if not model:
        # Lança ValueError se a tabela não estiver no mapeamento, indicando uma falha de esquema.
        # É capturado em dependencies.py e transformado em HTTP 400 Bad Request.
        raise ValueError(f"A tabela '{table_name}' não é válida ou não está mapeada para esta operação.")
        
    # Retorna a CLASSE (não a instância) para ser usada na validação.
    # Enviada para 'dependencies.py'.
    return model
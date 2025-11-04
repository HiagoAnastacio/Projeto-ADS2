# =======================================================================================
# MÓDULO DE CARREGADOR - FATOS NÍVEL 3 (L do ETL)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Contém a função `load_fact_data` (movida de populate_lvl3.py).
# 2. Encapsula a lógica de iteração sobre os dados extraídos da API e a
#    execução da query SQL INSERT (sem ON DUPLICATE KEY) para as tabelas de fato.
# 3. Utiliza o `utils.function_execute.execute` (conforme solicitado) para a 
#    execução real da query.
#
# RAZÃO DE EXISTIR: Isolar a lógica de *Carga* (o "L") das tabelas de fato.
# =======================================================================================

import logging
from typing import Dict, Any, List
import datetime

# Importa o executor de SQL do ETL (conforme solicitado)
from utils.function_execute import execute

logger = logging.getLogger(__name__)

# --- Carregador 3: Tabelas de Fato (Genérico) ---

def load_fact_data(
    sql_query: str, 
    records: List[Dict[str, Any]], 
    hero_map: Dict[str, int], 
    context: Dict[str, Any], 
    timestamp: datetime.datetime
):
    """
    Função genérica para inserir dados (win/pick) em uma tabela de fato.
    (Lógica movida de populate_lvl3.py - v0.7.0)
    """
    insert_count = 0
    # Determina se a query é para win_rate ou pick_rate com base no nome da coluna
    is_win_rate_query = "win_rate" in sql_query
    
    # Itera sobre os dados extraídos
    for hero_data in records:
        stats = hero_data.get('cells', {})
        # Pega o nome de exibição (ex: 'Ana') ou usa o ID/slug (ex: 'ana') como fallback
        hero_display_name = stats.get('name') or hero_data.get('id')
        if not hero_display_name:
            continue
        # Mapeia o nome do herói da API para o hero_id do nosso banco de dados
        hero_id = hero_map.get(hero_display_name)
        if not hero_id:
            continue
        
        # Pega a métrica (win_rate ou pick_rate)
        rate = stats.get("winrate") if is_win_rate_query else stats.get("pickrate")

        if rate is not None:
            try:
                # Constrói a tupla de parâmetros na ordem correta
                params_list = [hero_id]
                params_list.extend(context.values()) # Adiciona FKs de contexto (rank_id, map_id, etc.)
                params_list.append(rate) # Adiciona a métrica
                params_list.append(timestamp) # Adiciona o timestamp
                params_tuple = tuple(params_list)
                
                # Executa o INSERT simples
                execute(sql_query, params_tuple)
                insert_count += 1
            except Exception as e:
                # Se o erro for 'Duplicate entry', significa que já inserimos esse snapshot
                # (ex: rodando o script duas vezes rápido). Isso é esperado e pode ser ignorado.
                if 'Duplicate entry' not in str(e) and '1062' not in str(e):
                    pass # Ignora erro de snapshot duplicado
                else:
                    logger.error(f"Falha ao inserir em {sql_query.split()[2]}: {e} - Params: {params_tuple}")
    return insert_count
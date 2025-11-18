# ===============================================================================
# CAMADA DE ACESSO A DADOS ANALÍTICOS (DIMENSÕES)
# ===============================================================================

from utils.db_manager import execute_api_query
from mysql.connector.connection import MySQLConnection
from typing import List, Dict, Any

def get_dimension_data(connection: MySQLConnection, dimension_name: str) -> List[Dict[str, Any]]:
    """
    Busca a lista de IDs e Nomes para uma tabela de dimensão específica.
    
    @param connection: Conexão MySQL do Pool (injetada pelo FastAPI).
    @param dimension_name: Nome da tabela de dimensão (ex: 'hero', 'rank', 'map').
    @return: Lista de dicionários com ID e Nome.
    """
    # Evita SQL Injection garantindo que dimension_name seja um nome de tabela válido
    # Nomes das colunas são determinados dinamicamente com base no nome da tabela.
    
    if dimension_name == 'hero':
        sql = "SELECT hero_id AS id, hero_name AS name FROM hero ORDER BY hero_name;"
    elif dimension_name == 'rank':
        sql = "SELECT rank_id AS id, rank_name AS name FROM rank ORDER BY rank_id;"
    elif dimension_name == 'game_mode':
        sql = "SELECT game_mode_id AS id, game_mode_name AS name FROM game_mode ORDER BY game_mode_name;"
    elif dimension_name == 'map':
        # Retorna o nome do mapa e o nome do modo de jogo
        sql = """
            SELECT m.map_id AS id, m.map_name AS name, gm.game_mode_name AS mode 
            FROM map m
            JOIN game_mode gm ON m.game_mode_id = gm.game_mode_id
            ORDER BY m.map_name;
        """
    else:
        # Lança erro 400 (Bad Request) para o FastAPI
        raise ValueError(f"Dimensão '{dimension_name}' não suportada.")

    # Executa a consulta e retorna a lista de dicionários
    result = execute_api_query(connection, sql)
    return result
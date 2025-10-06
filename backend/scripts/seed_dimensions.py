# backend/scripts/seed_dimensions.py

import sys
from os.path import abspath, dirname

# Configuração de Path para encontrar os módulos da aplicação
project_root = dirname(dirname(abspath(__file__)))
sys.path.append(project_root)

# Importação dos Módulos da Aplicação
try:
    from utils.function_execute import execute
except ImportError as e:
    print(f"ERRO: Falha ao importar módulos. Verifique o ambiente virtual e a estrutura de pastas. {e}")
    sys.exit(1)

# --- DADOS ESTÁTICOS (DIMENSÕES) ---

ROLES = ["TANK", "DAMAGE", "SUPPORT"]
RANKS = ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster and Champion"]
GAME_MODES = ["Control", "Escort", "Flashpoint", "Hybrid", "Push", "Clash", "Assault"]

# --- LISTA DE MAPAS ATUALIZADA ---
MAPS = [
    # Control
    ("Antarctic Peninsula", "Control"), ("Busan", "Control"), ("Ilios", "Control"),
    ("Lijiang Tower", "Control"), ("Nepal", "Control"), ("Oasis", "Control"), ("Samoa", "Control"),
    # Escort
    ("Circuit Royal", "Escort"), ("Dorado", "Escort"), ("Havana", "Escort"),
    ("Junkertown", "Escort"), ("Rialto", "Escort"), ("Route 66", "Escort"),
    ("Shambali Monastery", "Escort"), ("Watchpoint: Gibraltar", "Escort"),
    # Flashpoint
    ("New Junk City", "Flashpoint"), ("Suravasa", "Flashpoint"), ("Aatlis", "Flashpoint"),
    # Hybrid
    ("Blizzard World", "Hybrid"), ("Eichenwalde", "Hybrid"), ("Hollywood", "Hybrid"),
    ("King's Row", "Hybrid"), ("Midtown", "Hybrid"), ("Numbani", "Hybrid"),
    ("Paraíso", "Hybrid"),
    # Push
    ("Colosseo", "Push"), ("Esperança", "Push"), ("New Queen Street", "Push"), ("Runasapi", "Push"),
    # Clash
    ("Hanaoka", "Clash"), ("Throne of Anubis", "Clash"),
    # Assault (Mapas antigos, incluídos para dados históricos)
    ("Hanamura", "Assault"), ("Horizon Lunar Colony", "Assault"), ("Paris", "Assault"),
    ("Temple of Anubis", "Assault"), ("Volskaya Industries", "Assault")
]

# --- FUNÇÕES DE "SEEDING" ---

def seed_single_column_table(table_name: str, column_name: str, data: list):
    """Popula uma tabela de dimensão com uma única coluna de texto."""
    print(f"--- Populando tabela: {table_name} ---")
    
    # AJUSTE: Adicionadas crases (`) para proteger nomes de tabelas e colunas.
    sql = f"INSERT INTO `{table_name}` (`{column_name}`) VALUES (%s) ON DUPLICATE KEY UPDATE `{column_name}`=VALUES(`{column_name}`);"
    
    count = 0
    for item in data:
        rows_affected = execute(sql, (item,))
        if rows_affected == 1:
            count += 1
    print(f"{count} novo(s) registro(s) inserido(s) em '{table_name}'.")

def seed_maps_table():
    """Popula a tabela 'map', que possui uma dependência (chave estrangeira)."""
    print("--- Populando tabela: map ---")
    
    game_modes_from_db = execute("SELECT game_mode_id, game_mode_name FROM game_mode;")
    if not game_modes_from_db:
        print("ERRO: A tabela 'game_mode' precisa ser populada primeiro. Abortando.")
        return
        
    game_mode_map = {mode['game_mode_name']: mode['game_mode_id'] for mode in game_modes_from_db}

    # AJUSTE: Adicionadas crases (`) para proteger nomes de tabelas e colunas.
    sql = "INSERT INTO `map` (`map_name`, `game_mode_id`) VALUES (%s, %s) ON DUPLICATE KEY UPDATE `map_name`=VALUES(`map_name`);"
    
    count = 0
    for map_name, game_mode_name in MAPS:
        game_mode_id = game_mode_map.get(game_mode_name)
        if game_mode_id:
            rows_affected = execute(sql, (map_name, game_mode_id))
            if rows_affected > 0:
                count += 1
        else:
            print(f"AVISO: Modo de jogo '{game_mode_name}' para o mapa '{map_name}' não encontrado no banco.")
            
    print(f"{count} novo(s) mapa(s) inserido(s).")

# --- PONTO DE ENTRADA DO SCRIPT ---
if __name__ == "__main__":
    print("Iniciando o processo de 'seeding' do banco de dados para dados estáticos...")
    
    seed_single_column_table("role", "role", ROLES)
    seed_single_column_table("rank", "rank_name", RANKS)
    seed_single_column_table("game_mode", "game_mode_name", GAME_MODES)
    seed_maps_table()
    
    print("\nProcesso de 'seeding' concluído.")
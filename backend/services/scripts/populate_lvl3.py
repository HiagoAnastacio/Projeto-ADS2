# =======================================================================================
# SCRIPT ORQUESTRADOR - POPULAÇÃO DE TABELAS DE FATO (NÍVEL 3)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. É o "coletor" principal, responsável por buscar as estatísticas dinâmicas.
# 2. A função `main_populate_facts` orquestra o processo:
#    a. LÊ todas as tabelas de dimensão (`hero`, `rank`, `map`) para a memória.
#    b. Entra em um loop aninhado, iterando sobre cada `rank` e cada `map`.
#    c. CHAMA o helper `fetch_api_data` para cada combinação.
#       Esta função (fetch_api_data) é responsável tanto por BUSCAR (Extract)
#       quanto por LIMPAR (Transform) os dados.
#    d. CHAMA a função local `load_stats_to_db` para inserir os dados (Load).
#
# RAZÃO DE EXISTIR: Orquestrar a busca massiva de dados estatísticos.
#
# (ALTERAÇÃO 2025-10-21): As queries SQL foram alteradas de 'INSERT...ON DUPLICATE KEY UPDATE'
# para 'INSERT' simples, para permitir o armazenamento historiográfico.
# =======================================================================================

import sys
import logging
import argparse
from typing import Dict, Any, List
from slugify import slugify

# --- Configuração de Path e Logger ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

# --- Importações ---
try:
    from utils.function_execute import execute
    from utils.extraction_helpers import fetch_api_data
except ImportError:
    logger.critical("Erro fatal: Não foi possível importar os módulos `utils`. "
                    "Certifique-se de que o projeto foi instalado com `pip install -e .` "
                    "ou que o sys.path está correto.", exc_info=True)
    sys.exit(1)

# --- LÓGICA DE CARGA (LOAD) ---
def load_stats_to_db(records: Dict[str, Dict[str, float]], rank_id: int, map_id: int, hero_map: Dict[str, int]): #
    """Carrega as estatísticas transformadas para as tabelas de fato."""
    
    sql_win = """
        INSERT INTO `hero_rank_map_win` (`hero_id`, `rank_id`, `map_id`, `win_rate`)
        VALUES (%s, %s, %s, %s);
    """ #
    
    sql_pick = """
        INSERT INTO `hero_rank_map_pick` (`hero_id`, `rank_id`, `map_id`, `pick_rate`)
        VALUES (%s, %s, %s, %s);
    """ #
    
    insert_count_win = 0
    insert_count_pick = 0
    
    for hero_name, stats in records.items():
        hero_id = hero_map.get(hero_name)
        if hero_id:
            try:
                # Insere Win Rate
                if "win_rate" in stats:
                    execute(sql_win, (hero_id, rank_id, map_id, stats["win_rate"])) #
                    insert_count_win += 1
                
                # Insere Pick Rate
                if "pick_rate" in stats:
                    execute(sql_pick, (hero_id, rank_id, map_id, stats["pick_rate"])) #
                    insert_count_pick += 1
                    
            except Exception as e:
                logger.error(f"Falha ao inserir estatística para {hero_name} (ID: {hero_id}) no rank {rank_id}, mapa {map_id}. Erro: {e}")
                
    logger.info(f"Inseridos {insert_count_win} registros de win_rate e {insert_count_pick} registros de pick_rate.")

# --- ORQUESTRAÇÃO ---
# ALTERAÇÃO: A função agora aceita 'limit' como um parâmetro opcional,
# em vez de um objeto 'args' complexo.
def main_populate_facts(limit: int = 0): #
    """Função principal que orquestra a busca e carga das estatísticas."""
    logger.info("--- LENDO DIMENSÕES DO BANCO DE DADOS ---")
    
    try:
        heroes = execute("SELECT hero_id, hero_name FROM hero") #
        ranks = execute("SELECT rank_id, rank_name FROM `rank`") #
        maps = execute("SELECT map_id, map_name FROM map") #

        if not all([heroes, ranks, maps]):
            logger.error("Uma ou mais tabelas de dimensão (hero, rank, map) estão vazias. "
                         "Execute os scripts de Nível 1 (SQL) e Nível 2 (populate_hero, populate_map) primeiro.")
            return

        dims = {
            "heroes": {h['hero_name']: h['hero_id'] for h in heroes},
            "ranks": {r['rank_name']: r['rank_id'] for r in ranks},
            "maps": {m['map_name']: m['map_id'] for m in maps}
        }
        logger.info(f"Dimensões carregadas: {len(dims['heroes'])} heróis, {len(dims['ranks'])} ranks, {len(dims['maps'])} mapas.")
        
    except Exception as e:
        logger.critical(f"Falha fatal ao ler as tabelas de dimensão. Verifique a conexão com o banco. Erro: {e}")
        return

    logger.info("--- INICIANDO BUSCA E CARGA DE DADOS DE FATO (WIN/PICK RATE) ---")
    base_url = "https://overwatch.blizzard.com/en-us/rates/data?"
    
    ranks_to_process = list(dims["ranks"].items())
    
    # ALTERAÇÃO: Usa o parâmetro 'limit' diretamente.
    if limit > 0:
        ranks_to_process = ranks_to_process[:limit]
        logger.warning(f"Execução limitada aos primeiros {limit} rank(s) para fins de teste.")
    
    total_ranks = len(ranks_to_process)
    total_maps = len(dims["maps"])
    
    for i, (rank_name, rank_id) in enumerate(ranks_to_process, 1):
        logger.info(f"== Processando Rank: {rank_name} ({i}/{total_ranks}) ==")
        
        for j, (map_name, map_id) in enumerate(dims["maps"].items(), 1):
            
            rank_slug = slugify(rank_name)
            map_slug = slugify(map_name)
            
            api_url = f"{base_url}{rank_slug}/{map_slug}/"
            
            transformed_data = fetch_api_data(api_url) #
            
            if transformed_data:
                # O `load_stats_to_db` agora só carrega (Load)
                load_stats_to_db(transformed_data, rank_id, map_id, dims["heroes"]) #
            else:
                logger.warning(f"Não foram encontrados dados (ou dados transformáveis) para Rank: '{rank_name}', Mapa: '{map_name}'")
            
            logger.info(f"Processamento do mapa '{map_name}' ({j}/{total_maps}) concluído.")
                
    logger.info("Execução do script de população de fatos (Nível 3) concluída.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script para popular as tabelas de fato com estatísticas de Win/Pick Rate.")
    parser.add_argument(
        "--limit", 
        type=int, 
        default=0, 
        help="Limita a execução a um número X de ranks. Use 0 (padrão) para rodar todos os ranks."
    )
    args = parser.parse_args()
    
    # ALTERAÇÃO: Passa apenas o valor 'limit', não o objeto 'args' inteiro.
    main_populate_facts(limit=args.limit) #
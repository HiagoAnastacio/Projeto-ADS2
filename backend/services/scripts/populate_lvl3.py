# =======================================================================================
# SCRIPT ORQUESTRADOR - POPULAÇÃO DE TABELAS DE FATO (NÍVEL 3) (REFATORADO v3)
# =======================================================================================
# ... (restante dos imports e config de logger) ...
# ARQUITETURA (Mudança v3):
# 1. Corrige o loop em `load_stats_to_db` para iterar sobre a lista de heróis
#    recebida da API, em vez de esperar um dicionário.
# ... (restante das mudanças anteriores) ...
# =======================================================================================

import sys
import logging
import argparse
from typing import Dict, Any, List # Importa List
from slugify import slugify
from types import SimpleNamespace

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

from utils.function_execute import execute
from utils.extraction_helpers import fetch_api_data

# --- LÓGICA DE CARGA (LOAD) - COM LOOP CORRIGIDO ---
def load_stats_to_db(records: List[Dict[str, Any]], rank_id: int, rank_name: str, map_id: int, map_name: str, hero_map: Dict[str, int]):
    """Carrega as estatísticas transformadas (lista de heróis) para as tabelas de fato."""
    sql_win = """
        INSERT INTO `hero_rank_map_win` (`hero_id`, `rank_id`, `map_id`, `win_rate`)
        VALUES (%s, %s, %s, %s);
    """
    sql_pick = """
        INSERT INTO `hero_rank_map_pick` (`hero_id`, `rank_id`, `map_id`, `pick_rate`)
        VALUES (%s, %s, %s, %s);
    """

    win_count = 0
    pick_count = 0
    
    # --- CORREÇÃO DO LOOP ---
    # 'records' é a LISTA de dicionários de heróis vinda de raw_data['rates']
    for hero_data in records: 
        # Cada hero_data é um dicionário como: {'id': 'ana', 'cells': {'name': 'Ana', ...}, 'hero': {...}}
        
        # Tenta obter o nome do herói. A chave pode ser 'name' dentro de 'cells', ou 'name' dentro de 'hero', 
        # ou talvez o 'id' seja o nome/slug. VERIFIQUE A ESTRUTURA EXATA DO JSON DA API.
        # Vamos tentar algumas opções comuns:
        hero_api_identifier = hero_data.get('id') # Ex: 'ana'
        stats = hero_data.get('cells', {}) # Pega o dict 'cells' onde geralmente ficam as stats
        hero_display_name = stats.get('name') # Ex: 'Ana'
        
        # Usa o nome de exibição (se disponível) ou o identificador para mapear para o ID do nosso banco
        hero_name_to_map = hero_display_name if hero_display_name else hero_api_identifier
        
        if not hero_name_to_map:
            logger.warning(f"Não foi possível identificar o nome/ID do herói nos dados: {hero_data}")
            continue # Pula este registro

        hero_id = hero_map.get(hero_name_to_map) # Mapeia 'Ana' ou 'ana' para o hero_id

        if hero_id:
            # Insere Win Rate (usa 'stats' que pegamos de 'cells')
            win_rate = stats.get("winrate") # A API parece usar 'winrate' (minúsculo) no log
            if win_rate is not None:
                params_win = (hero_id, rank_id, map_id, win_rate)
                try:
                    execute(sql_win, params_win)
                    logger.info(f"INSERT WinRate: Hero='{hero_name_to_map}' ({hero_id}), Rank='{rank_name}' ({rank_id}), Map='{map_name}' ({map_id}), Rate={win_rate}")
                    win_count += 1
                except Exception as e:
                    logger.error(f"Falha ao inserir win_rate para {hero_name_to_map} (R:{rank_id}, M:{map_id}): {e}")

            # Insere Pick Rate (usa 'stats' que pegamos de 'cells')
            pick_rate = stats.get("pickrate") # A API parece usar 'pickrate' (minúsculo) no log
            if pick_rate is not None:
                params_pick = (hero_id, rank_id, map_id, pick_rate)
                try:
                    execute(sql_pick, params_pick)
                    logger.info(f"INSERT PickRate: Hero='{hero_name_to_map}' ({hero_id}), Rank='{rank_name}' ({rank_id}), Map='{map_name}' ({map_id}), Rate={pick_rate}")
                    pick_count += 1
                except Exception as e:
                    logger.error(f"Falha ao inserir pick_rate para {hero_name_to_map} (R:{rank_id}, M:{map_id}): {e}")
        else:
            logger.warning(f"Herói '{hero_name_to_map}' encontrado nos dados da API, mas não existe na tabela 'hero'. Pulando inserção.")
    # --- FIM DA CORREÇÃO DO LOOP ---

    # logger.debug(f"Processados {win_count} win_rates e {pick_count} pick_rates para Rank ID: {rank_id}, Mapa ID: {map_id}")


# --- ORQUESTRAÇÃO (main_populate_facts) ---
# (O restante da função main_populate_facts permanece o mesmo da versão anterior)
def main_populate_facts(args):
    """Função principal que busca dados da API por rank/mapa e os carrega."""
    logger.info("--- Iniciando busca das Dimensões para o Nível 3 ---")
    try:
        dims = {
            "heroes": {item['hero_name']: item['hero_id'] for item in execute("SELECT `hero_id`, `hero_name` FROM `hero`")},
            "ranks": {item['rank_name']: item['rank_id'] for item in execute("SELECT `rank_id`, `rank_name` FROM `rank`")},
            "maps": {item['map_name']: item['map_id'] for item in execute("SELECT `map_id`, `map_name` FROM `map`")}
        }
        if not all([dims["heroes"], dims["ranks"], dims["maps"]]):
             raise Exception("Uma ou mais tabelas de dimensão estão vazias. Abortando.")
        logger.info(f"Dimensões carregadas: {len(dims['heroes'])} heróis, {len(dims['ranks'])} ranks, {len(dims['maps'])} mapas.")

    except Exception as e:
        logger.critical(f"Falha CRÍTICA ao carregar dimensões: {e}. Abortando Nível 3.", exc_info=True)
        raise e

    logger.info("--- INICIANDO BUSCA E CARGA DE DADOS DE FATO (WIN/PICK RATE) ---")
    base_url = "https://overwatch.blizzard.com/pt-br/rates/data?" # VERIFICAR SE ESTA URL BASE AINDA É VÁLIDA

    ranks_to_process = list(dims["ranks"].items())
    if hasattr(args, 'limit') and args.limit > 0:
        ranks_to_process = ranks_to_process[:args.limit]
        logger.warning(f"Execução limitada a {args.limit} rank(s).")

    total_requests = len(ranks_to_process) * len(dims["maps"])
    request_count = 0

    for rank_name, rank_id in ranks_to_process:
        logger.info(f"== Processando Rank: {rank_name} ==")
        for map_name, map_id in dims["maps"].items():
            request_count += 1
            logger.debug(f"Processando {request_count}/{total_requests}: Rank='{rank_name}', Mapa='{map_name}'")

            rank_slug = slugify(rank_name)
            map_slug = slugify(map_name)

            # VERIFICAR SLUG CORRETO PARA GRANDMASTER!
            # Exemplo:
            # if rank_name == "Grandmaster":
            #     rank_slug = "grandmaster" # Ou o slug correto da API

            params = f"platform=pc&gamemode=competitive&rank={rank_slug}&map={map_slug}"
            api_url = f"{base_url}{params}"

            raw_data = fetch_api_data(api_url)
            if raw_data:
                # Trata se a API retorna {'rates': [...]} ou a lista direto
                data_list_to_process = None
                if isinstance(raw_data, list):
                    data_list_to_process = raw_data
                elif isinstance(raw_data, dict) and 'rates' in raw_data and isinstance(raw_data['rates'], list):
                    data_list_to_process = raw_data['rates']

                if data_list_to_process is not None:
                     # Chama a função load_stats_to_db com a LISTA correta
                     load_stats_to_db(data_list_to_process, rank_id, rank_name, map_id, map_name, dims["heroes"])
                else:
                    logger.warning(f"Formato de dados inesperado recebido da API para Rank: '{rank_name}', Mapa: '{map_name}'. Dados: {str(raw_data)[:100]}...")
            else:
                pass # Erro já logado por fetch_api_data

    logger.info("Execução do script de população de fatos concluída.")


# --- Ponto de Entrada (se executado diretamente com argparse) ---
# (Permanece o mesmo)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Popula tabelas de fato (Win/Pick Rate) de Overwatch.")
    parser.add_argument("-l", "--limit", type=int, default=0, help="Limita a execução aos N primeiros ranks para teste.")
    script_args = parser.parse_args()
    logger.info(f"Executando 'populate_lvl3.py' diretamente {'com limite de ' + str(script_args.limit) + ' rank(s)' if script_args.limit > 0 else 'sem limite'}.")
    try:
        main_populate_facts(script_args)
    except Exception as e:
        logger.critical(f"Falha crítica na execução direta: {e}", exc_info=True)
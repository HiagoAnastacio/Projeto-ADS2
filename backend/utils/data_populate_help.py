import requests
import json
import logging
from typing import Dict, Any, List

# Pega o logger configurado pelo script que o chamou.
logger = logging.getLogger(__name__)

def fetch_api_data(api_url: str) -> dict | None:
    """
    Função: Faz uma chamada genérica a uma API e retorna o JSON.
    Razão de Existência: Centralizar a lógica de requisição HTTP, incluindo headers e
    tratamento de erro, para ser reutilizada por qualquer script de população.
    """
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    headers = {'User-Agent': user_agent}
    
    logger.debug(f"Buscando dados de: {api_url}")
    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except json.JSONDecodeError:
        logger.warning(f"Resposta não é um JSON válido para a URL: {api_url}")
        logger.debug(f"Conteúdo recebido (início): {response.text[:200]}")
        return None
    except requests.exceptions.RequestException as e:
        logger.warning(f"Erro na requisição para {api_url}: {e}")
        return None

def load_heroes_to_db(records: List[Dict[str, Any]], execute_func, role_map: Dict[str, int]):
    """
    Função: Insere ou atualiza registros na tabela 'hero'.
    Razão de Existência: Isolar a lógica SQL específica para a tabela 'hero'.
    """
    sql = "INSERT INTO `hero` (`hero_name`, `role_id`, `hero_icon_img_link`) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE `role_id`=VALUES(`role_id`), `hero_icon_img_link`=VALUES(`hero_icon_img_link`);"
    
    inserted_count = 0
    for hero_data in records:
        details = hero_data.get("hero", {})
        role_id = role_map.get(details.get("role"))
        
        if details.get("name") and role_id:
            params = (details["name"], role_id, details.get("portrait"))
            rows_affected = execute_func(sql, params)
            if rows_affected == 1:
                inserted_count += 1
    logger.info(f"{inserted_count} novo(s) herói(s) inserido(s) ou atualizado(s).")

def load_stats_to_db(records: List[Dict[str, Any]], execute_func, rank_id: int, map_id: int, hero_map: Dict[str, int]):
    """
    Função: Insere ou atualiza registros nas tabelas de fato.
    Razão de Existência: Isolar a lógica SQL específica para as tabelas de estatísticas.
    """
    if not records:
        return

    sql_win = "INSERT INTO `hero_rank_map_win` (`hero_id`, `rank_id`, `map_id`, `win_rate`) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE `win_rate`=VALUES(`win_rate`);"
    sql_pick = "INSERT INTO `hero_rank_map_pick` (`hero_id`, `rank_id`, `map_id`, `pick_rate`) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE `pick_rate`=VALUES(`pick_rate`);"

    for record in records:
        hero_id = hero_map.get(record["hero_name"])
        if hero_id:
            execute_func(sql_win, (hero_id, rank_id, map_id, record["win_rate"]))
            execute_func(sql_pick, (hero_id, rank_id, map_id, record["pick_rate"]))
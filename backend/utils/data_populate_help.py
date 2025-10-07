# =======================================================================================
# MÓDULO DE HELPERS PARA POPULAÇÃO DE DADOS
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Contém funções reutilizáveis que encapsulam a lógica de ETL (Extração e Carga).
# 2. `fetch_api_data`: Responsável por fazer uma requisição HTTP genérica, incluindo
#    o header `User-Agent` e tratamento de erros de rede e JSON.
# 3. `load_heroes_to_db`: Contém a lógica SQL específica para inserir/atualizar heróis.
# 4. `load_stats_to_db`: Contém a lógica SQL específica para inserir/atualizar estatísticas.
#
# RAZÃO DE EXISTIR: Seguir o princípio DRY (Don't Repeat Yourself). Em vez de repetir a lógica
# de fetch e load em cada script de população, nós a centralizamos aqui. Os scripts orquestradores
# (como `populate_lvl2.py` e `populate_lvl3.py`) apenas importam e chamam estas funções,
# tornando o código deles mais limpo, mais curto e focado na orquestração.
# =======================================================================================

# Módulo para fazer requisições HTTP para a API da Blizzard.
import requests
# Módulo para decodificar o formato de dados JSON.
import json
# Módulo padrão do Python para registrar logs de execução.
import logging
# Tipagem para clareza e robustez do código.
from typing import Dict, Any, List

# Pega o logger configurado pelo script que o chamou (ex: populate_lvl2),
# permitindo que as mensagens de log deste helper apareçam no console da execução principal.
logger = logging.getLogger(__name__)

def fetch_api_data(api_url: str) -> dict | None:
    """
    Função: Faz uma chamada genérica a uma API e retorna o JSON.
    Razão de Existência: Centralizar a lógica de requisição HTTP, incluindo headers e
    tratamento de erro, para ser reutilizada por qualquer script de população.
    """
    # Define um User-Agent de um navegador comum para simular um acesso legítimo e evitar bloqueios simples.
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    # Cria o dicionário de cabeçalhos da requisição.
    headers = {'User-Agent': user_agent}
    
    # Log em nível DEBUG para rastrear qual URL está sendo chamada (só aparece se o modo verbose estiver ativo).
    logger.debug(f"Buscando dados de: {api_url}")
    try:
        # Executa a requisição GET com um tempo limite de 15 segundos para evitar que o script fique preso indefinidamente.
        response = requests.get(api_url, headers=headers, timeout=15)
        # Lança uma exceção se a resposta tiver um status de erro HTTP (ex: 404, 500), interrompendo o fluxo `try`.
        response.raise_for_status()
        # Se a requisição foi bem-sucedida, tenta decodificar o corpo da resposta como JSON.
        return response.json()
    except json.JSONDecodeError:
        # Se o corpo da resposta não for um JSON válido, loga um aviso e o início do conteúdo para diagnóstico.
        logger.warning(f"Resposta não é um JSON válido para a URL: {api_url}")
        logger.debug(f"Conteúdo recebido (início): {response.text[:200]}")
        # Retorna None para indicar falha.
        return None
    except requests.exceptions.RequestException as e:
        # Se ocorrer um erro de rede (ex: sem conexão, DNS inválido), loga um aviso.
        logger.warning(f"Erro na requisição para {api_url}: {e}")
        # Retorna None para indicar falha.
        return None

def load_heroes_to_db(records: List[Dict[str, Any]], execute_func, role_map: Dict[str, int]):
    """
    Função: Insere ou atualiza registros na tabela 'hero'.
    Razão de Existência: Isolar a lógica SQL específica para a tabela 'hero', mantendo o script orquestrador limpo.
    """
    # Define a query SQL idempotente para inserir um novo herói ou atualizar um existente se o nome já estiver no banco.
    # Requer que a coluna `hero_name` tenha uma constraint UNIQUE.
    sql = "INSERT INTO `hero` (`hero_name`, `role_id`, `hero_icon_img_link`) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE `role_id`=VALUES(`role_id`), `hero_icon_img_link`=VALUES(`hero_icon_img_link`);"
    
    # Contador para fornecer feedback ao usuário.
    inserted_count = 0
    # Itera sobre a lista de heróis recebida da API.
    for hero_data in records:
        # Extrai os sub-dicionários para facilitar o acesso.
        details = hero_data.get("hero", {})
        # Usa o mapa de roles (carregado na memória pelo orquestrador) para resolver a chave estrangeira `role_id`.
        role_id = role_map.get(details.get("role"))
        
        # Procede apenas se os dados essenciais (nome e role_id) forem válidos.
        if details.get("name") and role_id:
            # Prepara a tupla de parâmetros para a execução segura da query.
            params = (details["name"], role_id, details.get("portrait"))
            # Executa a query, passando a função `execute` como um parâmetro (injeção de dependência).
            rows_affected = execute_func(sql, params)
            # `rows_affected` é 1 para uma nova inserção.
            if rows_affected == 1:
                inserted_count += 1
    # Loga o resultado da operação.
    logger.info(f"{inserted_count} novo(s) herói(s) inserido(s) ou atualizado(s).")

def load_stats_to_db(records: List[Dict[str, Any]], execute_func, rank_id: int, map_id: int, hero_map: Dict[str, int]):
    """
    Função: Insere ou atualiza registros nas tabelas de fato (estatísticas).
    Razão de Existência: Isolar a lógica SQL específica para as tabelas de estatísticas,
    resolvendo todas as chaves estrangeiras necessárias.
    """
    # Se não houver registros, a função termina para evitar processamento desnecessário.
    if not records:
        return

    # Query para a tabela de win rate. `ON DUPLICATE KEY UPDATE` requer uma chave UNIQUE composta (hero_id, rank_id, map_id).
    sql_win = "INSERT INTO `hero_rank_map_win` (`hero_id`, `rank_id`, `map_id`, `win_rate`) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE `win_rate`=VALUES(`win_rate`);"
    # Query para a tabela de pick rate.
    sql_pick = "INSERT INTO `hero_rank_map_pick` (`hero_id`, `rank_id`, `map_id`, `pick_rate`) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE `pick_rate`=VALUES(`pick_rate`);"

    # Itera sobre os registros de estatísticas já transformados.
    for record in records:
        # Resolve a chave estrangeira `hero_id` usando o mapa de heróis.
        hero_id = hero_map.get(record["hero_name"])
        # Procede apenas se o herói existir no nosso banco de dados.
        if hero_id:
            # Executa a inserção dos dados de win rate, passando as FKs resolvidas.
            execute_func(sql_win, (hero_id, rank_id, map_id, record["win_rate"]))
            # Executa a inserção dos dados de pick rate.
            execute_func(sql_pick, (hero_id, rank_id, map_id, record["pick_rate"]))
# =======================================================================================
# SCRIPT ORQUESTRADOR - POPULAÇÃO DE DIMENSÕES (NÍVEL 2 - HERO) (REFATORADO v2)
# =======================================================================================
# ARQUITETURA (Mudança v2):
# 1. Ajuste na 'main_populate_heroes' para lidar com a estrutura real da API,
#    que retorna um dicionário com a chave 'rates' contendo a lista de heróis.
# 2. Mantém a validação de tipo, mas agora verifica a estrutura aninhada.
# =======================================================================================

import sys
import logging
from typing import Dict, List, Any

# --- Configuração de Logger ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

# --- Importações da Aplicação ---
# Assume que 'utils' está acessível (via pyproject.toml / pip install -e .)
from utils.function_execute import execute
from utils.extraction_helpers import fetch_api_data

# --- LÓGICA DE CARGA (LOAD) ---
def load_heroes_to_db(records: List[Dict[str, Any]], role_map: Dict[str, int]):
    """
    Processa os registros de heróis (já validados como lista de dicionários)
    e os insere/atualiza no banco de dados.
    Usa ON DUPLICATE KEY UPDATE pois esta é uma tabela de Dimensão.
    """
    sql = """INSERT INTO `hero` (`hero_name`, `role_id`, `hero_icon_img_link`) 
             VALUES (%s, %s, %s) 
             ON DUPLICATE KEY UPDATE `role_id`=VALUES(`role_id`), `hero_icon_img_link`=VALUES(`hero_icon_img_link`);"""
    
    inserted_count = 0
    updated_count = 0
    skipped_count = 0
    
    for hero_entry in records:
        # A estrutura aninhada parece ser { 'hero': { 'color': ..., 'name': ..., 'portrait': ... }, 'cells': { ... } }
        # ou pode variar ligeiramente. Precisamos ser defensivos com .get()
        
        hero_details = hero_entry.get("hero") 
        if not isinstance(hero_details, dict):
            logger.warning(f"Estrutura inesperada para entrada de herói, faltando chave 'hero' ou não é dicionário: {hero_entry}")
            skipped_count += 1
            continue # Pula para o próximo herói na lista

        hero_name = hero_details.get("name")
        hero_role_name = hero_details.get("role") # A role pode estar aqui também, verificar a API real
        hero_portrait = hero_details.get("portrait")
        
        # Se a role não estiver em 'hero', pode estar em 'cells' ou em outro lugar. Ajuste se necessário.
        # Exemplo alternativo (se a role estivesse em 'cells'):
        # cells_details = hero_entry.get("cells", {})
        # hero_role_name = cells_details.get("role") 

        role_id = role_map.get(hero_role_name)
        
        if hero_name and role_id:
            params = (hero_name, role_id, hero_portrait)
            try:
                rows_affected = execute(sql, params)
                
                if rows_affected == 1: # 1 = Novo INSERT
                    inserted_count += 1
                elif rows_affected == 2: # 2 = Registro existente atualizado
                    updated_count += 1
                # rows_affected == 0 significa que a linha existe mas nada mudou.
                    
            except Exception as e:
                logger.error(f"Erro ao inserir/atualizar herói '{hero_name}': {e}")
                skipped_count += 1
        else:
            if not hero_name:
                logger.warning(f"Nome do herói ausente na entrada: {hero_details}")
            if not role_id:
                 logger.warning(f"Role '{hero_role_name}' para o herói '{hero_name}' não encontrada no banco de dados ou ausente nos dados da API.")
            skipped_count += 1
                
    logger.info(f"{inserted_count} novo(s) herói(s) inserido(s).")
    logger.info(f"{updated_count} herói(s) existente(s) atualizado(s).")
    if skipped_count > 0:
        logger.warning(f"{skipped_count} herói(s) pulado(s) devido a dados ausentes ou erros.")

# --- ORQUESTRAÇÃO ---
def main_populate_heroes():
    """Função principal que orquestra todo o fluxo de população de heróis."""
    logger.info("Iniciando processo de população da dimensão 'hero'...")
    
    try:
        # 1. Buscar Dependências (Roles)
        roles_from_db = execute("SELECT `role_id`, `role` FROM `role`")
        if not roles_from_db:
            logger.error("A tabela 'role' está vazia. Execute o script SQL de 'seed' primeiro.")
            raise Exception("Dependência 'role' não populada.")
        role_map = {item['role']: item['role_id'] for item in roles_from_db}
        
        # 2. Extrair Dados da API
        # NOTA: Esta URL ainda pode estar quebrada ou desatualizada. Verifique-a.
        api_url = "https://overwatch.blizzard.com/pt-br/rates/data?platform=pc&gamemode=competitive" 
        api_response_data = fetch_api_data(api_url)
        
        if not api_response_data:
            logger.error("Nenhum dado retornado pela API de Heróis.")
            raise Exception("API de Heróis não retornou dados.")

        # --- VALIDAÇÃO DE ESTRUTURA (Correção v2) ---
        # Verificamos se recebemos um DICIONÁRIO e se ele contém a chave 'rates'.
        if not isinstance(api_response_data, dict):
            logger.error(f"Falha na API de Heróis. Formato de dados inesperado. Esperado: 'dict', Recebido: '{type(api_response_data).__name__}'")
            raise TypeError("A API de Heróis não retornou um dicionário.")
        
        hero_list = api_response_data.get('rates') # Extrai a lista da chave 'rates'
        
        # Verificamos se a chave 'rates' existe e se seu valor é uma LISTA.
        if not isinstance(hero_list, list):
            logger.error(f"Falha na API de Heróis. Estrutura de dados inesperada. Chave 'rates' ausente ou não é uma lista. Recebido: '{type(hero_list).__name__}'")
            raise TypeError("A API de Heróis retornou um dicionário, mas a chave 'rates' não contém uma lista.")
        # --- Fim da Validação ---

        # 3. Carregar Dados no Banco
        if not hero_list:
             logger.warning("A API retornou uma lista vazia de heróis na chave 'rates'. Nenhum herói será carregado.")
        else:
            load_heroes_to_db(hero_list, role_map) # Passa a LISTA extraída
        
        logger.info("Processo de população de 'hero' concluído.")

    except Exception as e:
        logger.error(f"Falha no 'main_populate_heroes': {e}")
        # Propaga a falha para o data_uploader
        raise e

# --- Ponto de Entrada (se executado diretamente) ---
if __name__ == "__main__":
     # Permite rodar este script isoladamente para teste
     logger.info("Executando 'populate_hero_lvl2.py' diretamente para teste...")
     try:
         main_populate_heroes()
     except Exception as e:
         logger.critical(f"Falha crítica na execução direta: {e}", exc_info=True)
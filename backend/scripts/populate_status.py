# scripts/populate_stats.py

import requests
import sys
import logging
import argparse
import json
from os.path import abspath, dirname

# --- Configuração de Path e Logger ---
project_root = dirname(dirname(abspath(__file__)))
sys.path.append(project_root)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

# --- Importações da Aplicação (Reutilização de Código) ---
# 1. Reutiliza a camada de acesso a dados (DRY)
from utils.function_execute import execute
# 2. Reutiliza o mapeamento de tabelas para validação (DRY)
from model.model_resolver import TABLE_MODEL_MAPPING

# --- Funções do ETL ---

def fetch_data_from_api(api_url: str) -> dict | None:
    """Faz a requisição HTTP com User-Agent e retorna o JSON."""
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    headers = {'User-Agent': user_agent}
    
    logger.info(f"Buscando dados de: {api_url}")
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info("Dados recebidos com sucesso.")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao buscar dados: {e}", exc_info=True)
        return None

def transform_data(raw_data: dict, table_name: str) -> list:
    """
    (PLACEHOLDER) Transforma os dados brutos no formato esperado pelo banco.
    A lógica aqui deve ser específica para cada `table_name`.
    """
    logger.info(f"Iniciando transformação de dados para a tabela '{table_name}'...")
    
    # --- IMPORTANTE: LÓGICA DE NEGÓCIO A SER IMPLEMENTADA ---
    # Aqui você implementaria a lógica para processar `raw_data`
    # com base na tabela alvo (`table_name`).
    # Por exemplo:
    # if table_name == 'hero_win':
    #     # Lógica para extrair e formatar dados de win rate
    # elif table_name == 'hero_pick':
    #     # Lógica para extrair e formatar dados de pick rate
    
    transformed_records = []
    # Exemplo de registro para visualização no dry-run
    transformed_records.append({'exemplo': True, 'tabela_alvo': table_name, 'dados': 'a_serem_formatados'})
    
    logger.info(f"Transformação concluída. {len(transformed_records)} registros prontos.")
    return transformed_records

def load_data_to_db(records: list, table_name: str):
    """
    (PLACEHOLDER) Carrega os registros no banco de dados.
    A query SQL deve ser dinâmica ou selecionada com base na `table_name`.
    """
    if not records:
        logger.warning(f"Nenhum registro para carregar na tabela '{table_name}'.")
        return

    logger.info(f"Iniciando carga de {len(records)} registros na tabela '{table_name}'.")
    
    # --- IMPORTANTE: LÓGICA DE NEGÓCIO A SER IMPLEMENTADA ---
    # A query deve ser construída dinamicamente com base nos dados e na tabela.
    # Exemplo para uma tabela simples (deve ser adaptado):
    # columns = records[0].keys()
    # placeholders = ", ".join(["%s"] * len(columns))
    # sql_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE ..."
    
    # for record in records:
    #     execute(sql=sql_query, params=tuple(record.values()))
    
    logger.info(f"Carga na tabela '{table_name}' concluída (simulação).")

def save_data_to_file(data: list, filename: str):
    """Salva os dados transformados em um arquivo JSON."""
    logger.info(f"Modo Dry Run: Salvando {len(data)} registros em '{filename}'...")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f"Arquivo '{filename}' salvo com sucesso.")
    except IOError as e:
        logger.error(f"Falha ao salvar o arquivo: {e}", exc_info=True)

# --- PONTO DE ENTRADA DO SCRIPT ---

if __name__ == "__main__":
    valid_tables = ", ".join(TABLE_MODEL_MAPPING.keys())
    
    parser = argparse.ArgumentParser(
        description="Script genérico para popular tabelas do Overwatch a partir de uma API.",
        formatter_class=argparse.RawTextHelpFormatter # Melhora a formatação da ajuda
    )
    
    # Argumentos obrigatórios
    parser.add_argument("table_name", type=str, help=f"Nome da tabela a ser populada. Válidos: \n{valid_tables}")
    parser.add_argument("api_url", type=str, help="URL da API de onde os dados serão extraídos.")
    
    # Argumentos opcionais
    parser.add_argument("--dry-run", action="store_true", help="Executa sem inserir no banco, salvando a saída em um arquivo.")
    parser.add_argument("-o", "--output", type=str, default="output.json", help="Nome do arquivo de saída para --dry-run.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Aumenta a verbosidade para nível DEBUG.")
    
    args = parser.parse_args()

    # Validação do nome da tabela contra o mapeamento importado
    if args.table_name not in TABLE_MODEL_MAPPING:
        logger.error(f"Erro: Tabela '{args.table_name}' não é válida.")
        logger.info(f"Tabelas permitidas: {valid_tables}")
        sys.exit(1) # Encerra o script com código de erro

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Modo verbose ativado.")

    # --- Fluxo Principal ---
    raw_data = fetch_data_from_api(args.api_url)
    
    if raw_data:
        transformed_data = transform_data(raw_data, args.table_name)
        
        if args.dry_run:
            save_data_to_file(transformed_data, args.output)
        else:
            load_data_to_db(transformed_data, args.table_name)
    
    logger.info("Execução do script concluída.")
# =======================================================================================
# MÓDULO DE HELPERS PARA EXTRAÇÃO DE DADOS (API)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Contém a função reutilizável `fetch_api_data` que encapsula a lógica de Extração (o 'E' do ETL) para fontes JSON.
# 2. É responsável por fazer uma requisição HTTP genérica, incluindo o header `User-Agent` para
#    simular um navegador e tratar erros de rede e de decodificação JSON.
#
# RAZÃO DE EXISTIR: Centralizar toda a lógica de obtenção de dados de fontes externas baseadas em API.
# Os scripts orquestradores importam esta função para buscar os dados brutos antes de
# processá-los e carregá-los no banco de dados.
# =======================================================================================

import requests
import json
import logging
from typing import Dict

# Pega o logger configurado pelo script que o chamou.
logger = logging.getLogger(__name__)

def fetch_api_data(api_url: str) -> dict | None:
    """
    Função: Faz uma chamada genérica a uma API e retorna o JSON.
    Razão de Existência: Centralizar a lógica de requisição HTTP, incluindo headers e
    tratamento de erro, para ser reutilizada por qualquer script de população.
    """
    # Define um User-Agent de um navegador comum para simular um acesso legítimo.
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    headers = {'User-Agent': user_agent}
    
    logger.debug(f"Buscando dados de API de: {api_url}")
    try:
        # Executa a requisição GET com um tempo limite.
        response = requests.get(api_url, headers=headers, timeout=15)
        # Lança um erro se a resposta tiver um status de erro HTTP (4xx ou 5xx).
        response.raise_for_status()
        # Tenta decodificar a resposta como JSON.
        return response.json()
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        # Em caso de erro de rede ou de parsing, loga um aviso e retorna None.
        logger.warning(f"Falha na requisição para {api_url}: {e}")
        return None
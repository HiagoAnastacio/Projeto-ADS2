# =======================================================================================
# MÓDULO DE HELPERS PARA EXTRAÇÃO DE DADOS (API) (REFATORADO v2)
# =======================================================================================
# ARQUITETURA (Mudança v2):
# 1. Aumenta o valor do timeout da requisição para 30 segundos.
# =======================================================================================

import requests
import json
import logging
from typing import Dict, Optional # Corrigido: Usar Optional para o tipo de retorno

# Pega o logger configurado pelo script que o chamou.
logger = logging.getLogger(__name__)

def fetch_api_data(api_url: str) -> Optional[Dict | list]: # Ajustado para dict OU list
    """
    Função: Faz uma chamada genérica a uma API e retorna o JSON.
    Razão de Existência: Centralizar a lógica de requisição HTTP, incluindo headers e
    tratamento de erro, para ser reutilizada por qualquer script de população.
    """
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    headers = {'User-Agent': user_agent}

    logger.debug(f"Buscando dados de API de: {api_url}")
    try:
        # --- ALTERAÇÃO: Timeout aumentado para 30 segundos ---
        response = requests.get(api_url, headers=headers, timeout=30)
        # --- Fim da Alteração ---

        response.raise_for_status()

        # Verifica se a resposta tem conteúdo antes de tentar decodificar JSON
        if not response.content:
            logger.warning(f"Resposta vazia recebida de {api_url}")
            return None
            
        # Tenta decodificar a resposta como JSON.
        # Adiciona tratamento para caso a resposta não seja JSON válido.
        try:
            return response.json()
        except json.JSONDecodeError:
             logger.error(f"Falha ao decodificar JSON da resposta de {api_url}. Conteúdo (início): {response.text[:200]}...")
             return None # Retorna None se não for JSON

    except requests.exceptions.Timeout as e:
        # Log específico para timeout
        logger.warning(f"Falha na requisição para {api_url}: {e}")
        return None # Retorna None em caso de timeout
    except requests.exceptions.RequestException as e:
        # Log geral para outros erros de requisição (4xx, 5xx, etc.)
        logger.error(f"Erro na requisição para {api_url}: {e}")
        return None # Retorna None em caso de erro
    except Exception as e:
        # Captura qualquer outro erro inesperado
        logger.error(f"Erro inesperado ao buscar dados de {api_url}: {e}", exc_info=True)
        return None
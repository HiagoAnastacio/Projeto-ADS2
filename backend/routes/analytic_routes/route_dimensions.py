# ===============================================================================
# ROTEADOR: DADOS DE DIMENSÃO (FILTROS)
# ===============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from mysql.connector.connection import MySQLConnection
import logging
from typing import List, Dict, Any

# Importações internas
from utils.db_manager import get_db_connection
from model.analytic_model import get_dimension_data # A nova função de acesso a dados

logger = logging.getLogger(__name__)

# O router não precisa de prefixo, pois o prefixo /API/V1-DATA será aplicado no main.py
router = APIRouter(prefix="/DIMENSIONS",tags=["Dimensions and Filters"],
)

@router.get(
    "/{dimension_name}",
    response_model=List[Dict[str, Any]],
    summary="Obtém a lista completa de Heróis, Ranks, ou Mapas para filtros.",
)
async def get_dimensions(
    dimension_name: str,
    db: MySQLConnection = Depends(get_db_connection)
) -> List[Dict[str, Any]]:
    """
    Retorna todos os dados de uma dimensão específica para popular os filtros.
    Exemplo de uso: /API/V1-DATA/DIMENSIONS/hero
    """
    try:
        # A validação da dimensão é feita dentro da camada de modelo (get_dimension_data)
        data = get_dimension_data(db, dimension_name.lower())
        logger.info(f"Dimensão '{dimension_name}' carregada com sucesso. Total: {len(data)}")
        return data
    except ValueError as e:
        # Captura o erro levantado na camada de modelo para dimensões não suportadas
        logger.error(f"Tentativa de acesso a dimensão inválida: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Dimensão '{dimension_name}' não encontrada ou não suportada."
        )
    except Exception as e:
        logger.error(f"Erro no processamento da dimensão {dimension_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar dados de dimensão."
        )
# =======================================================================================
# SERVIÇO DE AGENDAMENTO DE TAREFAS (DATA UPLOADER)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. É um serviço de segundo plano (daemon) que usa `APScheduler` para agendar tarefas.
# 2. A tarefa `run_update_pipeline` é configurada para rodar em um horário específico.
# 3. Esta função chama os scripts de população na ordem hierárquica correta:
#    a. `scrape_maps` para atualizar a lista de mapas.
#    b. `populate_lvl2` para atualizar a lista de heróis.
#    c. `populate_lvl3` para coletar todas as estatísticas.
# 4. É gerenciado pelo `lifespan` do FastAPI, sendo iniciado junto com a API.
#
# RAZÃO DE EXISTIR: Automatizar completamente a manutenção do banco de dados.
# =======================================================================================

import logging
import asyncio
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- Importa as funções principais dos scripts que ele vai orquestrar ---
from services.scripts.scrape_maps import main_scrape_and_populate_maps
from services.scripts.populate_lvl2 import main_populate_heroes
from services.scripts.populate_lvl3 import main_populate_facts

logger = logging.getLogger(__name__)

def run_update_pipeline():
    """Executa o pipeline de atualização de dados na ordem correta."""
    try:
        logger.info("==== INICIANDO PIPELINE DE ATUALIZAÇÃO AGENDADO ====")
        
        # ETAPA 1: Popula/Atualiza Dimensões de Nível 2
        logger.info("--- [ETAPA 1/3] Executando 'scrape_maps.py' ---")
        main_scrape_and_populate_maps()
        
        logger.info("--- [ETAPA 2/3] Executando 'populate_lvl2.py' (heróis) ---")
        main_populate_heroes()
        
        # ETAPA 3: Popular Fatos de Nível 3
        logger.info("--- [ETAPA 3/3] Executando 'populate_lvl3.py' para tabelas de fato ---")
        main_populate_facts()
        
        logger.info("==== PIPELINE DE ATUALIZAÇÃO AGENDADO CONCLUÍDO COM SUCESSO ====")
    except Exception as e:
        logger.error(f"==== FALHA NO PIPELINE DE ATUALIZAÇÃO AGENDADO. Erro: {e} ====", exc_info=True)

@asynccontextmanager
async def scheduler_lifespan(app):
    """
    Context manager para o ciclo de vida do FastAPI. Inicia o scheduler.
    O aviso '"asyncio" is not accessed' pode aparecer aqui, mas é um falso positivo do linter,
    pois o `asyncio` é usado implicitamente pela biblioteca `apscheduler` e pelo `lifespan`.
    """
    logger.info("Iniciando o serviço de agendamento em segundo plano...")
    scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(run_update_pipeline, 'cron', day_of_week='sun', hour=3, minute=0)
    scheduler.start()
    
    yield
    
    logger.info("Encerrando o serviço de agendamento...")
    scheduler.shutdown()
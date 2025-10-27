# =======================================================================================
# SERVIÇO DE AGENDAMENTO DE TAREFAS (DATA UPLOADER) (REFATORADO v3)
# =======================================================================================
# ARQUITETURA (Mudança v3):
# 1. Adiciona flag `pipeline_successful` para rastrear falhas críticas.
# 2. Modifica a mensagem final de log para indicar sucesso explícito se nenhuma
#    falha crítica ocorreu.
# 3. Mantém a criação do objeto SimpleNamespace para `main_populate_facts`.
# =======================================================================================

import logging
import asyncio
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.job import Job # Importa Job para type hinting
from types import SimpleNamespace

from services.scripts.populate_scrape_map_lvl2 import main_scrape_and_populate_maps
from services.scripts.populate_hero_lvl2 import main_populate_heroes
from services.scripts.populate_lvl3 import main_populate_facts

logger = logging.getLogger(__name__)

# --- Variável Global para o Scheduler (para acessar jobs depois) ---
# Precisamos dela para pegar o next_run_time no final.
scheduler: AsyncIOScheduler | None = None

async def run_update_pipeline():
    """
    Função principal do pipeline, chamada pelo agendador.
    Executa os scripts de população em ordem, com tratamento de erro granular.
    """
    logger.info("==== INICIANDO PIPELINE DE ATUALIZAÇÃO AGENDADO ====")
    pipeline_successful = True # Assume sucesso inicialmente

    # Etapa 1: Mapas (Scraping)
    try:
        logger.info("--- [ETAPA 1/3] Executando 'populate_scrape_map_lvl2.py' ---")
        main_scrape_and_populate_maps()
        logger.info("--- [ETAPA 1/3] 'populate_scrape_map_lvl2.py' concluído (pode conter erros não fatais). ---")
    except Exception as e:
        logger.error(f"==== FALHA NA ETAPA 1 (scrape_maps). Erro: {e} ====", exc_info=True)
        # Consideramos falha no scraping como não crítica para o log final, mas logamos o erro.

    # Etapa 2: Heróis (API) - Crítico
    try:
        logger.info("--- [ETAPA 2/3] Executando 'populate_hero_lvl2.py' (heróis) ---")
        main_populate_heroes()
        logger.info("--- [ETAPA 2/3] 'populate_hero_lvl2.py' concluído com sucesso. ---")
    except Exception as e:
        logger.error(f"==== FALHA CRÍTICA NA ETAPA 2 (populate_hero). O pipeline será abortado. Erro: {e} ====", exc_info=True)
        pipeline_successful = False # Marca como falha crítica
        return # Interrompe o pipeline

    # Etapa 3: Tabelas de Fato (API) - Crítico
    if pipeline_successful: # Só executa se a etapa 2 passou
        try:
            logger.info("--- [ETAPA 3/3] Executando 'populate_lvl3.py' para tabelas de fato ---")
            default_args = SimpleNamespace(limit=0)
            main_populate_facts(default_args)
            logger.info("--- [ETAPA 3/3] 'populate_lvl3.py' concluído com sucesso. ---")
        except Exception as e:
            logger.error(f"==== FALHA CRÍTICA NA ETAPA 3 (populate_facts). Erro: {e} ====", exc_info=True)
            pipeline_successful = False # Marca como falha crítica

    # --- LOG FINAL MELHORADO ---
    if pipeline_successful:
        logger.info("✅ ==== PIPELINE DE ATUALIZAÇÃO AGENDADO CONCLUÍDO COM SUCESSO ==== ✅")
    else:
         logger.warning("❌ ==== PIPELINE DE ATUALIZAÇÃO AGENDADO CONCLUÍDO COM FALHAS CRÍTICAS ==== ❌")

    # O log do APScheduler que vem logo após esta função já informa o next run time.
    # Ex: INFO - Job "run_update_pipeline (...) next run at: 2025-11-03 12:26:00 -03)" executed successfully


@asynccontextmanager
async def scheduler_lifespan(app):
    """
    Context manager para o ciclo de vida do FastAPI. Inicia o scheduler.
    """
    global scheduler # Permite modificar a variável global
    logger.info("Iniciando o serviço de agendamento em segundo plano...")
    # Cria a instância do agendador.
    scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")

    # Adiciona a tarefa ao agendador com um ID fixo para referência futura
    scheduler.add_job(
        run_update_pipeline,
        'cron',
        day_of_week='mon',
        hour=4, # Ajuste a hora/minuto conforme necessário
        minute=30,
        id="weekly_data_pipeline" # ID do Job
    )

    # Para testes: Rodar imediatamente (descomente se necessário)
    # scheduler.add_job(run_update_pipeline, id="immediate_run")

    scheduler.start()
    current_job: Job | None = scheduler.get_job("weekly_data_pipeline")
    if current_job and current_job.next_run_time:
        logger.info(f"Próxima execução do pipeline agendada para: {current_job.next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    else:
        logger.warning("Não foi possível determinar a próxima execução agendada do pipeline.")


    try:
        yield
    finally:
        # Este bloco é executado quando o servidor FastAPI é encerrado.
        logger.info("Encerrando o serviço de agendamento...")
        if scheduler:
            scheduler.shutdown()
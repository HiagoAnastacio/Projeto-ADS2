# =======================================================================================
# SERVIÇO DE AGENDAMENTO DE TAREFAS (DATA UPLOADER) (v0.7.0 - Refatorado SoC)
# =======================================================================================
# ARQUITETURA:
# 1. Este é o Orquestrador de Nível 1 ("Maestro").
# 2. Sua única responsabilidade é agendar e executar o pipeline principal.
# 3. A função `run_update_pipeline` chama os Orquestradores de Nível 2
#    (das novas pastas `services/orchestrators/`) na ordem correta.
# =======================================================================================

import logging
import asyncio
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.job import Job
from types import SimpleNamespace

# --- Importa as funções principais dos scripts ORQUESTRADORES ---
# (Importa dos novos locais)
from services.orchestrators.run_dims_lvl2_pipeline import run_map_pipeline, run_hero_pipeline
from services.orchestrators.run_stats_lvl3_pipeline import run_stats_pipeline

logger = logging.getLogger(__name__)
scheduler: AsyncIOScheduler | None = None

async def run_update_pipeline():
    """
    Função principal do pipeline, chamada pelo agendador.
    Executa os scripts de população de dimensões e depois o de fatos.
    """
    logger.info("==== INICIANDO PIPELINE DE ATUALIZAÇÃO AGENDADO (v0.7.0 - SoC Refactor) ====")
    pipeline_successful = True # Assume sucesso

    # Etapa 1: Mapas (Scraping)
    try:
        logger.info("--- [ETAPA 1/3] Executando 'run_map_pipeline' (Dimensão Mapas) ---")
        # Chama o orquestrador de mapas
        run_map_pipeline()
        logger.info("--- [ETAPA 1/3] 'run_map_pipeline' concluído. ---")
    except Exception as e:
        logger.error(f"==== FALHA NA ETAPA 1 (run_map_pipeline). Erro: {e} ====", exc_info=True)
        # Pode continuar, mas loga.

    # Etapa 2: Heróis (API Dimensão) - Crítico
    try:
        logger.info("--- [ETAPA 2/3] Executando 'run_hero_pipeline' (Dimensão Heróis) ---")
        # Chama o orquestrador de heróis
        run_hero_pipeline()
        logger.info("--- [ETAPA 2/3] 'run_hero_pipeline' concluído com sucesso. ---")
    except Exception as e:
        logger.error(f"==== FALHA CRÍTICA NA ETAPA 2 (run_hero_pipeline). Abortando. Erro: {e} ====", exc_info=True)
        pipeline_successful = False
        return

    # Etapa 3: Tabelas de Fato (API Agregados) - Crítico
    if pipeline_successful:
        try:
            logger.info("--- [ETAPA 3/3] Executando 'run_stats_pipeline' (Fatos) ---")
            # Simula args para compatibilidade com o __main__ do script
            default_args = SimpleNamespace(limit=0) 
            # Chama o orquestrador de fatos
            run_stats_pipeline(default_args)
            logger.info("--- [ETAPA 3/3] 'run_stats_pipeline' concluído com sucesso. ---")
        except Exception as e:
            logger.error(f"==== FALHA CRÍTICA NA ETAPA 3 (run_stats_pipeline). Erro: {e} ====", exc_info=True)
            pipeline_successful = False

    # --- LOG FINAL ---
    if pipeline_successful:
        logger.info("✅ ==== PIPELINE DE ATUALIZAÇÃO AGENDADO CONCLUÍDO COM SUCESSO ==== ✅")
    else:
         logger.warning("❌ ==== PIPELINE DE ATUALIZAÇÃO AGENDADO CONCLUÍDO COM FALHAS CRÍTICAS ==== ❌")

# --- Gerenciador de Ciclo de Vida (Lifespan) ---
@asynccontextmanager
async def scheduler_lifespan(app):
    """Inicia e encerra o scheduler APScheduler."""
    global scheduler
    logger.info("Iniciando o serviço de agendamento em segundo plano...")
    scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")

    scheduler.add_job(
        run_update_pipeline, 'cron', day_of_week='mon', hour=12, minute=40, id="weekly_data_pipeline"
    )
    # Para testes: Rodar imediatamente (descomente se necessário)
    # scheduler.add_job(run_update_pipeline, id="immediate_run")

    scheduler.start()
    try:
        current_job: Job | None = scheduler.get_job("weekly_data_pipeline")
        if current_job and current_job.next_run_time:
            logger.info(f"Próxima execução do pipeline agendada para: {current_job.next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        else:
            logger.info("Execução imediata do pipeline configurada (se descomentada).")
    except Exception as e:
         logger.error(f"Erro ao obter informações do job agendado: {e}")

    try:
        yield # FastAPI inicia
    finally:
        logger.info("Encerrando o serviço de agendamento...")
        if scheduler and scheduler.running:
            scheduler.shutdown()
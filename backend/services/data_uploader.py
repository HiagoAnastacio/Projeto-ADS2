# =======================================================================================
# SERVIÇO DE AGENDAMENTO DE TAREFAS (DATA UPLOADER)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. É um serviço de segundo plano (daemon) que usa `APScheduler` para agendar tarefas.
# 2. A tarefa `run_update_pipeline` é configurada para rodar em um horário específico.
# 3. Esta função chama os scripts de população em uma ordem hierárquica rigorosa,
#    utilizando blocos try/except separados para cada etapa, garantindo um tratamento
#    de erro granular e a interrupção do pipeline em caso de falha crítica.
# 4. É gerenciado pelo `lifespan` do FastAPI, sendo iniciado junto com a API.
#
# RAZÃO DE EXISTIR: Automatizar completamente a manutenção do banco de dados de forma
# robusta e com logging detalhado sobre o sucesso ou falha de cada etapa.
# =======================================================================================

import logging
import asyncio
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- Importa as funções principais dos scripts que ele vai orquestrar ---
# A ordem de importação não afeta a ordem de execução.
from services.scripts.populate_scrape_map_lvl2 import main_scrape_and_populate_maps
from services.scripts.populate_hero_lvl2 import main_populate_heroes
from services.scripts.populate_lvl3 import main_populate_facts

# Pega o logger configurado pelo script chamador (main.py).
logger = logging.getLogger(__name__)

def run_update_pipeline():
    """
    Executa o pipeline de atualização de dados na ordem correta, com tratamento
    de erro granular para cada etapa.
    """
    logger.info("==== INICIANDO PIPELINE DE ATUALIZAÇÃO AGENDADO ====")
    
    # ----------------------------------------------------------------------------------
    # ETAPA 1: Popula/Atualiza a dimensão 'map' via Web Scraping
    # ----------------------------------------------------------------------------------
    try:
        logger.info("--- [ETAPA 1/3] Executando 'populate_scrape_map_lvl2.py' ---")
        main_scrape_and_populate_maps()
        logger.info("--- [ETAPA 1/3] 'populate_scrape_map_lvl2.py' concluído com sucesso. ---")
    except Exception as e:
        # Se o scraping falhar, logamos o erro, mas o pipeline pode continuar,
        # pois a lista de mapas pode já estar no banco de dados de uma execução anterior.
        logger.error(f"==== FALHA NA ETAPA 1 (populate_scrape_map_lvl2). Continuando com os mapas existentes. Erro: {e} ====", exc_info=True)

    # ----------------------------------------------------------------------------------
    # ETAPA 2: Popula/Atualiza a dimensão 'hero' via API
    # Esta etapa é CRÍTICA. Se falhar, não podemos prosseguir para a Etapa 3.
    # ----------------------------------------------------------------------------------
    try:
        logger.info("--- [ETAPA 2/3] Executando 'populate_hero_lvl2.py' (heróis) ---")
        main_populate_heroes()
        logger.info("--- [ETAPA 2/3] 'populate_hero_lvl2.py' concluído com sucesso. ---")
    except Exception as e:
        # Se a população de heróis falhar, o pipeline é inútil.
        logger.error(f"==== FALHA CRÍTICA NA ETAPA 2 (populate_hero). O pipeline será abortado. Erro: {e} ====", exc_info=True)
        # O comando 'return' interrompe a execução da função aqui. A Etapa 3 não será executada.
        return

    # ----------------------------------------------------------------------------------
    # ETAPA 3: Popula as tabelas de fato (estatísticas)
    # Este bloco só será executado se a Etapa 2 for bem-sucedida.
    # ----------------------------------------------------------------------------------
    try:
        logger.info("--- [ETAPA 3/3] Executando 'populate_lvl3.py' para tabelas de fato ---")
        main_populate_facts()
        logger.info("--- [ETAPA 3/3] 'populate_lvl3.py' concluído com sucesso. ---")
    except Exception as e:
        # Logamos a falha na etapa final.
        logger.error(f"==== FALHA NA ETAPA 3 (populate_facts). Erro: {e} ====", exc_info=True)

    logger.info("==== PIPELINE DE ATUALIZAÇÃO AGENDADO CONCLUÍDO (com ou sem falhas parciais) ====")

@asynccontextmanager
async def scheduler_lifespan(app):
    """
    Context manager para o ciclo de vida do FastAPI. Inicia o scheduler.
    O aviso '"asyncio" is not accessed' pode aparecer, mas é um falso positivo do linter,
    pois o `asyncio` é usado implicitamente pelo `apscheduler` e pelo `lifespan`.
    """
    logger.info("Iniciando o serviço de agendamento em segundo plano...")
    # Cria a instância do agendador.
    scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")
    
    # Adiciona a tarefa ao agendador.
    # Para testes, você pode mudar o agendamento (ex: 'cron', second='*/10' para rodar a cada 10s).
    scheduler.add_job(run_update_pipeline, 'cron', day_of_week='mon', hour=2, minute=30)
    
    # Inicia o processo do agendador.
    scheduler.start()
    
    try:
        # 'yield' passa o controle para o FastAPI, que começa a servir requisições.
        # O agendador continua rodando em sua própria thread/tarefa.
        yield
    finally:
        # Este bloco é executado quando o servidor FastAPI é encerrado.
        logger.info("Encerrando o serviço de agendamento...")
        # Desliga o agendador de forma limpa.
        scheduler.shutdown()
        logger.info("Agendador encerrado de forma limpa.")
# backend/services/scheduler.py

import asyncio
import logging
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import sys
from os.path import abspath, dirname

# --- AJUSTE CRÍTICO DE PATH ---
# Razão: Para que o Python encontre os módulos em `utils`, `model`, etc.,
# precisamos adicionar a pasta 'backend' ao path.
project_root = dirname(dirname(abspath(__file__))) # Sobe 2 níveis: services -> backend
sys.path.append(project_root)

# Configuração de Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Importa as funções principais dos scripts de população ---
try:
    # A importação agora parte da raiz 'backend' que adicionamos ao path.
    from services.scripts.populate_lvl2 import main_populate_dimensions
    from services.scripts.populate_lvl3 import main_populate_facts
except ImportError as e:
    logger.error(f"Não foi possível importar os scripts de população. Verifique os nomes e a estrutura. Erro: {e}")
    sys.exit(1)

# --- Definição das Tarefas Agendadas ---

def run_update_pipeline():
    """Executa o pipeline de atualização de dados na ordem correta."""
    try:
        logger.info("==== INICIANDO PIPELINE DE ATUALIZAÇÃO AGENDADO ====")
        main_populate_dimensions()
        main_populate_facts()
        logger.info("==== PIPELINE DE ATUALIZAÇÃO AGENDADO CONCLUÍDO COM SUCESSO ====")
    except Exception as e:
        logger.error(f"==== FALHA NO PIPELINE DE ATUALIZAÇÃO AGENDADO. Erro: {e} ====", exc_info=True)

# --- Gerenciador de Contexto para o Serviço ---

@asynccontextmanager
async def scheduler_lifespan():
    """Context manager para iniciar e parar o agendador de forma segura."""
    scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")
    
    # Agenda a tarefa para rodar todo domingo às 3 da manhã.
    scheduler.add_job(run_update_pipeline, 'cron', day_of_week='sun', hour=3, minute=0)
    
    logger.info("Iniciando o serviço de agendamento...")
    print("---------------------------------------------------------")
    print("Serviço de agendamento em execução.")
    print("A tarefa de atualização de dados está agendada para rodar todo domingo às 03:00.")
    print("Pressione Ctrl+C para encerrar o serviço.")
    print("---------------------------------------------------------")
    
    scheduler.start()
    
    try:
        yield
    finally:
        logger.info("Encerrando o serviço de agendamento...")
        scheduler.shutdown()
        logger.info("Agendador encerrado de forma limpa.")

# --- Ponto de Entrada do Serviço ---

async def main():
    """Função principal que mantém o serviço rodando."""
    async with scheduler_lifespan():
        while True:
            await asyncio.sleep(3600) # Mantém o processo vivo.

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Serviço encerrado pelo usuário.")
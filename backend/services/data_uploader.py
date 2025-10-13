# =======================================================================================
# SERVIÇO DE AGENDAMENTO DE TAREFAS (DATA UPLOADER)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Este script opera como um serviço de segundo plano (daemon), completamente
#    independente da API principal (Uvicorn).
# 2. Ele usa a biblioteca `APScheduler` para agendar a execução de tarefas.
# 3. A principal tarefa agendada é a função `run_update_pipeline`, configurada para
#    rodar em um horário específico (ex: semanalmente).
# 4. A função `run_update_pipeline` chama os scripts de população (`populate_lvl2` e `populate_lvl3`)
#    na ordem correta, garantindo que uma etapa só comece se a anterior for bem-sucedida.
# 5. Um `asynccontextmanager` (`scheduler_lifespan`) gerencia o ciclo de vida do
#    agendador, garantindo que ele seja iniciado e encerrado de forma limpa.
#
# RAZÃO DE EXISTIR: Automatizar a atualização do banco de dados. Sua única
# responsabilidade é "acordar" em horários pré-definidos e orquestrar a execução
# do pipeline de ETL, mantendo os dados da aplicação sempre relevantes sem
# intervenção manual.
# =======================================================================================

# --- Módulos Padrão do Python ---
# Biblioteca para programação assíncrona, essencial para o APScheduler e para manter o serviço rodando.
import asyncio
# Módulo para registrar logs de execução.
import logging
# Módulo para manipulação de caminhos do sistema operacional.
import sys
from os.path import abspath, dirname
# Ferramenta para criar gerenciadores de contexto assíncronos (a sugestão do professor).
from contextlib import asynccontextmanager

# --- Módulos de Terceiros ---
# A biblioteca principal para agendamento de tarefas. Usamos a versão para asyncio.
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- Configuração de Path do Projeto ---
# Razão: Para que o Python encontre os módulos em `utils`, `model`, etc.,
# precisamos adicionar a pasta 'backend' ao path de busca.
# Sobe 2 níveis: services -> backend
project_root = dirname(dirname(abspath(__file__)))
sys.path.append(project_root)

# --- Configuração do Logger ---
# Define um formato padrão para os logs que serão exibidos no terminal.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
# Cria uma instância do logger para este módulo.
logger = logging.getLogger(__name__)

# --- Importação das Funções dos Scripts de População ---
# Razão: Importar as funções principais que serão agendadas.
try:
    # Importa a função principal do script de população de dimensões (Nível 2).
    from services.scripts.populate_lvl2 import main_populate_dimensions
    # Importa a função principal do script de população de fatos (Nível 3).
    from services.scripts.populate_lvl3 import main_populate_facts
except ImportError as e:
    # Se a importação falhar (ex: erro de digitação no nome do arquivo), o serviço não pode iniciar.
    logger.error(f"Não foi possível importar os scripts de população. Verifique os nomes e a estrutura. Erro: {e}")
    sys.exit(1)

# --- Definição da Tarefa Agendada ---

def run_update_pipeline():
    """
    Função: Executa o pipeline de atualização de dados na ordem correta, com verificação de falhas.
    Razão de Existência: Agrupar a sequência de tarefas em uma única função que pode ser
    passada para o agendador.
    """
    logger.info("==== INICIANDO PIPELINE DE ATUALIZAÇÃO AGENDADO ====")
    
    # ETAPA 1: Popular/Atualizar Dimensões (heróis)
    try:
        logger.info("--- [ETAPA 1/2] Executando 'populate_lvl2.py' para dimensões dinâmicas ---")
        # Chama a função principal do primeiro script. O programa espera esta função terminar.
        main_populate_dimensions()
        logger.info("--- [ETAPA 1/2] 'populate_lvl2.py' concluído com sucesso. ---")
    except Exception as e:
        # Se QUALQUER erro ocorrer durante a Etapa 1, ele será capturado aqui.
        logger.error(f"==== FALHA CRÍTICA NA ETAPA 1 (populate_lvl2). O pipeline será abortado. Erro: {e} ====", exc_info=True)
        # O comando 'return' interrompe a execução da função aqui. A Etapa 2 não será executada.
        return

    # ETAPA 2: Popular Fatos (estatísticas) - Só executa se a Etapa 1 for bem-sucedida.
    try:
        logger.info("--- [ETAPA 2/2] Executando 'populate_lvl3.py' para tabelas de fato ---")
        # Chama a função principal do segundo script.
        main_populate_facts()
        logger.info("--- [ETAPA 2/2] 'populate_lvl3.py' concluído com sucesso. ---")
    except Exception as e:
        # Se a Etapa 2 falhar, o erro será logado, mas o pipeline já terá concluído a maior parte do trabalho.
        logger.error(f"==== FALHA NA ETAPA 2 (populate_lvl3). Erro: {e} ====", exc_info=True)

    logger.info("==== PIPELINE DE ATUALIZAÇÃO AGENDADO CONCLUÍDO ====")

# --- Gerenciador de Contexto para o Serviço ---

@asynccontextmanager
async def scheduler_lifespan():
    """
    Função: Context manager que gerencia o ciclo de vida do agendador.
    Razão de Existência: Implementar a sugestão do professor para garantir que o serviço
    seja iniciado e encerrado de forma segura e limpa.
    """
    # Cria uma instância do agendador, configurando o fuso horário para o de São Paulo.
    scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")
    
    # Adiciona a tarefa ao agendador.
    # 'cron': Define um agendamento recorrente baseado em tempo.
    # 'day_of_week='sun'': Define que a tarefa rodará todo domingo.
    # 'hour=3', 'minute=0': Define o horário para 03:00.
    # Para testes, você pode alterar para algo como: day_of_week='mon', hour=16, minute=30
    scheduler.add_job(run_update_pipeline, 'cron', day_of_week='mon', hour=16, minute=25)
    
    # Exibe mensagens informativas no console quando o serviço é iniciado.
    logger.info("Iniciando o serviço de agendamento...")
    print("---------------------------------------------------------")
    print("Serviço de agendamento em execução.")
    print("A tarefa de atualização de dados está agendada para rodar todo domingo às 03:00.")
    print("Pressione Ctrl+C para encerrar o serviço.")
    print("---------------------------------------------------------")
    
    # Inicia o processo do agendador em segundo plano.
    scheduler.start()
    
    try:
        # 'yield' passa o controle para o bloco 'async with', permitindo que o programa principal continue.
        yield
    finally:
        # Este bloco é garantido de ser executado quando o serviço for encerrado (ex: com Ctrl+C).
        logger.info("Encerrando o serviço de agendamento...")
        # Desliga o agendador de forma limpa, esperando as tarefas atuais terminarem.
        scheduler.shutdown()
        logger.info("Agendador encerrado de forma limpa.")

# --- Ponto de Entrada do Serviço ---

async def main():
    """
    Função: Mantém o serviço rodando indefinidamente.
    Razão de Existência: Um script de serviço precisa de um loop principal para não
    encerrar imediatamente após ser iniciado.
    """
    # Usa o context manager para garantir que o scheduler inicie e pare corretamente.
    async with scheduler_lifespan():
        # Loop infinito que mantém o processo Python vivo.
        while True:
            # `asyncio.sleep` é uma forma eficiente de "pausar" sem consumir CPU.
            await asyncio.sleep(3600) # Pausa por uma hora antes de verificar o loop novamente.

# Ponto de entrada padrão para um script Python.
if __name__ == "__main__":
    try:
        # Inicia a execução da função principal assíncrona.
        asyncio.run(main())
    except KeyboardInterrupt:
        # Captura o comando Ctrl+C do usuário para encerrar o serviço de forma elegante.
        logger.info("Serviço encerrado pelo usuário.")
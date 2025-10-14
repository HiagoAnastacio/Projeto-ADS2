# =======================================================================================
# MÓDULO EXECUTOR DE SQL (CAMADA DE ACESSO A DADOS - DAO)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Uma instância global da classe `Database` é criada para ser reutilizada.
# 2. A função 'execute' é o único ponto de entrada para qualquer operação no banco de dados.
# 3. (NOVO) Antes da execução, a função verifica se o comando é um INSERT. Se for,
#    ela extrai o nome da tabela e loga os dados que serão inseridos.
# 4. Ela gerencia o ciclo de vida completo da conexão: conectar, executar, desconectar.
# 5. Captura qualquer erro do banco e o transforma em uma `HTTPException` padronizada.
#
# RAZÃO DE EXISTIR: Abstrair a complexidade do gerenciamento de conexões, centralizar
# o tratamento de erros e, agora, centralizar o logging de operações de escrita.
# =======================================================================================

from fastapi import HTTPException 
from model.db import Database 
import logging  # Importa o módulo de logging
import re       # Importa o módulo de expressões regulares para extrair o nome da tabela

# --- Configuração do Logger ---
# Pega a instância do logger configurada no main.py ou nos scripts.
logger = logging.getLogger(__name__)

# Variável 'db' (Escopo Global/Módulo): Instância única da classe Database.
db = Database()

def execute(sql: str, params: tuple = None): 
    """
    Executa um comando SQL, gerenciando a conexão, o tratamento de erros e o logging de inserções.
    """
    # --- LOGGING DE INSERÇÃO ADICIONADO ---
    # Verifica se o comando é um INSERT para logar os dados que serão inseridos.
    if sql.strip().lower().startswith("insert"):
        try:
            # Usa uma expressão regular para extrair o nome da tabela de forma segura da string SQL.
            # Procura por "INSERT INTO `nome_da_tabela`".
            table_name_match = re.search(r"INSERT INTO `(.*?)`", sql, re.IGNORECASE)
            if table_name_match:
                # `group(1)` captura o que está dentro dos parênteses na regex.
                table_name = table_name_match.group(1)
                # Loga a informação no formato solicitado.
                logger.info(f"Dado a ser inserido na tabela '{table_name}': {params}")
            else:
                # Caso a regex falhe, loga uma mensagem genérica.
                logger.info(f"Tentativa de inserção com dados: {params}")
        except Exception as log_error:
            # Garante que uma falha no logging não interrompa a operação principal.
            logger.error(f"Erro ao tentar logar dados de inserção: {log_error}")

    try:
        # Passo 1: Abre a conexão com o banco de dados.
        db.connect()
        # Passo 2: Chama o método da classe Database para executar a query.
        result = db.execute_comand(sql, params) 
        # Retorna o resultado da operação.
        return result 
    except Exception as e:
        # Em caso de erro, cria uma mensagem detalhada.
        detail_message = f"Erro no banco de dados: {type(e).__name__}: {e}"
        # Imprime o erro no console para debug.
        print(f"DEBUG SQL ERRO 500: {detail_message}") 
        
        # Levanta uma exceção HTTP 500 para a API.
        raise HTTPException(status_code=500, detail=detail_message)
    finally:
        # Passo 3: Garante que a conexão seja sempre fechada.
        db.disconnect()
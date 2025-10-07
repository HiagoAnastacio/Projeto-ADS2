# =======================================================================================
# MÓDULO EXECUTOR DE SQL (CAMADA DE ACESSO A DADOS - DAO)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. Uma instância global da classe `Database` é criada para ser reutilizada.
# 2. A função 'execute' é o único ponto de entrada para qualquer operação no banco de dados.
# 3. Ela gerencia o ciclo de vida completo da conexão para cada chamada:
#    a. Abre a conexão (`db.connect()`).
#    b. Executa o comando SQL de forma segura (`db.execute_comand()`).
#    c. Fecha a conexão (`db.disconnect()`), garantindo que os recursos sejam liberados.
# 4. Implementa um bloco `try...except...finally` robusto para garantir que a conexão
#    seja fechada mesmo em caso de erro.
# 5. Captura qualquer erro vindo da camada de banco de dados (`db.py`) e o transforma
#    em uma `HTTPException` padronizada do FastAPI com uma mensagem de erro detalhada,
#    facilitando o debug tanto no frontend quanto no backend.
#
# RAZÃO DE EXISTIR: Abstrair a complexidade do gerenciamento de conexões e centralizar
# o tratamento de erros do banco de dados. Este módulo atua como um "portão" seguro
# para o banco, garantindo que todas as interações sigam um padrão consistente e seguro.
# =======================================================================================

# Importa a classe para levantar erros HTTP padronizados do FastAPI.
from fastapi import HTTPException 
# Importa a nossa classe personalizada de gerenciamento de banco de dados.
from model.db import Database 

# Variável 'db' (Escopo Global/Módulo): Uma única instância da classe Database é criada
# quando o módulo é carregado. Ela será reutilizada por todas as chamadas à função `execute`.
db = Database()

def execute(sql: str, params: tuple = None): 
    """
    Executa um comando SQL, gerenciando todo o ciclo de conexão e tratamento de erros.
    """
    try:
        # Passo 1: Abre a conexão com o banco de dados.
        db.connect()
        # Passo 2: Chama o método da classe Database para executar a query.
        # `result` conterá os dados de um SELECT, o ID de um INSERT, ou as linhas afetadas.
        result = db.execute_comand(sql, params) 
        # Retorna o resultado da operação bem-sucedida.
        return result 
    except Exception as e:
        # Este bloco é executado se `db.connect()` ou `db.execute_comand()` levantarem um erro.
        
        # Cria uma mensagem de erro detalhada, incluindo o tipo do erro e a mensagem.
        detail_message = f"Erro no banco de dados: {type(e).__name__}: {e}"
        # Imprime o erro no console do servidor para visibilidade imediata do desenvolvedor.
        print(f"DEBUG SQL ERRO 500: {detail_message}") 
        
        # Levanta uma exceção HTTP 500 (Erro Interno do Servidor) que será enviada
        # como resposta JSON ao cliente da API, informando a causa do problema.
        raise HTTPException(status_code=500, detail=detail_message)
    finally:
        # Passo 3: Garante que a conexão seja sempre fechada, quer a operação
        # tenha sido bem-sucedida ou tenha falhado.
        db.disconnect()
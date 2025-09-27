# FLUXO E A LÓGICA:
# 1. Inicializa o objeto de conexão 'db' (Escopo Global/Módulo).
# 2. A função `execute` recebe o `sql` e `params` da rota (Escopo de Requisição).
# 3. `execute` encapsula o fluxo de conexão: `db.connect()`, `db.execute_comand()`, `db.disconnect()`.
# 4. Trata erros do DB (propagados de `db.py`), transformando-os em `HTTPException 500`.
# A razão de existir: Camada DAO (Data Access Object) centralizada. Garante que todas as interações com o DB sigam o mesmo fluxo de conexão e tratamento de erros.

from fastapi import HTTPException # Razão: Para levantar erros HTTP para a rota em caso de falha do DB (500 Internal Server Error).
from model.db import Database # Razão: Classe que armazena credenciais e gerencia a conexão MySQL.

# Variável 'db' (Escopo Global/Módulo): Objeto de conexão criado UMA VEZ no startup da aplicação.
# Armazena as credenciais lidas do .env.
db = Database()

def execute(sql: str, params: tuple = None): # Variáveis 'sql' e 'params' (Escopo de Requisição): Query e valores enviados da rota.
    """Executa um comando SQL. Conecta, executa, desconecta, e gerencia erros."""
    try:
        # 1. Gerenciamento da Conexão (Escopo de Requisição)
        db.connect() # Abre a conexão com o banco de dados.
        # Variável 'result' (Escopo de Requisição): Dados retornados ou lastrowid/rowcount.
        result = db.execute_comand(sql, params) # Executa o SQL (db.py lida com o COMMIT).
        db.disconnect() # Fecha a conexão e o cursor (CRÍTICO para não estourar o limite de conexões do DB).
        return result 
    except Exception as e:
        # Garante que a conexão seja sempre fechada, mesmo em caso de erro.
        # Chamada defensiva caso o erro ocorra antes do db.disconnect().
        db.disconnect() 
        # Erro 500 (Internal Server Error) em caso de falha de conexão, deadlock, ou erro de sintaxe SQL.
        raise HTTPException(status_code=500, detail=f"Erro de Banco de Dados: {e}")
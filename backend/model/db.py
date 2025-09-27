# FLUXO E A LÓGICA:
# 1. O construtor `__init__` lê as variáveis de ambiente (Escopo Global/Módulo).
# 2. `connect()` abre a conexão com o DB (Escopo de Requisição).
# 3. `execute_comand()` executa o SQL, faz `COMMIT` ou retorna dados (Escopo de Requisição).
# 4. `disconnect()` fecha a conexão (Escopo de Requisição).
# A razão de existir: Encapsular o acesso ao driver MySQL. É a interface de baixo nível entre a aplicação Python e o banco de dados.

from typing import Any, Optional, Tuple, Union, List # Razão: Tipagem complexa.
import mysql.connector as mc # Razão: Driver principal do MySQL.
from mysql.connector import Error, MySQLConnection # Razão: Importa as classes de Erro e Conexão.
from dotenv import load_dotenv # Razão: Carregar o arquivo .env (onde estão as credenciais).
from os import getenv # Razão: Acessar as variáveis de ambiente.

class Database: # Classe que gerencia a conexão com o banco
    def __init__(self) -> None:
        load_dotenv() # Carrega as variáveis do arquivo .env.
        # Variáveis self.host, self.username, etc. (Escopo Global/Módulo - Atributos da Instância): Credenciais de conexão.
        self.host: str = getenv('DB_HOST')
        # ... outras credenciais ...
        self.connection: Optional[MySQLConnection] = None # Variável 'connection' (Escopo de Requisição - Atributo Mutável): Objeto de conexão real. Inicia como None.
        self._cursor: Union[List[dict], None] = None # Variável '_cursor' (Escopo de Requisição - Atributo Mutável): Objeto de execução. Inicia como None.
 
    def connect(self) -> None:
        """Abre a conexão com o MySQL."""
        # Tenta criar e atribuir a conexão ao self.connection.
        # Variável 'connection' passa a ser o objeto de conexão real do driver.
        self.connection = mc.connect(...) 

    def disconnect(self) -> None:
        """Fecha a conexão com o banco de dados e o cursor."""
        # Garante que os recursos do DB sejam liberados.
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Conexão com o banco de dados encerrada com sucesso;")
   
    def execute_comand(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Union[List[dict], Any]]:
        """Executa um comando SQL de forma segura, gerencia o cursor e o COMMIT."""
        
        # Variável 'cursor' (Escopo de Função/Local): O objeto que executa o comando SQL.
        cursor = self.connection.cursor(dictionary=True) # Cria um NOVO cursor.
        try:
            # Executa o comando SQL (os 'params' são usados para prevenir SQL Injection).
            cursor.execute(sql, params)
            if sql.strip().lower().startswith("select"):
                result = cursor.fetchall() # Busca os dados (SELECT).
                return result
            else:
                self.connection.commit() # Confirma a transação (INSERT/UPDATE/DELETE).
                # Retorna o ID inserido ou o número de linhas afetadas.
                return cursor.lastrowid if sql.strip().lower().startswith("insert") else cursor.rowcount
        except Error as e:
            # A exceção é levantada para ser capturada e tratada em function_execute.py.
            raise e
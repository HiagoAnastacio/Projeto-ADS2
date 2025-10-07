# =======================================================================================
# MÓDULO DE CONEXÃO COM O BANCO DE DADOS (CAMADA DE ACESSO A DADOS - DAO)
# =======================================================================================
# FLUXO E A LÓGICA:
# 1. A classe `Database` é instanciada e suas credenciais são carregadas do arquivo `.env`
#    quando o módulo é importado pela primeira vez.
# 2. O método `connect()` é chamado para abrir uma conexão com o MySQL. Ele é projetado
#    para falhar de forma explícita (levantando um erro) se a conexão não for estabelecida.
# 3. O método `execute_comand()` recebe uma string SQL e parâmetros, executa a query de
#    forma segura (prevenindo SQL Injection) e gerencia a transação (fazendo `commit` para
#    escritas ou `fetchall` para leituras).
# 4. O método `disconnect()` fecha a conexão e o cursor, liberando os recursos.
#
# RAZÃO DE EXISTIR: Encapsular toda a complexidade de interagir com o driver do
# MySQL (`mysql-connector-python`). Nenhuma outra parte da aplicação precisa saber
# como uma conexão é aberta ou como um comando é executado; eles apenas usam esta classe.
# =======================================================================================

from typing import Any, Optional, Tuple, Union, List
import mysql.connector as mc
from mysql.connector import Error, MySQLConnection
from dotenv import load_dotenv
from os import getenv

class Database:
    # O construtor é chamado uma vez quando o objeto é criado.
    def __init__(self) -> None:
        # Carrega as variáveis do arquivo .env para o ambiente.
        load_dotenv()
        # Lê as variáveis de ambiente e as armazena nos atributos da classe.
        # Estas variáveis têm escopo de instância (self).
        self.host: str = getenv('DB_HOST')
        self.username: str = getenv('DB_USER')
        self.password: str = getenv('DB_PSWD')
        self.database: str = getenv('DB_NAME')
        # Atributos para a conexão e o cursor, inicializados como None.
        self.connection: Optional[MySQLConnection] = None
        self.cursor: Union[List[dict], None] = None
 
    def connect(self) -> None:
        """
        Estabelece uma conexão com o banco de dados.
        Levanta a exceção (raise) em caso de falha para ser tratada pela camada superior.
        """
        try:
            # Tenta estabelecer a conexão com o MySQL.
            self.connection = mc.connect(
                host = self.host,
                database = self.database,
                user = self.username,
                password = self.password
            )
            # Verifica se a conexão foi bem-sucedida.
            if self.connection.is_connected():
                # Cria um cursor que retorna resultados como dicionários.
                self.cursor = self.connection.cursor(dictionary=True)
                print("Conexão ao banco de dados realizada com sucesso.")
        except Error as e:
            # Em caso de erro, limpa os atributos e re-levanta a exceção.
            print(f"Erro de conexão do DB: {e}")
            self.connection = None
            self.cursor = None
            raise e
 
    def disconnect(self) -> None:
        """Encerra a conexão com o banco de dados e o cursor."""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
        print("Conexão com o banco de dados encerrada.")
    
    def execute_comand(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Union[List[dict], Any]]:
        """Executa um comando SQL, gerenciando o cursor e o COMMIT."""
        if not self.connection or not self.connection.is_connected():
            print('ERRO: Conexão ao banco de dados não estabelecida.')
            # Levanta um erro explícito se a conexão não existir.
            raise ConnectionError("A conexão com o banco de dados não está ativa.")

        # Cria um novo cursor para cada execução, garantindo isolamento.
        cursor = self.connection.cursor(dictionary=True) 
        try:
            # Executa o comando SQL. A passagem de 'params' separadamente previne SQL Injection.
            cursor.execute(sql, params)
            
            # Verifica se o comando é uma consulta (SELECT).
            if sql.strip().lower().startswith("select"):
                # Se for SELECT, busca todos os resultados e os retorna.
                result = cursor.fetchall()
                return result
            else:
                # Se for INSERT, UPDATE, ou DELETE, confirma a transação no banco.
                self.connection.commit()
                # Para INSERT, retorna o ID da nova linha. Para outros, o número de linhas afetadas.
                return cursor.lastrowid if sql.strip().lower().startswith("insert") else cursor.rowcount
        except Error as e:
            # Se ocorrer um erro de SQL, levanta a exceção para ser tratada pela camada superior.
            raise e
        finally:
            # Garante que o cursor seja sempre fechado, mesmo em caso de erro.
            cursor.close()
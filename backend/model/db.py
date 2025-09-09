# Ponto das funções de conexão com o banco de dados e parte do Model da arquitetura MVC.
from typing import Any, Optional, Tuple, Union, List
import mysql.connector as mc #Biblioteca do conector do MySQL
from mysql.connector import Error, MySQLConnection #Importando a classe Error para tratar as mensagens de erro do código
from dotenv import load_dotenv #Importando a função load_dotenv
from os import getenv #Importando a função getenv
 
class Database:
    def __init__(self) -> None:
        load_dotenv()
        self.host: str = getenv('DB_HOST')
        self.username: str = getenv('DB_USER')
        self.password: str = getenv('DB_PSWD')
        self.database: str = getenv('DB_NAME')
        self.connection: Optional[MySQLConnection] = None #Inicialização da conexão
        self._cursor: Union[List[dict], None] = None #Inicialização do cursor
 
# ===============================================================================================================
# Métodos de conexão, desconexão e execução de comandos no banco de dados.
# ===============================================================================================================
    # Conectar ao banco de dados
    def connect(self) -> None:
        """Estabelece uma conexão com o banco de dados."""
        try:
            self.connection = mc.connect(
                host = self.host,
                database = self.database,
                user = self.username,
                password = self.password
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                print("Conexão ao banco de dados realizada com sucesso,")
        except Error as e:
            print(f"Erro de conexão: {e}")
            self.connection = None
            self.cursor = None
 
    # Desconectar do banco de dados
    def disconnect(self) -> None:
        """Encerra a conexão com o banco de dados e o cursor, se eles existirem."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Conexão com o banco de dados encerrada com sucesso;")
   
    # Executar comando no banco de dados
    def execute_comand(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Union[List[dict], Any]]:
        if self.connection is None:
            print('Conexão ao banco de dados não estabelecida.')
            return None
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(sql, params)
            if sql.strip().lower().startswith("select"):
                result = cursor.fetchall()
                return result
            else:
                self.connection.commit()
                return cursor.rowcount
        except Error as e:
            # Não capture a exceção aqui, deixe-a propagar
            # A função `function_execute` já trata a exceção
            raise e
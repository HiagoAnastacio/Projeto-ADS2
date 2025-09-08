# Função para executar comandos SQL no banco de dados de maneira reutilizável.
from fastapi import FastAPI, HTTPException
from model.db import Database

app = FastAPI()
db = Database()

def execute(sql: str, params: tuple = None):
    """
    Executa um comando SQL usando a conexão do banco.
    1. Conecta ao banco.
    2. Executa o comando SQL com os parâmetros.
    3. Desconecta do banco.
    4. Retorna o resultado ou lança exceção em caso de erro.
    """
    try:
        db.connect()
        result = db.execute_comand(sql, params)  # Executa o comando SQL
        db.disconnect()
        return result  # Retorna o resultado da consulta
    except Exception as e:
        db.disconnect()
        raise HTTPException(status_code=500, detail=str(e))  # Lança erro HTTP em caso de exceção
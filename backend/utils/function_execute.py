# Uma função para executar comandos SQL no banco de dados de maneira reutilizavel.
from fastapi import FastAPI, HTTPException
from model.db import Database

app = FastAPI()
db = Database()

def execute(sql: str, params: tuple = None):
    try:
        db.connect()
        result = db.execute_comand(sql, params)
        db.disconnect()
        return result
    except Exception as e:
        db.disconnect()
        raise HTTPException(status_code=500, detail=str(e))
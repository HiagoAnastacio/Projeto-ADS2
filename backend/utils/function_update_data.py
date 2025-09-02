from fastapi import FastAPI, HTTPException
from model.db import Database

app = FastAPI()
db = Database()

def scrap_update_data():

import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client.hub_jogador_db

treinos_collection = db.treinos
jogos_collection = db.jogos
usuarios_collection = db.usuarios
import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId
import datetime

load_dotenv()

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.hub_jogador_db
treinos_collection = db.treinos

@app.route('/treino', methods=['POST'])
def adicionar_treino():
    dados = request.get_json()

    if not dados or 'duracao_minutos' not in dados or 'intensidade' not in dados:
        return jsonify({"erro": "Dados incompletos"}), 400

    dados['data_registro'] = datetime.datetime.now()

    resultado = treinos_collection.insert_one(dados)

    return jsonify({"mensagem": "Treino registrado com sucesso!", "id": str(resultado.inserted_id)}), 201

@app.route('/treinos', methods=['GET'])
def listar_treinos():
    lista_de_treinos = []
    for treino in treinos_collection.find({}):
        treino['_id'] = str(treino['_id'])
        lista_de_treinos.append(treino)

    return jsonify(lista_de_treinos), 200

if __name__ == '__main__':
    app.run(debug=True)
from flask import Blueprint, request, jsonify
import datetime
from app.database import treinos_collection
from app.auth import token_required

treinos_bp = Blueprint('treinos', __name__)

@treinos_bp.route('/treino', methods=['POST'])
@token_required
def adicionar_treino(current_user):
    dados = request.get_json()
    if not dados or 'duracao_minutos' not in dados or 'intensidade' not in dados or 'foco' not in dados:
        return jsonify({"erro": "Dados incompletos"}), 400
    dados['usuario_id'] = current_user['_id']
    dados['data_registro'] = datetime.datetime.now()
    resultado = treinos_collection.insert_one(dados)
    return jsonify({"mensagem": "Treino registrado com sucesso!", "id": str(resultado.inserted_id)}), 201


@treinos_bp.route('/treinos', methods=['GET'])
def listar_treinos():
    lista_de_treinos = []
    for treino in treinos_collection.find({}):
        treino['_id'] = str(treino['_id'])
        lista_de_treinos.append(treino)
    return jsonify(lista_de_treinos), 200
from flask import Blueprint, request, jsonify
import datetime
from app.database import jogos_collection
from app.auth import token_required

jogos_bp = Blueprint('jogos', __name__)

@jogos_bp.route('/jogos', methods=['POST'])
@token_required
def adicionar_jogo(current_user):
    dados = request.get_json()
    if not dados or 'tempo_jogado' not in dados or 'intensidade' not in dados or 'adversário' not in dados or 'gols' not in dados or 'assistências' not in dados or 'dificuldade' not in dados:    
        return jsonify({"erro": "Dados incompletos"}), 400
    dados['usuario_id'] = current_user['_id']
    dados['data_registro'] = datetime.datetime.now()
    resultado = jogos_collection.insert_one(dados)
    return jsonify({"mensagem": "Jogo registrado com sucesso!", "id": str(resultado.inserted_id)}), 201


@jogos_bp.route('/jogos', methods=['GET'])
def listar_jogos():
    lista_de_jogos = []
    for jogo in jogos_collection.find({}):
        jogo['_id'] = str(jogo['_id'])
        lista_de_jogos.append(jogo)
    return jsonify(lista_de_jogos), 200
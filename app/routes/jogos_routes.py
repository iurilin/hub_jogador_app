from flask import Blueprint, request, jsonify
import datetime
from bson import ObjectId
from bson.errors import InvalidId
from app.database import jogos_collection
from app.auth import token_required

jogos_bp = Blueprint('jogos', __name__)

@jogos_bp.route('/jogo', methods=['POST'])
@token_required
def adicionar_jogo(current_user):
    dados = request.get_json()
    if not dados or 'minutos_jogados' not in dados or 'intensidade' not in dados or 'adversário' not in dados or 'gols' not in dados or 'assistências' not in dados or 'dificuldade' not in dados or 'resultado' not in dados or 'campeonato' not in dados or 'local' not in dados or 'posicao' not in dados or 'chutes' not in dados or 'desarmes' not in dados or 'faltas_cometidas' not in dados or 'faltas_sofridas' not in dados or 'cartao' not in dados or 'desempenho' not in dados or 'data_hora' not in dados:    
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


@jogos_bp.route('/jogo/<id>', methods=['PUT'])
@token_required
def atualizar_jogo(current_user, id):
    try:
        dados_novos = request.get_json()

        if not dados_novos or 'minutos_jogados' not in dados_novos or 'intensidade' not in dados_novos or 'adversário' not in dados_novos or 'gols' not in dados_novos or 'assistências' not in dados_novos or 'dificuldade' not in dados_novos or 'resultado' not in dados_novos or 'campeonato' not in dados_novos or 'local' not in dados_novos or 'posicao' not in dados_novos or 'chutes' not in dados_novos or 'desarmes' not in dados_novos or 'faltas_cometidas' not in dados_novos or 'faltas_sofridas' not in dados_novos or 'cartao' not in dados_novos or 'desempenho' not in dados_novos or 'data_hora' not in dados_novos:
             return jsonify({"erro": "Dados incompletos"}), 400

        dados_novos['data_atualizacao'] = datetime.datetime.now()

        resultado = jogos_collection.update_one(
            {'_id': ObjectId(id), 'usuario_id': current_user['_id']},
            {'$set': dados_novos}
        )

        if resultado.modified_count == 1:
            return jsonify({"mensagem": "Jogo atualizado com sucesso!"}), 200
        else:
            return jsonify({"erro": "Jogo não encontrado ou não pertence a este usuário"}), 404

    except InvalidId:
        return jsonify({"erro": "ID do jogo inválido"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    

@jogos_bp.route('/jogo/<id>', methods=['DELETE'])
@token_required
def deletar_jogo(current_user, id):
    try:
        resultado = jogos_collection.delete_one(
            {'_id': ObjectId(id), 'usuario_id': current_user['_id']}
        )
        if resultado.deleted_count == 1:
            return jsonify({"mensagem": "Jogo deletado com sucesso!"}), 200
        else:
            return jsonify({"erro": "Jogo não encontrado ou não pertence a este usuário"}), 404

    except InvalidId:
        return jsonify({"erro": "ID do jogo inválido"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
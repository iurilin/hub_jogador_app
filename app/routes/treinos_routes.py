from flask import Blueprint, request, jsonify
import datetime
from bson import ObjectId
from bson.errors import InvalidId
from app.database import treinos_collection
from app.auth import token_required

treinos_bp = Blueprint('treinos', __name__)

@treinos_bp.route('/treino', methods=['POST'])
@token_required
def adicionar_treino(current_user):
    dados = request.get_json()
    if not dados or 'duracao_minutos' not in dados or 'intensidade' not in dados or 'tipo_treino' not in dados or 'local' not in dados or 'descricao_objetivo' not in dados or 'data_hora' not in dados:
        return jsonify({"erro": "Dados incompletos"}), 400
    dados['usuario_id'] = current_user['_id']
    dados['data_registro'] = datetime.datetime.now()
    resultado = treinos_collection.insert_one(dados)
    return jsonify({"mensagem": "Treino registrado com sucesso!", "id": str(resultado.inserted_id)}), 201


@treinos_bp.route('/treinos', methods=['GET'])
@token_required
def listar_treinos(current_user):
    lista_de_treinos = []

    treinos_do_usuario = treinos_collection.find({'usuario_id': current_user['_id']})
    
    for treino in treinos_do_usuario:
        treino['_id'] = str(treino['_id'])

        if 'usuario_id' in treino:
            treino['usuario_id'] = str(treino['usuario_id'])
        
        lista_de_treinos.append(treino)
        
    return jsonify(lista_de_treinos), 200


@treinos_bp.route('/treino/<id>', methods=['PUT'])
@token_required
def atualizar_treino(current_user, id):
    try:
        dados_novos = request.get_json()

        if not dados_novos or 'duracao_minutos' not in dados_novos or 'intensidade' not in dados_novos or 'tipo_treino' not in dados_novos or 'local' not in dados_novos or 'descricao_objetivo' not in dados_novos or 'data_hora' not in dados_novos:
             return jsonify({"erro": "Dados incompletos"}), 400

        dados_novos['data_atualizacao'] = datetime.datetime.now()

        resultado = treinos_collection.update_one(
            {'_id': ObjectId(id), 'usuario_id': current_user['_id']},
            {'$set': dados_novos}
        )

        if resultado.modified_count == 1:
            return jsonify({"mensagem": "Treino atualizado com sucesso!"}), 200
        else:
            return jsonify({"erro": "Treino não encontrado ou não pertence a este usuário"}), 404

    except InvalidId:
        return jsonify({"erro": "ID do treino inválido"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    

@treinos_bp.route('/treino/<id>', methods=['DELETE'])
@token_required
def deletar_treino(current_user, id):
    try:
        resultado = treinos_collection.delete_one(
            {'_id': ObjectId(id), 'usuario_id': current_user['_id']}
        )
        if resultado.deleted_count == 1:
            return jsonify({"mensagem": "Treino deletado com sucesso!"}), 200
        else:
            return jsonify({"erro": "Treino não encontrado ou não pertence a este usuário"}), 404

    except InvalidId:
        return jsonify({"erro": "ID do treino inválido"}), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
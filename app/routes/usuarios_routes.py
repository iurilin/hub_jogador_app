from flask import Blueprint, request, jsonify
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from app.auth import token_required
from app.database import usuarios_collection
from werkzeug.utils import secure_filename
import time
from flask import Blueprint, request, jsonify, current_app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/usuario/registrar', methods=['POST'])
def registrar_usuario():
    dados = request.get_json()
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')
    posicao = dados.get('posicao')


    if not email or not senha:
        return jsonify({'erro': 'Email e senha são obrigatórios'}), 400

    if usuarios_collection.find_one({'email': email}):
        return jsonify({'erro': 'Este email já está cadastrado'}), 409

    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

    usuarios_collection.insert_one({
        'nome': nome,
        'email': email,
        'senha_hash': senha_hash,
        'posicao': posicao
    })

    return jsonify({'mensagem': 'Usuário registrado com sucesso!'}), 201


# login
@usuarios_bp.route('/usuario/login', methods=['POST'])
def login_usuario():
    dados = request.get_json()
    email = dados.get('email')
    senha = dados.get('senha')

    if not email or not senha:
        return jsonify({'erro': 'Email e senha são obrigatórios'}), 400

    usuario = usuarios_collection.find_one({'email': email})

    if usuario and bcrypt.checkpw(senha.encode('utf-8'), usuario['senha_hash']):
  
        token = jwt.encode({
            'user_id': str(usuario['_id']),
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, os.getenv('SECRET_KEY'), algorithm='HS256')

        return jsonify({'token': token})

    return jsonify({'erro': 'Credenciais inválidas'}), 401

@usuarios_bp.route('/usuario/perfil', methods=['GET'])
@token_required
def get_user_profile(current_user):
    if current_user:
        current_user['_id'] = str(current_user['_id']) 

        current_user.pop('senha_hash', None) 
        
        return jsonify(current_user), 200
    else:
        return jsonify({"erro": "Usuário não encontrado"}), 404
    
@usuarios_bp.route('/usuario/perfil', methods=['PUT'])
@token_required
def update_user_profile(current_user):
    try:
        dados_novos = request.get_json()

        if not dados_novos:
            return jsonify({"erro": "Nenhum dado enviado para atualização"}), 400

        campos_permitidos = ['nome', 'email', 'posicao']

        update_data = {}
        for campo in campos_permitidos:
            if campo in dados_novos:
                update_data[campo] = dados_novos[campo]

        if not update_data:
             return jsonify({"erro": "Nenhum campo válido enviado para atualização"}), 400

        if 'email' in update_data and update_data['email'] != current_user.get('email'):
            if usuarios_collection.find_one({'email': update_data['email']}):
                return jsonify({'erro': 'Este email já está sendo usado por outra conta'}), 409
        resultado = usuarios_collection.update_one(
            {'_id': current_user['_id']},
            {'$set': update_data}
        )

        if resultado.modified_count == 1:
            usuario_atualizado = usuarios_collection.find_one({'_id': current_user['_id']})
            if usuario_atualizado:
                 usuario_atualizado['_id'] = str(usuario_atualizado['_id'])
                 usuario_atualizado.pop('senha_hash', None)
                 return jsonify(usuario_atualizado), 200
            else:
                 return jsonify({"erro": "Usuário não encontrado após atualização"}), 404
        elif resultado.matched_count == 1:
             current_user['_id'] = str(current_user['_id'])
             current_user.pop('senha_hash', None)
             return jsonify(current_user), 200 
        else:
            return jsonify({"erro": "Usuário não encontrado"}), 404

    except Exception as e:
        print(f"Erro ao atualizar perfil: {e}")
        return jsonify({"erro": "Ocorreu um erro interno ao atualizar o perfil"}), 500
    
@usuarios_bp.route('/usuario/perfil/foto', methods=['POST'])
@token_required
def upload_profile_picture(current_user):
    if 'photo' not in request.files:
        return jsonify({"erro": "Nenhum arquivo de foto enviado"}), 400
    
    file = request.files['photo']

    if file.filename == '':
        return jsonify({"erro": "Nenhum arquivo selecionado"}), 400

    if file and allowed_file(file.filename):
        filename_base, file_extension = os.path.splitext(file.filename)
        unique_filename = secure_filename(f"{str(current_user['_id'])}_{int(time.time())}{file_extension}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        try:
            file.save(filepath)

            foto_url = f"/uploads/profile_pics/{unique_filename}" 

            usuarios_collection.update_one(
                {'_id': current_user['_id']},
                {'$set': {'foto': foto_url}}
            )

            usuario_atualizado = usuarios_collection.find_one({'_id': current_user['_id']})
            if usuario_atualizado:
                 usuario_atualizado['_id'] = str(usuario_atualizado['_id'])
                 usuario_atualizado.pop('senha_hash', None)
                 usuario_atualizado['foto'] = foto_url 
                 return jsonify(usuario_atualizado), 200
            else:
                 return jsonify({"erro": "Usuário não encontrado após upload"}), 404

        except Exception as e:
            print(f"Erro ao salvar arquivo: {e}")
            return jsonify({"erro": "Falha ao salvar a foto"}), 500
            
    else:
        return jsonify({"erro": "Tipo de arquivo não permitido"}), 400


from flask import send_from_directory

@usuarios_bp.route('/uploads/profile_pics/<filename>')
def serve_profile_picture(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
from flask import Blueprint, request, jsonify
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from app.database import usuarios_collection

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
from functools import wraps
from flask import request, jsonify
import jwt
import os
from bson import ObjectId
from app.database import usuarios_collection

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'erro': 'Token não encontrado'}), 401

        try:
            data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
            current_user = usuarios_collection.find_one({'_id': ObjectId(data['user_id'])})
        except Exception as e:
            return jsonify({'erro': 'Token inválido', 'details': str(e)}), 401

        return f(current_user, *args, **kwargs)
    return decorated
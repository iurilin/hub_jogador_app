from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path
import os

UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'uploads', 'profile_pics')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

base_dir = Path(__file__).resolve().parent.parent
caminho_env = base_dir / '.env'
load_dotenv(dotenv_path=caminho_env)


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    from .routes.treinos_routes import treinos_bp
    from .routes.jogos_routes import jogos_bp
    from .routes.usuarios_routes import usuarios_bp

    app.register_blueprint(treinos_bp)
    app.register_blueprint(jogos_bp)
    app.register_blueprint(usuarios_bp)

    return app

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
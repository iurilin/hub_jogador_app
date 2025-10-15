from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
caminho_env = base_dir / '.env'
load_dotenv(dotenv_path=caminho_env)


def create_app():
    app = Flask(__name__)
    CORS(app)

    from .routes.treinos_routes import treinos_bp
    from .routes.jogos_routes import jogos_bp
    from .routes.usuarios_routes import usuarios_bp

    app.register_blueprint(treinos_bp)
    app.register_blueprint(jogos_bp)
    app.register_blueprint(usuarios_bp)

    return app
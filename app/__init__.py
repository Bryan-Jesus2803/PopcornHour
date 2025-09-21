from flask import Flask
from supabase import create_client
from .config import SUPABASE_URL, SUPABASE_KEY


def create_app():
    app = Flask(__name__)
    from .config import SECRET_KEY
    app.secret_key = SECRET_KEY

    # Importar las rutas dentro de la función para evitar circular imports
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app

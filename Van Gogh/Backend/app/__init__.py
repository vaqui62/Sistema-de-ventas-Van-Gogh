from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from app.config import Config
from app.extensions import db
from app.models.models import *  # noqa: F401, F403 — necesario para que Migrate detecte los modelos
from app.routes.categorias import categorias_bp
from app.routes.productos import productos_bp
from app.routes.usuarios import usuarios_bp
from app.routes.pedidos import pedidos_bp
from app.routes.variantes import variantes_bp
from app.routes.imagenes import imagenes_bp
from app.routes.pagos import pagos_bp
from app.routes.direcciones import direcciones_bp
from app.routes.paginas import paginas_bp
from app.routes.cupones import cupones_bp
from app.routes.clientes import clientes_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Crear directorio de uploads si no existe
    import os
    os.makedirs(app.config.get('UPLOAD_FOLDER', app.root_path + '/static/uploads'), exist_ok=True)

    CORS(app)
    db.init_app(app)
    Migrate(app, db)

    app.register_blueprint(categorias_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(variantes_bp)
    app.register_blueprint(imagenes_bp)
    app.register_blueprint(pagos_bp)
    app.register_blueprint(direcciones_bp)
    app.register_blueprint(cupones_bp)
    app.register_blueprint(paginas_bp)
    app.register_blueprint(clientes_bp)

    @app.route("/")
    def home():
        return {"mensaje": "Backend Flask funcionando"}

    return app
from flask import Flask
from flask_migrate import Migrate          
from app.config import Config
from app.extensions import db
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

    db.init_app(app)

    # Importar modelos ANTES de Migrate para que los detecte




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
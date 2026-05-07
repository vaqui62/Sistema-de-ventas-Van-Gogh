# test_conexion.py
from app.config import Config
from app.extensions import db
from app import create_app

app = create_app()
with app.app_context():
    db.engine.connect()
    print("✅ Conexión exitosa a Neon")
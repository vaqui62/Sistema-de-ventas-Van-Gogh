import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(encoding='utf-8', override=False)  # ← estos dos parámetros

class Config:

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    if not SQLALCHEMY_DATABASE_URI:
        basedir = Path(__file__).resolve().parent.parent
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'instance' / 'van_gogh.db'}"
        print("[WARN] DATABASE_URL no configurado. Usando SQLite local para desarrollo.")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-cambiar-en-produccion")

    UPLOAD_FOLDER = Path(__file__).resolve().parent.parent / 'app' / 'static' / 'uploads'
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
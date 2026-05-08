from app import db

class Producto(db.Model):
    __tablename__ = "productos"

    id_producto  = db.Column(db.Integer, primary_key=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey("categorias.id_categoria"), nullable=False)
    nombre       = db.Column(db.String(150), nullable=False)
    slug         = db.Column(db.String(150), unique=True, nullable=False)
    descripcion  = db.Column(db.Text)
    precio_base  = db.Column(db.Numeric(10, 2), nullable=False)
    obra_vangogh = db.Column(db.String(120))
    activo       = db.Column(db.Boolean, default=True)

    # Relacion con variantes
    variantes = db.relationship("Variante", backref="producto", lazy=True)
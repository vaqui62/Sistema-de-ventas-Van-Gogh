from flask import Blueprint, jsonify
from app.models.models import Cupon

cupones_bp = Blueprint('cupones', __name__, url_prefix='/api/cupones')

@cupones_bp.route('/', methods=['GET'])
def listar_cupones():
    cupones = Cupon.query.filter_by(activo=True).all()
    return jsonify([{
        'id_cupon': c.id_cupon,
        'codigo': c.codigo,
        'tipo': c.tipo.value,
        'descuento': float(c.descuento),
        'activo': c.activo
    } for c in cupones]), 200
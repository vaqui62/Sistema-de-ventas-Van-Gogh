from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.models import Cupon, TipoCupon
from datetime import date

cupones_bp = Blueprint('cupones', __name__, url_prefix='/api/cupones')


def _serializar(c):
    return {
        'id_cupon':      c.id_cupon,
        'codigo':        c.codigo,
        'tipo':          c.tipo.value,
        'descuento':     float(c.descuento),
        'monto_minimo':  float(c.monto_minimo) if c.monto_minimo else 0,
        'fecha_inicio':  c.fecha_inicio.isoformat() if c.fecha_inicio else None,
        'fecha_fin':     c.fecha_fin.isoformat() if c.fecha_fin else None,
        'usos_maximos':  c.usos_maximos,
        'usos_actuales': c.usos_actuales,
        'activo':        c.activo,
        'updated_at':    c.updated_at.isoformat() if c.updated_at else None,
    }


@cupones_bp.route('/', methods=['GET'])
def listar_cupones():
    solo_activos = request.args.get('activos', 'false').lower() == 'true'
    query = Cupon.query
    if solo_activos:
        query = query.filter_by(activo=True)
    cupones = query.order_by(Cupon.codigo).all()
    return jsonify([_serializar(c) for c in cupones]), 200


@cupones_bp.route('/<int:id_cupon>', methods=['GET'])
def obtener_cupon(id_cupon):
    cupon = Cupon.query.get_or_404(id_cupon)
    return jsonify(_serializar(cupon)), 200


@cupones_bp.route('/', methods=['POST'])
def crear_cupon():
    data = request.get_json()
    if not data or not data.get('codigo') or not data.get('tipo') or not data.get('descuento'):
        return jsonify({'error': 'codigo, tipo y descuento son obligatorios'}), 400

    if Cupon.query.filter_by(codigo=data['codigo'].upper()).first():
        return jsonify({'error': 'Ya existe un cupón con ese código'}), 409

    try:
        tipo = TipoCupon(data['tipo'])
    except ValueError:
        return jsonify({'error': f'Tipo inválido. Opciones: {[t.value for t in TipoCupon]}'}), 400

    nuevo = Cupon(
        codigo        = data['codigo'].upper(),
        tipo          = tipo,
        descuento     = data['descuento'],
        monto_minimo  = data.get('monto_minimo', 0),
        fecha_inicio  = data.get('fecha_inicio', date.today()),
        fecha_fin     = data.get('fecha_fin'),
        usos_maximos  = data.get('usos_maximos'),
        usos_actuales = 0,
        activo        = data.get('activo', True),
    )
    db.session.add(nuevo)
    db.session.commit()

    return jsonify({'mensaje': 'Cupón creado', 'id_cupon': nuevo.id_cupon, 'codigo': nuevo.codigo}), 201


@cupones_bp.route('/<int:id_cupon>', methods=['PUT'])
def actualizar_cupon(id_cupon):
    cupon = Cupon.query.get_or_404(id_cupon)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se enviaron datos'}), 400

    if 'codigo' in data and data['codigo'].upper() != cupon.codigo:
        if Cupon.query.filter_by(codigo=data['codigo'].upper()).first():
            return jsonify({'error': 'Ya existe un cupón con ese código'}), 409
        cupon.codigo = data['codigo'].upper()

    if 'tipo' in data:
        try:
            cupon.tipo = TipoCupon(data['tipo'])
        except ValueError:
            return jsonify({'error': f'Tipo inválido'}), 400

    campos = ['descuento', 'monto_minimo', 'fecha_inicio', 'fecha_fin', 'usos_maximos', 'usos_actuales', 'activo']
    for campo in campos:
        if campo in data:
            setattr(cupon, campo, data[campo])

    db.session.commit()
    return jsonify({'mensaje': 'Cupón actualizado', 'id_cupon': cupon.id_cupon}), 200


@cupones_bp.route('/<int:id_cupon>', methods=['DELETE'])
def eliminar_cupon(id_cupon):
    cupon = Cupon.query.get_or_404(id_cupon)
    cupon.activo = False
    db.session.commit()
    return jsonify({'mensaje': f'Cupón "{cupon.codigo}" desactivado'}), 200

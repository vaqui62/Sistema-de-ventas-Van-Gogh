from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.models import Pago, Pedido, MetodoPago, EstadoPago

pagos_bp = Blueprint('pagos', __name__, url_prefix='/api/pagos')


# ---------------------------------------------------------------
# HELPER: serializar pago
# ---------------------------------------------------------------
def _serializar(p):
    return {
        'id_pago':    p.id_pago,
        'id_pedido':  p.id_pedido,
        'metodo':     p.metodo.value,
        'estado':     p.estado.value,
        'monto':      float(p.monto),
        'fecha_pago': p.fecha_pago.isoformat(),
        'updated_at': p.updated_at.isoformat() if p.updated_at else None
    }


# ---------------------------------------------------------------
# GET /api/pagos — listar (filtro por pedido, estado)
# ---------------------------------------------------------------
@pagos_bp.route('/', methods=['GET'])
def listar_pagos():
    id_pedido  = request.args.get('pedido', type=int)
    estado_str = request.args.get('estado')

    query = Pago.query

    if id_pedido:
        query = query.filter_by(id_pedido=id_pedido)

    if estado_str:
        try:
            estado = EstadoPago(estado_str)
            query = query.filter_by(estado=estado)
        except ValueError:
            return jsonify({'error': f'Estado inválido. Opciones: {[e.value for e in EstadoPago]}'}), 400

    pagos = query.order_by(Pago.fecha_pago.desc()).all()
    return jsonify([_serializar(p) for p in pagos]), 200


# ---------------------------------------------------------------
# GET /api/pagos/<id> — obtener uno
# ---------------------------------------------------------------
@pagos_bp.route('/<int:id_pago>', methods=['GET'])
def obtener_pago(id_pago):
    pago = Pago.query.get_or_404(id_pago)
    return jsonify(_serializar(pago)), 200


# ---------------------------------------------------------------
# POST /api/pagos — crear un pago
# ---------------------------------------------------------------
@pagos_bp.route('/', methods=['POST'])
def crear_pago():
    data = request.get_json()

    if not data or not data.get('id_pedido') or not data.get('metodo') or not data.get('monto'):
        return jsonify({'error': 'id_pedido, metodo y monto son obligatorios'}), 400

    # Validar pedido
    pedido = Pedido.query.get(data['id_pedido'])
    if not pedido:
        return jsonify({'error': 'Pedido no encontrado'}), 404

    # Un pedido solo puede tener un pago (restricción UNIQUE en la DB)
    if Pago.query.filter_by(id_pedido=pedido.id_pedido).first():
        return jsonify({'error': 'Este pedido ya tiene un pago registrado'}), 409

    # Validar método de pago
    try:
        metodo = MetodoPago(data['metodo'])
    except ValueError:
        return jsonify({'error': f'Método inválido. Opciones: {[m.value for m in MetodoPago]}'}), 400

    # Validar monto positivo
    try:
        monto = float(data['monto'])
        if monto <= 0:
            return jsonify({'error': 'El monto debe ser mayor a 0'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'El monto debe ser un número válido'}), 400

    # Opcional: no debería superar el total del pedido (regla de negocio)
    if monto > float(pedido.total):
        return jsonify({'error': f'El monto ingresado ({monto}) supera el total del pedido ({pedido.total})'}), 400

    pago = Pago(
        id_pedido = pedido.id_pedido,
        metodo    = metodo,
        estado    = EstadoPago.pendiente,   # estado inicial
        monto     = monto
    )

    db.session.add(pago)
    db.session.commit()

    return jsonify({
        'mensaje':  'Pago registrado',
        'id_pago':  pago.id_pago,
        'estado':   pago.estado.value
    }), 201


# ---------------------------------------------------------------
# PUT /api/pagos/<id> — actualizar estado
# ---------------------------------------------------------------
@pagos_bp.route('/<int:id_pago>', methods=['PUT'])
def actualizar_pago(id_pago):
    pago = Pago.query.get_or_404(id_pago)
    data = request.get_json()

    if not data or 'estado' not in data:
        return jsonify({'error': 'Se requiere el campo "estado"'}), 400

    try:
        nuevo_estado = EstadoPago(data['estado'])
    except ValueError:
        return jsonify({'error': f'Estado inválido. Opciones: {[e.value for e in EstadoPago]}'}), 400

    # Reglas de transición simples (puedes personalizarlas)
    if pago.estado == EstadoPago.completado and nuevo_estado != EstadoPago.reembolsado:
        return jsonify({'error': 'Un pago completado solo puede pasar a reembolsado'}), 400
    if pago.estado == EstadoPago.reembolsado:
        return jsonify({'error': 'No se puede modificar un pago reembolsado'}), 400

    pago.estado = nuevo_estado
    db.session.commit()

    return jsonify({
        'mensaje': f'Estado del pago actualizado a "{nuevo_estado.value}"',
        'id_pago': pago.id_pago
    }), 200


# ---------------------------------------------------------------
# DELETE /api/pagos/<id> — no implementado (no se eliminan pagos)
# ---------------------------------------------------------------
# Podrías añadir un soft delete si quieres, pero no es necesario.
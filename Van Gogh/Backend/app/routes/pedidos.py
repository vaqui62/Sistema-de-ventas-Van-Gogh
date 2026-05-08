from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.models import (
    Pedido, DetallePedido, Variante, Cupon,
    Cliente, Direccion, EstadoPedido, Producto
)
from datetime import datetime, timezone

pedidos_bp = Blueprint('pedidos', __name__, url_prefix='/api/pedidos')


# ---------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------
def _serializar_pedido(p):
    """Serializa un pedido con sus detalles básicos."""
    return {
        'id_pedido':          p.id_pedido,
        'id_cliente':         p.id_cliente,
        'cliente_nombre':     f"{p.cliente.usuario.nombres} {p.cliente.usuario.apellido_1}" if p.cliente and p.cliente.usuario else "Desconocido",
        'cliente_email':      p.cliente.usuario.email if p.cliente and p.cliente.usuario else None,
        'id_cupon':           p.id_cupon,
        'id_direccion':       p.id_direccion,
        'direccion':          f"{p.direccion.calle} {p.direccion.numero_ext}, {p.direccion.ciudad}" if p.direccion else None,
        'estado':             p.estado.value,
        'subtotal':           float(p.subtotal),
        'descuento_aplicado': float(p.descuento_aplicado),
        'costo_envio':        float(p.costo_envio),
        'total':              float(p.total),
        'fecha_pedido':       p.fecha_pedido.isoformat(),
        'updated_at':         p.updated_at.isoformat() if p.updated_at else None,
        'detalles':           [_serializar_detalle(d) for d in p.detalles]
    }

def _serializar_detalle(d):
    return {
        'id_detalle':      d.id_detalle,
        'id_variante':     d.id_variante,
        'producto_nombre': d.variante.producto.nombre if d.variante and d.variante.producto else None,
        'talla':           d.variante.talla.value if d.variante else None,
        'color':           d.variante.color if d.variante else None,
        'cantidad':        d.cantidad,
        'precio_unitario': float(d.precio_unitario),
        'subtotal':        float(d.subtotal) if d.subtotal else None
    }


# ---------------------------------------------------------------
# GET /api/pedidos — listar todos (filtro: cliente, estado)
# ---------------------------------------------------------------
@pedidos_bp.route('/', methods=['GET'])
def listar_pedidos():
    id_cliente = request.args.get('cliente', type=int)
    estado_str = request.args.get('estado')

    query = Pedido.query

    if id_cliente:
        query = query.filter_by(id_cliente=id_cliente)

    if estado_str:
        try:
            estado = EstadoPedido(estado_str)
            query = query.filter_by(estado=estado)
        except ValueError:
            return jsonify({'error': f'Estado inválido. Opciones: {[e.value for e in EstadoPedido]}'}), 400

    pedidos = query.order_by(Pedido.fecha_pedido.desc()).all()
    return jsonify([_serializar_pedido(p) for p in pedidos]), 200


# ---------------------------------------------------------------
# GET /api/pedidos/<id> — obtener uno con detalle
# ---------------------------------------------------------------
@pedidos_bp.route('/<int:id_pedido>', methods=['GET'])
def obtener_pedido(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    return jsonify(_serializar_pedido(pedido)), 200


# ---------------------------------------------------------------
# POST /api/pedidos — crear un pedido
# ---------------------------------------------------------------
@pedidos_bp.route('/', methods=['POST'])
def crear_pedido():
    data = request.get_json()

    # Validación de campos requeridos
    if not data:
        return jsonify({'error': 'Se requiere un JSON con los datos del pedido'}), 400

    id_cliente   = data.get('id_cliente')
    id_direccion = data.get('id_direccion')
    id_cupon     = data.get('id_cupon')      # opcional
    costo_envio  = float(data.get('costo_envio', 0.0))
    items        = data.get('items', [])     # lista de {id_variante, cantidad}

    if not id_cliente or not id_direccion or not items:
        return jsonify({'error': 'id_cliente, id_direccion e items son obligatorios'}), 400

    # Validar cliente
    cliente = Cliente.query.get(id_cliente)
    if not cliente:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    if not cliente.usuario.activo:
        return jsonify({'error': 'El usuario asociado al cliente está inactivo'}), 403

    # Validar dirección (y que pertenezca al cliente)
    direccion = Direccion.query.get(id_direccion)
    if not direccion:
        return jsonify({'error': 'Dirección no encontrada'}), 404
    if direccion.id_cliente != id_cliente:
        return jsonify({'error': 'La dirección no pertenece al cliente indicado'}), 400

    # Validar items y calcular subtotal antes del descuento
    subtotal_general = 0.0
    detalles_a_insertar = []

    for item in items:
        id_variante = item.get('id_variante')
        cantidad = item.get('cantidad')

        if not id_variante or not cantidad:
            return jsonify({'error': 'Cada item debe tener id_variante y cantidad'}), 400
        if not isinstance(cantidad, int) or cantidad <= 0:
            return jsonify({'error': 'La cantidad debe ser un entero positivo'}), 400

        variante = Variante.query.get(id_variante)
        if not variante:
            return jsonify({'error': f'Variante {id_variante} no encontrada'}), 404
        if not variante.activa:
            return jsonify({'error': f'Variante {id_variante} está desactivada'}), 400
        if variante.stock < cantidad:
            return jsonify({'error': f'Stock insuficiente para variante {id_variante} (disponible: {variante.stock})'}), 409

        # Calcular precio unitario = precio base del producto + precio extra de la variante
        producto = variante.producto
        precio_unitario = float(producto.precio_base) + float(variante.precio_extra)
        subtotal_item = precio_unitario * cantidad
        subtotal_general += subtotal_item

        detalles_a_insertar.append({
            'id_variante':     variante.id_variante,
            'cantidad':        cantidad,
            'precio_unitario': precio_unitario
        })

    # Aplicar cupón si se envió
    descuento = 0.0
    cupon_obj = None
    if id_cupon:
        cupon_obj = Cupon.query.get(id_cupon)
        if not cupon_obj:
            return jsonify({'error': 'Cupón no encontrado'}), 404
        if not cupon_obj.activo:
            return jsonify({'error': 'Cupón inactivo'}), 400
        if cupon_obj.fecha_fin and cupon_obj.fecha_fin < datetime.now(timezone.utc).date():
            return jsonify({'error': 'Cupón vencido'}), 400
        if cupon_obj.usos_maximos and cupon_obj.usos_actuales >= cupon_obj.usos_maximos:
            return jsonify({'error': 'Cupón agotado'}), 400
        if subtotal_general < float(cupon_obj.monto_minimo):
            return jsonify({'error': f'El subtotal mínimo para usar este cupón es {cupon_obj.monto_minimo}'}), 400

        # Calcular descuento según tipo
        if cupon_obj.tipo.value == 'porcentaje':
            descuento = subtotal_general * (float(cupon_obj.descuento) / 100)
        elif cupon_obj.tipo.value == 'monto_fijo':
            descuento = float(cupon_obj.descuento)

        # Asegurar que no supere el subtotal
        descuento = min(descuento, subtotal_general)

    # Calcular total
    total = subtotal_general - descuento + costo_envio
    if total < 0:
        return jsonify({'error': 'El total no puede ser negativo'}), 400

    # Crear el pedido
    nuevo_pedido = Pedido(
        id_cliente         = id_cliente,
        id_cupon           = id_cupon,
        id_direccion       = id_direccion,
        estado             = EstadoPedido.pendiente,
        subtotal           = subtotal_general,
        descuento_aplicado = descuento,
        costo_envio        = costo_envio,
        total              = total
    )
    db.session.add(nuevo_pedido)
    db.session.flush()  # obtener id_pedido

    # Insertar detalles
    for detalle_data in detalles_a_insertar:
        detalle = DetallePedido(
            id_pedido       = nuevo_pedido.id_pedido,
            id_variante     = detalle_data['id_variante'],
            cantidad        = detalle_data['cantidad'],
            precio_unitario = detalle_data['precio_unitario']
            # subtotal se genera automáticamente por la DB
        )
        db.session.add(detalle)

    # Incrementar usos del cupón si se usó
    if cupon_obj:
        cupon_obj.usos_actuales += 1

    db.session.commit()

    return jsonify({
        'mensaje':    'Pedido creado exitosamente',
        'id_pedido':  nuevo_pedido.id_pedido,
        'total':      float(nuevo_pedido.total),
        'estado':     nuevo_pedido.estado.value
    }), 201


# ---------------------------------------------------------------
# PUT /api/pedidos/<id> — actualizar estado (sin lógica compleja)
# ---------------------------------------------------------------
@pedidos_bp.route('/<int:id_pedido>', methods=['PUT'])
def actualizar_estado(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    data = request.get_json()

    if not data or 'estado' not in data:
        return jsonify({'error': 'Se requiere el campo "estado"'}), 400

    try:
        nuevo_estado = EstadoPedido(data['estado'])
    except ValueError:
        return jsonify({'error': f'Estado inválido. Opciones: {[e.value for e in EstadoPedido]}'}), 400

    # Validar transiciones simples (ej: no permitir cancelar algo ya enviado)
    # Aquí puedes agregar reglas de negocio específicas si deseas.
    pedido.estado = nuevo_estado
    db.session.commit()

    return jsonify({
        'mensaje':   f'Estado del pedido actualizado a "{nuevo_estado.value}"',
        'id_pedido': pedido.id_pedido
    }), 200


# ---------------------------------------------------------------
# PATCH /api/pedidos/<id>/cancelar — cancelar pedido
# ---------------------------------------------------------------
@pedidos_bp.route('/<int:id_pedido>/cancelar', methods=['PATCH'])
def cancelar_pedido(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)

    if pedido.estado in (EstadoPedido.entregado, EstadoPedido.cancelado):
        return jsonify({'error': f'No se puede cancelar un pedido en estado "{pedido.estado.value}"'}), 400

    # Reponer stock (opcional, ya que el trigger no hace rollback automático)
    # Podemos iterar los detalles y sumar stock
    for detalle in pedido.detalles:
        variante = detalle.variante
        variante.stock += detalle.cantidad
        # No validamos stock porque estamos devolviendo

    pedido.estado = EstadoPedido.cancelado
    db.session.commit()

    return jsonify({'mensaje': f'Pedido {id_pedido} cancelado y stock repuesto'}), 200
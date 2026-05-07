from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.models import Variante, TallaRopa, Producto

variantes_bp = Blueprint('variantes', __name__, url_prefix='/api/variantes')


# ---------------------------------------------------------------
# HELPER: serializar variante
# ---------------------------------------------------------------
def _serializar(v):
    return {
        'id_variante':  v.id_variante,
        'id_producto':  v.id_producto,
        'producto':     v.producto.nombre if v.producto else None,
        'talla':        v.talla.value,
        'color':        v.color,
        'sku':          v.sku,
        'stock':        v.stock,
        'precio_extra': float(v.precio_extra),
        'activa':       v.activa,
        'created_at':   v.created_at.isoformat() if v.created_at else None,
        'updated_at':   v.updated_at.isoformat() if v.updated_at else None,
    }


# ---------------------------------------------------------------
# GET /api/variantes — listar (filtro opcional por producto, talla, color, activas)
# ---------------------------------------------------------------
@variantes_bp.route('/', methods=['GET'])
def listar_variantes():
    id_producto = request.args.get('producto', type=int)
    solo_activas = request.args.get('activas', 'false').lower() == 'true'
    talla = request.args.get('talla')
    color = request.args.get('color')

    query = Variante.query

    if id_producto:
        query = query.filter_by(id_producto=id_producto)
    if solo_activas:
        query = query.filter_by(activa=True)
    if talla:
        try:
            query = query.filter_by(talla=TallaRopa(talla))
        except ValueError:
            return jsonify({'error': f'Talla inválida. Opciones: {[t.value for t in TallaRopa]}'}), 400
    if color:
        query = query.filter(Variante.color.ilike(f'%{color}%'))

    variantes = query.order_by(Variante.id_producto, Variante.talla, Variante.color).all()
    return jsonify([_serializar(v) for v in variantes]), 200


# ---------------------------------------------------------------
# GET /api/variantes/<id> — obtener una
# ---------------------------------------------------------------
@variantes_bp.route('/<int:id_variante>', methods=['GET'])
def obtener_variante(id_variante):
    variante = Variante.query.get_or_404(id_variante)
    return jsonify(_serializar(variante)), 200


# ---------------------------------------------------------------
# POST /api/variantes — crear (debe enviarse id_producto, talla, color, sku, etc.)
# ---------------------------------------------------------------
@variantes_bp.route('/', methods=['POST'])
def crear_variante():
    data = request.get_json()

    campos_requeridos = ['id_producto', 'talla', 'color', 'sku']
    for campo in campos_requeridos:
        if not data or campo not in data:
            return jsonify({'error': f'El campo "{campo}" es obligatorio'}), 400

    # Validar que el producto existe
    producto = Producto.query.get(data['id_producto'])
    if not producto:
        return jsonify({'error': 'El producto indicado no existe'}), 404

    # Validar talla
    try:
        talla = TallaRopa(data['talla'])
    except ValueError:
        return jsonify({'error': f'Talla inválida. Opciones: {[t.value for t in TallaRopa]}'}), 400

    # Validar stock y precio_extra
    stock = data.get('stock', 0)
    if not isinstance(stock, int) or stock < 0:
        return jsonify({'error': 'El stock debe ser un entero no negativo'}), 400

    try:
        precio_extra = float(data.get('precio_extra', 0.0))
        if precio_extra < 0:
            return jsonify({'error': 'El precio extra no puede ser negativo'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'precio_extra debe ser un número válido'}), 400

    # Verificar unicidad de sku
    if Variante.query.filter_by(sku=data['sku']).first():
        return jsonify({'error': 'Ya existe una variante con ese SKU'}), 409

    # Verificar combinación única producto+talla+color
    if Variante.query.filter_by(
        id_producto=data['id_producto'],
        talla=talla,
        color=data['color']
    ).first():
        return jsonify({'error': 'Esa combinación de producto, talla y color ya existe'}), 409

    nueva = Variante(
        id_producto  = data['id_producto'],
        talla        = talla,
        color        = data['color'],
        sku          = data['sku'],
        stock        = stock,
        precio_extra = precio_extra,
        activa       = data.get('activa', True),
    )

    db.session.add(nueva)
    db.session.commit()

    return jsonify({
        'mensaje':     'Variante creada',
        'id_variante': nueva.id_variante,
        'sku':         nueva.sku,
    }), 201


# ---------------------------------------------------------------
# PUT /api/variantes/<id> — actualizar
# ---------------------------------------------------------------
@variantes_bp.route('/<int:id_variante>', methods=['PUT'])
def actualizar_variante(id_variante):
    variante = Variante.query.get_or_404(id_variante)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No se enviaron datos'}), 400

    # Validar producto si cambia
    if 'id_producto' in data and data['id_producto'] != variante.id_producto:
        if not Producto.query.get(data['id_producto']):
            return jsonify({'error': 'El nuevo producto no existe'}), 404

    # Validar talla
    if 'talla' in data:
        try:
            variante.talla = TallaRopa(data['talla'])
        except ValueError:
            return jsonify({'error': f'Talla inválida. Opciones: {[t.value for t in TallaRopa]}'}), 400

    # Validar stock
    if 'stock' in data:
        stock = data['stock']
        if not isinstance(stock, int) or stock < 0:
            return jsonify({'error': 'El stock debe ser un entero no negativo'}), 400
        variante.stock = stock

    # Validar precio_extra
    if 'precio_extra' in data:
        try:
            precio_extra = float(data['precio_extra'])
            if precio_extra < 0:
                return jsonify({'error': 'El precio extra no puede ser negativo'}), 400
            variante.precio_extra = precio_extra
        except (ValueError, TypeError):
            return jsonify({'error': 'precio_extra debe ser un número válido'}), 400

    # Validar unicidad del sku si cambia
    if 'sku' in data and data['sku'] != variante.sku:
        if Variante.query.filter_by(sku=data['sku']).first():
            return jsonify({'error': 'Ya existe una variante con ese SKU'}), 409
        variante.sku = data['sku']

    # Validar combinación única si cambian producto, talla o color
    if any(k in data for k in ('id_producto', 'talla', 'color')):
        producto_id = data.get('id_producto', variante.id_producto)
        talla = data.get('talla', variante.talla.value)
        color = data.get('color', variante.color)

        # Verificar que no exista otra variante con la misma combinación (excluyendo la actual)
        conflicto = Variante.query.filter(
            Variante.id_producto == producto_id,
            Variante.talla == talla,
            Variante.color == color,
            Variante.id_variante != id_variante
        ).first()
        if conflicto:
            return jsonify({'error': 'Esa combinación de producto, talla y color ya existe'}), 409

    # Campos simples
    if 'color' in data:
        variante.color = data['color']
    if 'activa' in data:
        variante.activa = data['activa']

    db.session.commit()

    return jsonify({'mensaje': 'Variante actualizada', 'id_variante': variante.id_variante}), 200


# ---------------------------------------------------------------
# DELETE /api/variantes/<id> — desactivar (soft delete)
# ---------------------------------------------------------------
@variantes_bp.route('/<int:id_variante>', methods=['DELETE'])
def desactivar_variante(id_variante):
    variante = Variante.query.get_or_404(id_variante)
    variante.activa = False
    db.session.commit()
    return jsonify({'mensaje': f'Variante {variante.sku} desactivada'}), 200
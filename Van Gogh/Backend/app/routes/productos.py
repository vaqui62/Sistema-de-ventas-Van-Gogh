from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.models import Producto, Categoria, PrecioHistorial
 
productos_bp = Blueprint('productos', __name__, url_prefix='/api/productos')
 
 
# GET /api/productos — listar todos
@productos_bp.route('/', methods=['GET'])
def listar_productos():
    # Filtros opcionales por query params
    id_categoria = request.args.get('categoria', type=int)
    solo_activos = request.args.get('activos', 'false').lower() == 'true'
    busqueda     = request.args.get('q', '').strip()
 
    query = Producto.query
 
    if id_categoria:
        query = query.filter_by(id_categoria=id_categoria)
    if solo_activos:
        query = query.filter_by(activo=True)
    if busqueda:
        query = query.filter(Producto.nombre.ilike(f'%{busqueda}%'))
 
    productos = query.order_by(Producto.nombre).all()
 
    return jsonify([_serializar(p) for p in productos]), 200
 
 
# GET /api/productos/<id> — obtener uno con variantes e imágenes
@productos_bp.route('/<int:id_producto>', methods=['GET'])
def obtener_producto(id_producto):
    producto = Producto.query.get_or_404(id_producto)
 
    return jsonify(_serializar(producto, detalle=True)), 200
 
 
# GET /api/productos/slug/<slug> — obtener por slug (útil para el frontend)
@productos_bp.route('/slug/<string:slug>', methods=['GET'])
def obtener_por_slug(slug):
    producto = Producto.query.filter_by(slug=slug).first_or_404()
 
    return jsonify(_serializar(producto, detalle=True)), 200
 
 
# POST /api/productos — crear
@productos_bp.route('/', methods=['POST'])
def crear_producto():
    data = request.get_json()
 
    campos_requeridos = ['nombre', 'slug', 'precio_base', 'id_categoria']
    for campo in campos_requeridos:
        if not data or campo not in data:
            return jsonify({'error': f'El campo "{campo}" es obligatorio'}), 400
 
    # Verificar que la categoría existe
    if not Categoria.query.get(data['id_categoria']):
        return jsonify({'error': 'La categoría indicada no existe'}), 404
 
    # Verificar slug único
    if Producto.query.filter_by(slug=data['slug']).first():
        return jsonify({'error': 'Ya existe un producto con ese slug'}), 409
 
    nuevo = Producto(
        id_categoria = data['id_categoria'],
        nombre       = data['nombre'],
        slug         = data['slug'],
        descripcion  = data.get('descripcion'),
        precio_base  = data['precio_base'],
        obra_vangogh = data.get('obra_vangogh'),
        anio_obra    = data.get('anio_obra'),
        activo       = data.get('activo', True),
    )
 
    db.session.add(nuevo)
    db.session.commit()
 
    return jsonify({
        'mensaje':     'Producto creado',
        'id_producto': nuevo.id_producto,
        'nombre':      nuevo.nombre,
        'slug':        nuevo.slug,
    }), 201
 
 
# PUT /api/productos/<id> — actualizar
@productos_bp.route('/<int:id_producto>', methods=['PUT'])
def actualizar_producto(id_producto):
    producto = Producto.query.get_or_404(id_producto)
    data = request.get_json()
 
    if not data:
        return jsonify({'error': 'No se enviaron datos'}), 400
 
    # Si cambia el precio, registrar en historial
    if 'precio_base' in data and float(data['precio_base']) != float(producto.precio_base):
        if not data.get('motivo_precio'):
            return jsonify({'error': 'Se requiere "motivo_precio" al cambiar el precio'}), 400
 
        historial = PrecioHistorial(
            id_producto     = producto.id_producto,
            id_usuario      = data.get('id_usuario'),  # quien hace el cambio
            precio_anterior = producto.precio_base,
            precio_nuevo    = data['precio_base'],
            motivo          = data['motivo_precio'],
        )
        db.session.add(historial)
        producto.precio_base = data['precio_base']
 
    if 'slug' in data and data['slug'] != producto.slug:
        if Producto.query.filter_by(slug=data['slug']).first():
            return jsonify({'error': 'Ya existe un producto con ese slug'}), 409
        producto.slug = data['slug']
 
    if 'id_categoria' in data:
        if not Categoria.query.get(data['id_categoria']):
            return jsonify({'error': 'La categoría indicada no existe'}), 404
        producto.id_categoria = data['id_categoria']
 
    campos_simples = ['nombre', 'descripcion', 'obra_vangogh', 'anio_obra', 'activo']
    for campo in campos_simples:
        if campo in data:
            setattr(producto, campo, data[campo])
 
    db.session.commit()
 
    return jsonify({'mensaje': 'Producto actualizado', 'id_producto': producto.id_producto}), 200
 
 
# DELETE /api/productos/<id> — desactivar (soft delete)
@productos_bp.route('/<int:id_producto>', methods=['DELETE'])
def desactivar_producto(id_producto):
    producto = Producto.query.get_or_404(id_producto)
 
    producto.activo = False
    db.session.commit()
 
    return jsonify({'mensaje': f'Producto "{producto.nombre}" desactivado'}), 200
 
 
# GET /api/productos/<id>/historial — historial de precios
@productos_bp.route('/<int:id_producto>/historial', methods=['GET'])
def historial_precios(id_producto):
    Producto.query.get_or_404(id_producto)  # valida que existe
 
    historial = PrecioHistorial.query\
        .filter_by(id_producto=id_producto)\
        .order_by(PrecioHistorial.fecha_cambio.desc())\
        .all()
 
    return jsonify([{
        'id_historial':    h.id_historial,
        'precio_anterior': float(h.precio_anterior) if h.precio_anterior else None,
        'precio_nuevo':    float(h.precio_nuevo),
        'motivo':          h.motivo,
        'fecha_cambio':    h.fecha_cambio.isoformat(),
        'id_usuario':      h.id_usuario,
    } for h in historial]), 200
@productos_bp.route('/historial', methods=['GET'])
def historial_global():
    historial = PrecioHistorial.query\
        .order_by(PrecioHistorial.fecha_cambio.desc())\
        .limit(50)\
        .all()
    return jsonify([{
        'id_historial': h.id_historial,
        'id_producto': h.id_producto,
        'precio_anterior': float(h.precio_anterior) if h.precio_anterior else None,
        'precio_nuevo': float(h.precio_nuevo),
        'motivo': h.motivo,
        'fecha_cambio': h.fecha_cambio.isoformat()
    } for h in historial]), 200
 
# =====================================
# HELPER: serializar producto
# =====================================
 
def _serializar(p, detalle=False):
    imagenes_lista = sorted(p.imagenes, key=lambda x: x.orden)
    data = {
        'id_producto':  p.id_producto,
        'id_categoria': p.id_categoria,
        'categoria':    p.categoria.nombre if p.categoria else None,
        'nombre':       p.nombre,
        'slug':         p.slug,
        'descripcion':  p.descripcion,
        'precio_base':  float(p.precio_base),
        'obra_vangogh': p.obra_vangogh,
        'anio_obra':    p.anio_obra,
        'activo':       p.activo,
        'created_at':   p.created_at.isoformat() if p.created_at else None,
        'imagenes': [{
            'id_imagen':    i.id_imagen,
            'url':          i.url,
            'alt_text':     i.alt_text,
            'orden':        i.orden,
            'es_principal': i.es_principal,
        } for i in imagenes_lista],
    }
 
    if detalle:
        data['variantes'] = [{
            'id_variante':  v.id_variante,
            'talla':        v.talla.value,
            'color':        v.color,
            'sku':          v.sku,
            'stock':        v.stock,
            'precio_extra': float(v.precio_extra),
            'activa':       v.activa,
        } for v in p.variantes]
 
    return data
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.models import Categoria
 
categorias_bp = Blueprint('categorias', __name__, url_prefix='/api/categorias')
 
 
# GET /api/categorias — listar todas
@categorias_bp.route('/', methods=['GET'])
def listar_categorias():
    solo_activas = request.args.get('activas', 'false').lower() == 'true'
 
    query = Categoria.query
    if solo_activas:
        query = query.filter_by(activa=True)
 
    categorias = query.order_by(Categoria.nombre).all()
 
    return jsonify([{
        'id_categoria': c.id_categoria,
        'nombre':       c.nombre,
        'slug':         c.slug,
        'descripcion':  c.descripcion,
        'activa':       c.activa,
        'created_at':   c.created_at.isoformat() if c.created_at else None,
    } for c in categorias]), 200
 
 
# GET /api/categorias/<id> — obtener una
@categorias_bp.route('/<int:id_categoria>', methods=['GET'])
def obtener_categoria(id_categoria):
    categoria = Categoria.query.get_or_404(id_categoria)
 
    return jsonify({
        'id_categoria': categoria.id_categoria,
        'nombre':       categoria.nombre,
        'slug':         categoria.slug,
        'descripcion':  categoria.descripcion,
        'activa':       categoria.activa,
        'created_at':   categoria.created_at.isoformat() if categoria.created_at else None,
        'updated_at':   categoria.updated_at.isoformat() if categoria.updated_at else None,
    }), 200
 
 
# POST /api/categorias — crear
@categorias_bp.route('/', methods=['POST'])
def crear_categoria():
    data = request.get_json()
 
    # Validar campos obligatorios
    if not data or not data.get('nombre') or not data.get('slug'):
        return jsonify({'error': 'nombre y slug son obligatorios'}), 400
 
    # Verificar que no existan duplicados
    if Categoria.query.filter_by(nombre=data['nombre']).first():
        return jsonify({'error': 'Ya existe una categoría con ese nombre'}), 409
 
    if Categoria.query.filter_by(slug=data['slug']).first():
        return jsonify({'error': 'Ya existe una categoría con ese slug'}), 409
 
    nueva = Categoria(
        nombre      = data['nombre'],
        slug        = data['slug'],
        descripcion = data.get('descripcion'),
        activa      = data.get('activa', True),
    )
 
    db.session.add(nueva)
    db.session.commit()
 
    return jsonify({
        'mensaje':      'Categoría creada',
        'id_categoria': nueva.id_categoria,
        'nombre':       nueva.nombre,
        'slug':         nueva.slug,
    }), 201
 
 
# PUT /api/categorias/<id> — actualizar
@categorias_bp.route('/<int:id_categoria>', methods=['PUT'])
def actualizar_categoria(id_categoria):
    categoria = Categoria.query.get_or_404(id_categoria)
    data = request.get_json()
 
    if not data:
        return jsonify({'error': 'No se enviaron datos'}), 400
 
    # Verificar duplicados solo si el valor cambió
    if 'nombre' in data and data['nombre'] != categoria.nombre:
        if Categoria.query.filter_by(nombre=data['nombre']).first():
            return jsonify({'error': 'Ya existe una categoría con ese nombre'}), 409
        categoria.nombre = data['nombre']
 
    if 'slug' in data and data['slug'] != categoria.slug:
        if Categoria.query.filter_by(slug=data['slug']).first():
            return jsonify({'error': 'Ya existe una categoría con ese slug'}), 409
        categoria.slug = data['slug']
 
    if 'descripcion' in data:
        categoria.descripcion = data['descripcion']
 
    if 'activa' in data:
        categoria.activa = data['activa']
 
    db.session.commit()
 
    return jsonify({'mensaje': 'Categoría actualizada', 'id_categoria': categoria.id_categoria}), 200
 
 
# DELETE /api/categorias/<id> — desactivar (soft delete)
@categorias_bp.route('/<int:id_categoria>', methods=['DELETE'])
def desactivar_categoria(id_categoria):
    categoria = Categoria.query.get_or_404(id_categoria)
 
    # Soft delete: no borramos el registro, solo desactivamos
    # (la DB tiene ON DELETE RESTRICT en productos, así que borrar físicamente fallaría si tiene productos)
    categoria.activa = False
    db.session.commit()
 
    return jsonify({'mensaje': f'Categoría "{categoria.nombre}" desactivada'}), 200
 
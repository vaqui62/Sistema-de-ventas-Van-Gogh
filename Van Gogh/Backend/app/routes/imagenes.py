import os
import uuid
from pathlib import Path
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.models import ProductoImagen, Producto

imagenes_bp = Blueprint('imagenes', __name__, url_prefix='/api/imagenes')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------
# HELPER: serializar imagen
# ---------------------------------------------------------------
def _serializar(i):
    return {
        'id_imagen':    i.id_imagen,
        'id_producto':  i.id_producto,
        'url':          i.url,
        'alt_text':     i.alt_text,
        'orden':        i.orden,
        'es_principal': i.es_principal,
        'created_at':   i.created_at.isoformat() if i.created_at else None,
    }


# ---------------------------------------------------------------
# GET /api/imagenes — listar (filtro opcional por producto)
# ---------------------------------------------------------------
@imagenes_bp.route('/', methods=['GET'])
def listar_imagenes():
    id_producto = request.args.get('producto', type=int)

    query = ProductoImagen.query

    if id_producto:
        query = query.filter_by(id_producto=id_producto)

    imagenes = query.order_by(ProductoImagen.id_producto, ProductoImagen.orden).all()
    return jsonify([_serializar(i) for i in imagenes]), 200


# ---------------------------------------------------------------
# GET /api/imagenes/<id> — obtener una
# ---------------------------------------------------------------
@imagenes_bp.route('/<int:id_imagen>', methods=['GET'])
def obtener_imagen(id_imagen):
    imagen = ProductoImagen.query.get_or_404(id_imagen)
    return jsonify(_serializar(imagen)), 200


# ---------------------------------------------------------------
# POST /api/imagenes — crear
# ---------------------------------------------------------------
@imagenes_bp.route('/', methods=['POST'])
def crear_imagen():
    data = request.get_json()

    # Validar campos obligatorios
    if not data or not data.get('id_producto') or not data.get('url'):
        return jsonify({'error': 'id_producto y url son obligatorios'}), 400

    # Verificar que el producto existe
    producto = Producto.query.get(data['id_producto'])
    if not producto:
        return jsonify({'error': 'El producto indicado no existe'}), 404

    # Validar orden (entero no negativo)
    orden = data.get('orden', 0)
    if not isinstance(orden, int) or orden < 0:
        return jsonify({'error': 'El orden debe ser un entero no negativo'}), 400

    # Validar es_principal
    es_principal = data.get('es_principal', False)
    if not isinstance(es_principal, bool):
        return jsonify({'error': 'es_principal debe ser booleano'}), 400

    # Si se marca como principal, desmarcar las demás del mismo producto
    if es_principal:
        ProductoImagen.query.filter_by(id_producto=data['id_producto']).update({'es_principal': False})
        db.session.flush()

    nueva = ProductoImagen(
        id_producto  = data['id_producto'],
        url          = data['url'],
        alt_text     = data.get('alt_text'),
        orden        = orden,
        es_principal = es_principal,
    )

    db.session.add(nueva)
    db.session.commit()

    return jsonify({
        'mensaje':   'Imagen creada',
        'id_imagen': nueva.id_imagen,
        'url':       nueva.url,
    }), 201


# ---------------------------------------------------------------
# PUT /api/imagenes/<id> — actualizar
# ---------------------------------------------------------------
@imagenes_bp.route('/<int:id_imagen>', methods=['PUT'])
def actualizar_imagen(id_imagen):
    imagen = ProductoImagen.query.get_or_404(id_imagen)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No se enviaron datos'}), 400

    # Verificar si cambia el producto (poco común pero lo permitimos)
    if 'id_producto' in data and data['id_producto'] != imagen.id_producto:
        if not Producto.query.get(data['id_producto']):
            return jsonify({'error': 'El nuevo producto no existe'}), 404
        imagen.id_producto = data['id_producto']

    if 'url' in data:
        if not data['url']:
            return jsonify({'error': 'La URL no puede estar vacía'}), 400
        imagen.url = data['url']

    if 'alt_text' in data:
        imagen.alt_text = data['alt_text']

    if 'orden' in data:
        orden = data['orden']
        if not isinstance(orden, int) or orden < 0:
            return jsonify({'error': 'El orden debe ser un entero no negativo'}), 400
        imagen.orden = orden

    if 'es_principal' in data:
        es_principal = data['es_principal']
        if not isinstance(es_principal, bool):
            return jsonify({'error': 'es_principal debe ser booleano'}), 400
        if es_principal and not imagen.es_principal:
            # Desmarcar otras principales del mismo producto
            ProductoImagen.query.filter_by(id_producto=imagen.id_producto).update({'es_principal': False})
            db.session.flush()
        imagen.es_principal = es_principal

    db.session.commit()

    return jsonify({'mensaje': 'Imagen actualizada', 'id_imagen': imagen.id_imagen}), 200


# ---------------------------------------------------------------
# DELETE /api/imagenes/<id> — eliminar físicamente
# ---------------------------------------------------------------
@imagenes_bp.route('/<int:id_imagen>', methods=['DELETE'])
def eliminar_imagen(id_imagen):
    imagen = ProductoImagen.query.get_or_404(id_imagen)
    # Borrar archivo físico si existe en uploads
    if imagen.url and '/uploads/' in imagen.url:
        try:
            ruta = Path(imagen.url.replace('/static/', str(current_app.static_folder.parent / 'static') + '/'))
            if ruta.exists():
                ruta.unlink()
        except Exception:
            pass
    db.session.delete(imagen)
    db.session.commit()
    return jsonify({'mensaje': f'Imagen {id_imagen} eliminada'}), 200


# ---------------------------------------------------------------
# POST /api/imagenes/subir — subir archivo de imagen
# ---------------------------------------------------------------
@imagenes_bp.route('/subir', methods=['POST'])
def subir_imagen():
    if 'imagen' not in request.files:
        return jsonify({'error': 'No se envió el archivo "imagen"'}), 400

    file = request.files['imagen']
    id_producto = request.form.get('id_producto', type=int)
    es_principal = request.form.get('es_principal', 'false').lower() == 'true'

    if not id_producto:
        return jsonify({'error': 'id_producto es obligatorio'}), 400

    producto = Producto.query.get(id_producto)
    if not producto:
        return jsonify({'error': 'El producto no existe'}), 404

    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Archivo inválido. Extensiones permitidas: png, jpg, jpeg, gif, webp'}), 400

    upload_dir = Path(current_app.root_path) / 'static' / 'uploads'
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = file.filename.rsplit('.', 1)[1].lower()
    nombre_unico = f"{uuid.uuid4().hex}_{id_producto}.{ext}"
    filepath = upload_dir / nombre_unico
    file.save(str(filepath))

    url = f"/static/uploads/{nombre_unico}"
    alt_text = request.form.get('alt_text', producto.nombre)

    if es_principal:
        ProductoImagen.query.filter_by(id_producto=id_producto).update({'es_principal': False})
        db.session.flush()

    nueva = ProductoImagen(
        id_producto=id_producto,
        url=url,
        alt_text=alt_text,
        orden=request.form.get('orden', 0, type=int),
        es_principal=es_principal,
    )
    db.session.add(nueva)
    db.session.commit()

    return jsonify({
        'mensaje': 'Imagen subida correctamente',
        'id_imagen': nueva.id_imagen,
        'url': url,
    }), 201
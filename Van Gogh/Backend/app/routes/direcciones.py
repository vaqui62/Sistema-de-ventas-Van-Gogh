from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.models import Direccion, TipoDireccion, Cliente

direcciones_bp = Blueprint('direcciones', __name__, url_prefix='/api/direcciones')

def _serializar(d):
    return {
        'id_direccion':        d.id_direccion,
        'id_cliente':          d.id_cliente,
        'tipo':                d.tipo.value,
        'nombre_destinatario': d.nombre_destinatario,
        'calle':               d.calle,
        'numero_ext':          d.numero_ext,
        'ciudad':              d.ciudad,
        'estado':              d.estado,
        'pais':                d.pais,
        'codigo_postal':       d.codigo_postal,
        'es_predeterminada':   d.es_predeterminada
    }

@direcciones_bp.route('/', methods=['GET'])
def listar():
    id_cliente = request.args.get('cliente', type=int)
    query = Direccion.query
    if id_cliente:
        query = query.filter_by(id_cliente=id_cliente)
    direcciones = query.all()
    return jsonify([_serializar(d) for d in direcciones]), 200

@direcciones_bp.route('/<int:id>', methods=['GET'])
def obtener(id):
    d = Direccion.query.get_or_404(id)
    return jsonify(_serializar(d)), 200

@direcciones_bp.route('/', methods=['POST'])
def crear():
    data = request.get_json()
    if not data or not data.get('id_cliente') or not data.get('nombre_destinatario') or not data.get('calle') or not data.get('ciudad') or not data.get('codigo_postal'):
        return jsonify({'error': 'Faltan campos obligatorios'}), 400
    cliente = Cliente.query.get(data['id_cliente'])
    if not cliente:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    if 'tipo' in data:
        try:
            tipo = TipoDireccion(data['tipo'])
        except ValueError:
            return jsonify({'error': f'Tipo inválido. Opciones: {[t.value for t in TipoDireccion]}'}), 400
    else:
        tipo = TipoDireccion.Casa

    nueva = Direccion(
        id_cliente          = data['id_cliente'],
        tipo                = tipo,
        nombre_destinatario = data['nombre_destinatario'],
        calle               = data['calle'],
        numero_ext          = data.get('numero_ext', ''),
        ciudad              = data['ciudad'],
        estado              = data.get('estado', ''),
        codigo_postal       = data['codigo_postal'],
        pais                = data.get('pais', 'Mexico'),
        es_predeterminada   = data.get('es_predeterminada', False)
    )
    db.session.add(nueva)
    db.session.commit()
    return jsonify({'mensaje': 'Dirección creada', 'id_direccion': nueva.id_direccion}), 201

# También podrías añadir PUT y DELETE si necesitas.
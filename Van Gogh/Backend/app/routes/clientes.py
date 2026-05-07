from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.models import Cliente, UsuarioRol

clientes_bp = Blueprint('clientes', __name__, url_prefix='/api/clientes')


# ---------------------------------------------------------------
# GET /api/clientes — listar todos (útil para admin)
# ---------------------------------------------------------------
@clientes_bp.route('/', methods=['GET'])
def listar_clientes():
    clientes = Cliente.query.all()
    return jsonify([{
        'id_cliente': c.id_cliente,
        'id_usuario': c.id_usuario,
        'email': c.usuario.email,
        'nombres': c.usuario.nombres,
        'telefono': c.telefono,
        'puntos_fidelidad': c.puntos_fidelidad,
        'acepta_marketing': c.acepta_marketing,
        'fecha_registro': c.fecha_registro.isoformat() if c.fecha_registro else None
    } for c in clientes]), 200


# ---------------------------------------------------------------
# GET /api/clientes/<id> — obtener un cliente por su ID
# ---------------------------------------------------------------
@clientes_bp.route('/<int:id_cliente>', methods=['GET'])
def obtener_cliente(id_cliente):
    cliente = Cliente.query.get_or_404(id_cliente)
    return jsonify({
        'id_cliente': cliente.id_cliente,
        'id_usuario': cliente.id_usuario,
        'email': cliente.usuario.email,
        'nombres': cliente.usuario.nombres,
        'telefono': cliente.telefono,
        'puntos_fidelidad': cliente.puntos_fidelidad,
        'acepta_marketing': cliente.acepta_marketing,
        'fecha_registro': cliente.fecha_registro.isoformat() if cliente.fecha_registro else None
    }), 200


# ---------------------------------------------------------------
# GET /api/clientes/usuario/<id_usuario> — obtener cliente por ID de usuario
# (Para carrito y otras funcionalidades)
# ---------------------------------------------------------------
@clientes_bp.route('/usuario/<int:id_usuario>', methods=['GET'])
def cliente_por_usuario(id_usuario):
    cliente = Cliente.query.filter_by(id_usuario=id_usuario).first_or_404()
    return jsonify({
        'id_cliente': cliente.id_cliente,
        'id_usuario': cliente.id_usuario,
        'email': cliente.usuario.email,
        'nombres': cliente.usuario.nombres,
        'telefono': cliente.telefono
    }), 200


# ---------------------------------------------------------------
# PUT /api/clientes/<id> — actualizar datos del cliente
# ---------------------------------------------------------------
@clientes_bp.route('/<int:id_cliente>', methods=['PUT'])
def actualizar_cliente(id_cliente):
    cliente = Cliente.query.get_or_404(id_cliente)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se enviaron datos'}), 400

    if 'telefono' in data:
        cliente.telefono = data['telefono']
    if 'acepta_marketing' in data:
        cliente.acepta_marketing = data['acepta_marketing']
    if 'puntos_fidelidad' in data:
        cliente.puntos_fidelidad = data['puntos_fidelidad']

    db.session.commit()
    return jsonify({'mensaje': 'Cliente actualizado'}), 200
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models.models import UsuarioRol, Cliente, RolUsuario

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/api/usuarios')


# ---------------------------------------------------------------
# HELPER: serializar usuario (sin exponer password_hash)
# ---------------------------------------------------------------
def _serializar(u):
    return {
        'id_usuario': u.id_usuario,
        'nombres':    u.nombres,
        'apellido_1': u.apellido_1,
        'apellido_2': u.apellido_2,
        'email':      u.email,
        'rol':        u.rol.value,
        'activo':     u.activo,
        'creado_por': u.creado_por,
        'created_at': u.created_at.isoformat() if u.created_at else None,
        'updated_at': u.updated_at.isoformat() if u.updated_at else None,
    }


# ---------------------------------------------------------------
# GET /api/usuarios — listar todos
# ---------------------------------------------------------------
@usuarios_bp.route('/', methods=['GET'])
def listar_usuarios():
    rol      = request.args.get('rol')       # filtrar por rol
    activos  = request.args.get('activos', 'false').lower() == 'true'
    busqueda = request.args.get('q', '').strip()

    query = UsuarioRol.query

    if rol:
        try:
            query = query.filter_by(rol=RolUsuario(rol))
        except ValueError:
            return jsonify({'error': f'Rol inválido. Opciones: {[r.value for r in RolUsuario]}'}), 400

    if activos:
        query = query.filter_by(activo=True)

    if busqueda:
        query = query.filter(
            UsuarioRol.email.ilike(f'%{busqueda}%') |
            UsuarioRol.nombres.ilike(f'%{busqueda}%')
        )

    usuarios = query.order_by(UsuarioRol.nombres).all()

    return jsonify([_serializar(u) for u in usuarios]), 200


# ---------------------------------------------------------------
# GET /api/usuarios/<id> — obtener uno
# ---------------------------------------------------------------
@usuarios_bp.route('/<int:id_usuario>', methods=['GET'])
def obtener_usuario(id_usuario):
    usuario = UsuarioRol.query.get_or_404(id_usuario)
    return jsonify(_serializar(usuario)), 200


# ---------------------------------------------------------------
# POST /api/usuarios — crear usuario (y cliente si es comprador)
# ---------------------------------------------------------------
@usuarios_bp.route('/', methods=['POST'])
def crear_usuario():
    data = request.get_json()

    campos_requeridos = ['nombres', 'apellido_1', 'email', 'password']
    for campo in campos_requeridos:
        if not data or campo not in data or not data[campo]:
            return jsonify({'error': f'El campo "{campo}" es obligatorio'}), 400

    # Verificar email único
    if UsuarioRol.query.filter_by(email=data['email'].lower().strip()).first():
        return jsonify({'error': 'Ya existe un usuario con ese email'}), 409

    # Validar rol si se envía
    rol = RolUsuario.comprador  # por defecto
    if 'rol' in data:
        try:
            rol = RolUsuario(data['rol'])
        except ValueError:
            return jsonify({'error': f'Rol inválido. Opciones: {[r.value for r in RolUsuario]}'}), 400

    # Crear el usuario
    nuevo = UsuarioRol(
        nombres       = data['nombres'],
        apellido_1    = data['apellido_1'],
        apellido_2    = data.get('apellido_2'),
        email         = data['email'].lower().strip(),
        password_hash = generate_password_hash(data['password']),
        rol           = rol,
        activo        = data.get('activo', True),
        creado_por    = data.get('creado_por'),
    )

    db.session.add(nuevo)
    db.session.flush()  # obtener id_usuario antes del commit

    # Si es comprador, crear cliente automáticamente
    if rol == RolUsuario.comprador:
        cliente = Cliente(
            id_usuario       = nuevo.id_usuario,
            telefono         = data.get('telefono'),
            acepta_marketing = data.get('acepta_marketing', False)
        )
        db.session.add(cliente)

    db.session.commit()

    return jsonify({
        'mensaje':    'Usuario creado',
        'id_usuario': nuevo.id_usuario,
        'email':      nuevo.email,
        'rol':        nuevo.rol.value,
    }), 201


# ---------------------------------------------------------------
# PUT /api/usuarios/<id> — actualizar
# ---------------------------------------------------------------
@usuarios_bp.route('/<int:id_usuario>', methods=['PUT'])
def actualizar_usuario(id_usuario):
    usuario = UsuarioRol.query.get_or_404(id_usuario)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No se enviaron datos'}), 400

    if 'email' in data and data['email'].lower().strip() != usuario.email:
        if UsuarioRol.query.filter_by(email=data['email'].lower().strip()).first():
            return jsonify({'error': 'Ya existe un usuario con ese email'}), 409
        usuario.email = data['email'].lower().strip()

    if 'rol' in data:
        try:
            usuario.rol = RolUsuario(data['rol'])
        except ValueError:
            return jsonify({'error': f'Rol inválido. Opciones: {[r.value for r in RolUsuario]}'}), 400

    campos_simples = ['nombres', 'apellido_1', 'apellido_2', 'activo']
    for campo in campos_simples:
        if campo in data:
            setattr(usuario, campo, data[campo])

    db.session.commit()

    return jsonify({'mensaje': 'Usuario actualizado', 'id_usuario': usuario.id_usuario}), 200


# ---------------------------------------------------------------
# PATCH /api/usuarios/<id>/password — cambiar contraseña
# ---------------------------------------------------------------
@usuarios_bp.route('/<int:id_usuario>/password', methods=['PATCH'])
def cambiar_password(id_usuario):
    usuario = UsuarioRol.query.get_or_404(id_usuario)
    data = request.get_json()

    if not data or not data.get('password_actual') or not data.get('password_nueva'):
        return jsonify({'error': 'Se requiere "password_actual" y "password_nueva"'}), 400

    if not check_password_hash(usuario.password_hash, data['password_actual']):
        return jsonify({'error': 'La contraseña actual es incorrecta'}), 401

    if len(data['password_nueva']) < 8:
        return jsonify({'error': 'La nueva contraseña debe tener al menos 8 caracteres'}), 400

    usuario.password_hash = generate_password_hash(data['password_nueva'])
    db.session.commit()

    return jsonify({'mensaje': 'Contraseña actualizada'}), 200


# ---------------------------------------------------------------
# DELETE /api/usuarios/<id> — desactivar (soft delete)
# ---------------------------------------------------------------
@usuarios_bp.route('/<int:id_usuario>', methods=['DELETE'])
def desactivar_usuario(id_usuario):
    usuario = UsuarioRol.query.get_or_404(id_usuario)

    usuario.activo = False
    db.session.commit()

    return jsonify({'mensaje': f'Usuario "{usuario.email}" desactivado'}), 200


# ---------------------------------------------------------------
# POST /api/usuarios/login — verificar credenciales (sin token aún)
# ---------------------------------------------------------------
@usuarios_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'email y password son obligatorios'}), 400

    usuario = UsuarioRol.query.filter_by(email=data['email'].lower().strip()).first()

    if not usuario or not check_password_hash(usuario.password_hash, data['password']):
        return jsonify({'error': 'Credenciales incorrectas'}), 401

    if not usuario.activo:
        return jsonify({'error': 'Usuario inactivo'}), 403

    return jsonify({
        'mensaje':    'Login exitoso',
        'id_usuario': usuario.id_usuario,
        'email':      usuario.email,
        'rol':        usuario.rol.value,
        'nombres':    usuario.nombres,
    }), 200
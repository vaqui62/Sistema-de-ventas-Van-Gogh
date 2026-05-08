import enum
from datetime import datetime, date, timezone
from app.extensions import db
from sqlalchemy import Computed, CheckConstraint

# =====================================
# FUNCIÓN AUXILIAR
# =====================================
def ahora_utc():
    """Retorna la fecha/hora actual con zona horaria UTC."""
    return datetime.now(timezone.utc)

# =====================================
# ENUMS
# =====================================
class RolUsuario(enum.Enum):
    gerente   = 'gerente'
    empleado  = 'empleado'
    comprador = 'comprador'

class TallaRopa(enum.Enum):
    XS = 'XS'
    S  = 'S'
    M  = 'M'
    L  = 'L'
    X  = 'X'
    XL = 'XL'

class TipoDireccion(enum.Enum):
    Casa    = 'Casa'
    Oficina = 'Oficina'
    Regalo  = 'Regalo'
    Otro    = 'Otro'

class TipoCupon(enum.Enum):
    porcentaje = 'porcentaje'
    monto_fijo = 'monto_fijo'

class EstadoPedido(enum.Enum):
    pendiente  = 'pendiente'
    confirmado = 'confirmado'
    enviado    = 'enviado'
    entregado  = 'entregado'
    cancelado  = 'cancelado'

class MetodoPago(enum.Enum):
    tarjeta_credito = 'tarjeta_credito'
    tarjeta_debito  = 'tarjeta_debito'
    transferencia   = 'transferencia'
    efectivo        = 'efectivo'
    paypal          = 'paypal'

class EstadoPago(enum.Enum):
    pendiente   = 'pendiente'
    completado  = 'completado'
    fallido     = 'fallido'
    reembolsado = 'reembolsado'

# =====================================
# MODELO: UsuarioRol
# =====================================
class UsuarioRol(db.Model):
    __tablename__ = 'usuarios_roles'

    id_usuario    = db.Column(db.Integer, primary_key=True)
    nombres       = db.Column(db.String(100), nullable=False)
    apellido_1    = db.Column(db.String(50),  nullable=False)
    apellido_2    = db.Column(db.String(50))
    email         = db.Column(db.String(150), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.Text,        nullable=False)
    rol           = db.Column(db.Enum(RolUsuario, name='rol_usuario'), nullable=False, default=RolUsuario.comprador)
    activo        = db.Column(db.Boolean,     nullable=False, default=True)
    creado_por    = db.Column(db.Integer,     db.ForeignKey('usuarios_roles.id_usuario', ondelete='SET NULL'))
    created_at    = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc)
    updated_at    = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc, onupdate=ahora_utc)

    creador = db.relationship(
        'UsuarioRol',
        remote_side=[id_usuario],
        backref=db.backref('creados', lazy='dynamic')
    )
    cliente           = db.relationship('Cliente', back_populates='usuario', uselist=False)
    historial_precios = db.relationship('PrecioHistorial', back_populates='usuario')

    def __repr__(self):
        return f'<UsuarioRol {self.email} [{self.rol.value}]>'

# =====================================
# MODELO: Categoria
# =====================================
class Categoria(db.Model):
    __tablename__ = 'categorias'

    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre       = db.Column(db.String(80), nullable=False, unique=True)
    slug         = db.Column(db.String(80), nullable=False, unique=True)
    descripcion  = db.Column(db.Text)
    activa       = db.Column(db.Boolean, nullable=False, default=True)
    created_at   = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc)
    updated_at   = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc, onupdate=ahora_utc)

    productos = db.relationship('Producto', back_populates='categoria')

    def __repr__(self):
        return f'<Categoria {self.nombre}>'

# =====================================
# MODELO: Producto
# =====================================
class Producto(db.Model):
    __tablename__ = 'productos'

    id_producto  = db.Column(db.Integer, primary_key=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id_categoria', ondelete='RESTRICT'), nullable=False)
    nombre       = db.Column(db.String(150), nullable=False)
    slug         = db.Column(db.String(150), nullable=False, unique=True)
    descripcion  = db.Column(db.Text)
    precio_base  = db.Column(db.Numeric(10, 2), CheckConstraint('precio_base >= 0'), nullable=False)
    obra_vangogh = db.Column(db.String(120))
    anio_obra    = db.Column(db.SmallInteger, CheckConstraint('anio_obra BETWEEN 1800 AND 2100'))
    activo       = db.Column(db.Boolean, nullable=False, default=True)
    created_at   = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc)
    updated_at   = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc, onupdate=ahora_utc)

    categoria         = db.relationship('Categoria', back_populates='productos')
    variantes         = db.relationship('Variante', back_populates='producto', cascade='all, delete-orphan')
    imagenes          = db.relationship('ProductoImagen', back_populates='producto', cascade='all, delete-orphan')
    historial_precios = db.relationship('PrecioHistorial', back_populates='producto')

    def __repr__(self):
        return f'<Producto {self.nombre}>'

# =====================================
# MODELO: Variante
# =====================================
class Variante(db.Model):
    __tablename__ = 'variantes'
    __table_args__ = (
        db.UniqueConstraint('id_producto', 'talla', 'color', name='uq_variante_producto_talla_color'),
    )

    id_variante  = db.Column(db.Integer, primary_key=True)
    id_producto  = db.Column(db.Integer, db.ForeignKey('productos.id_producto', ondelete='CASCADE'), nullable=False)
    talla        = db.Column(db.Enum(TallaRopa, name='talla_ropa'), nullable=False)
    color        = db.Column(db.String(60), nullable=False)
    sku          = db.Column(db.String(60), nullable=False, unique=True)
    stock        = db.Column(db.Integer, CheckConstraint('stock >= 0'), nullable=False, default=0)
    precio_extra = db.Column(db.Numeric(10, 2), CheckConstraint('precio_extra >= 0'), nullable=False, default=0.00)
    activa       = db.Column(db.Boolean,    nullable=False, default=True)
    created_at   = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc)
    updated_at   = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc, onupdate=ahora_utc)

    producto        = db.relationship('Producto', back_populates='variantes')
    detalles_pedido = db.relationship('DetallePedido', back_populates='variante')

    def __repr__(self):
        return f'<Variante {self.sku} | {self.talla.value} {self.color}>'

# =====================================
# MODELO: ProductoImagen
# =====================================
class ProductoImagen(db.Model):
    __tablename__ = 'producto_imagenes'

    id_imagen    = db.Column(db.Integer, primary_key=True)
    id_producto  = db.Column(db.Integer, db.ForeignKey('productos.id_producto', ondelete='CASCADE'), nullable=False)
    url          = db.Column(db.Text,         nullable=False)
    alt_text     = db.Column(db.String(200))
    orden        = db.Column(db.SmallInteger, CheckConstraint('orden >= 0'), nullable=False, default=0)
    es_principal = db.Column(db.Boolean,      nullable=False, default=False)
    created_at   = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc)

    producto = db.relationship('Producto', back_populates='imagenes')

    def __repr__(self):
        return f'<ProductoImagen {self.id_imagen} - Producto {self.id_producto}>'

# =====================================
# MODELO: Cliente
# =====================================
class Cliente(db.Model):
    __tablename__ = 'clientes'

    id_cliente       = db.Column(db.Integer, primary_key=True)
    id_usuario       = db.Column(db.Integer, db.ForeignKey('usuarios_roles.id_usuario', ondelete='CASCADE'), nullable=False, unique=True)
    telefono         = db.Column(db.String(20))
    fecha_nacimiento = db.Column(db.Date)
    genero           = db.Column(db.String(30))
    acepta_marketing = db.Column(db.Boolean, nullable=False, default=False)
    puntos_fidelidad = db.Column(db.Integer, CheckConstraint('puntos_fidelidad >= 0'), nullable=False, default=0)
    fecha_registro   = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc)
    updated_at       = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc, onupdate=ahora_utc)

    usuario     = db.relationship('UsuarioRol', back_populates='cliente')
    direcciones = db.relationship('Direccion', back_populates='cliente', cascade='all, delete-orphan')
    pedidos     = db.relationship('Pedido', back_populates='cliente')

    def __repr__(self):
        return f'<Cliente {self.id_cliente} - Usuario {self.id_usuario}>'

# =====================================
# MODELO: Direccion
# =====================================
class Direccion(db.Model):
    __tablename__ = 'direcciones'

    id_direccion        = db.Column(db.Integer, primary_key=True)
    id_cliente          = db.Column(db.Integer, db.ForeignKey('clientes.id_cliente', ondelete='CASCADE'), nullable=False)
    tipo                = db.Column(db.Enum(TipoDireccion, name='tipo_direccion'), nullable=False, default=TipoDireccion.Casa)
    nombre_destinatario = db.Column(db.String(120), nullable=False)
    calle               = db.Column(db.String(200), nullable=False)
    numero_ext          = db.Column(db.String(20),  nullable=False)
    ciudad              = db.Column(db.String(100), nullable=False)
    estado              = db.Column(db.String(80),  nullable=False)
    pais                = db.Column(db.String(60),  nullable=False, default='Mexico')
    codigo_postal       = db.Column(db.String(10),  nullable=False)
    es_predeterminada   = db.Column(db.Boolean,     nullable=False, default=False)
    updated_at          = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc, onupdate=ahora_utc)

    cliente = db.relationship('Cliente', back_populates='direcciones')
    pedidos = db.relationship('Pedido', back_populates='direccion')

    def __repr__(self):
        return f'<Direccion {self.tipo.value} - {self.ciudad}>'

# =====================================
# MODELO: Cupon
# =====================================
class Cupon(db.Model):
    __tablename__ = 'cupones'

    id_cupon      = db.Column(db.Integer, primary_key=True)
    codigo        = db.Column(db.String(30), nullable=False, unique=True)
    tipo          = db.Column(db.Enum(TipoCupon, name='tipo_cupon'), nullable=False)
    descuento     = db.Column(db.Numeric(10, 2), CheckConstraint('descuento > 0'), nullable=False)
    monto_minimo  = db.Column(db.Numeric(10, 2), default=0)
    fecha_inicio  = db.Column(db.Date, default=date.today)
    fecha_fin     = db.Column(db.Date)
    usos_maximos  = db.Column(db.Integer)
    usos_actuales = db.Column(db.Integer, nullable=False, default=0)
    activo        = db.Column(db.Boolean, nullable=False, default=True)
    updated_at    = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc, onupdate=ahora_utc)

    pedidos = db.relationship('Pedido', back_populates='cupon')

    def __repr__(self):
        return f'<Cupon {self.codigo} [{self.tipo.value}]>'

# =====================================
# MODELO: Pedido
# =====================================
class Pedido(db.Model):
    __tablename__ = 'pedidos'

    id_pedido          = db.Column(db.Integer, primary_key=True)
    id_cliente         = db.Column(db.Integer, db.ForeignKey('clientes.id_cliente'), nullable=False)
    id_cupon           = db.Column(db.Integer, db.ForeignKey('cupones.id_cupon'))
    id_direccion       = db.Column(db.Integer, db.ForeignKey('direcciones.id_direccion'), nullable=False)
    estado             = db.Column(db.Enum(EstadoPedido, name='estado_pedido'), nullable=False, default=EstadoPedido.pendiente)
    subtotal           = db.Column(db.Numeric(10, 2), CheckConstraint('subtotal >= 0'), nullable=False)
    descuento_aplicado = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    costo_envio        = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    total              = db.Column(db.Numeric(10, 2), CheckConstraint('total >= 0'), nullable=False)
    fecha_pedido       = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc)
    updated_at         = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc, onupdate=ahora_utc)

    cliente   = db.relationship('Cliente',   back_populates='pedidos')
    cupon     = db.relationship('Cupon',     back_populates='pedidos')
    direccion = db.relationship('Direccion', back_populates='pedidos')
    detalles  = db.relationship('DetallePedido', back_populates='pedido', cascade='all, delete-orphan')
    pago      = db.relationship('Pago', back_populates='pedido', uselist=False)

    def __repr__(self):
        return f'<Pedido {self.id_pedido} [{self.estado.value}]>'

# =====================================
# MODELO: DetallePedido
# =====================================
class DetallePedido(db.Model):
    __tablename__ = 'detalle_pedido'

    id_detalle      = db.Column(db.Integer, primary_key=True)
    id_pedido       = db.Column(db.Integer, db.ForeignKey('pedidos.id_pedido', ondelete='CASCADE'), nullable=False)
    id_variante     = db.Column(db.Integer, db.ForeignKey('variantes.id_variante'), nullable=False)
    cantidad        = db.Column(db.Integer, CheckConstraint('cantidad > 0'), nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    # Columna generada por PostgreSQL, solo lectura
    subtotal        = db.Column(db.Numeric(10, 2), Computed(None, persisted=True))

    pedido   = db.relationship('Pedido',   back_populates='detalles')
    variante = db.relationship('Variante', back_populates='detalles_pedido')

    def __repr__(self):
        return f'<DetallePedido pedido={self.id_pedido} variante={self.id_variante} x{self.cantidad}>'

# =====================================
# MODELO: Pago
# =====================================
class Pago(db.Model):
    __tablename__ = 'pagos'

    id_pago    = db.Column(db.Integer, primary_key=True)
    id_pedido  = db.Column(db.Integer, db.ForeignKey('pedidos.id_pedido'), nullable=False, unique=True)
    metodo     = db.Column(db.Enum(MetodoPago, name='metodo_pago'), nullable=False)
    estado     = db.Column(db.Enum(EstadoPago, name='estado_pago'), nullable=False, default=EstadoPago.pendiente)
    monto      = db.Column(db.Numeric(10, 2), CheckConstraint('monto > 0'), nullable=False)
    fecha_pago = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc, onupdate=ahora_utc)

    pedido = db.relationship('Pedido', back_populates='pago')

    def __repr__(self):
        return f'<Pago {self.id_pago} [{self.estado.value}] ${self.monto}>'

# =====================================
# MODELO: PrecioHistorial
# =====================================
class PrecioHistorial(db.Model):
    __tablename__ = 'precio_historial'

    id_historial    = db.Column(db.Integer, primary_key=True)
    id_producto     = db.Column(db.Integer, db.ForeignKey('productos.id_producto'))
    id_usuario      = db.Column(db.Integer, db.ForeignKey('usuarios_roles.id_usuario'))
    precio_anterior = db.Column(db.Numeric(10, 2))
    precio_nuevo    = db.Column(db.Numeric(10, 2), nullable=False)
    motivo          = db.Column(db.Text, nullable=False)
    fecha_cambio    = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora_utc)

    producto = db.relationship('Producto', back_populates='historial_precios')
    usuario  = db.relationship('UsuarioRol', back_populates='historial_precios')

    def __repr__(self):
        return f'<PrecioHistorial producto={self.id_producto} {self.precio_anterior}->{self.precio_nuevo}>'
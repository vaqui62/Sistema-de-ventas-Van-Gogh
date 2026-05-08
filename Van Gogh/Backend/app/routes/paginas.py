from flask import Blueprint, render_template

paginas_bp = Blueprint('paginas', __name__)

@paginas_bp.route('/')
def index():
    return render_template('index.html')

@paginas_bp.route('/login')
def login():
    return render_template('login.html')

@paginas_bp.route('/registro')
def registro():
    return render_template('registro.html')

@paginas_bp.route('/catalogo')
def catalogo():
    return render_template('catalogo.html')

@paginas_bp.route('/producto')
def producto():
    return render_template('producto.html')

@paginas_bp.route('/ofertas')
def ofertas():
    return render_template('ofertas.html')
@paginas_bp.route('/carrito')
def carrito():
    return render_template('carrito.html')
@paginas_bp.route('/admin')
def admin():
    return render_template('admin.html')

@paginas_bp.route('/contacto')
def contacto():
    return render_template('contacto.html')
from app import create_app
from app.extensions import db
from app.models.models import (
    Categoria, Producto, Variante, ProductoImagen,
    UsuarioRol, Cliente, Direccion, RolUsuario, TallaRopa
)
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()

    if Categoria.query.count() > 0:
        print("La base de datos ya tiene datos. Omitiendo seed.")
        print()
        print("=== CREDENCIALES DE PRUEBA ===")
        print("Gerente:   gerente@vangogh.com / admin123")
        print("Empleado:  empleado@vangogh.com / emple123")
        print("Cliente:   cliente@test.com / cliente123")
        print("Cliente:   maria@test.com / maria123")
        exit()

    print("Creando datos de prueba...")

    # ── CATEGORÍAS ──
    cats = [
        Categoria(nombre='Camisas', slug='camisas', descripcion='Camisas de arte'),
        Categoria(nombre='Pantalones', slug='pantalones', descripcion='Pantalones con estilo'),
        Categoria(nombre='Vestidos', slug='vestidos', descripcion='Vestidos inspirados en Van Gogh'),
        Categoria(nombre='Accesorios', slug='accesorios', descripcion='Accesorios únicos'),
    ]
    db.session.add_all(cats)
    db.session.flush()

    cat_map = {c.nombre.lower(): c for c in Categoria.query.all()}

    # ── USUARIOS ──
    users_data = [
        ('Gerente', 'Admin', 'gerente@vangogh.com', 'admin123', RolUsuario.gerente),
        ('Empleado', 'Ventas', 'empleado@vangogh.com', 'emple123', RolUsuario.empleado),
        ('Cliente', 'Uno', 'cliente@test.com', 'cliente123', RolUsuario.comprador),
        ('María', 'López', 'maria@test.com', 'maria123', RolUsuario.comprador),
    ]
    usuarios = []
    for nombres, apellido, email, pwd, rol in users_data:
        u = UsuarioRol(
            nombres=nombres, apellido_1=apellido,
            email=email, password_hash=generate_password_hash(pwd),
            rol=rol, activo=True
        )
        db.session.add(u)
        db.session.flush()
        usuarios.append(u)
        if rol == RolUsuario.comprador:
            c = Cliente(id_usuario=u.id_usuario, telefono='+591 70000000')
            db.session.add(c)
    db.session.flush()

    # ── DIRECCIONES ──
    for c in Cliente.query.all():
        d = Direccion(
            id_cliente=c.id_cliente,
            nombre_destinatario=c.usuario.nombres,
            calle='Av. Principal',
            numero_ext='123',
            ciudad='La Paz',
            estado='La Paz',
            codigo_postal='0000',
            es_predeterminada=True
        )
        db.session.add(d)
    db.session.flush()

    # ── PRODUCTOS ──
    productos_data = [
        ('Camisa Noche Estrellada', 'camisa-noche-estrellada', 'camisas', 150.00,
         'Inspirada en "La Noche Estrellada"', 'La Noche Estrellada', 1889,
         [('S', 'Azul', 'CAM-NOCHE-S', 10, 0), ('M', 'Azul', 'CAM-NOCHE-M', 15, 5), ('L', 'Azul', 'CAM-NOCHE-L', 8, 10)]),
        ('Pantalón Los Girasoles', 'pantalon-girasoles', 'pantalones', 220.00,
         'Estampado con "Los Girasoles"', 'Los Girasoles', 1888,
         [('S', 'Amarillo', 'PAN-GIRA-S', 12, 0), ('M', 'Amarillo', 'PAN-GIRA-M', 10, 5), ('L', 'Amarillo', 'PAN-GIRA-L', 6, 10)]),
        ('Vestido Terraza de Café', 'vestido-terraza', 'vestidos', 320.00,
         'Estampado floral "Terraza de Café por la Noche"', 'Terraza de Café por la Noche', 1888,
         [('S', 'Multicolor', 'VES-TERR-S', 5, 0), ('M', 'Multicolor', 'VES-TERR-M', 8, 10), ('L', 'Multicolor', 'VES-TERR-L', 4, 15)]),
        ('Bufanda Autorretrato', 'bufanda-autorretrato', 'accesorios', 80.00,
         'Diseño basado en "Autorretrato"', 'Autorretrato', 1889,
         [('X', 'Negro', 'BUF-AUTO-X', 20, 0)]),
        ('Camisa Almendro', 'camisa-almendro', 'camisas', 190.00,
         'Ramas floridas de "Almendro en Flor"', 'Almendro en Flor', 1890,
         [('S', 'Rosa', 'CAM-ALM-S', 10, 0), ('M', 'Rosa', 'CAM-ALM-M', 12, 5), ('L', 'Rosa', 'CAM-ALM-L', 7, 10)]),
        ('Vestido Iris', 'vestido-iris', 'vestidos', 280.00,
         'Inspirado en "Iris"', 'Iris', 1889,
         [('S', 'Morado', 'VES-IRIS-S', 6, 0), ('M', 'Morado', 'VES-IRIS-M', 9, 10), ('L', 'Morado', 'VES-IRIS-L', 5, 15)]),
    ]

    for nombre, slug, cat_nombre, precio, desc, obra, anio, variantes in productos_data:
        cat = cat_map[cat_nombre]
        p = Producto(
            id_categoria=cat.id_categoria, nombre=nombre, slug=slug,
            precio_base=precio, descripcion=desc,
            obra_vangogh=obra, anio_obra=anio, activo=True
        )
        db.session.add(p)
        db.session.flush()

        for talla, color, sku, stock, extra in variantes:
            talla_enum = next(t for t in TallaRopa if t.value == talla)
            v = Variante(
                id_producto=p.id_producto, talla=talla_enum, color=color,
                sku=sku, stock=stock, precio_extra=extra, activa=True
            )
            db.session.add(v)

        img = ProductoImagen(
            id_producto=p.id_producto,
            url='img/placeholder.jpg',
            alt_text=nombre,
            es_principal=True,
            orden=0
        )
        db.session.add(img)

    db.session.commit()
    print("[OK] Seed completado exitosamente.")
    print()
    print("=== CREDENCIALES DE PRUEBA ===")
    print("Gerente:   gerente@vangogh.com / admin123")
    print("Empleado:  empleado@vangogh.com / emple123")
    print("Cliente:   cliente@test.com / cliente123")
    print("Cliente:   maria@test.com / maria123")

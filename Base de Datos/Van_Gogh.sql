-- EXTENSIONES Y TIPOS ENUM
-- Definicion de tipos de datos personalizados para asegurar la integridad
CREATE TYPE rol_usuario    AS ENUM ('gerente', 'empleado', 'comprador');
CREATE TYPE talla_ropa     AS ENUM ('XS', 'S', 'M', 'L', 'XL', 'XXL', 'UNICA');
CREATE TYPE tipo_direccion AS ENUM ('Casa', 'Oficina', 'Regalo', 'Otro');
CREATE TYPE tipo_cupon     AS ENUM ('porcentaje', 'monto_fijo');
CREATE TYPE estado_pedido  AS ENUM ('pendiente', 'confirmado', 'enviado', 'entregado', 'cancelado');
CREATE TYPE metodo_pago    AS ENUM ('tarjeta_credito', 'tarjeta_debito', 'transferencia', 'efectivo', 'paypal');
CREATE TYPE estado_pago    AS ENUM ('pendiente', 'completado', 'fallido', 'reembolsado');

-- FUNCION GLOBAL PARA UPDATED_AT
-- Automatiza la actualizacion de la fecha de modificacion en todas las tablas
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- TABLA: usuarios_roles
-- Almacena credenciales y roles. Relacion recursiva con 'creado_por'
CREATE TABLE usuarios_roles (
    id_usuario      SERIAL          PRIMARY KEY,
    nombres          VARCHAR(100)    NOT NULL,
    apellido_1      VARCHAR(50)     NOT NULL,
    apellido_2      VARCHAR(50),
    email           VARCHAR(150)    NOT NULL UNIQUE,
    password_hash   TEXT            NOT NULL,
    rol             rol_usuario     NOT NULL DEFAULT 'comprador',
    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    creado_por      INTEGER         REFERENCES usuarios_roles(id_usuario) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_usuarios_email ON usuarios_roles(email);
CREATE TRIGGER set_timestamp_usuarios BEFORE UPDATE ON usuarios_roles FOR EACH ROW EXECUTE PROCEDURE trigger_set_timestamp();

-- TABLA: categorias
-- Organizacion logica de productos con slugs para URLs amigables
CREATE TABLE categorias (
    id_categoria    SERIAL          PRIMARY KEY,
    nombre          VARCHAR(80)     NOT NULL UNIQUE,
    slug            VARCHAR(80)     NOT NULL UNIQUE,
    descripcion     TEXT,
    activa          BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE TRIGGER set_timestamp_categorias BEFORE UPDATE ON categorias FOR EACH ROW EXECUTE PROCEDURE trigger_set_timestamp();

-- TABLA: productos
-- Informacion general. Relacion 1:N con categorias
CREATE TABLE productos (
    id_producto     SERIAL          PRIMARY KEY,
    id_categoria    INTEGER         NOT NULL REFERENCES categorias(id_categoria) ON DELETE RESTRICT,
    nombre          VARCHAR(150)    NOT NULL,
    slug            VARCHAR(150)    NOT NULL UNIQUE,
    descripcion     TEXT,
    precio_base     NUMERIC(10,2)   NOT NULL CHECK (precio_base >= 0),
    obra_vangogh    VARCHAR(120),
    anio_obra       SMALLINT        CHECK (anio_obra BETWEEN 1800 AND 2100),
    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE TRIGGER set_timestamp_productos BEFORE UPDATE ON productos FOR EACH ROW EXECUTE PROCEDURE trigger_set_timestamp();

-- TABLA: variantes
-- SKU especifico (Talla/Color). Aqui se gestiona el inventario fisico (stock)
CREATE TABLE variantes (
    id_variante     SERIAL          PRIMARY KEY,
    id_producto     INTEGER         NOT NULL REFERENCES productos(id_producto) ON DELETE CASCADE,
    talla           talla_ropa      NOT NULL,
    color           VARCHAR(60)     NOT NULL,
    sku             VARCHAR(60)     NOT NULL UNIQUE,
    stock           INTEGER         NOT NULL DEFAULT 0 CHECK (stock >= 0),
    precio_extra    NUMERIC(10,2)   NOT NULL DEFAULT 0.00 CHECK (precio_extra >= 0),
    activa          BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_variante_producto_talla_color UNIQUE (id_producto, talla, color)
);

CREATE TRIGGER set_timestamp_variantes BEFORE UPDATE ON variantes FOR EACH ROW EXECUTE PROCEDURE trigger_set_timestamp();

-- TABLA: producto_imagenes
-- Soporte multimedia. Relacion N:1 con productos
CREATE TABLE producto_imagenes (
    id_imagen       SERIAL          PRIMARY KEY,
    id_producto     INTEGER         NOT NULL REFERENCES productos(id_producto) ON DELETE CASCADE,
    url             TEXT            NOT NULL,
    alt_text        VARCHAR(200),
    orden           SMALLINT        NOT NULL DEFAULT 0 CHECK (orden >= 0),
    es_principal    BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- TABLA: clientes
-- Perfil comercial. Extiende a usuarios_roles (Herencia logica 1:1)
CREATE TABLE clientes (
    id_cliente       SERIAL          PRIMARY KEY,
    id_usuario       INTEGER         NOT NULL UNIQUE REFERENCES usuarios_roles(id_usuario) ON DELETE CASCADE,
    telefono         VARCHAR(20),
    fecha_nacimiento DATE,
    genero           VARCHAR(30),
    acepta_marketing BOOLEAN         NOT NULL DEFAULT FALSE,
    puntos_fidelidad INTEGER         NOT NULL DEFAULT 0 CHECK (puntos_fidelidad >= 0),
    fecha_registro   TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE TRIGGER set_timestamp_clientes BEFORE UPDATE ON clientes FOR EACH ROW EXECUTE PROCEDURE trigger_set_timestamp();

-- TABLA: direcciones
-- Direcciones de envio. Relacion N:1 con clientes
CREATE TABLE direcciones (
    id_direccion        SERIAL          PRIMARY KEY,
    id_cliente          INTEGER         NOT NULL REFERENCES clientes(id_cliente) ON DELETE CASCADE,
    tipo                tipo_direccion  NOT NULL DEFAULT 'Casa',
    nombre_destinatario VARCHAR(120)    NOT NULL,
    calle               VARCHAR(200)    NOT NULL,
    numero_ext          VARCHAR(20)     NOT NULL,
    ciudad              VARCHAR(100)    NOT NULL,
    estado              VARCHAR(80)     NOT NULL,
    pais                VARCHAR(60)     NOT NULL DEFAULT 'Mexico',
    codigo_postal       VARCHAR(10)     NOT NULL,
    es_predeterminada   BOOLEAN         NOT NULL DEFAULT FALSE,
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE TRIGGER set_timestamp_direcciones BEFORE UPDATE ON direcciones FOR EACH ROW EXECUTE PROCEDURE trigger_set_timestamp();

-- TABLA: cupones
-- Reglas de descuento con validacion de fechas y limites de uso
CREATE TABLE cupones (
    id_cupon        SERIAL          PRIMARY KEY,
    codigo          VARCHAR(30)     NOT NULL UNIQUE,
    tipo            tipo_cupon      NOT NULL,
    descuento       NUMERIC(10,2)   NOT NULL CHECK (descuento > 0),
    monto_minimo    NUMERIC(10,2)   DEFAULT 0,
    fecha_inicio    DATE            DEFAULT CURRENT_DATE,
    fecha_fin       DATE,
    usos_maximos    INTEGER,
    usos_actuales   INTEGER         NOT NULL DEFAULT 0,
    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_fechas_cupon CHECK (fecha_fin IS NULL OR fecha_fin >= fecha_inicio)
);

-- TABLA: pedidos
-- Encabezado de orden. Relaciona cliente, direccion y cupon
CREATE TABLE pedidos (
    id_pedido          SERIAL          PRIMARY KEY,
    id_cliente         INTEGER         NOT NULL REFERENCES clientes(id_cliente),
    id_cupon           INTEGER         REFERENCES cupones(id_cupon),
    id_direccion       INTEGER         NOT NULL REFERENCES direcciones(id_direccion),
    estado             estado_pedido   NOT NULL DEFAULT 'pendiente',
    subtotal           NUMERIC(10,2)   NOT NULL CHECK (subtotal >= 0),
    descuento_aplicado NUMERIC(10,2)   NOT NULL DEFAULT 0.00,
    costo_envio        NUMERIC(10,2)   NOT NULL DEFAULT 0.00,
    total              NUMERIC(10,2)   NOT NULL CHECK (total >= 0),
    fecha_pedido       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE TRIGGER set_timestamp_pedidos BEFORE UPDATE ON pedidos FOR EACH ROW EXECUTE PROCEDURE trigger_set_timestamp();

-- TABLA: detalle_pedido
-- Lineas de productos comprados. Incluye trigger de stock (abajo)
CREATE TABLE detalle_pedido (
    id_detalle      SERIAL          PRIMARY KEY,
    id_pedido       INTEGER         NOT NULL REFERENCES pedidos(id_pedido) ON DELETE CASCADE,
    id_variante     INTEGER         NOT NULL REFERENCES variantes(id_variante),
    cantidad        INTEGER         NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(10,2)   NOT NULL,
    subtotal        NUMERIC(10,2)   GENERATED ALWAYS AS (cantidad * precio_unitario) STORED
);

-- TABLA: pagos
-- Registro financiero unico por pedido
CREATE TABLE pagos (
    id_pago                SERIAL          PRIMARY KEY,
    id_pedido              INTEGER         NOT NULL UNIQUE REFERENCES pedidos(id_pedido),
    metodo                 metodo_pago     NOT NULL,
    estado                 estado_pago     NOT NULL DEFAULT 'pendiente',
    monto                  NUMERIC(10,2)   NOT NULL CHECK (monto > 0),
    fecha_pago             TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at             TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE TRIGGER set_timestamp_pagos BEFORE UPDATE ON pagos FOR EACH ROW EXECUTE PROCEDURE trigger_set_timestamp();

-- TRIGGER: CONTROL DE INVENTARIO
-- Resta automaticamente el stock de la variante cuando se crea un detalle de pedido
CREATE OR REPLACE FUNCTION funcion_actualizar_stock()
RETURNS TRIGGER AS $$
BEGIN
-- Verificar si hay stock suficiente
    IF (SELECT stock FROM variantes WHERE id_variante = NEW.id_variante) < NEW.cantidad THEN
        RAISE EXCEPTION 'Stock insuficiente para la variante %', NEW.id_variante;
    END IF;

    UPDATE variantes 
    SET stock = stock - NEW.cantidad 
    WHERE id_variante = NEW.id_variante;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_stock_descontar AFTER INSERT ON detalle_pedido
FOR EACH ROW EXECUTE PROCEDURE funcion_actualizar_stock();

-- TABLA: precio_historial
-- Auditoria de cambios de precios realizada por empleados/gerentes
CREATE TABLE precio_historial (
    id_historial    SERIAL          PRIMARY KEY,
    id_producto     INTEGER         REFERENCES productos(id_producto),
    id_usuario      INTEGER         REFERENCES usuarios_roles(id_usuario),
    precio_anterior NUMERIC(10,2),
    precio_nuevo    NUMERIC(10,2)   NOT NULL,
    motivo          TEXT            NOT NULL,
    fecha_cambio    TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);
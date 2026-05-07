// js/carrito.js
let carrito = [];

function cargarCarrito() {
    carrito = JSON.parse(localStorage.getItem('carrito') || '[]');
    renderizarCarrito();
}

function guardarCarrito() {
    localStorage.setItem('carrito', JSON.stringify(carrito));
}

function actualizarContadorCarrito() {
    const total = carrito.reduce((sum, item) => sum + item.cantidad, 0);
    const badge = document.getElementById('cart-count');
    if (badge) {
        badge.textContent = total;
        badge.style.display = total > 0 ? 'block' : 'none';
    }
}

function eliminarItem(index) {
    carrito.splice(index, 1);
    guardarCarrito();
    renderizarCarrito();
}

function cambiarCantidad(index, nuevaCantidad) {
    const cantidad = parseInt(nuevaCantidad);
    if (isNaN(cantidad) || cantidad < 1) return;
    carrito[index].cantidad = cantidad;
    guardarCarrito();
    renderizarCarrito();
}

function calcularSubtotal() {
    return carrito.reduce((sum, item) => sum + (item.precio_unitario * item.cantidad), 0);
}

function renderizarCarrito() {
    const emptyDiv = document.getElementById('cart-empty');
    const contentDiv = document.getElementById('cart-content');
    const tbody = document.getElementById('cart-items');

    if (carrito.length === 0) {
        emptyDiv.style.display = 'block';
        contentDiv.style.display = 'none';
    } else {
        emptyDiv.style.display = 'none';
        contentDiv.style.display = 'block';

        tbody.innerHTML = carrito.map((item, index) => `
            <tr>
                <td>${item.nombre}</td>
                <td>${item.talla} / ${item.color}</td>
                <td>Bs. ${item.precio_unitario.toFixed(2)}</td>
                <td>
                    <input type="number" value="${item.cantidad}" min="1" 
                           onchange="cambiarCantidad(${index}, this.value)" style="width:60px;">
                </td>
                <td>Bs. ${(item.precio_unitario * item.cantidad).toFixed(2)}</td>
                <td><button onclick="eliminarItem(${index})">🗑️</button></td>
            </tr>
        `).join('');

        const subtotal = calcularSubtotal();
        const descuento = 0; // Se calculará al aplicar cupón
        const envio = 3.99;
        const total = subtotal + envio;

        document.getElementById('subtotal').textContent = subtotal.toFixed(2);
        document.getElementById('descuento').textContent = descuento.toFixed(2);
        document.getElementById('envio').textContent = envio.toFixed(2);
        document.getElementById('total').textContent = total.toFixed(2);

        // Verificar sesión para mostrar checkout
        const sesion = obtenerSesion();
        const checkoutSection = document.getElementById('checkout-section');
        const loginRequired = document.getElementById('login-required');
        if (sesion && sesion.rol === 'comprador') {
            loginRequired.style.display = 'none';
            checkoutSection.style.display = 'block';
            cargarDirecciones(sesion);
        } else {
            checkoutSection.style.display = 'none';
            loginRequired.style.display = 'block';
        }
    }
    actualizarContadorCarrito();
}

async function cargarDirecciones(sesion) {
    try {
        const cliente = await fetchGet(`/clientes/usuario/${sesion.id_usuario}`);
        const direcciones = await fetchGet(`/direcciones?cliente=${cliente.id_cliente}`);
        const select = document.getElementById('direccion-select');
        select.innerHTML = direcciones.map(d => 
            `<option value="${d.id_direccion}">${d.calle} ${d.numero_ext}, ${d.ciudad} (${d.tipo})</option>`
        ).join('');
    } catch (err) {
        console.error('Error cargando direcciones:', err);
    }
}

async function realizarPedido() {
    const sesion = obtenerSesion();
    if (!sesion) {
        alert('Debes iniciar sesión');
        return;
    }
    const id_direccion = document.getElementById('direccion-select').value;
    const cuponInput = document.getElementById('cupon-input').value.trim();
    const id_cupon = cuponInput ? await obtenerIdCupon(cuponInput) : null;

    if (!id_direccion) {
        alert('Selecciona una dirección');
        return;
    }

    const items = carrito.map(item => ({
        id_variante: item.id_variante,
        cantidad: item.cantidad
    }));

    const body = {
        id_cliente: await obtenerIdCliente(sesion),
        id_direccion: parseInt(id_direccion),
        costo_envio: 3.99,
        id_cupon: id_cupon,
        items
    };

    try {
        const pedido = await fetchPost('/pedidos/', body);
        alert(`Pedido #${pedido.id_pedido} creado. Total: Bs. ${pedido.total}`);
        localStorage.removeItem('carrito');
        window.location.href = '/catalogo';
    } catch (error) {
        alert('Error al crear el pedido: ' + error.message);
    }
}

async function obtenerIdCliente(sesion) {
    const cliente = await fetchGet(`/clientes/usuario/${sesion.id_usuario}`);
    return cliente.id_cliente;
}

async function obtenerIdCupon(codigo) {
    try {
        const cupones = await fetchGet('/cupones');
        const cupon = cupones.find(c => c.codigo === codigo && c.activo);
        return cupon ? cupon.id_cupon : null;
    } catch {
        return null;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    cargarCarrito();
    document.getElementById('btn-pagar')?.addEventListener('click', realizarPedido);
});
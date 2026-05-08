let productoActual = null;
let variantes = [];

document.addEventListener('DOMContentLoaded', async () => {
    const params = new URLSearchParams(window.location.search);
    const id = params.get('id');
    if (!id) {
        document.getElementById('nombre-producto').textContent = 'Producto no encontrado';
        return;
    }

    try {
        const data = await apiRequest(`/productos/${id}`);
        productoActual = data;
        variantes = data.variantes || [];
        renderProducto(data);
    } catch (err) {
        document.getElementById('nombre-producto').textContent = 'Error al cargar producto';
        document.getElementById('descripcion-txt').textContent = err.message;
    }
});

function renderProducto(p) {
    document.getElementById('nombre-producto').textContent = p.nombre;
    document.getElementById('precio-producto').textContent = `Bs. ${p.precio_base.toFixed(2)}`;
    document.getElementById('descripcion-txt').textContent = p.descripcion || 'Sin descripción disponible.';
    document.getElementById('categoria-txt').textContent = p.categoria || 'General';

    if (p.imagenes && p.imagenes.length > 0) {
        const imgPrincipal = document.getElementById('img-principal');
        const principal = p.imagenes.find(i => i.es_principal) || p.imagenes[0];
        imgPrincipal.src = principal.url;
        imgPrincipal.alt = principal.alt_text || p.nombre;
    }

    const tallaSelect = document.getElementById('talla');
    tallaSelect.innerHTML = '<option value="">Seleccionar talla...</option>';
    const tallasUnicas = [...new Set(variantes.filter(v => v.activa).map(v => v.talla))];
    tallasUnicas.forEach(talla => {
        const option = document.createElement('option');
        option.value = talla;
        option.textContent = talla;
        tallaSelect.appendChild(option);
    });

    actualizarStock();
    tallaSelect.addEventListener('change', actualizarStock);

    document.getElementById('btn-comprar').addEventListener('click', abrirCheckout);
}

function actualizarStock() {
    const talla = document.getElementById('talla').value;
    const stockSpan = document.getElementById('stock-num');
    const variante = variantes.find(v => v.talla === talla && v.activa);
    if (variante) {
        stockSpan.textContent = variante.stock;
        stockSpan.style.color = variante.stock > 0 ? '#4caf50' : '#ff4757';
    } else if (talla) {
        stockSpan.textContent = '0';
        stockSpan.style.color = '#ff4757';
    } else {
        stockSpan.textContent = '—';
        stockSpan.style.color = '#ccc';
    }
}

function getVarianteSeleccionada() {
    const talla = document.getElementById('talla').value;
    if (!talla) return null;
    return variantes.find(v => v.talla === talla && v.activa) || null;
}

function abrirCheckout() {
    const usuario = getUsuario();
    if (!usuario) {
        alert('Debes iniciar sesión para comprar.');
        window.location.href = 'login.html';
        return;
    }

    const variante = getVarianteSeleccionada();
    if (!variante) {
        alert('Selecciona una talla disponible.');
        return;
    }

    const cantidad = parseInt(document.getElementById('cantidad').value) || 1;
    if (cantidad < 1) {
        alert('La cantidad debe ser al menos 1.');
        return;
    }
    if (cantidad > variante.stock) {
        alert(`Solo hay ${variante.stock} unidades disponibles.`);
        return;
    }

    document.getElementById('modal-variante-info').textContent =
        `${productoActual.nombre} - Talla: ${variante.talla} - Cant: ${cantidad}`;
    const totalItem = (productoActual.precio_base + variante.precio_extra) * cantidad;
    document.getElementById('modal-total').textContent = `Bs. ${totalItem.toFixed(2)}`;

    document.getElementById('checkout-modal').style.display = 'flex';
    document.getElementById('btn-cerrar-modal').onclick = () => {
        document.getElementById('checkout-modal').style.display = 'none';
    };
    document.getElementById('checkout-modal').onclick = (e) => {
        if (e.target === e.currentTarget) {
            document.getElementById('checkout-modal').style.display = 'none';
        }
    };

    const form = document.getElementById('checkout-form');
    form.onsubmit = async (e) => {
        e.preventDefault();
        await realizarCompra(variante, cantidad);
    };
}

async function realizarCompra(variante, cantidad) {
    const usuario = getUsuario();
    const form = document.getElementById('checkout-form');
    const btnSubmit = form.querySelector('button[type="submit"]');
    btnSubmit.disabled = true;
    btnSubmit.textContent = 'Procesando...';

    const metodoPago = document.getElementById('metodo-pago').value;
    const calle = document.getElementById('checkout-calle').value.trim();
    const ciudad = document.getElementById('checkout-ciudad').value.trim();
    const codigoPostal = document.getElementById('checkout-cp').value.trim();

    if (!calle || !ciudad || !codigoPostal) {
        alert('Completa todos los campos de dirección.');
        btnSubmit.disabled = false;
        btnSubmit.textContent = 'Confirmar Compra';
        return;
    }

    try {
        let idCliente, idDireccion;

        const clienteData = await apiRequest(`/clientes/usuario/${usuario.id_usuario}`);
        idCliente = clienteData.id_cliente;

        const direcciones = await apiRequest(`/direcciones/?cliente=${idCliente}`);
        let direccion = direcciones.find(d => d.calle === calle && d.ciudad === ciudad);

        if (!direccion) {
            const nuevaDir = await apiRequest('/direcciones/', {
                method: 'POST',
                body: JSON.stringify({
                    id_cliente: idCliente,
                    nombre_destinatario: usuario.nombres,
                    calle,
                    ciudad,
                    codigo_postal: codigoPostal,
                    numero_ext: 'S/N',
                    estado: ciudad,
                })
            });
            idDireccion = nuevaDir.id_direccion;
        } else {
            idDireccion = direccion.id_direccion;
        }

        const pedidoData = await apiRequest('/pedidos/', {
            method: 'POST',
            body: JSON.stringify({
                id_cliente: idCliente,
                id_direccion: idDireccion,
                costo_envio: 0,
                items: [{ id_variante: variante.id_variante, cantidad }]
            })
        });

        await apiRequest('/pagos/', {
            method: 'POST',
            body: JSON.stringify({
                id_pedido: pedidoData.id_pedido,
                metodo: metodoPago,
                monto: pedidoData.total
            })
        });

        document.getElementById('checkout-modal').style.display = 'none';

        const resumenDiv = document.getElementById('compra-exitosa');
        resumenDiv.style.display = 'block';
        document.getElementById('resumen-pedido-id').textContent = pedidoData.id_pedido;
        document.getElementById('resumen-total').textContent = `Bs. ${pedidoData.total.toFixed(2)}`;
        document.getElementById('resumen-estado').textContent = pedidoData.estado;
        document.getElementById('resumen-producto').textContent =
            `${productoActual.nombre} x${cantidad} (Talla: ${variante.talla})`;

        document.getElementById('btn-seguir-comprando').onclick = () => {
            window.location.href = 'catalogo.html';
        };

        btnSubmit.disabled = false;
        btnSubmit.textContent = 'Confirmar Compra';
    } catch (err) {
        alert('Error al procesar la compra: ' + err.message);
        btnSubmit.disabled = false;
        btnSubmit.textContent = 'Confirmar Compra';
    }
}

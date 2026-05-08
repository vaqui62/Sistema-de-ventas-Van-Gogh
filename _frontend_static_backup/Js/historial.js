document.addEventListener('DOMContentLoaded', async () => {
    const usuario = getUsuario();
    if (!usuario || (usuario.rol !== 'gerente' && usuario.rol !== 'empleado')) {
        document.getElementById('historial-content').innerHTML = `
            <div class="error-acceso">
                <h2>Acceso denegado</h2>
                <p>Solo gerentes y empleados pueden ver el historial de pedidos.</p>
                <a href="login.html" class="btn-auth">Iniciar Sesión</a>
            </div>
        `;
        return;
    }

    try {
        const pedidos = await apiRequest('/pedidos/');
        renderHistorial(pedidos);
    } catch (err) {
        document.getElementById('tabla-body').innerHTML =
            `<tr><td colspan="7">Error al cargar: ${err.message}</td></tr>`;
    }
});

function renderHistorial(pedidos) {
    const tbody = document.getElementById('tabla-body');
    if (!pedidos || pedidos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7">No hay pedidos registrados aún.</td></tr>';
        return;
    }

    tbody.innerHTML = pedidos.map(p => `
        <tr>
            <td>#${p.id_pedido}</td>
            <td>${p.cliente_nombre || '—'}</td>
            <td>${p.cliente_email || '—'}</td>
            <td>Bs. ${p.total.toFixed(2)}</td>
            <td><span class="estado-badge estado-${p.estado}">${p.estado}</span></td>
            <td>${new Date(p.fecha_pedido).toLocaleDateString('es-BO')}</td>
            <td>
                <button class="btn-ver-detalle" onclick="verDetalle(${p.id_pedido})">Ver</button>
            </td>
        </tr>
    `).join('');
}

async function verDetalle(idPedido) {
    try {
        const p = await apiRequest(`/pedidos/${idPedido}`);
        const modal = document.getElementById('detalle-modal');
        const body = document.getElementById('detalle-body');

        body.innerHTML = `
            <p><strong>Pedido:</strong> #${p.id_pedido}</p>
            <p><strong>Cliente:</strong> ${p.cliente_nombre}</p>
            <p><strong>Email:</strong> ${p.cliente_email}</p>
            <p><strong>Dirección:</strong> ${p.direccion || '—'}</p>
            <p><strong>Estado:</strong> <span class="estado-badge estado-${p.estado}">${p.estado}</span></p>
            <p><strong>Subtotal:</strong> Bs. ${p.subtotal.toFixed(2)}</p>
            <p><strong>Descuento:</strong> Bs. ${p.descuento_aplicado.toFixed(2)}</p>
            <p><strong>Envío:</strong> Bs. ${p.costo_envio.toFixed(2)}</p>
            <p><strong>Total:</strong> Bs. ${p.total.toFixed(2)}</p>
            <p><strong>Fecha:</strong> ${new Date(p.fecha_pedido).toLocaleString('es-BO')}</p>
            <hr>
            <h4>Productos</h4>
            <table class="tabla-historial">
                <thead><tr><th>Producto</th><th>Talla</th><th>Cant</th><th>Precio</th><th>Subtotal</th></tr></thead>
                <tbody>
                    ${p.detalles.map(d => `
                        <tr>
                            <td>${d.producto_nombre || '—'}</td>
                            <td>${d.talla || '—'}</td>
                            <td>${d.cantidad}</td>
                            <td>Bs. ${d.precio_unitario.toFixed(2)}</td>
                            <td>Bs. ${(d.subtotal || d.cantidad * d.precio_unitario).toFixed(2)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        modal.style.display = 'flex';
        document.getElementById('cerrar-detalle').onclick = () => {
            modal.style.display = 'none';
        };
        modal.onclick = (e) => {
            if (e.target === e.currentTarget) modal.style.display = 'none';
        };
    } catch (err) {
        alert('Error al cargar detalle: ' + err.message);
    }
}

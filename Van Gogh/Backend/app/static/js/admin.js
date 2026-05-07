// admin.js – Panel de empleados/gerentes

const sesion = obtenerSesion();

// Verificar acceso: solo empleado o gerente
if (!sesion || (sesion.rol !== 'empleado' && sesion.rol !== 'gerente')) {
    alert('Acceso denegado');
    window.location.href = '/login';
}

document.addEventListener('DOMContentLoaded', async () => {
    document.getElementById('admin-bienvenida').textContent =
        `Bienvenido/a ${sesion.nombres} (${sesion.rol})`;

    await Promise.all([
        cargarPedidos(),
        cargarHistorialPrecios(),
        cargarStockBajo(),
        cargarPagosRecientes()
    ]);
});

async function cargarPedidos() {
    try {
        const pedidos = await fetchGet('/pedidos');
        const tbody = document.querySelector('#tabla-pedidos tbody');
        tbody.innerHTML = pedidos.map(p => `
            <tr>
                <td>${p.id_pedido}</td>
                <td>${p.id_cliente}</td>
                <td>Bs. ${p.total}</td>
                <td>${p.estado}</td>
                <td>
                    <select onchange="cambiarEstadoPedido(${p.id_pedido}, this.value)">
                        <option value="">--</option>
                        <option value="pendiente" ${p.estado==='pendiente'?'selected':''}>pendiente</option>
                        <option value="confirmado" ${p.estado==='confirmado'?'selected':''}>confirmado</option>
                        <option value="enviado" ${p.estado==='enviado'?'selected':''}>enviado</option>
                        <option value="entregado" ${p.estado==='entregado'?'selected':''}>entregado</option>
                        <option value="cancelado" ${p.estado==='cancelado'?'selected':''}>cancelado</option>
                    </select>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error cargando pedidos:', error);
    }
}

async function cambiarEstadoPedido(idPedido, nuevoEstado) {
    if (!nuevoEstado) return;
    try {
        await fetchPut(`/pedidos/${idPedido}`, { estado: nuevoEstado });
        alert(`Pedido #${idPedido} actualizado a ${nuevoEstado}`);
        cargarPedidos(); // Refrescar tabla
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function cargarHistorialPrecios() {
    try {
        const historial = await fetchGet('/productos/historial'); // Necesitamos endpoint TODO
        const tbody = document.getElementById('historial-precios');
        tbody.innerHTML = historial.slice(0, 10).map(h => `
            <tr>
                <td>${h.id_producto}</td>
                <td>Bs. ${h.precio_anterior ?? '—'}</td>
                <td>Bs. ${h.precio_nuevo}</td>
                <td>${h.motivo}</td>
                <td>${new Date(h.fecha_cambio).toLocaleString()}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error historial precios:', error);
    }
}

async function cargarStockBajo() {
    try {
        const variantes = await fetchGet('/variantes');
        const bajas = variantes.filter(v => v.stock <= 5);
        const tbody = document.getElementById('stock-bajo');
        tbody.innerHTML = bajas.map(v => `
            <tr>
                <td>${v.sku} - ${v.talla} ${v.color}</td>
                <td>${v.sku}</td>
                <td style="color:#ff4757">${v.stock}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error stock bajo:', error);
    }
}

async function cargarPagosRecientes() {
    try {
        const pagos = await fetchGet('/pagos');
        const tbody = document.getElementById('pagos-recientes');
        tbody.innerHTML = pagos.slice(0, 10).map(p => `
            <tr>
                <td>${p.id_pago}</td>
                <td>${p.id_pedido}</td>
                <td>${p.metodo}</td>
                <td>${p.estado}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error pagos:', error);
    }
}
async function cargarClientes() {
    try {
        const clientes = await fetchGet('/clientes');
        const tbody = document.getElementById('lista-clientes');
        tbody.innerHTML = clientes.map(c => `
            <tr>
                <td>${c.id_cliente}</td>
                <td>${c.nombres}</td>
                <td>${c.email}</td>
                <td>${c.telefono || '—'}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error cargando clientes:', error);
    }
}
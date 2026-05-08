// js/perfil.js
let idClienteActual = null;

document.addEventListener('DOMContentLoaded', async () => {
    const sesion = obtenerSesion();
    if (!sesion) {
        window.location.href = '/login';
        return;
    }

    document.getElementById('profile-email').textContent = sesion.email;

    try {
        const cliente = await fetchGet(`/clientes/usuario/${sesion.id_usuario}`);
        idClienteActual = cliente.id_cliente;
        cargarDirecciones();
        cargarPedidos();
    } catch (err) {
        console.error('Error al cargar perfil:', err);
    }

    document.getElementById('btn-nueva-direccion').addEventListener('click', () => {
        document.getElementById('modal-direccion').style.display = 'block';
        document.getElementById('modal-overlay').style.display = 'block';
    });

    document.getElementById('modal-dir-close').addEventListener('click', cerrarModalDir);
    document.getElementById('modal-overlay').addEventListener('click', cerrarModalDir);

    document.getElementById('form-direccion').addEventListener('submit', guardarDireccion);

    document.getElementById('btn-logout-profile').addEventListener('click', cerrarSesion);
});

function cerrarModalDir() {
    document.getElementById('modal-direccion').style.display = 'none';
    document.getElementById('modal-overlay').style.display = 'none';
}

async function cargarDirecciones() {
    try {
        const direcciones = await fetchGet(`/direcciones?cliente=${idClienteActual}`);
        const container = document.getElementById('lista-direcciones');
        if (direcciones.length === 0) {
            container.innerHTML = '<p style="color:rgba(255,255,255,0.5); padding:20px; text-align:center;">No tienes direcciones registradas.</p>';
            return;
        }
        container.innerHTML = direcciones.map(d => `
            <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(212,175,55,0.15); border-radius:8px; padding:15px; margin-bottom:10px;">
                <strong style="color:#d4af37;">${d.tipo}</strong>
                <p style="margin:5px 0;">${d.nombre_destinatario}</p>
                <p style="margin:5px 0; color:rgba(255,255,255,0.7);">${d.calle} ${d.numero_ext}, ${d.ciudad}, ${d.estado}, ${d.pais} - CP ${d.codigo_postal}</p>
            </div>
        `).join('');
    } catch (err) {
        document.getElementById('lista-direcciones').innerHTML = '<p style="color:#e74c3c; padding:20px; text-align:center;">Error al cargar direcciones.</p>';
    }
}

async function cargarPedidos() {
    try {
        const pedidos = await fetchGet(`/pedidos/?cliente=${idClienteActual}`);
        const container = document.getElementById('lista-pedidos');
        if (pedidos.length === 0) {
            container.innerHTML = '<p style="color:rgba(255,255,255,0.5); padding:20px; text-align:center;">No tienes pedidos aún.</p>';
            return;
        }
        container.innerHTML = pedidos.map(p => `
            <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(212,175,55,0.15); border-radius:8px; padding:15px; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                    <div>
                        <strong style="color:#d4af37;">Pedido #${p.id_pedido}</strong>
                        <span style="margin-left:15px; padding:3px 10px; border-radius:12px; font-size:0.8rem; background:${p.estado === 'entregado' ? 'rgba(46,204,113,0.2)' : p.estado === 'cancelado' ? 'rgba(231,76,60,0.2)' : 'rgba(241,196,15,0.2)'}; color:${p.estado === 'entregado' ? '#2ecc71' : p.estado === 'cancelado' ? '#e74c3c' : '#f1c40f'};">
                            ${p.estado.charAt(0).toUpperCase() + p.estado.slice(1)}
                        </span>
                    </div>
                    <strong>Bs. ${p.total}</strong>
                </div>
                <p style="margin:5px 0 0 0; font-size:0.85rem; color:rgba(255,255,255,0.5);">${new Date(p.fecha_pedido).toLocaleDateString('es-MX', { year: 'numeric', month: 'long', day: 'numeric' })}</p>
                <p style="margin:5px 0 0 0; font-size:0.85rem; color:rgba(255,255,255,0.5);">${p.detalles.length} artículo(s)</p>
            </div>
        `).join('');
    } catch (err) {
        document.getElementById('lista-pedidos').innerHTML = '<p style="color:#e74c3c; padding:20px; text-align:center;">Error al cargar pedidos.</p>';
    }
}

async function guardarDireccion(e) {
    e.preventDefault();
    const data = {
        id_cliente: idClienteActual,
        tipo: document.getElementById('dir-tipo').value,
        nombre_destinatario: document.getElementById('dir-nombre').value.trim(),
        calle: document.getElementById('dir-calle').value.trim(),
        numero_ext: document.getElementById('dir-numero').value.trim(),
        ciudad: document.getElementById('dir-ciudad').value.trim(),
        estado: document.getElementById('dir-estado').value.trim(),
        codigo_postal: document.getElementById('dir-cp').value.trim(),
        pais: document.getElementById('dir-pais').value.trim()
    };

    try {
        await fetchPost('/direcciones/', data);
        alert('Dirección guardada exitosamente');
        cerrarModalDir();
        document.getElementById('form-direccion').reset();
        cargarDirecciones();
    } catch (error) {
        alert('Error al guardar dirección: ' + error.message);
    }
}
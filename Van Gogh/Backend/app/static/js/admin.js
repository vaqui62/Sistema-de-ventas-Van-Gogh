const sesion = obtenerSesion();

if (!sesion || (sesion.rol !== 'empleado' && sesion.rol !== 'gerente')) {
    alert('Acceso denegado');
    window.location.href = '/login';
}

const esGerente = sesion.rol === 'gerente';

document.addEventListener('DOMContentLoaded', async () => {
    document.getElementById('admin-bienvenida').textContent =
        `Bienvenido/a ${sesion.nombres} (${sesion.rol})`;

    renderizarTabs();
    activarTab('dashboard');

    await Promise.all([
        cargarPedidos(),
        cargarHistorialPrecios(),
        cargarStockBajo(),
        cargarPagosRecientes(),
        cargarClientes(),
    ]);

    if (esGerente) {
        await cargarUsuarios();
        document.getElementById('usuario-form').addEventListener('submit', guardarUsuario);
    }

    await cargarProductosAdmin();
    document.getElementById('producto-form').addEventListener('submit', guardarProducto);
    document.getElementById('pf-imagen').addEventListener('change', previsualizarImagen);
    document.getElementById('variante-form').addEventListener('submit', guardarVariante);
});

function renderizarTabs() {
    const tabs = document.getElementById('admin-tabs');
    const items = [
        { id: 'dashboard', label: 'Dashboard', icon: 'dashboard', roles: ['gerente', 'empleado'] },
        { id: 'productos', label: 'Productos', icon: 'inventory_2', roles: ['gerente', 'empleado'] },
    ];
    if (esGerente) {
        items.push({ id: 'usuarios', label: 'Usuarios', icon: 'group', roles: ['gerente'] });
    }

    tabs.innerHTML = items.map(t =>
        `<button class="admin-tab-btn" data-tab="${t.id}" onclick="activarTab('${t.id}')">
            <span class="material-symbols-outlined">${t.icon}</span> ${t.label}
        </button>`
    ).join('');
}

function activarTab(tabId) {
    document.querySelectorAll('.admin-tab-content').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.admin-tab-btn').forEach(el => el.classList.remove('activo'));

    const content = document.getElementById('tab-' + tabId);
    if (content) content.style.display = 'block';

    const btn = document.querySelector(`.admin-tab-btn[data-tab="${tabId}"]`);
    if (btn) btn.classList.add('activo');
}

// =============================================
// DASHBOARD
// =============================================

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
                    <select onchange="cambiarEstadoPedido(${p.id_pedido}, this.value)" style="background:#222;color:white;border:1px solid #d4af37;padding:3px;">
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
        cargarPedidos();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function cargarHistorialPrecios() {
    try {
        const historial = await fetchGet('/productos/historial');
        const tbody = document.getElementById('historial-precios');
        tbody.innerHTML = (historial || []).slice(0, 10).map(h => `
            <tr>
                <td>Producto #${h.id_producto}</td>
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
        const bajas = (variantes || []).filter(v => v.stock <= 5);
        const tbody = document.getElementById('stock-bajo');
        tbody.innerHTML = bajas.map(v => `
            <tr>
                <td>${v.producto || '—'} - ${v.talla} ${v.color}</td>
                <td>${v.sku}</td>
                <td style="color:#ff4757;font-weight:bold;">${v.stock}</td>
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
        tbody.innerHTML = (pagos || []).slice(0, 10).map(p => `
            <tr>
                <td>${p.id_pago}</td>
                <td>#${p.id_pedido}</td>
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
        if (!tbody) return;
        tbody.innerHTML = (clientes || []).map(c => `
            <tr>
                <td>${c.id_cliente}</td>
                <td>${c.nombres || '—'}</td>
                <td>${c.email || '—'}</td>
                <td>${c.telefono || '—'}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error cargando clientes:', error);
    }
}

// =============================================
// GESTIÓN DE USUARIOS (solo gerente)
// =============================================

async function cargarUsuarios() {
    try {
        const usuarios = await fetchGet('/usuarios');
        const tbody = document.getElementById('usuarios-tbody');
        tbody.innerHTML = (usuarios || []).map(u => `
            <tr>
                <td>${u.id_usuario}</td>
                <td>${u.nombres} ${u.apellido_1}</td>
                <td>${u.email}</td>
                <td><span class="producto-activo-badge ${u.rol === 'gerente' ? 'badge-activo' : u.rol === 'empleado' ? '' : ''}">${u.rol}</span></td>
                <td class="${u.activo ? 'usuario-activo' : 'usuario-inactivo'}">${u.activo ? 'Activo' : 'Inactivo'}</td>
                <td>
                    ${u.activo && u.id_usuario !== sesion.id_usuario
                        ? `<button class="btn-small btn-peligro" onclick="desactivarUsuario(${u.id_usuario})" style="padding:4px 12px;font-size:0.8rem;">Desactivar</button>`
                        : '—'}
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error cargando usuarios:', error);
    }
}

function mostrarFormUsuario(rol) {
    document.getElementById('form-usuario-admin').style.display = 'block';
    document.getElementById('form-usuario-titulo').textContent =
        rol === 'empleado' ? 'Nuevo Empleado' : 'Nuevo Comprador';
    document.getElementById('uf-rol-destino').value = rol;
    document.getElementById('usuario-form').reset();
    document.getElementById('form-usuario-admin').scrollIntoView({ behavior: 'smooth' });
}

function cancelarFormUsuario() {
    document.getElementById('form-usuario-admin').style.display = 'none';
}

async function guardarUsuario(e) {
    e.preventDefault();
    const rol = document.getElementById('uf-rol-destino').value;
    const datos = {
        nombres: document.getElementById('uf-nombres').value,
        apellido_1: document.getElementById('uf-apellido1').value,
        apellido_2: document.getElementById('uf-apellido2').value || null,
        email: document.getElementById('uf-email').value,
        password: document.getElementById('uf-password').value,
        rol: rol,
        telefono: document.getElementById('uf-telefono').value || null,
        creado_por: sesion.id_usuario,
        acepta_marketing: true,
    };

    try {
        await fetchPost('/usuarios/', datos);
        alert(`Usuario ${rol} creado correctamente`);
        cancelarFormUsuario();
        await cargarUsuarios();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function desactivarUsuario(id) {
    if (!confirm('¿Desactivar este usuario? No podrá iniciar sesión.')) return;
    try {
        await fetchDelete(`/usuarios/${id}`);
        alert('Usuario desactivado');
        await cargarUsuarios();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// =============================================
// GESTIÓN DE PRODUCTOS (gerente y empleado)
// =============================================

async function cargarProductosAdmin() {
    try {
        const productos = await fetchGet('/productos/?activas=true');
        const tbody = document.getElementById('productos-tbody');
        tbody.innerHTML = (productos || []).map(p => {
            const imgUrl = p.imagenes && p.imagenes.length > 0
                ? p.imagenes.find(i => i.es_principal)?.url || p.imagenes[0].url
                : null;
            return `
            <tr>
                <td>${p.id_producto}</td>
                <td>${imgUrl ? `<img src="${imgUrl}" class="img-thumb">` : '—'}</td>
                <td><strong>${p.nombre}</strong></td>
                <td>Bs. ${p.precio_base}</td>
                <td>${p.categoria || '—'}</td>
                <td id="stock-prod-${p.id_producto}">—</td>
                <td><span class="producto-activo-badge ${p.activo ? 'badge-activo' : 'badge-inactivo'}">${p.activo ? 'Activo' : 'Inactivo'}</span></td>
                <td>
                    <button class="btn-small" onclick="editarProducto(${p.id_producto})" style="padding:4px 12px;font-size:0.8rem;margin:2px;">Editar</button>
                    <button class="btn-small" onclick="mostrarFormVariante(${p.id_producto})" style="padding:4px 12px;font-size:0.8rem;margin:2px;">+ Variante</button>
                    ${esGerente ? `
                        <button class="btn-small ${p.activo ? 'btn-peligro' : ''}" onclick="toggleProducto(${p.id_producto}, ${!p.activo})" style="padding:4px 12px;font-size:0.8rem;margin:2px;">
                            ${p.activo ? 'Ocultar' : 'Mostrar'}
                        </button>
                    ` : ''}
                </td>
            </tr>`;
        }).join('');

        // Cargar stock para cada producto
        (productos || []).forEach(p => {
            cargarStockProducto(p.id_producto);
        });
    } catch (error) {
        console.error('Error cargando productos:', error);
    }
}

async function cargarStockProducto(idProducto) {
    try {
        const variantes = await fetchGet(`/variantes/?producto=${idProducto}`);
        const total = (variantes || []).reduce((sum, v) => sum + v.stock, 0);
        const el = document.getElementById(`stock-prod-${idProducto}`);
        if (el) {
            el.textContent = total;
            if (total <= 5) el.style.color = '#ff4757';
        }
    } catch (e) { /* ignore */ }
}

async function cargarCategoriasSelect() {
    try {
        const categorias = await fetchGet('/categorias/?activas=true');
        const select = document.getElementById('pf-categoria');
        select.innerHTML = '<option value="">Seleccionar categoría</option>' +
            (categorias || []).map(c => `<option value="${c.id_categoria}">${c.nombre}</option>`).join('');
    } catch (error) {
        console.error('Error cargando categorías:', error);
    }
}

async function cargarProductoDetalle(id) {
    try {
        return await fetchGet(`/productos/${id}`);
    } catch (error) {
        console.error('Error cargando detalle:', error);
        return null;
    }
}

function mostrarFormProducto(datos) {
    cargarCategoriasSelect();
    const form = document.getElementById('form-producto-admin');
    const titulo = document.getElementById('form-producto-titulo');
    const submitBtn = document.getElementById('pf-submit');

    if (datos) {
        titulo.textContent = 'Editar Producto';
        submitBtn.textContent = 'Actualizar';
        document.getElementById('pf-id').value = datos.id_producto;
        document.getElementById('pf-nombre').value = datos.nombre;
        document.getElementById('pf-slug').value = datos.slug;
        document.getElementById('pf-precio').value = datos.precio_base;
        document.getElementById('pf-categoria').value = datos.id_categoria;
        document.getElementById('pf-descripcion').value = datos.descripcion || '';
        document.getElementById('pf-obra').value = datos.obra_vangogh || '';
        document.getElementById('pf-anio').value = datos.anio_obra || '';
        document.getElementById('pf-activo').checked = datos.activo;

        const preview = document.getElementById('pf-imagen-preview');
        if (datos.imagenes && datos.imagenes.length > 0) {
            const img = datos.imagenes.find(i => i.es_principal) || datos.imagenes[0];
            preview.innerHTML = `<img src="${img.url}" alt="${img.alt_text || ''}">`;
        } else {
            preview.innerHTML = '';
        }
    } else {
        titulo.textContent = 'Nuevo Producto';
        submitBtn.textContent = 'Guardar';
        document.getElementById('producto-form').reset();
        document.getElementById('pf-id').value = '';
        document.getElementById('pf-imagen-preview').innerHTML = '';
    }

    form.style.display = 'block';
    form.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function cancelarFormProducto() {
    document.getElementById('form-producto-admin').style.display = 'none';
}

async function guardarProducto(e) {
    e.preventDefault();
    const id = document.getElementById('pf-id').value;
    const datos = {
        nombre: document.getElementById('pf-nombre').value,
        slug: document.getElementById('pf-slug').value,
        precio_base: parseFloat(document.getElementById('pf-precio').value),
        id_categoria: parseInt(document.getElementById('pf-categoria').value),
        descripcion: document.getElementById('pf-descripcion').value,
        obra_vangogh: document.getElementById('pf-obra').value || null,
        anio_obra: document.getElementById('pf-anio').value ? parseInt(document.getElementById('pf-anio').value) : null,
        activo: document.getElementById('pf-activo').checked,
    };

    try {
        let resultado;
        if (id) {
            datos.motivo_precio = 'Actualización desde admin';
            datos.id_usuario = sesion.id_usuario;
            resultado = await fetchPut(`/productos/${id}`, datos);
        } else {
            resultado = await fetchPost('/productos/', datos);
        }

        const productoId = id || resultado.id_producto;
        const fileInput = document.getElementById('pf-imagen');
        if (fileInput.files.length > 0) {
            await subirImagenProducto(productoId, fileInput.files[0]);
        }

        alert(id ? 'Producto actualizado' : 'Producto creado');
        cancelarFormProducto();
        await cargarProductosAdmin();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function subirImagenProducto(idProducto, file) {
    const formData = new FormData();
    formData.append('imagen', file);
    formData.append('id_producto', idProducto);
    formData.append('es_principal', 'true');

    const resp = await fetch(`${API_BASE}/imagenes/subir`, {
        method: 'POST',
        body: formData
    });
    if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.error || 'Error al subir imagen');
    }
    return await resp.json();
}

function previsualizarImagen(e) {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(ev) {
        document.getElementById('pf-imagen-preview').innerHTML =
            `<img src="${ev.target.result}" alt="Preview">`;
    };
    reader.readAsDataURL(file);
}

async function editarProducto(id) {
    const datos = await cargarProductoDetalle(id);
    if (datos) mostrarFormProducto(datos);
}

async function toggleProducto(id, activar) {
    const accion = activar ? 'Mostrar' : 'Ocultar';
    if (!confirm(`${accion} este producto en la tienda?`)) return;
    try {
        await fetchPut(`/productos/${id}`, {
            activo: activar,
            motivo_precio: `${accion} en tienda desde admin`,
            id_usuario: sesion.id_usuario,
        });
        alert(`Producto ${activar ? 'visible' : 'oculto'} en tienda`);
        await cargarProductosAdmin();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// =============================================
// VARIANTES
// =============================================

async function mostrarFormVariante(idProducto, datos) {
    document.getElementById('vf-id-producto').value = idProducto;
    const titulo = document.getElementById('form-variante-titulo');
    const form = document.getElementById('form-variante-admin');

    if (datos) {
        titulo.textContent = 'Editar Variante';
        document.getElementById('vf-id').value = datos.id_variante;
        document.getElementById('vf-talla').value = datos.talla;
        document.getElementById('vf-color').value = datos.color;
        document.getElementById('vf-sku').value = datos.sku;
        document.getElementById('vf-stock').value = datos.stock;
        document.getElementById('vf-precio-extra').value = datos.precio_extra;
        document.getElementById('vf-activa').checked = datos.activa;
    } else {
        titulo.textContent = 'Nueva Variante';
        document.getElementById('variante-form').reset();
        document.getElementById('vf-id').value = '';
        document.getElementById('vf-activa').checked = true;
    }

    form.style.display = 'block';
    form.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function cancelarFormVariante() {
    document.getElementById('form-variante-admin').style.display = 'none';
}

async function guardarVariante(e) {
    e.preventDefault();
    const id = document.getElementById('vf-id').value;
    const datos = {
        id_producto: parseInt(document.getElementById('vf-id-producto').value),
        talla: document.getElementById('vf-talla').value,
        color: document.getElementById('vf-color').value,
        sku: document.getElementById('vf-sku').value,
        stock: parseInt(document.getElementById('vf-stock').value),
        precio_extra: parseFloat(document.getElementById('vf-precio-extra').value),
        activa: document.getElementById('vf-activa').checked,
    };

    try {
        if (id) {
            await fetchPut(`/variantes/${id}`, datos);
        } else {
            await fetchPost('/variantes/', datos);
        }
        alert(id ? 'Variante actualizada' : 'Variante creada');
        cancelarFormVariante();
        await cargarProductosAdmin();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const productos = await fetchGet('/productos/?activas=true');
        const grid = document.getElementById('lista-ofertas');
        grid.innerHTML = productos.map(p => `
            <div class="producto-card oferta">
                <span class="badge-descuento">-10%</span>
                <img src="/static/img/placeholder.jpg" alt="${p.nombre}">
                <h3>${p.nombre}</h3>
                <div class="precios">
                    <span class="precio-original">Bs. ${p.precio_base}</span>
                    <span class="precio-oferta">Bs. ${(p.precio_base * 0.9).toFixed(2)}</span>
                </div>
                <a href="/producto?id=${p.id_producto}" class="btn-ver">Ver Detalles</a>
            </div>
        `).join('');
    } catch (err) {
        console.error(err);
    }
    configurarAuth();
});
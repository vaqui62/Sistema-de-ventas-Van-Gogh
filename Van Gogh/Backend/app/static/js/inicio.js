document.addEventListener('DOMContentLoaded', async () => {
    try {
        const productos = await fetchGet('/productos/?activas=true');
        const grid = document.querySelector('.grid-productos');
        grid.innerHTML = '';
        productos.slice(0, 4).forEach(p => {
            const imgUrl = p.imagenes && p.imagenes.length > 0
                ? p.imagenes.find(i => i.es_principal)?.url || p.imagenes[0].url
                : '/static/img/placeholder.jpg';
            const card = document.createElement('div');
            card.className = 'producto-card';
            card.innerHTML = `
                <div class="card-img-wrap">
                    <img src="${imgUrl}" alt="${p.nombre}" loading="lazy" onerror="this.src='/static/img/placeholder.jpg'">
                </div>
                <h3>${p.nombre}</h3>
                <p class="precio">Bs. ${p.precio_base}</p>
                <a href="/producto?id=${p.id_producto}" class="btn-ver">Ver Detalles</a>
            `;
            grid.appendChild(card);
        });
    } catch (err) {
        console.error('Error cargando productos destacados:', err);
    }
    configurarAuth();
});
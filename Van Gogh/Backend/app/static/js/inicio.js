document.addEventListener('DOMContentLoaded', async () => {
    try {
        const productos = await fetchGet('/productos/?activas=true');
        const grid = document.querySelector('.grid-productos');
        grid.innerHTML = '';
        productos.slice(0, 4).forEach(p => {
            const card = document.createElement('div');
            card.className = 'producto-card';
            card.innerHTML = `
                <img src="/static/img/placeholder.jpg" alt="${p.nombre}">
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
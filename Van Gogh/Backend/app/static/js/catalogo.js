let todosLosProductos = [];

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const [productos, categorias] = await Promise.all([
            fetchGet('/productos/?activas=true'),
            fetchGet('/categorias/?activas=true')
        ]);
        todosLosProductos = productos;
        renderizarCategorias(categorias);
        renderizarProductos(productos);
        configurarAuth();
    } catch (err) {
        console.error(err);
    }

    document.getElementById('busqueda').addEventListener('input', aplicarFiltros);
    document.getElementById('ordenar').addEventListener('change', aplicarFiltros);
});

function renderizarCategorias(categorias) {
    const grupo = document.querySelector('.grupo-filtro');
    grupo.innerHTML = '<h3>Categorías</h3>';
    categorias.forEach(cat => {
        grupo.innerHTML += `
            <label><input type="checkbox" value="${cat.id_categoria}" checked> ${cat.nombre}</label>
        `;
    });
    grupo.querySelectorAll('input[type="checkbox"]').forEach(chk => {
        chk.addEventListener('change', aplicarFiltros);
    });
}

function aplicarFiltros() {
    const texto = document.getElementById('busqueda').value.toLowerCase();
    const catsSeleccionadas = Array.from(document.querySelectorAll('.grupo-filtro input[type="checkbox"]:checked')).map(c => parseInt(c.value));
    const orden = document.getElementById('ordenar').value;

    let filtrados = todosLosProductos.filter(p => {
        if (texto && !p.nombre.toLowerCase().includes(texto)) return false;
        if (catsSeleccionadas.length && !catsSeleccionadas.includes(p.id_categoria)) return false;
        return true;
    });

    if (orden === 'menor') filtrados.sort((a,b) => a.precio_base - b.precio_base);
    else if (orden === 'mayor') filtrados.sort((a,b) => b.precio_base - a.precio_base);

    renderizarProductos(filtrados);
}

function renderizarProductos(lista) {
    const grid = document.getElementById('lista-productos');
    grid.innerHTML = '';
    lista.forEach(p => {
        const card = document.createElement('article');
        card.className = 'producto-card';
        card.innerHTML = `
            <img src="/static/img/placeholder.jpg" alt="${p.nombre}">
            <h3>${p.nombre}</h3>
            <p class="precio">Bs. ${p.precio_base}</p>
            <a href="/producto?id=${p.id_producto}" class="btn-ver">Ver Detalles</a>
        `;
        grid.appendChild(card);
    });
}
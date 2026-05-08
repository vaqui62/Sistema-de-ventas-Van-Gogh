let todosLosProductos = [];
let todasLasVariantes = [];
let todasLasCategorias = [];

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const [productos, categorias] = await Promise.all([
            fetchGet('/productos/?activas=true'),
            fetchGet('/categorias/?activas=true')
        ]);
        todosLosProductos = productos;
        todasLasCategorias = categorias;

        // Cargar variantes para filtros de talla/color
        try {
            todasLasVariantes = await fetchGet('/variantes/?activas=true');
        } catch(e) { /* ignore */ }

        renderizarCategorias(categorias);
        renderizarFiltrosTalla();
        renderizarFiltrosColor();
        renderizarProductos(productos);
        configurarAuth();
    } catch (err) {
        console.error(err);
    }

    document.getElementById('busqueda').addEventListener('input', aplicarFiltros);
    document.getElementById('ordenar').addEventListener('change', aplicarFiltros);
    document.getElementById('rango-precio').addEventListener('input', aplicarFiltros);
});

function renderizarCategorias(categorias) {
    const grupo = document.querySelector('.grupo-categorias');
    if (!grupo) return;
    grupo.innerHTML = categorias.map(cat => `
        <label><input type="checkbox" class="filtro-categoria" value="${cat.id_categoria}" checked> ${cat.nombre}</label>
    `).join('');
    grupo.querySelectorAll('input[type="checkbox"]').forEach(chk => {
        chk.addEventListener('change', aplicarFiltros);
    });
}

function renderizarFiltrosTalla() {
    const grupo = document.getElementById('filtro-talla');
    if (!grupo || !todasLasVariantes.length) return;
    const tallas = [...new Set(todasLasVariantes.map(v => v.talla))];
    grupo.innerHTML = tallas.map(t => `
        <label><input type="checkbox" class="filtro-talla" value="${t}" checked> ${t}</label>
    `).join('');
    grupo.querySelectorAll('input[type="checkbox"]').forEach(chk => {
        chk.addEventListener('change', aplicarFiltros);
    });
}

function renderizarFiltrosColor() {
    const grupo = document.getElementById('filtro-color');
    if (!grupo || !todasLasVariantes.length) return;
    const colores = [...new Set(todasLasVariantes.map(v => v.color))];
    grupo.innerHTML = colores.map(c => `
        <label><input type="checkbox" class="filtro-color" value="${c}" checked> ${c}</label>
    `).join('');
    grupo.querySelectorAll('input[type="checkbox"]').forEach(chk => {
        chk.addEventListener('change', aplicarFiltros);
    });
}

function obtenerVariantesProducto(idProducto) {
    return todasLasVariantes.filter(v => v.id_producto === idProducto && v.activa);
}

function aplicarFiltros() {
    const texto = document.getElementById('busqueda').value.toLowerCase();
    const catsSeleccionadas = Array.from(document.querySelectorAll('.filtro-categoria:checked')).map(c => parseInt(c.value));
    const tallasSel = Array.from(document.querySelectorAll('.filtro-talla:checked')).map(c => c.value);
    const coloresSel = Array.from(document.querySelectorAll('.filtro-color:checked')).map(c => c.value);
    const precioMax = parseInt(document.getElementById('rango-precio').value);
    const orden = document.getElementById('ordenar').value;

    document.getElementById('valor-precio').textContent = `Bs. ${precioMax}`;

    let filtrados = todosLosProductos.filter(p => {
        if (!p.activo) return false;
        if (texto && !p.nombre.toLowerCase().includes(texto)) return false;
        if (catsSeleccionadas.length && !catsSeleccionadas.includes(p.id_categoria)) return false;
        if (p.precio_base > precioMax) return false;

        // Filtro por talla/color: ver si el producto tiene variantes que coincidan
        if (tallasSel.length || coloresSel.length) {
            const variantes = obtenerVariantesProducto(p.id_producto);
            if (!variantes.length) return false;
            const tieneTalla = tallasSel.length === 0 || variantes.some(v => tallasSel.includes(v.talla));
            const tieneColor = coloresSel.length === 0 || variantes.some(v => coloresSel.includes(v.color));
            if (!tieneTalla || !tieneColor) return false;
        }

        return true;
    });

    if (orden === 'menor') filtrados.sort((a,b) => a.precio_base - b.precio_base);
    else if (orden === 'mayor') filtrados.sort((a,b) => b.precio_base - a.precio_base);

    renderizarProductos(filtrados);
}

function renderizarProductos(lista) {
    const grid = document.getElementById('lista-productos');
    grid.innerHTML = '';
    if (!lista.length) {
        grid.innerHTML = '<p style="grid-column:1/-1;text-align:center;padding:40px;color:rgba(255,255,255,0.5);">No se encontraron productos</p>';
        return;
    }
    lista.forEach(p => {
        const imgUrl = p.imagenes && p.imagenes.length > 0
            ? p.imagenes.find(i => i.es_principal)?.url || p.imagenes[0].url
            : '/static/img/placeholder.jpg';
        const card = document.createElement('article');
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
}
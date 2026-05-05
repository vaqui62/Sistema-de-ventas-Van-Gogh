const filtrosCheckbox = Array.from(document.querySelectorAll('.filtros input[type="checkbox"]'));
const rangoPrecio = document.getElementById('rango-precio');
const valorPrecio = document.getElementById('valor-precio');
const busqueda = document.getElementById('busqueda');
const ordenar = document.getElementById('ordenar');
const productos = Array.from(document.querySelectorAll('.producto-card'));

function actualizarFiltro() {
    const precioMax = Number(rangoPrecio.value);
    const textoBusqueda = busqueda.value.trim().toLowerCase();
    const categoriasSeleccionadas = filtrosCheckbox.filter(input => input.checked).map(input => input.value);

    productos.forEach(producto => {
        const categoria = producto.dataset.category.toLowerCase();
        const precio = Number(producto.dataset.price);
        const titulo = producto.querySelector('h3').textContent.toLowerCase();
        const coincideCategoria = categoriasSeleccionadas.includes(categoria);
        const coincidePrecio = precio <= precioMax;
        const coincideBusqueda = titulo.includes(textoBusqueda);

        producto.style.display = (coincideCategoria && coincidePrecio && coincideBusqueda) ? 'grid' : 'none';
    });
}

function ordenarProductos() {
    const opcion = ordenar.value;
    const contenedor = document.getElementById('lista-productos');
    const tarjetas = Array.from(productos);

    tarjetas.sort((a, b) => {
        const precioA = Number(a.dataset.price);
        const precioB = Number(b.dataset.price);

        if (opcion === 'menor') return precioA - precioB;
        if (opcion === 'mayor') return precioB - precioA;
        return 0;
    });

    tarjetas.forEach(tarjeta => contenedor.appendChild(tarjeta));
}

rangoPrecio.addEventListener('input', () => {
    valorPrecio.textContent = `Bs. ${rangoPrecio.value}`;
    actualizarFiltro();
});

busqueda.addEventListener('input', actualizarFiltro);
filtrosCheckbox.forEach(input => input.addEventListener('change', actualizarFiltro));
ordenar.addEventListener('change', () => {
    ordenarProductos();
    actualizarFiltro();
});

window.addEventListener('DOMContentLoaded', () => {
    ordenarProductos();
    actualizarFiltro();
});
const urlParams = new URLSearchParams(window.location.search);
const idProducto = urlParams.get('id');

document.addEventListener('DOMContentLoaded', async () => {
    if (!idProducto) {
        document.getElementById('nombre-producto').textContent = 'Producto no encontrado';
        return;
    }
    try {
        const producto = await fetchGet(`/productos/${idProducto}`);
        renderizarProducto(producto);
    } catch (err) {
        console.error(err);
        alert('Error al cargar el producto');
    }
    configurarAuth();
});

function renderizarProducto(p) {
    document.getElementById('nombre-producto').textContent = p.nombre;
    document.getElementById('precio-producto').textContent = `Bs. ${p.precio_base}`;
    document.getElementById('descripcion-txt').textContent = p.descripcion || 'Sin descripción disponible.';
    document.getElementById('categoria-txt').textContent = p.categoria;
    document.getElementById('stock-num').textContent = '...';

    // Info de la obra
    const obraInfo = document.getElementById('obra-info');
    if (p.obra_vangogh) {
        obraInfo.innerHTML = `
            <p><strong>Inspirado en:</strong> "${p.obra_vangogh}"${p.anio_obra ? ` (${p.anio_obra})` : ''}</p>
        `;
    }

    // Galería de imágenes
    const imgPrincipal = document.getElementById('img-principal');
    const galeria = document.getElementById('galeria-imagenes');

    if (p.imagenes && p.imagenes.length > 0) {
        imgPrincipal.src = p.imagenes[0].url;
        imgPrincipal.onerror = () => { imgPrincipal.src = '/static/img/placeholder.jpg'; };

        if (p.imagenes.length > 1) {
            galeria.innerHTML = p.imagenes.map((img, i) => `
                <img src="${img.url}" alt="${img.alt_text || p.nombre}"
                     class="${i === 0 ? 'activa' : ''}"
                     onclick="cambiarImagen(this, '${img.url}')"
                     onerror="this.src='/static/img/placeholder.jpg'">
            `).join('');
            galeria.style.display = 'flex';
        }
    } else {
        imgPrincipal.src = '/static/img/placeholder.jpg';
    }

    // Variantes
    const selectTalla = document.getElementById('talla');
    selectTalla.innerHTML = '';
    if (!p.variantes || p.variantes.length === 0) {
        selectTalla.innerHTML = '<option value="">Sin variantes disponibles</option>';
        document.getElementById('stock-num').textContent = '0';
        return;
    }

    p.variantes.forEach(v => {
        const option = document.createElement('option');
        option.value = v.id_variante;
        option.textContent = `Talla ${v.talla} (stock: ${v.stock})`;
        selectTalla.appendChild(option);
    });

    selectTalla.addEventListener('change', () => {
        const varianteId = parseInt(selectTalla.value);
        const variante = p.variantes.find(v => v.id_variante === varianteId);
        if (variante) {
            const precioTotal = parseFloat(p.precio_base) + parseFloat(variante.precio_extra);
            document.getElementById('precio-producto').textContent = `Bs. ${precioTotal.toFixed(2)}`;
            document.getElementById('stock-num').textContent = variante.stock;
        }
    });

    if (p.variantes.length > 0) {
        selectTalla.dispatchEvent(new Event('change'));
    }

    function agregarAlCarrito() {
        const varianteId = parseInt(selectTalla.value);
        const cantidad = parseInt(document.getElementById('cantidad').value);
        const variante = p.variantes.find(v => v.id_variante === varianteId);
        if (!variante || cantidad > variante.stock) {
            alert('Stock insuficiente');
            return null;
        }
        const carrito = JSON.parse(localStorage.getItem('carrito') || '[]');
        const itemExistente = carrito.find(i => i.id_variante === varianteId);
        if (itemExistente) {
            itemExistente.cantidad += cantidad;
        } else {
            carrito.push({
                id_variante: varianteId,
                nombre: p.nombre,
                talla: variante.talla,
                color: variante.color,
                precio_unitario: parseFloat(p.precio_base) + parseFloat(variante.precio_extra),
                cantidad
            });
        }
        localStorage.setItem('carrito', JSON.stringify(carrito));
        return variante;
    }

    document.getElementById('btn-agregar').addEventListener('click', () => {
        if (agregarAlCarrito()) {
            alert('Agregado al carrito');
        }
    });

    document.getElementById('btn-comprar-ahora').addEventListener('click', () => {
        if (agregarAlCarrito()) {
            window.location.href = '/carrito';
        }
    });
}

function cambiarImagen(el, url) {
    document.getElementById('img-principal').src = url;
    document.querySelectorAll('#galeria-imagenes img').forEach(i => i.classList.remove('activa'));
    el.classList.add('activa');
}

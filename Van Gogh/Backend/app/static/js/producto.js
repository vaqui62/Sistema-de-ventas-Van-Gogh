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
    document.getElementById('descripcion-txt').textContent = p.descripcion || '';
    document.getElementById('categoria-txt').textContent = p.categoria;
    document.getElementById('stock-num').textContent = '...';

    const img = document.getElementById('img-principal');
    if (p.imagenes && p.imagenes.length > 0) {
        img.src = p.imagenes[0].url;
    } else {
        img.src = '/static/img/placeholder.jpg';
    }

    const selectTalla = document.getElementById('talla');
    selectTalla.innerHTML = '';
    if (p.variantes.length === 0) {
        selectTalla.innerHTML = '<option value="">Sin variantes</option>';
        document.getElementById('stock-num').textContent = '0';
        return;
    }

    p.variantes.forEach(v => {
        const option = document.createElement('option');
        option.value = v.id_variante;
        option.textContent = `${v.talla} - ${v.color} (stock: ${v.stock})`;
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

    document.getElementById('btn-agregar').addEventListener('click', () => {
        const varianteId = parseInt(selectTalla.value);
        const cantidad = parseInt(document.getElementById('cantidad').value);
        const variante = p.variantes.find(v => v.id_variante === varianteId);
        if (!variante || cantidad > variante.stock) {
            alert('Stock insuficiente');
            return;
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
        alert('Agregado al carrito');
        window.location.href = '/catalogo';
    });
}
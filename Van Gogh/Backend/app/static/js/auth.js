function configurarAuth() {
    const userMenu = document.querySelector('.dropdown-content');
    if (!userMenu) return;

    const sesion = obtenerSesion();
    userMenu.innerHTML = '';

    if (sesion) {
        userMenu.innerHTML = `
            <a href="#" style="pointer-events:none; color: #d4af37;">Hola, ${sesion.nombres}</a>
            ${sesion.rol === 'comprador' ? '<a href="/perfil">Mi Perfil</a>' : ''}
            <a href="#" id="btn-logout">Cerrar sesión</a>
        `;
        document.getElementById('btn-logout').addEventListener('click', cerrarSesion);
    } else {
        userMenu.innerHTML = `
            <a href="/login">Iniciar Sesión</a>
            <a href="/registro">Registrarse</a>
        `;
    }
}

async function manejarLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;
    try {
        const data = await fetchPost('/usuarios/login', { email, password });
        guardarSesion(data);
        alert('Inicio de sesión exitoso');
        // Redirigir según rol
        if (data.rol === 'empleado' || data.rol === 'gerente') {
            window.location.href = '/admin';
        } else {
            window.location.href = '/';
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function manejarRegistro(e) {
    e.preventDefault();
    const nombres = document.getElementById('reg-nombres').value.trim();
    const apellido_1 = document.getElementById('reg-apellido1').value.trim();
    const apellido_2 = document.getElementById('reg-apellido2').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;
    const telefono = document.getElementById('reg-telefono').value.trim();

    try {
        const data = await fetchPost('/usuarios/', {
            nombres,
            apellido_1,
            apellido_2,
            email,
            password,
            rol: 'comprador',
            telefono
        });
        alert('Cuenta creada con éxito. Ahora inicia sesión.');
        window.location.href = '/login';
    } catch (error) {
        alert('Error: ' + error.message);
    }
}
function insertarIconoCarrito() {
    const userMenu = document.querySelector('.user-menu');
    if (!userMenu) return;
    // Verificar si ya existe para no duplicar
    if (document.getElementById('cart-icon-container')) return;

    const cartLink = document.createElement('a');
    cartLink.href = '/carrito';
    cartLink.id = 'cart-icon-container';
    cartLink.className = 'cart-link';
    cartLink.style.position = 'relative';
    cartLink.style.marginLeft = '15px';
    cartLink.innerHTML = `
        <span class="material-symbols-outlined" style="font-size:28px; color:#dfdd8c;">shopping_cart</span>
        <span id="cart-count" style="position: absolute; top: -5px; right: -8px; background: #ff4757; color: white; border-radius: 50%; padding: 2px 6px; font-size: 12px; display: none;">0</span>
    `;
    userMenu.appendChild(cartLink);

    // Actualizar contador cada vez que cambie el carrito (se llama desde carrito.js también)
    function refrescarContador() {
        const carrito = JSON.parse(localStorage.getItem('carrito') || '[]');
        const total = carrito.reduce((sum, item) => sum + item.cantidad, 0);
        const badge = document.getElementById('cart-count');
        if (badge) {
            badge.textContent = total;
            badge.style.display = total > 0 ? 'block' : 'none';
        }
    }
    // Escuchar cambios en otras pestañas (opcional)
    window.addEventListener('storage', refrescarContador);
    refrescarContador();
}

// Ejecutar después de que el DOM esté listo (ya que configurarAuth se llama en cada página)
document.addEventListener('DOMContentLoaded', () => {
    insertarIconoCarrito();
});
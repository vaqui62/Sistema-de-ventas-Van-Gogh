const API_BASE = 'http://localhost:5000/api';

async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
        headers: { 'Content-Type': 'application/json' },
        ...options
    };
    const response = await fetch(url, config);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Error en la solicitud');
    return data;
}

function getUsuario() {
    try {
        return JSON.parse(localStorage.getItem('usuario'));
    } catch {
        return null;
    }
}

function setUsuario(data) {
    localStorage.setItem('usuario', JSON.stringify(data));
}

function logout() {
    localStorage.removeItem('usuario');
    window.location.href = 'inicio.html';
}

function actualizarNav() {
    const usuario = getUsuario();
    const dropdown = document.querySelector('.dropdown-content');
    if (!dropdown) return;

    if (usuario) {
        dropdown.innerHTML = `
            <a style="color:#d4af37;font-weight:bold;">${usuario.nombres}</a>
            ${usuario.rol === 'gerente' || usuario.rol === 'empleado' ? '<a href="historial.html">Historial de Pedidos</a>' : ''}
            <a href="#" onclick="logout(); return false;">Cerrar Sesión</a>
        `;
    } else {
        dropdown.innerHTML = `
            <a href="login.html">Iniciar Sesión</a>
            <a href="registro.html">Registrarse</a>
        `;
    }
}

document.addEventListener('DOMContentLoaded', actualizarNav);

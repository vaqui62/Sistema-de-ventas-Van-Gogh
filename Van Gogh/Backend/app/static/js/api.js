const API_BASE = 'http://127.0.0.1:5000/api';

function guardarSesion(usuario) {
    localStorage.setItem('usuario', JSON.stringify(usuario));
}

function obtenerSesion() {
    const data = localStorage.getItem('usuario');
    return data ? JSON.parse(data) : null;
}

function cerrarSesion() {
    localStorage.removeItem('usuario');
    window.location.href = '/';
}

async function fetchGet(endpoint) {
    const res = await fetch(`${API_BASE}${endpoint}`);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
}

async function fetchPost(endpoint, body) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
}

async function fetchPut(endpoint, body) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
}

async function fetchPatch(endpoint, body) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
}

async function fetchDelete(endpoint) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'DELETE'
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
}
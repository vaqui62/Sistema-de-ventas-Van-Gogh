document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('login-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value;

        try {
            const data = await apiRequest('/usuarios/login', {
                method: 'POST',
                body: JSON.stringify({ email, password })
            });
            setUsuario(data);
            alert(`¡Bienvenido ${data.nombres}!`);
            window.location.href = 'inicio.html';
        } catch (err) {
            alert('Error: ' + err.message);
        }
    });
});

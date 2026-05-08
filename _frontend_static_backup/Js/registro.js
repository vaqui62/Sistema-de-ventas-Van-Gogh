document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registro-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const nombres = document.getElementById('reg-nombres').value.trim();
        const apellido1 = document.getElementById('reg-apellido1').value.trim();
        const email = document.getElementById('reg-email').value.trim();
        const password = document.getElementById('reg-password').value;
        const telefono = document.getElementById('reg-telefono').value.trim();

        try {
            const data = await apiRequest('/usuarios/', {
                method: 'POST',
                body: JSON.stringify({
                    nombres,
                    apellido_1: apellido1,
                    email,
                    password,
                    telefono: telefono || undefined,
                    rol: 'comprador',
                })
            });
            alert('Cuenta creada exitosamente. Ahora inicia sesión.');
            window.location.href = 'login.html';
        } catch (err) {
            alert('Error: ' + err.message);
        }
    });
});

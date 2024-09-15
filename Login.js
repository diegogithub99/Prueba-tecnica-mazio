import React, { useState } from 'react';

function Login({ setAuthToken }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('https://dexrabg564vqo6pkhahe3puj6q0uthwf.lambda-url.us-east-2.on.aws/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();
      if (response.ok) {
        setAuthToken(data.access_token);
        localStorage.setItem('token', data.access_token); // Guardar el token en localStorage
      } else {
        setError('Credenciales incorrectas');
      }
    } catch (err) {
      setError('Error en el servidor');
    }
  };

  return (
    <div>
      <h1>Iniciar sesión</h1>
      <form onSubmit={handleLogin}>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Usuario"
          required
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Contraseña"
          required
        />
        <button type="submit">Iniciar sesión</button>
      </form>
      {error && <p>{error}</p>}
    </div>
  );
}

export default Login;

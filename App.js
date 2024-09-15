import React, { useState, useEffect } from 'react';
import Login from './Login'; // Importar el componente de Login
import './App.css'; // Archivo CSS para mejorar la estética

function App() {
  const [authToken, setAuthToken] = useState(localStorage.getItem('token') || ''); // Guardar el token en el estado
  const [pedidos, setPedidos] = useState([]);
  const [metricas, setMetricas] = useState(null); // Para guardar las métricas
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPedidos = async () => {
      if (!authToken) return; // Solo llamar la API si hay un token

      try {
        const response = await fetch('https://dexrabg564vqo6pkhahe3puj6q0uthwf.lambda-url.us-east-2.on.aws/pedidos', {
          headers: {
            Authorization: `Bearer ${authToken}`, // Usar el token guardado
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        setPedidos(data.pedidos);
      } catch (err) {
        setError(err.message);
      }
    };

    const fetchMetricas = async () => {
      if (!authToken) return;

      try {
        const response = await fetch('https://dexrabg564vqo6pkhahe3puj6q0uthwf.lambda-url.us-east-2.on.aws/metrics', {
          headers: {
            Authorization: `Bearer ${authToken}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        setMetricas(data);
      } catch (err) {
        setError(err.message);
      }
    };

    fetchPedidos();
    fetchMetricas();
  }, [authToken]);

  // Función para cerrar sesión
  const handleLogout = () => {
    localStorage.removeItem('token');
    setAuthToken(''); // Limpiar el estado del token
  };

  return (
    <div className="app-container">
      {!authToken ? (
        <Login setAuthToken={setAuthToken} /> // Si no hay token, mostrar el formulario de login
      ) : (
        <div>
          <div className="header">
            <h1>Monitoreo de Indicadores - Cargo Express</h1>
            <button onClick={handleLogout} className="logout-button">Cerrar sesión</button>
          </div>

          {error && <p>Error: {error}</p>}

          <h2>Métricas del Día</h2>
          {metricas && (
            <div className="metrics-container">
              <p>Top 3 Productos más Vendidos:</p>
              <ul>
                {metricas.top_3_productos.map(([producto, cantidad]) => (
                  <li key={producto}>{producto}: {cantidad} vendidos</li>
                ))}
              </ul>
              <p>Precio Promedio por Pedido: ${metricas.precio_promedio_por_pedido.toFixed(2)}</p>
              <p>Acumulado en Ventas del Día: ${metricas.acumulado_ventas_dia.toFixed(2)}</p>
            </div>
          )}

          <h2>Listado de Pedidos</h2>
          <ul>
            {pedidos.map((pedido) => (
              <li key={pedido.pedido_id}>
                Pedido ID: {pedido.pedido_id}, Repartidor: {pedido.repartidor.Nombre}, Productos: {pedido.productos.length}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;

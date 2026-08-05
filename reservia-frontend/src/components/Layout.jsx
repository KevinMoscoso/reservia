import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate('/login');
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="flex items-center justify-between bg-white px-6 py-4 shadow-sm">
        <span className="text-lg font-semibold text-gray-800">Reservia</span>
        <div className="flex items-center gap-4">
          {user && (
            <span className="text-sm text-gray-600">
              {user.full_name} ({user.role})
            </span>
          )}
          <button
            onClick={handleLogout}
            className="rounded bg-red-600 px-3 py-1.5 text-sm text-white hover:bg-red-700"
          >
            Cerrar sesión
          </button>
        </div>
      </header>
      <nav className="flex gap-4 border-b border-gray-200 bg-white px-6 py-2 text-sm">
        <Link to="/recursos/salas">Salas</Link>
        <Link to="/recursos/equipos">Equipos</Link>
        <Link to="/proveedores">Proveedores</Link>
        <Link to="/mis-reservas">Mis reservas</Link>
      </nav>
      <main className="p-6">{children}</main>
    </div>
  );
}

export default Layout;
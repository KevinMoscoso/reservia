import { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import { createSala, deactivateSala, listSalas, updateSala } from '../api/resources';

function isCapacidadValid(capacidad) {
  const value = Number(capacidad);
  return Number.isInteger(value) && value > 0;
}

function SalasPage() {
  const [salas, setSalas] = useState([]);
  const [loading, setLoading] = useState(true);

  const [nombre, setNombre] = useState('');
  const [ubicacion, setUbicacion] = useState('');
  const [capacidad, setCapacidad] = useState('');
  const [createError, setCreateError] = useState('');

  const [editingId, setEditingId] = useState(null);
  const [editNombre, setEditNombre] = useState('');
  const [editUbicacion, setEditUbicacion] = useState('');
  const [editCapacidad, setEditCapacidad] = useState('');
  const [editError, setEditError] = useState('');

  useEffect(() => {
    listSalas()
      .then((data) => setSalas(data))
      .finally(() => setLoading(false));
  }, []);

  async function handleCreate(event) {
    event.preventDefault();
    setCreateError('');

    if (!isCapacidadValid(capacidad)) {
      setCreateError('La capacidad debe ser un número entero mayor a 0.');
      return;
    }

    try {
      const nuevaSala = await createSala({
        nombre,
        ubicacion,
        capacidad: Number(capacidad),
      });
      setSalas((prev) => [...prev, nuevaSala]);
      setNombre('');
      setUbicacion('');
      setCapacidad('');
    } catch (err) {
      setCreateError(err.message);
    }
  }

  function startEdit(sala) {
    setEditingId(sala.id);
    setEditNombre(sala.nombre);
    setEditUbicacion(sala.ubicacion);
    setEditCapacidad(String(sala.capacidad));
    setEditError('');
  }

  function cancelEdit() {
    setEditingId(null);
    setEditError('');
  }

  async function handleSaveEdit(id) {
    setEditError('');

    if (!isCapacidadValid(editCapacidad)) {
      setEditError('La capacidad debe ser un número entero mayor a 0.');
      return;
    }

    try {
      const actualizada = await updateSala(id, {
        nombre: editNombre,
        ubicacion: editUbicacion,
        capacidad: Number(editCapacidad),
      });
      setSalas((prev) => prev.map((sala) => (sala.id === id ? actualizada : sala)));
      setEditingId(null);
    } catch (err) {
      setEditError(err.message);
    }
  }

  async function handleDeactivate(id) {
    const actualizada = await deactivateSala(id);
    setSalas((prev) => prev.map((sala) => (sala.id === id ? actualizada : sala)));
  }

  if (loading) {
    return (
      <Layout>
        <div>Cargando...</div>
      </Layout>
    );
  }

  return (
    <Layout>
      <h1 className="mb-4 text-xl font-semibold text-gray-800">Salas</h1>

      <form onSubmit={handleCreate} className="mb-6 flex max-w-sm flex-col gap-3">
        {createError && <p className="text-sm text-red-600">{createError}</p>}

        <div>
          <label htmlFor="nombre" className="mb-1 block text-sm text-gray-700">
            Nombre
          </label>
          <input
            id="nombre"
            type="text"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            className="w-full rounded border border-gray-300 px-3 py-2"
            required
          />
        </div>

        <div>
          <label htmlFor="ubicacion" className="mb-1 block text-sm text-gray-700">
            Ubicación
          </label>
          <input
            id="ubicacion"
            type="text"
            value={ubicacion}
            onChange={(e) => setUbicacion(e.target.value)}
            className="w-full rounded border border-gray-300 px-3 py-2"
            required
          />
        </div>

        <div>
          <label htmlFor="capacidad" className="mb-1 block text-sm text-gray-700">
            Capacidad
          </label>
          <input
            id="capacidad"
            type="number"
            value={capacidad}
            onChange={(e) => setCapacidad(e.target.value)}
            className="w-full rounded border border-gray-300 px-3 py-2"
            required
          />
        </div>

        <button
          type="submit"
          className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          Crear sala
        </button>
      </form>

      {editError && <p className="mb-2 text-sm text-red-600">{editError}</p>}

      <table className="w-full border-collapse text-left text-sm">
        <thead>
          <tr className="border-b border-gray-300">
            <th className="py-2">Nombre</th>
            <th className="py-2">Ubicación</th>
            <th className="py-2">Capacidad</th>
            <th className="py-2">Estado</th>
            <th className="py-2">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {salas.map((sala) => {
            const isEditing = editingId === sala.id;
            const isActive = sala.estado === 'active';

            return (
              <tr
                key={sala.id}
                className={`border-b border-gray-100 ${!isActive ? 'text-gray-400' : ''}`}
              >
                {isEditing ? (
                  <>
                    <td className="py-2">
                      <input
                        aria-label={`editar-nombre-${sala.id}`}
                        value={editNombre}
                        onChange={(e) => setEditNombre(e.target.value)}
                        className="w-full rounded border border-gray-300 px-2 py-1"
                      />
                    </td>
                    <td className="py-2">
                      <input
                        aria-label={`editar-ubicacion-${sala.id}`}
                        value={editUbicacion}
                        onChange={(e) => setEditUbicacion(e.target.value)}
                        className="w-full rounded border border-gray-300 px-2 py-1"
                      />
                    </td>
                    <td className="py-2">
                      <input
                        aria-label={`editar-capacidad-${sala.id}`}
                        type="number"
                        value={editCapacidad}
                        onChange={(e) => setEditCapacidad(e.target.value)}
                        className="w-full rounded border border-gray-300 px-2 py-1"
                      />
                    </td>
                    <td className="py-2">{sala.estado}</td>
                    <td className="py-2">
                      <button
                        onClick={() => handleSaveEdit(sala.id)}
                        className="mr-2 rounded bg-blue-600 px-2 py-1 text-white"
                      >
                        Guardar
                      </button>
                      <button onClick={cancelEdit} className="rounded bg-gray-300 px-2 py-1">
                        Cancelar
                      </button>
                    </td>
                  </>
                ) : (
                  <>
                    <td className="py-2">{sala.nombre}</td>
                    <td className="py-2">{sala.ubicacion}</td>
                    <td className="py-2">{sala.capacidad}</td>
                    <td className="py-2">{sala.estado}</td>
                    <td className="py-2">
                      {isActive && (
                        <>
                          <button
                            onClick={() => startEdit(sala)}
                            className="mr-2 rounded bg-blue-600 px-2 py-1 text-white"
                          >
                            Editar
                          </button>
                          <button
                            onClick={() => handleDeactivate(sala.id)}
                            className="rounded bg-red-600 px-2 py-1 text-white"
                          >
                            Desactivar
                          </button>
                        </>
                      )}
                    </td>
                  </>
                )}
              </tr>
            );
          })}
        </tbody>
      </table>
    </Layout>
  );
}

export default SalasPage;
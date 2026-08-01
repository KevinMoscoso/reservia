import { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import { createEquipo, deactivateEquipo, listEquipos, updateEquipo } from '../api/resources';

function EquiposPage() {
  const [equipos, setEquipos] = useState([]);
  const [loading, setLoading] = useState(true);

  const [nombre, setNombre] = useState('');
  const [codigo, setCodigo] = useState('');
  const [categoria, setCategoria] = useState('');
  const [createError, setCreateError] = useState('');

  const [editingId, setEditingId] = useState(null);
  const [editNombre, setEditNombre] = useState('');
  const [editCodigo, setEditCodigo] = useState('');
  const [editCategoria, setEditCategoria] = useState('');
  const [editError, setEditError] = useState('');

  useEffect(() => {
    listEquipos()
      .then((data) => setEquipos(data))
      .finally(() => setLoading(false));
  }, []);

  async function handleCreate(event) {
    event.preventDefault();
    setCreateError('');

    try {
      const nuevoEquipo = await createEquipo({ nombre, codigo, categoria });
      setEquipos((prev) => [...prev, nuevoEquipo]);
      setNombre('');
      setCodigo('');
      setCategoria('');
    } catch (err) {
      setCreateError(err.message);
    }
  }

  function startEdit(equipo) {
    setEditingId(equipo.id);
    setEditNombre(equipo.nombre);
    setEditCodigo(equipo.codigo);
    setEditCategoria(equipo.categoria);
    setEditError('');
  }

  function cancelEdit() {
    setEditingId(null);
    setEditError('');
  }

  async function handleSaveEdit(id) {
    setEditError('');

    try {
      const actualizado = await updateEquipo(id, {
        nombre: editNombre,
        codigo: editCodigo,
        categoria: editCategoria,
      });
      setEquipos((prev) => prev.map((equipo) => (equipo.id === id ? actualizado : equipo)));
      setEditingId(null);
    } catch (err) {
      setEditError(err.message);
    }
  }

  async function handleDeactivate(id) {
    const actualizado = await deactivateEquipo(id);
    setEquipos((prev) => prev.map((equipo) => (equipo.id === id ? actualizado : equipo)));
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
      <h1 className="mb-4 text-xl font-semibold text-gray-800">Equipos</h1>

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
          <label htmlFor="codigo" className="mb-1 block text-sm text-gray-700">
            Código
          </label>
          <input
            id="codigo"
            type="text"
            value={codigo}
            onChange={(e) => setCodigo(e.target.value)}
            className="w-full rounded border border-gray-300 px-3 py-2"
            required
          />
        </div>

        <div>
          <label htmlFor="categoria" className="mb-1 block text-sm text-gray-700">
            Categoría
          </label>
          <input
            id="categoria"
            type="text"
            value={categoria}
            onChange={(e) => setCategoria(e.target.value)}
            className="w-full rounded border border-gray-300 px-3 py-2"
            required
          />
        </div>

        <button
          type="submit"
          className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          Crear equipo
        </button>
      </form>

      {editError && <p className="mb-2 text-sm text-red-600">{editError}</p>}

      <table className="w-full border-collapse text-left text-sm">
        <thead>
          <tr className="border-b border-gray-300">
            <th className="py-2">Nombre</th>
            <th className="py-2">Código</th>
            <th className="py-2">Categoría</th>
            <th className="py-2">Estado</th>
            <th className="py-2">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {equipos.map((equipo) => {
            const isEditing = editingId === equipo.id;
            const isActive = equipo.estado === 'active';

            return (
              <tr
                key={equipo.id}
                className={`border-b border-gray-100 ${!isActive ? 'text-gray-400' : ''}`}
              >
                {isEditing ? (
                  <>
                    <td className="py-2">
                      <input
                        aria-label={`editar-nombre-${equipo.id}`}
                        value={editNombre}
                        onChange={(e) => setEditNombre(e.target.value)}
                        className="w-full rounded border border-gray-300 px-2 py-1"
                      />
                    </td>
                    <td className="py-2">
                      <input
                        aria-label={`editar-codigo-${equipo.id}`}
                        value={editCodigo}
                        onChange={(e) => setEditCodigo(e.target.value)}
                        className="w-full rounded border border-gray-300 px-2 py-1"
                      />
                    </td>
                    <td className="py-2">
                      <input
                        aria-label={`editar-categoria-${equipo.id}`}
                        value={editCategoria}
                        onChange={(e) => setEditCategoria(e.target.value)}
                        className="w-full rounded border border-gray-300 px-2 py-1"
                      />
                    </td>
                    <td className="py-2">{equipo.estado}</td>
                    <td className="py-2">
                      <button
                        onClick={() => handleSaveEdit(equipo.id)}
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
                    <td className="py-2">{equipo.nombre}</td>
                    <td className="py-2">{equipo.codigo}</td>
                    <td className="py-2">{equipo.categoria}</td>
                    <td className="py-2">{equipo.estado}</td>
                    <td className="py-2">
                      {isActive && (
                        <>
                          <button
                            onClick={() => startEdit(equipo)}
                            className="mr-2 rounded bg-blue-600 px-2 py-1 text-white"
                          >
                            Editar
                          </button>
                          <button
                            onClick={() => handleDeactivate(equipo.id)}
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

export default EquiposPage;
import { useState } from 'react';
import Layout from '../components/Layout';
import { createProvider } from '../api/auth';

function isPasswordValid(password) {
  return password.length >= 8 && /\d/.test(password);
}

function CreateProviderPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    setSuccess('');

    if (!isPasswordValid(password)) {
      setError('La contraseña debe tener al menos 8 caracteres y un dígito.');
      return;
    }

    try {
      await createProvider({ email, password, full_name: fullName });
      setSuccess('Proveedor creado exitosamente');
      setEmail('');
      setPassword('');
      setFullName('');
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <Layout>
      <div className="max-w-sm">
        <h1 className="mb-4 text-xl font-semibold text-gray-800">Crear proveedor</h1>

        {success && <p className="mb-4 text-sm text-green-600">{success}</p>}
        {error && <p className="mb-4 text-sm text-red-600">{error}</p>}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label htmlFor="full_name" className="mb-1 block text-sm text-gray-700">
              Nombre completo
            </label>
            <input
              id="full_name"
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full rounded border border-gray-300 px-3 py-2"
              required
            />
          </div>

          <div>
            <label htmlFor="email" className="mb-1 block text-sm text-gray-700">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded border border-gray-300 px-3 py-2"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="mb-1 block text-sm text-gray-700">
              Contraseña
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded border border-gray-300 px-3 py-2"
              required
            />
          </div>

          <button
            type="submit"
            className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
          >
            Crear proveedor
          </button>
        </form>
      </div>
    </Layout>
  );
}

export default CreateProviderPage;
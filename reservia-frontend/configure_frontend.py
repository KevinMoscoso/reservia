"""
Script de configuracion para Reservia Frontend.
Ejecutar UNA sola vez, DESPUES de:
    npm create vite@latest reservia-frontend -- --template react
    npm install
    npm install tailwindcss @tailwindcss/vite
    npm install react-router-dom
Ejecutar dentro de la carpeta reservia-frontend/.

NOTA: usa Tailwind CSS v4 (plugin de Vite). No genera tailwind.config.js
ni postcss.config.js porque ya no son necesarios en esta version.

Uso:
    python configure_frontend.py
"""
import os

VITE_CONFIG = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
"""

INDEX_CSS = """@import "tailwindcss";
"""

APP_JSX = """function App() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100">
      <div className="bg-white shadow-md rounded-lg p-8 text-center">
        <h1 className="text-2xl font-bold text-slate-800">Reservia</h1>
        <p className="text-slate-500 mt-2">Frontend base funcionando correctamente.</p>
      </div>
    </div>
  )
}

export default App
"""


def main():
    with open("vite.config.js", "w", encoding="utf-8") as f:
        f.write(VITE_CONFIG)
    print("Configurado: vite.config.js (plugin Tailwind v4 + proxy /api -> http://localhost:8000)")

    with open(os.path.join("src", "index.css"), "w", encoding="utf-8") as f:
        f.write(INDEX_CSS)
    print("Configurado: src/index.css (directivas Tailwind)")

    with open(os.path.join("src", "App.jsx"), "w", encoding="utf-8") as f:
        f.write(APP_JSX)
    print("Configurado: src/App.jsx (placeholder de verificacion)")

    print("\n Frontend configurado. Siguiente paso: npm run dev")


if __name__ == "__main__":
    main()

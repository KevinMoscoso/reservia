"""
Script de scaffolding para Reservia Backend.
Crea la estructura de carpetas y archivos base (SIN logica de negocio).
Ejecutar UNA sola vez, dentro de la carpeta reservia-backend/ vacia.

Uso:
    python scaffold.py
"""
import os

FOLDERS = [
    "app",
    "app/core",
    "app/models",
    "app/models/shared",
    "app/models/auth",
    "app/schemas",
    "app/schemas/auth",
    "app/repositories",
    "app/repositories/shared",
    "app/repositories/auth",
    "app/services",
    "app/services/auth",
    "app/routers",
    "app/routers/auth",
    "app/middlewares",
    "app/utils",
    "tests",
    "tests/auth",
]

INIT_FILES = [
    "app/__init__.py",
    "app/core/__init__.py",
    "app/models/__init__.py",
    "app/models/shared/__init__.py",
    "app/models/auth/__init__.py",
    "app/schemas/__init__.py",
    "app/schemas/auth/__init__.py",
    "app/repositories/__init__.py",
    "app/repositories/shared/__init__.py",
    "app/repositories/auth/__init__.py",
    "app/services/__init__.py",
    "app/services/auth/__init__.py",
    "app/routers/__init__.py",
    "app/routers/auth/__init__.py",
    "app/middlewares/__init__.py",
    "app/utils/__init__.py",
    "tests/__init__.py",
    "tests/auth/__init__.py",
]

MAIN_PY = '''"""
Punto de entrada de la aplicacion.
NOTA: este archivo es un placeholder de verificacion.
Chat B lo reemplazara/extendera al implementar el modulo Auth & Roles
(registro de auth_router y admin_users_router).
"""
from fastapi import FastAPI

app = FastAPI(title="Reservia API")


@app.get("/health")
def health_check():
    return {"status": "ok"}
'''

REQUIREMENTS = """fastapi
uvicorn[standard]
sqlalchemy
pymysql
alembic
passlib[bcrypt]
pydantic
email-validator
pytest
httpx
"""

GITIGNORE = """venv/
__pycache__/
*.pyc
.vscode/
*.db
"""

README = """# Reservia - Backend

Proyecto de tesis: comparacion de calidad, mantenibilidad y sostenibilidad
entre desarrollo tradicional y desarrollo asistido por IA generativa.

## Como levantar el proyecto

1. Activar el entorno virtual (ver guia entregada por el Arquitecto/QA).
2. pip install -r requirements.txt
3. uvicorn app.main:app --reload
4. Verificar en el navegador: http://127.0.0.1:8000/health

## Estructura

Ver especificacion de arquitectura y el primer PROMPT PARA CHAT B
(modulo Auth & Roles) para el detalle de cada archivo.
"""


def main():
    for folder in FOLDERS:
        os.makedirs(folder, exist_ok=True)
        print(f"Carpeta creada: {folder}/")

    for init_file in INIT_FILES:
        if not os.path.exists(init_file):
            open(init_file, "w").close()
            print(f"Archivo creado: {init_file}")

    with open("app/main.py", "w", encoding="utf-8") as f:
        f.write(MAIN_PY)
    print("Archivo creado: app/main.py")

    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(REQUIREMENTS)
    print("Archivo creado: requirements.txt")

    with open(".gitignore", "w", encoding="utf-8") as f:
        f.write(GITIGNORE)
    print("Archivo creado: .gitignore")

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(README)
    print("Archivo creado: README.md")

    print("\n Estructura base creada. Siguiente paso: activar entorno virtual e instalar dependencias.")


if __name__ == "__main__":
    main()

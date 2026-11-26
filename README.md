# Talca Personas

Sistema interno de Recursos Humanos de TALCA.

El proyecto conserva la aplicación Flask estable mientras se realiza una migración incremental hacia React y Django REST Framework. La base operativa es PostgreSQL y la integración con Trilay utiliza SQL Server en modo de solo lectura.

## Estructura

- `frontend/`: React, TypeScript, Vite y Tailwind CSS.
- `backend/`: Django, Django REST Framework y aplicaciones organizadas por módulo.
- `backend/legacy-flask/`: sistema Flask/Jinja estable, conservado para operación, comparación funcional y rollback.
- `backend/scripts/`: scripts auxiliares de inicio.
- `backend/docs/`: documentación técnica y seguimiento de la migración.
- `.env.example`: referencia de configuración sin credenciales reales.

## Configuración

Crear el archivo `.env` en la raíz y completar las variables necesarias. No se deben guardar credenciales reales en Git.

La aplicación utiliza, entre otras, las variables `SECRET_KEY`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` y `TRILAY_SYNC_ENABLED`.

PostgreSQL utiliza la base `recursos_humanos` y el schema `rrhh`. La sincronización con Trilay debe permanecer desactivada en entornos de prueba salvo autorización específica.

## Aplicación estable: Flask

La versión funcional completa se inicia en Windows con:

```powershell
.\start.ps1
```

Luego se accede a:

```text
http://127.0.0.1:5000/auth/login
```

Desde Git Bash también puede iniciarse directamente:

```bash
cd backend/legacy-flask
../.venv/Scripts/python.exe app.py
```

Si el entorno virtual todavía no existe:

```bash
cd backend
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r legacy-flask/requirements.txt
```

No deben retirarse Flask, sus plantillas ni sus pruebas hasta demostrar paridad funcional y disponer de un rollback validado.

## Arquitectura en migración: Django y React

En Windows se pueden iniciar backend y frontend con:

```powershell
.\start-django.ps1
```

Inicio manual desde Git Bash, en dos terminales:

Backend:

```bash
cd backend
source .venv/Scripts/activate
python manage.py runserver 127.0.0.1:8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Direcciones de desarrollo:

- React: `http://127.0.0.1:5173`
- Django: `http://127.0.0.1:8000`
- Flask estable: `http://127.0.0.1:5000`

React y Django todavía forman parte de una migración progresiva. Para el uso funcional completo se debe utilizar Flask hasta completar la paridad.

## Pruebas

Pruebas de Django:

```bash
cd backend
.venv/Scripts/python.exe manage.py test
```

Pruebas y validaciones del frontend:

```bash
cd frontend
npm run lint
npm run build
npm run test -- --run
```

Regresión de Flask:

```bash
cd backend/legacy-flask
../.venv/Scripts/python.exe -m pip install -r requirements-test.txt
../.venv/Scripts/python.exe -m pytest -q
```

Alternativa sin Pytest:

```bash
cd backend/legacy-flask
../.venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py" -v
```

Las pruebas de Flask utilizan reglas puras, metadatos ORM, análisis estático y SQLite en memoria. La barrera `tests/safety.py` impide ejecutar la suite con Trilay activo, redes corporativas o una base PostgreSQL cuyo nombre no corresponda a pruebas.

## Seguridad

- No guardar `.env`, contraseñas, tokens ni datos personales en Git.
- No escribir en SQL Server; Trilay es una fuente de solo lectura.
- No ejecutar pruebas contra información productiva.
- No aplicar migraciones destructivas ni eliminar registros sin autorización.
- Los permisos deben validarse en el backend, no solo ocultarse en la interfaz.

## Documentación relacionada

Los documentos de `backend/docs/migration/` registran la línea base, la paridad funcional y el plan de retiro de Flask. `AGENTS.md` contiene las reglas permanentes de trabajo y seguridad del repositorio.

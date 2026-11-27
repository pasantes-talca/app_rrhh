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

### Recibos con verificación del dispositivo

El portal Flask incorpora registro de passkey y confirmación de recibos mediante WebAuthn.
Face ID se utiliza cuando el dispositivo lo ofrece; el sistema operativo puede ofrecer huella
o PIN. El servidor verifica una firma criptográfica y la verificación de usuario, sin recibir
rostros, huellas ni la clave privada. No puede determinar qué método biométrico se utilizó.
La constancia se guarda aparte del PDF; no incorpora una firma digital certificada al archivo.

La función queda desactivada hasta preparar el ambiente:

1. Instalar `backend/legacy-flask/requirements.txt` en el entorno del backend.
2. Respaldar la base destino y, previa aprobación para ese ambiente, aplicar
   `backend/legacy-flask/migrations/20261126_recibos_passkeys.sql` y luego
   `backend/legacy-flask/migrations/20261127_passkeys_perfil.sql`.
3. Configurar `WEBAUTHN_RP_ID` (dominio sin protocolo ni puerto),
   `WEBAUTHN_ORIGIN` (origen exacto con protocolo y puerto) y `RECEIPT_PASSKEY_ENABLED=true`.
4. Reiniciar Flask y validar con un empleado y un recibo de pruebas.

Para pruebas locales usar `WEBAUTHN_RP_ID=localhost` y
`WEBAUTHN_ORIGIN=http://localhost:5000`, entrando exactamente por esa dirección.
Un teléfono necesita una dirección HTTPS accesible desde él; su localhost apunta al propio
teléfono. Usar el dominio definitivo antes de registrar claves destinadas a producción.

Impacto del esquema: agrega `rrhh.recibo_credenciales`, `rrhh.recibo_desafios` y
`rrhh.recibo_firmas`, con claves foráneas a usuarios y recibos. No altera datos ni columnas
de tablas existentes en la primera migración. La segunda permite `recibo_id` nulo en
`recibo_desafios`, exclusivamente para registrar la passkey desde Mi perfil sin recibo.
El primer registro de dispositivo exige la contraseña actual;
no se admite reemplazar una clave desde el flujo de recibos. Recuperación por pérdida del
dispositivo requiere un procedimiento de identidad a cargo de Sistemas; no hay un bypass
de firma por contraseña. No se ofrecen mecanismos automáticos de recuperación todavía.

Cada desafío dura tres minutos y está ligado a usuario, sesión, PDF, recibo y respuesta.
La constancia y la respuesta se guardan juntas, con control de concurrencia en PostgreSQL.
El empleado registra la passkey en **Mi perfil → Face ID y firma de recibos**, sin necesitar
un recibo pendiente. Al responder cada recibo debe verificar su identidad nuevamente.
El endpoint antiguo de Flask y la API de respuesta en migración quedan bloqueados siempre.
Si la función está desactivada, la pantalla informa que falta habilitarla y conserva el recibo
pendiente; ya no ofrece confirmar sin verificación. Los recibos respondidos previamente
conservan su historial y no se presentan como firmados con passkey.

Rollback operativo: desactivar la variable y reiniciar suspende las nuevas firmas y mantiene
los recibos pendientes. Para volver al código anterior se requiere una decisión explícita,
porque aquella versión permite responder sin passkey. Conservar las tres
tablas y sus constancias; no ejecutar un borrado de esquema para revertir la aplicación.
Los respaldos deben incluir esas tablas y sus datos, con acceso restringido.

La activación en la base corporativa y la prueba real con Face ID están pendientes.

### Uso desde celulares

`static/css/responsive.css` adapta el menú desplegable, encabezado, formularios, tarjetas,
recibos y contenedores de tablas para pantallas pequeñas. Las tablas conservan desplazamiento
horizontal dentro de su contenedor. Bootstrap 5.3.0 y Bootstrap Icons 1.10.5 se sirven desde
`static/vendor/` (licencia MIT incluida en los archivos), evitando depender de un CDN externo
para la distribución y los controles de navegación. Las fuentes de Google conservan fuentes
del sistema como alternativa. Las pruebas visuales se realizan con registros sintéticos.

Validación del 27/11/2026: 31 pruebas aprobadas y 2 fallos esperados preexistentes en el
conjunto de regresión ejecutado. Se comprobaron 40 combinaciones de pantallas de empleado
y RRHH en anchos 360, 390, 768 y 1440, sin desbordamiento horizontal de página y con menú
móvil funcional. Se validó el flujo perfil → registro de passkey → firma del recibo →
constancia usando un autenticador virtual de Chromium. Esto no sustituye la prueba en un
iPhone físico ni valida el despliegue HTTPS corporativo. Las pruebas no usan datos del ERP
ni la base corporativa.

Los documentos de `backend/docs/migration/` registran la línea base, la paridad funcional y el plan de retiro de Flask. `AGENTS.md` contiene las reglas permanentes de trabajo y seguridad del repositorio.

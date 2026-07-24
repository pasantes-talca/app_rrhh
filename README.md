# Talca RRHH

Sistema interno de gestión de Recursos Humanos desarrollado con Flask y PostgreSQL.

## Configuración local

1. Crear un entorno virtual e instalar las dependencias:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r talca_rrhh/requirements.txt
   ```

2. Copiar `talca_rrhh/.env.example` como `talca_rrhh/.env` y configurar PostgreSQL.

3. Inicializar la base de datos:

   ```powershell
   cd talca_rrhh
   python init_db.py
   ```

4. Ejecutar la aplicación:

   ```powershell
   python app.py
   ```

Los documentos subidos y las credenciales locales están excluidos del repositorio.

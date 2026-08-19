# Talca RRHH

Sistema interno de gestión de Recursos Humanos desarrollado con Flask y PostgreSQL.

## Configuración local

1. Crear un entorno virtual e instalar las dependencias:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Copiar `.env.example` como `.env` y configurar PostgreSQL.

3. Inicializar la base de datos:

   ```powershell
   python init_db.py
   ```

4. Ejecutar la aplicación:

   ```powershell
   python app.py
   ```

Los documentos subidos y las credenciales locales están excluidos del repositorio.

# Baseline de Alembic

La base PostgreSQL ya existía antes de incorporar Alembic. La revisión `20261125_baseline` es deliberadamente no destructiva y no debe ejecutarse como mecanismo para construir una base vacía.

Procedimiento propuesto para QA, sujeto a autorización:

1. Crear backup de la base QA.
2. Configurar una URL exclusiva de QA y `TALCA_API_ENVIRONMENT=testing`.
3. Comparar el esquema real contra `Base.metadata` sin aplicar DDL.
4. Corregir únicamente diferencias documentadas y aprobadas.
5. Ejecutar `alembic stamp 20261125_baseline`, no `upgrade`, sobre la base existente.
6. Crear futuras revisiones pequeñas con `upgrade` y `downgrade` probados.

Alembic permanece bloqueado salvo que se configure explícitamente `ALLOW_ALEMBIC=true`. Nunca debe habilitarse contra producción durante una prueba.

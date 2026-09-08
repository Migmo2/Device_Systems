# Resumen del proyecto

`device_systems` evoluciono de una API basica GET/POST a una API REST con CRUD completo para usuarios.

## Cambios de la guia intermedia

- La persistencia simulada esta en `app/data/users_db.py`.
- La logica de negocio esta en `app/services/user_service.py`.
- La dependencia `get_user_or_404` esta en `app/dependencies/user_dependencies.py`.
- Los modelos `UserReplace` y `UserPatch` distinguen PUT de PATCH.
- Las rutas usan estados HTTP explicitos y documentacion OpenAPI.
- Se actualizo la documentacion, las colecciones y el flujo Git Flow.

## Verificacion

Se comprobaron GET, POST, PUT, PATCH y DELETE con `TestClient`, ademas de usuario inexistente, PATCH vacio y correo duplicado. El contrato OpenAPI confirma los seis endpoints de usuarios.

## Presentacion de cinco minutos

1. Mostrar la estructura por responsabilidades.
2. Explicar la diferencia entre PUT y PATCH.
3. Mostrar `Depends(get_user_or_404)` y el error 404 centralizado.
4. Probar Swagger y los casos de error.
5. Mostrar ramas y commits de Git Flow.
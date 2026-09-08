# Inicio rapido

## Checklist de la guia intermedia

- [x] CRUD completo de `/users`.
- [x] PUT completo y PATCH parcial.
- [x] DELETE con `204 No Content`.
- [x] Errores `400`, `404` y validacion `422`.
- [x] `Depends(get_user_or_404)` reutilizado en rutas por ID.
- [x] Swagger/OpenAPI version `2.0.0`, tags, summaries y descripciones.
- [x] Colecciones para Postman y Thunder Client.
- [x] Flujo Git Flow documentado.

## Comando

```powershell
venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Consulta `README.md` para ejemplos, estructura, estados HTTP y evidencias.
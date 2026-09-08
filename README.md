# device_systems API

API REST para administrar usuarios con FastAPI, Pydantic v2 y una base de datos en memoria. Esta version implementa la guia GA1-220501096-01-AA1-EV08: CRUD completo, errores HTTP, Swagger/OpenAPI y Dependency Injection.

## Tecnologias

- Python 3.14
- FastAPI y Uvicorn
- Pydantic v2
- Git Flow y GitHub
- Postman y Thunder Client

## Instalacion y ejecucion

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Documentacion: `http://127.0.0.1:8000/docs` y `http://127.0.0.1:8000/redoc`.

## Estructura

```text
app/
├── main.py
├── data/users_db.py
├── dependencies/user_dependencies.py
├── routes/user_routes.py
├── schemas/user_schema.py
└── services/user_service.py
```

`routes` recibe peticiones, `schemas` valida datos, `services` concentra la logica, `data` simula persistencia y `dependencies` reutiliza validaciones con `Depends()`.

## Endpoints

| Metodo | Ruta               | Exito | Funcion                                 |
| ------ | ------------------ | ----: | --------------------------------------- |
| GET    | `/users`           |   200 | Lista y filtra por `role` o `is_active` |
| GET    | `/users/{user_id}` |   200 | Consulta por ID                         |
| POST   | `/users`           |   201 | Crea un usuario                         |
| PUT    | `/users/{user_id}` |   200 | Reemplaza todos los campos              |
| PATCH  | `/users/{user_id}` |   200 | Actualiza solo campos enviados          |
| DELETE | `/users/{user_id}` |   204 | Elimina sin cuerpo de respuesta         |

Roles validos: `admin`, `support`, `user`. El correo debe ser valido y unico.

## Ejemplos

Crear:

```json
{
  "name": "Carlos Mendoza",
  "email": "carlos.mendoza@device-systems.com",
  "role": "support",
  "is_active": true
}
```

Actualizar parcialmente:

```json
{ "role": "admin" }
```

```bash
curl -X PATCH http://127.0.0.1:8000/users/1 -H "Content-Type: application/json" -d "{\"role\":\"support\"}"
curl -X DELETE http://127.0.0.1:8000/users/1
```

Respuestas esperadas:

```json
{
  "id": 1,
  "name": "Admin Actualizado",
  "email": "admin.actualizado@device-systems.com",
  "role": "support",
  "is_active": true
}
```

`POST` responde `201 Created`, mientras que `PUT` y `PATCH` responden `200 OK`. `DELETE` responde `204 No Content` sin cuerpo.

## Errores y Dependency Injection

- `400`: correo duplicado o PATCH sin campos.
- `404`: usuario inexistente.
- `422`: datos invalidos de Pydantic.
- `500`: error inesperado con respuesta JSON estructurada.

`get_user_or_404` vive en `app/dependencies/user_dependencies.py` y se inyecta en GET, PUT, PATCH y DELETE:

```python
async def patch_existing_user(user_data: UserPatch, user: dict = Depends(get_user_or_404)):
    ...
```

Asi se centraliza la busqueda y el error 404 sin repetirlo en cada endpoint.

## Pruebas y evidencias

Importar `device_systems_postman.json` en Postman o `device_systems_thunder.json` en Thunder Client. Revisar Swagger en `/docs` y ReDoc en `/redoc`. La carpeta `evidencias/` contiene las capturas de la guia anterior y las nuevas capturas ya incorporadas:

- [`6_swagger_crud.png`](evidencias/6_swagger_crud.png): Swagger con la API version 2.0.0.
- [`7_redoc_crud.png`](evidencias/7_redoc_crud.png): ReDoc con la documentacion de la API.
- [`7.1_redoc_crud.png`](evidencias/7.1_redoc_crud.png): evidencia adicional de ReDoc.
- [`8_post_exitoso.png`](evidencias/8_post_exitoso.png): POST con respuesta 201.
- [`9_put_exitoso.png`](evidencias/9_put_exitoso.png): PUT con respuesta 200.
- [`10_patch_exitoso.png`](evidencias/10_patch_exitoso.png): PATCH con respuesta 200.
- [`11_delete_exitoso.png`](evidencias/11_delete_exitoso.png): DELETE con respuesta 204.
- [`12_error_correo_duplicado.png`](evidencias/12_error_correo_duplicado.png): error 400 por correo duplicado.
- [`13_error_datos_invalidos.png`](evidencias/13_error_datos_invalidos.png): error 422 por datos invalidos.
- [`14_error_patch_vacio.png`](evidencias/14_error_patch_vacio.png): error 400 por PATCH sin datos.
- [`15_error_put_inexistente.png`](evidencias/15_error_put_inexistente.png): error 404 en PUT.
- [`16_error_delete_inexistente.png`](evidencias/16_error_delete_inexistente.png): error 404 en DELETE.
- [`RESULTADOS_GUIA8.md`](evidencias/RESULTADOS_GUIA8.md): registro reproducible de estados HTTP y respuestas.

Las pruebas funcionales completas incluyen creacion, actualizacion completa y parcial, eliminacion, filtros y los errores de correo duplicado, datos invalidos, recursos inexistentes y PATCH vacio. Los resultados detallados estan en `RESULTADOS_GUIA8.md` y las colecciones contienen las peticiones reproducibles.

## Reflexion final

La evolucion de `device_systems` permitio pasar de una API basica a una solucion REST organizada. Separar rutas, esquemas, servicios, datos y dependencias facilita el mantenimiento y evita repetir validaciones. PUT y PATCH muestran la diferencia entre reemplazar un recurso y modificar solo algunos campos, mientras que `HTTPException` y los codigos de estado hacen que los errores sean claros para el cliente. Swagger, ReDoc y Git Flow dejaron el proyecto documentado, verificable y preparado para futuras mejoras como autenticacion y persistencia real.

## Git Flow aplicado

```text
main
├── feature/crud-users
    ├── feat: separar datos, servicios y dependencias
    ├── feat: implementar CRUD completo de usuarios
    └── docs: actualizar guia intermedia y pruebas
└── feature/evidencias-guia8
    └── test: completar escenarios y evidencias de la guia 8
```

Flujo recomendado:

```bash
git switch main
git pull origin main
git switch -c feature/nombre-del-cambio
git add .
git commit -m "feat: describir el cambio"
git push -u origin feature/nombre-del-cambio
```

Luego se crea un Pull Request hacia `main` y se elimina la rama cuando se haga merge.

## Licencia

Proyecto academico para aprendizaje de FastAPI.

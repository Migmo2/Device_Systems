# device_systems

API REST segura para gestionar usuarios, dispositivos y prestamos con FastAPI. El proyecto evoluciona incrementalmente desde EV07 hasta EV11 y actualmente incluye persistencia SQLAlchemy, migraciones Alembic, relaciones, JWT, roles, CORS, middleware y rate limiting.

## Estado del proyecto

| Guia | Resultado |
| --- | --- |
| EV07 | GET/POST de usuarios, Pydantic, response models y cabeceras |
| EV08 | CRUD completo, errores HTTP, Depends y OpenAPI |
| EV09 | SQLAlchemy, SQLite, Alembic y persistencia de usuarios |
| EV10 | Dispositivos, prestamos, relaciones, joins y filtros |
| EV11 | JWT, bcrypt, roles, CORS, middleware y rate limiting |

## Tecnologias

- Python 3.14
- FastAPI y Uvicorn
- Pydantic v2
- SQLAlchemy 2 y SQLite
- Alembic
- Passlib con bcrypt
- Python-Jose y OAuth2 Bearer
- SlowAPI
- Pytest y TestClient
- Git y GitHub

## Instalacion

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `.env` y define un `SECRET_KEY` aleatorio antes de usar autenticacion. El archivo `.env` no se versiona.

## Base de datos y ejecucion

```powershell
python -m alembic upgrade head
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Documentacion interactiva:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health check: `http://127.0.0.1:8000/health`

## Estructura actual

```text
device_systems/
├── app/
│   ├── auth/
│   │   ├── auth_routes.py
│   │   └── security.py
│   ├── core/
│   │   ├── config.py
│   │   └── rate_limit.py
│   ├── database/
│   │   └── connection.py
│   ├── dependencies/
│   │   ├── auth_dependency.py
│   │   ├── database_dependency.py
│   │   └── user_dependencies.py
│   ├── models/
│   │   ├── user_model.py
│   │   ├── device_model.py
│   │   └── loan_model.py
│   ├── routes/
│   │   ├── user_routes.py
│   │   ├── device_routes.py
│   │   ├── loan_routes.py
│   │   └── relationship_routes.py
│   ├── schemas/
│   │   ├── user_schema.py
│   │   ├── device_schema.py
│   │   ├── loan_schema.py
│   │   └── auth_schema.py
│   ├── services/
│   │   ├── user_service.py
│   │   ├── device_service.py
│   │   └── loan_service.py
│   └── main.py
├── alembic/versions/
├── evidencias/
├── tests/
├── alembic.ini
├── requirements.txt
├── .env.example
└── README.md
```

Las rutas reciben peticiones, los schemas validan datos, los servicios concentran reglas de negocio, los modelos representan tablas y las dependencias reutilizan sesiones, autenticacion y autorizacion.

## Migraciones Alembic

Migraciones incluidas:

- `0001_create_users`: crea usuarios.
- `9959abeab4c6`: agrega dispositivos y prestamos.
- `a284dd73e877`: agrega `hashed_password` para EV11.

Comandos habituales:

```powershell
python -m alembic current
python -m alembic history
python -m alembic revision --autogenerate -m "describe el cambio"
python -m alembic upgrade head
```

La base local `device_systems.db` no se versiona en Git.

## Endpoints

### Usuarios

| Metodo | Ruta | Funcion | Seguridad |
| --- | --- | --- | --- |
| GET | `/users` | Lista y filtra por `role` o `is_active` | Bearer JWT |
| GET | `/users/{user_id}` | Consulta por ID | Bearer JWT |
| POST | `/users` | Crea un usuario legacy | Publica |
| PUT | `/users/{user_id}` | Reemplaza todos los campos | Publica |
| PATCH | `/users/{user_id}` | Actualiza campos enviados | Publica |
| DELETE | `/users/{user_id}` | Elimina sin contenido | Publica |

### Dispositivos y prestamos

| Metodo | Ruta | Funcion | Seguridad |
| --- | --- | --- | --- |
| GET | `/devices` | Filtra por tipo, marca, disponibilidad o busqueda | Publica |
| GET | `/devices/{device_id}` | Consulta dispositivo | Publica |
| POST | `/devices` | Crea dispositivo con serial unico | `admin`/`support` |
| PUT/PATCH | `/devices/{device_id}` | Actualiza dispositivo | `admin`/`support` |
| DELETE | `/devices/{device_id}` | Elimina sin historial | `admin` |
| GET | `/loans` | Filtra por estado, correo o tipo | Bearer JWT |
| GET | `/loans/details` | Consulta con datos relacionados | `admin`/`support` |
| POST | `/loans` | Registra prestamo y bloquea dispositivo | Bearer JWT |
| PATCH | `/loans/{loan_id}/return` | Devuelve y libera dispositivo | `admin`/`support` |
| GET | `/users/{user_id}/loans` | Historial del usuario | `admin`/`support` |
| GET | `/devices/{device_id}/loans` | Historial del dispositivo | `admin`/`support` |

### Autenticacion

| Metodo | Ruta | Funcion | Limite |
| --- | --- | --- | --- |
| POST | `/auth/register` | Registra usuario con password segura | 3/minuto |
| POST | `/auth/login` | Devuelve token JWT Bearer | 5/minuto |
| GET | `/auth/me` | Consulta usuario autenticado | JWT |

## Seguridad

Las contrasenas se almacenan exclusivamente como hash bcrypt y `hashed_password` nunca aparece en respuestas. Las nuevas contrasenas requieren minimo 8 caracteres, mayuscula, minuscula, numero y ningun espacio.

El middleware agrega `X-App-Name`, `X-API-Version`, `X-Process-Time` y `X-Request-ID`. CORS permite los origenes definidos en `ALLOWED_ORIGINS`; no se usa `*` junto con credenciales.

Rate limits adicionales: `GET /users` permite 30 solicitudes por minuto y `POST /loans` permite 10 por minuto. Al superar un limite se responde `429 Too Many Requests`.

## Ejemplos

Registro:

```json
{
  "name": "Ana Perez",
  "email": "ana@example.com",
  "password": "SecurePass1",
  "role": "user"
}
```

Login OAuth2 desde terminal:

```powershell
curl.exe -X POST http://127.0.0.1:8000/auth/login -H "Content-Type: application/x-www-form-urlencoded" -d "username=ana@example.com&password=SecurePass1"
```

Crear dispositivo autenticado:

```json
{
  "name": "Laptop ThinkPad",
  "serial_number": "LEN-2026-001",
  "device_type": "laptop",
  "brand": "Lenovo",
  "is_available": true
}
```

Crear prestamo:

```json
{
  "user_id": 1,
  "device_id": 1
}
```

## Errores y codigos HTTP

- `201`: recurso creado.
- `200`: consulta o actualizacion exitosa.
- `204`: eliminacion exitosa sin cuerpo.
- `400`: correo/serial duplicado o datos de actualizacion incompletos.
- `401`: token ausente, invalido o credenciales incorrectas.
- `403`: usuario inactivo o rol insuficiente.
- `404`: recurso inexistente.
- `409`: dispositivo no disponible, prestamo ya devuelto o regla de negocio incumplida.
- `422`: validacion Pydantic fallida.
- `429`: limite de solicitudes superado.

## Pruebas y evidencias

```powershell
python -m pytest -q
```

La suite cubre CRUD de usuarios, persistencia, dispositivos, prestamos, joins, devolucion, JWT, roles, ocultamiento del hash y rate limiting. Las capturas heredadas de EV08 estan en `evidencias/`; las colecciones reproducibles estan en `device_systems_postman.json` y `device_systems_thunder.json`.

Para las evidencias solicitadas por las guias, usar `/docs`, `/redoc`, Postman o Thunder Client y conservar capturas de:

- Registro, login y `/auth/me`.
- Acceso sin token y token invalido.
- Rol insuficiente y limite `429`.
- Cabeceras `X-Process-Time` y `X-Request-ID`.
- Migraciones `alembic revision` y `alembic upgrade head`.
- Creacion, prestamo, join, filtros y devolucion.

## Git Flow

Ramas oficiales usadas:

- `main`: rama integrada y publicada.
- `device_systems_alembic_relaciones`: EV10, Alembic, relaciones y joins.
- `device_systems_security`: EV11, seguridad y autenticacion.

Flujo:

```powershell
git switch main
git pull --ff-only origin main
git switch -c nombre-de-la-rama
git add .
git commit -m "tipo: describir el cambio"
git push -u origin nombre-de-la-rama
git switch main
git merge --no-ff nombre-de-la-rama -m "merge: integrar cambio"
git push origin main
```

Los commits usan la identidad `gilmaro6 <gilanmarsa@gmail.com>`. No se versionan `.env`, tokens, entornos virtuales ni bases SQLite.

## Licencia

Proyecto academico para aprendizaje de FastAPI.

# Guion de socializacion - device_systems

Duracion maxima: 15 minutos
Modalidad: video no listado en YouTube

## 0:00 - 1:00 | Presentacion

Mi proyecto se llama `device_systems` y consiste en una API REST desarrollada con FastAPI para gestionar usuarios, dispositivos tecnologicos y prestamos.

La aplicacion evoluciono desde una API basica hasta una solucion con persistencia en SQLite, SQLAlchemy, Alembic y mecanismos de seguridad como JWT, roles, CORS, middleware y rate limiting.

Durante esta presentacion mostrare la funcionalidad de la API, la estructura del proyecto, la seguridad implementada y las pruebas realizadas.

Mostrar:

- Repositorio de GitHub.
- Rama `main`.
- Swagger UI en `/docs`.

## 1:00 - 3:00 | Funcionalidades construidas

La API permite registrar y consultar usuarios, administrar dispositivos tecnologicos y controlar prestamos.

### Usuarios

- Crear usuarios.
- Consultar usuarios por ID.
- Actualizar usuarios completamente con PUT.
- Actualizar usuarios parcialmente con PATCH.
- Eliminar usuarios.
- Filtrar por rol y estado activo.

### Dispositivos

- Crear dispositivos.
- Consultar dispositivos.
- Actualizar dispositivos.
- Eliminar dispositivos.
- Filtrar por tipo, marca y disponibilidad.
- Buscar por nombre o numero de serie.
- Validar que el numero de serie sea unico.

### Prestamos

- Crear prestamos.
- Validar que exista el usuario.
- Validar que exista el dispositivo.
- Validar que el dispositivo este disponible.
- Cambiar el dispositivo a no disponible al prestar.
- Registrar devoluciones.
- Cambiar el dispositivo nuevamente a disponible.
- Consultar historial por usuario o dispositivo.
- Consultar prestamos con informacion relacionada mediante joins.

Mostrar brevemente Swagger y las evidencias de EV09 y EV10.

## 3:00 - 4:30 | Evolucion del proyecto

En la primera version los usuarios se almacenaban en memoria. Luego se implemento el CRUD completo y finalmente se migro la persistencia a SQLAlchemy y SQLite.

La evolucion fue la siguiente:

1. EV07: GET, POST, Pydantic, response models y cabeceras HTTP.
2. EV08: PUT, PATCH, DELETE, errores HTTP y Dependency Injection.
3. EV09: SQLAlchemy, SQLite, Alembic y persistencia de usuarios.
4. EV10: modelos User, Device y Loan, relaciones, prestamos, joins y filtros.
5. EV11: autenticacion, autorizacion, JWT, CORS, middleware y rate limiting.

Mostrar las ramas:

- `device_systems_alembic_relaciones`.
- `device_systems_security`.
- `main`.

## 4:30 - 6:00 | Arquitectura del proyecto

La aplicacion esta organizada por responsabilidades para facilitar el mantenimiento.

- `routes`: define los endpoints.
- `schemas`: valida solicitudes y respuestas.
- `models`: representa las tablas SQLAlchemy.
- `services`: contiene las reglas de negocio.
- `dependencies`: gestiona sesiones, tokens y roles.
- `auth`: contiene registro, login, JWT y hash de contrasenas.
- `middlewares`: controla trazabilidad y tiempo de respuesta.
- `database`: configura SQLAlchemy.
- `alembic`: versiona los cambios de la base de datos.
- `tests`: contiene las pruebas automatizadas.

Mostrar el arbol del proyecto en VS Code o la estructura del README.

## 6:00 - 8:00 | Proteccion de rutas

Para proteger las rutas utilice OAuth2 Bearer junto con tokens JWT. El token se envia mediante la cabecera `Authorization`.

Demostracion:

1. Intentar acceder a `GET /users` sin token.
2. Mostrar la respuesta `401 Unauthorized`.
3. Registrar un usuario desde `/auth/register`.
4. Iniciar sesion en `/auth/login`.
5. Copiar el token en Swagger usando el boton `Authorize`.
6. Consultar nuevamente `GET /users`.

Los roles implementados son:

- `user`: puede consultar y crear prestamos.
- `support`: puede administrar dispositivos y devolver prestamos.
- `admin`: tiene permisos administrativos completos.

Mostrar una prueba con rol insuficiente y la respuesta `403 Forbidden`.

## 8:00 - 9:30 | Hash de contrasenas

Las contrasenas nunca se guardan directamente en la base de datos. Antes de almacenar un usuario, la contrasena se transforma mediante un hash bcrypt usando Passlib.

El proceso es el siguiente:

- El cliente envia la contrasena durante el registro o login.
- La API genera un hash bcrypt.
- La base de datos almacena `hashed_password`.
- La contrasena original no se puede recuperar.
- Los response models nunca muestran `hashed_password`.

Las contrasenas nuevas deben tener:

- Minimo 8 caracteres.
- Una letra mayuscula.
- Una letra minuscula.
- Un numero.
- Ningun espacio.

Mostrar:

- Registro exitoso.
- Registro con contrasena debil.
- Respuesta de `/auth/me` sin el campo `hashed_password`.

No mostrar el archivo `.env`, el `SECRET_KEY` ni credenciales reales durante el video.

## 9:30 - 11:00 | OAuth2 y JWT

El login utiliza OAuth2 con formulario de usuario y contrasena. Cuando las credenciales son correctas, la API genera un token JWT.

El flujo funciona asi:

1. El cliente envia correo y contrasena a `/auth/login`.
2. La API busca el usuario en la base de datos.
3. Passlib verifica la contrasena contra el hash almacenado.
4. Se genera un JWT con el ID del usuario, su rol y una fecha de expiracion.
5. El cliente envia el token en las siguientes solicitudes.
6. `get_current_user` valida el token.
7. `require_roles` comprueba los permisos del usuario.

La respuesta del login tiene esta estructura:

```json
{
  "access_token": "token_generado",
  "token_type": "bearer"
}
```

Despues mostrar una consulta exitosa a `/auth/me`.

## 11:00 - 12:30 | Middleware y CORS

Implemente un middleware personalizado para mejorar la trazabilidad de las solicitudes.

Las respuestas incluyen:

- `X-App-Name`: nombre de la aplicacion.
- `X-API-Version`: version de la API.
- `X-Process-Time`: tiempo de procesamiento.
- `X-Request-ID`: identificador unico de la solicitud.

`X-Request-ID` se conserva si el cliente lo envia. Si no existe, la API genera uno nuevo.

CORS controla que aplicaciones frontend pueden consumir la API. En desarrollo se permiten los origenes definidos en `ALLOWED_ORIGINS`, como:

- `http://localhost:3000`.
- `http://localhost:5173`.

No se recomienda utilizar `allow_origins=["*"]` junto con credenciales en produccion, porque cualquier origen podria intentar acceder a recursos autenticados.

Mostrar la evidencia `evidencias/ev11/ev11_05_cors_middleware.png`.

## 12:30 - 13:30 | Rate limiting

Utilice SlowAPI para limitar solicitudes y evitar abusos contra la API.

Los limites configurados son:

- `/auth/register`: 3 solicitudes por minuto.
- `/auth/login`: 5 solicitudes por minuto.
- `GET /users`: 30 solicitudes por minuto.
- `POST /loans`: 10 solicitudes por minuto.

Cuando se supera el limite, la API responde con `429 Too Many Requests`.

Esto ayuda a reducir intentos repetidos de login, registros masivos, abuso de endpoints y consumo excesivo de recursos.

Mostrar la evidencia `evidencias/ev11/ev11_06_rate_limit_429.png`.

## 13:30 - 14:30 | Pruebas y Git Flow

El proyecto cuenta con pruebas automatizadas usando Pytest y TestClient.

Las pruebas cubren:

- CRUD de usuarios.
- Registro y login.
- Tokens invalidos.
- Contrasenas debiles.
- Roles insuficientes.
- Dispositivos no disponibles.
- Devolucion de prestamos.
- Joins y filtros.
- Rate limiting.
- Ocultamiento del hash.

Resultado actual:

```text
7 passed
```

El flujo Git utilizado fue:

- Desarrollo en ramas.
- Commits con la identidad `gilmaro6`.
- Pull y merge hacia `main`.
- Publicacion de cada avance en GitHub.

Ramas principales:

- `device_systems_alembic_relaciones`.
- `device_systems_security`.
- `main`.

## 14:30 - 15:00 | Aprendizaje y cierre

Durante el desarrollo aprendi que construir una API no consiste solamente en crear endpoints. Tambien es necesario validar datos, manejar errores, controlar permisos, proteger contrasenas y documentar cada operacion.

Aprendi la diferencia entre autenticacion y autorizacion. La autenticacion verifica quien es el usuario y la autorizacion determina que puede hacer segun su rol.

Tambien comprendi la importancia de JWT, CORS, middleware y rate limiting para construir APIs mas seguras y preparadas para conectarse con aplicaciones frontend.

Este proyecto demuestra la evolucion de `device_systems` desde una API basica hasta una API REST persistente, relacionada, documentada y protegida.

## Orden recomendado para mostrar evidencias

1. Swagger OAuth2: `evidencias/ev11/ev11_02_swagger_oauth2.png`.
2. Registro, login y JWT: `evidencias/ev11/ev11_03_auth_flow.png`.
3. `/auth/me` y rutas protegidas: `evidencias/ev11/ev11_04_protected_routes.png`.
4. Middleware y CORS: `evidencias/ev11/ev11_05_cors_middleware.png`.
5. Rate limiting: `evidencias/ev11/ev11_06_rate_limit_429.png`.
6. Estructura y Git Flow: `evidencias/ev09/38_gitflow_ev09.png`.

# Trivia Seguridad — Backend

API REST en Flask para la plataforma de capacitación gamificada (MVP, COT-2026-001).
Cubre las 7 funciones del alcance: acceso por roles, quiz tipo concurso con comodines,
banco de preguntas, puntos/insignias/rangos, reportes de supervisor, multiplataforma
(API consumida por Flutter web/Android) y protección de datos.

## Stack

Flask 3 · SQLAlchemy · PostgreSQL (SQLite en desarrollo) · JWT (local o AWS Cognito) ·
Gunicorn · Docker · GitHub Actions → ECR → ECS Fargate.

## Arranque rápido

### Con Docker (recomendado)

```bash
docker compose up --build
# API en http://localhost:8000/api/v1 — crea tablas y datos de ejemplo solos
```

### Sin Docker

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
flask --app wsgi init-db && flask --app wsgi seed
python wsgi.py          # http://localhost:8000
```

### Usuarios de ejemplo (seed)

El seed crea `admin@seguridaddeoro.co`, `supervisor@seguridaddeoro.co` y
`guarda1..3@seguridaddeoro.co`. La contraseña compartida se toma de la
variable `SEED_DEFAULT_PASSWORD`; si no está definida, se genera una
aleatoria y se imprime una sola vez en la salida del seed (en Docker:
`docker compose logs api | grep Contraseña`). No hay credenciales en el código.

## Autenticación

Dos modos vía `AUTH_MODE` (ver `.env.example`):

- **local** (desarrollo): `POST /api/v1/auth/login` devuelve un JWT HS256 propio.
- **cognito** (producción): el cliente obtiene el token de AWS Cognito (Amplify/Hosted UI)
  y el backend lo valida contra el JWKS del User Pool. El rol sale del claim
  `cognito:groups` (grupos `guarda`, `supervisor`, `admin`) y el usuario se
  aprovisiona automáticamente en la base local.

Configurar Cognito: crear User Pool + App Client (sin secret), crear los 3 grupos,
y definir `COGNITO_REGION`, `COGNITO_USER_POOL_ID`, `COGNITO_APP_CLIENT_ID`.

## Endpoints principales (`/api/v1`)

| Método y ruta | Rol mínimo | Descripción |
|---|---|---|
| `POST /auth/login` | — | Login (solo modo local) |
| `GET /auth/me` | guarda | Perfil + rango + insignias |
| `GET/POST/PATCH/DELETE /users…` | admin | Gestión de usuarios |
| `GET /topics` · `POST/PATCH/DELETE` | guarda · admin | Temas de capacitación |
| `GET/POST/PATCH/DELETE /questions…` | admin | Banco de preguntas (4 opciones, 1 correcta) |
| `POST /questions/import` | admin | Carga masiva atómica |
| `POST /game/sessions` | guarda | Inicia partida (preguntas elegidas en servidor) |
| `POST /game/sessions/{id}/answer` | guarda | Responde; devuelve feedback y siguiente pregunta |
| `POST /game/sessions/{id}/lifeline` | guarda | Comodín `fifty_fifty` o `skip` (1 c/u por partida) |
| `POST /game/sessions/{id}/abandon` | guarda | Abandona la partida |
| `GET /leaderboard?period=all|week|month` | guarda | Tabla de posiciones |
| `GET /badges` · `GET /ranks` | guarda | Insignias y Escala de Mando |
| `GET /reports/overview|users|topics` | supervisor | Panel del supervisor |
| `GET /reports/users/{id}` | supervisor | Detalle por guarda y tema |
| `GET /reports/export/users.csv` | supervisor | Exportar CSV |
| `GET /health` | — | Healthcheck (para el ALB/ECS) |

## Mecánica de juego

- Puntos base: fácil 100 · media 200 · difícil 300.
- Bono de racha: +10% por acierto consecutivo (tope +50%).
- Las preguntas se ordenan de fácil a difícil; la respuesta correcta nunca
  viaja al cliente y todo el puntaje se calcula en servidor.
- Rangos (igual que el boceto): Recluta → Vigilante I (10k) → Oficial de
  Primera (25k) → Jefe de Turno (50k) → Supervisor (90k).

## Tests

```bash
pytest -q          # 33 tests: auth, RBAC, banco, juego, comodines, reportes
```

## Despliegue (CI/CD)

`.github/workflows/ci.yml`: cada push corre los tests; en `main` además
construye la imagen, la sube a ECR y fuerza un nuevo deployment en ECS.
Los secrets requeridos están documentados en el propio workflow.

En producción configurar: `AUTH_MODE=cognito`, `DATABASE_URL` (Postgres),
`SECRET_KEY`/`JWT_SECRET` desde Secrets Manager, y `CORS_ORIGINS` con el
dominio real del frontend.

## Tickets relacionados

- [GP-13](https://froidbj.atlassian.net/browse/GP-13) — Diseño del modelo de datos (perfiles)
- [GP-16](https://froidbj.atlassian.net/browse/GP-16) — Control de acceso RBAC
- [GP-20](https://froidbj.atlassian.net/browse/GP-20) — Carga secuencial de preguntas
- [GP-30](https://froidbj.atlassian.net/browse/GP-30) — Motor de puntajes

# trivia-seguridad-backend

Backend del sistema de trivia para capacitación en seguridad (guardas, supervisores y administradores).

## Descripción

API REST que soporta el flujo de trivia con preguntas sobre normatividad, protocolos, primeros auxilios y atención al usuario. Gestiona perfiles de usuario (Guarda, Supervisor, Administrador), sesiones de juego, puntajes y comodines.

## Stack técnico

- **Runtime**: Node.js
- **Base de datos**: Por definir (ver GP-13)
- **Autenticación**: JWT con RBAC (ver GP-16)

## Estructura del proyecto (WIP)

```
trivia-seguridad-backend/
├── src/
│   ├── routes/
│   ├── controllers/
│   ├── models/
│   ├── middlewares/
│   └── services/
├── tests/
└── README.md
```

## Tickets relacionados

- [GP-13](https://froidbj.atlassian.net/browse/GP-13) — Diseño del modelo de datos (perfiles)
- [GP-16](https://froidbj.atlassian.net/browse/GP-16) — Control de acceso RBAC
- [GP-20](https://froidbj.atlassian.net/browse/GP-20) — Carga secuencial de preguntas
- [GP-30](https://froidbj.atlassian.net/browse/GP-30) — Motor de puntajes

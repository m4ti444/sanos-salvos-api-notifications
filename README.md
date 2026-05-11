# Sanos y Salvos - API Notifications

API de notificaciones del sistema, con soporte para eventos y WebSocket.

## Stack

- FastAPI
- RabbitMQ
- WebSocket
- Docker

## Variables de entorno

Copia `.env.example` como `.env` y ajusta los valores.

## Ejecucion local

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8004
```

## Docker

```bash
docker build -t sanos-salvos-api-notifications .
docker run --env-file .env -p 8004:8004 sanos-salvos-api-notifications
```

## Endpoints principales

- `GET /api/notifications/`
- `GET /api/notifications/unread-count`
- `PATCH /api/notifications/{notification_id}/read`
- WebSocket de notificaciones

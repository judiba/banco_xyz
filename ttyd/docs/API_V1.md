# API v1 — Talk to Your Data

> **Front Angular:** [FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md) · Tipos TS: [frontend-api.types.ts](./frontend-api.types.ts)  
> **Backend:** [BACKEND.md](./BACKEND.md)

Base URL: `{host}/v1`

## Autenticação

| Método | Endpoint | Auth |
|--------|----------|------|
| POST | `/auth/login` | Não |
| POST | `/auth/refresh` | Não |
| POST | `/auth/logout` | Bearer (opcional) |

**Credenciais dev (DEV_OFFLINE):** `adminrecord` / `record123`

## Sessão e usuário

| Método | Endpoint |
|--------|----------|
| GET | `/session/bootstrap` |
| GET | `/users/me` |

## Conversas

| Método | Endpoint |
|--------|----------|
| GET | `/conversations` |
| POST | `/conversations` |
| POST | `/conversations/with-message` |
| GET | `/conversations/{id}` |
| PATCH | `/conversations/{id}` |
| DELETE | `/conversations/{id}` |
| GET | `/conversations/{id}/messages` |
| POST | `/conversations/{id}/messages` |
| POST | `/conversations/{id}/messages/stream` |
| POST | `/conversations/{id}/messages/{messageId}/regenerate` |
| GET | `/conversations/{id}/export?format=txt` |

## Pastas

| Método | Endpoint |
|--------|----------|
| GET | `/folders` |
| GET | `/folders/{id}` |
| GET | `/folders/by-slug/{slug}` |
| POST | `/folders` |
| PATCH | `/folders/{id}` |
| DELETE | `/folders/{id}?cascade=true` |

## Feedback

| Método | Endpoint |
|--------|----------|
| PUT | `/messages/{messageId}/feedback` |

## DynamoDB

Tabelas (prefixo `ttyd` por padrão):

- `ttyd-users` (GSI `username-index`)
- `ttyd-folders` (GSI `userId-index`)
- `ttyd-conversations` (GSI `userId-lastUpdatedAt-index`)
- `ttyd-messages` (GSI `conversationId-createdAt-index`)
- `ttyd-refresh-tokens`

Criar tabelas:

```bash
DYNAMODB_ENDPOINT=http://localhost:8001 python scripts/create_dynamodb_tables.py
```

## Variáveis de ambiente

Ver `.env.example` — `JWT_SECRET`, `DYNAMODB_ENDPOINT`, `DEV_OFFLINE`, etc.

Com `DEV_OFFLINE=true`, os dados ficam em memória (sem DynamoDB).

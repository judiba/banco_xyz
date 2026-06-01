# Integração Front ↔ Backend TTYD

A integração foi implementada no código Angular. Este guia descreve como executar e configurar.

## Pré-requisitos

1. **Backend** rodando em `http://localhost:8000` (`make up` ou `make dev` no repositório do backend).
2. **Credenciais seed:** `adminrecord` / `record123`
3. **Login Microsoft (SAML):** opcional — ver § Login AD

## Rodar o front

```bash
cd talk-to-your-data
npm install
npm start
```

O `proxy.conf.json` encaminha `/api` e `/v1` → `http://localhost:8000` quando usar proxy. Por padrão o front aponta para `http://localhost:8000/v1` em `src/environments/environment.ts`.

Para usar só o proxy (sem CORS):

```typescript
// environment.ts
apiBaseUrl: '/v1',
useApiProxy: true,
```

## Login AD (Microsoft / SAML)

| Fluxo | Como |
|-------|------|
| Local | Formulário → `POST /v1/auth/login` |
| Microsoft | Botão → redirect `GET /api/auth/saml/login` |

Após SSO o backend redireciona para `/login?token=...&refresh=...`; o front persiste tokens e navega para `/home` + bootstrap.

**Mock SAML (dev):** no backend, `APP_AUTH_SAML_ENABLED=true`, `APP_AUTH_SAML_DEV_MOCK=true`, `APP_AUTH_SAML_FRONTEND_LOGIN_URL=http://localhost:4200/login`.

**Ocultar botão:** `environment.authSamlEnabled = false`.

## O que foi integrado

| Área | Implementação |
|------|----------------|
| Login / logout / refresh | `AuthService`, `authInterceptor`, `authGuard` |
| Login Microsoft (SAML) | Botão na login + callback `?token=` em `/login` |
| Bootstrap | `SessionInitService` + `GET /session/bootstrap` |
| Conversas | `ConversationsStore` + `ConversationsApiService` |
| Chat (SSE) | `ChatStreamService` quando `environment.chatStreaming === true` |
| Pastas | `FoldersStore` + `FoldersApiService` |
| Feedback | `MessagesApiService` no chat |
| Regenerar resposta | `POST .../regenerate` |

## Estrutura de código

```text
src/app/core/
  api/           # tipos, config, services HTTP
  auth/          # login, interceptor, guard
  session/       # bootstrap após login
src/environments/
  environment.ts
```

## Documentação de contrato

- [API-CONTRATO-FRONT-BACKEND.md](../../docs/API-CONTRATO-FRONT-BACKEND.md)
- OpenAPI: http://localhost:8000/docs

## Troubleshooting

| Problema | Solução |
|----------|---------|
| CORS | Usar `proxy.conf.json` ou configurar CORS no backend |
| 401 após login | Verificar se bootstrap e token estão corretos |
| Chat não responde | Confirmar backend LLM; testar com `chatStreaming: false` para modo síncrono |
| Lista vazia | Verificar `GET /session/bootstrap` no Network do browser |

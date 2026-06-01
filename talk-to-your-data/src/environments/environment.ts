export const environment = {
  production: false,
  apiBaseUrl: 'http://localhost:8000/v1',
  chatStreaming: true,
  /** Redireciona /api e /v1 pelo proxy do `ng serve` (proxy.conf.json). */
  useApiProxy: false,
  /** GET redirect — login AD Record (SAML). */
  samlLoginPath: '/api/auth/saml/login',
  /** Exibir botão "Entrar com Microsoft" (ocultar se SAML desligado no backend). */
  authSamlEnabled: true,
};

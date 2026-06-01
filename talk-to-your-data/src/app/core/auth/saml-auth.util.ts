import { environment } from '../../../environments/environment';

/** URL de redirect para iniciar login SAML (Microsoft / AD Record). */
export function buildSamlLoginUrl(): string {
  const path = environment.samlLoginPath.startsWith('/')
    ? environment.samlLoginPath
    : `/${environment.samlLoginPath}`;

  if (environment.useApiProxy) {
    return path;
  }

  const base = environment.apiBaseUrl.replace(/\/v1\/?$/, '');
  if (base.startsWith('http://') || base.startsWith('https://')) {
    return `${base}${path}`;
  }

  return path;
}

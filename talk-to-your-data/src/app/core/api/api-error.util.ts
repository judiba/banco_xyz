import { HttpErrorResponse } from '@angular/common/http';
import { ApiErrorBody } from './api.types';

export function parseApiError(err: unknown): ApiErrorBody['error'] | null {
  if (!(err instanceof HttpErrorResponse)) return null;
  const body = err.error as ApiErrorBody | undefined;
  return body?.error ?? null;
}

export function getApiErrorMessage(err: unknown, fallback = 'Erro inesperado.'): string {
  return parseApiError(err)?.message ?? fallback;
}

export function getApiErrorCode(err: unknown): string | null {
  return parseApiError(err)?.code ?? null;
}

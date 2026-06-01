import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from './auth.service';
import { getApiErrorCode } from '../api/api-error.util';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const isAuthRoute =
    req.url.includes('/auth/login') || req.url.includes('/auth/refresh');

  let cloned = req;
  const token = auth.getAccessToken();

  if (token && !isAuthRoute) {
    cloned = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`,
        'X-Request-Id': crypto.randomUUID(),
      },
    });
  } else if (!isAuthRoute) {
    cloned = req.clone({
      setHeaders: { 'X-Request-Id': crypto.randomUUID() },
    });
  }

  return next(cloned).pipe(
    catchError((err: HttpErrorResponse) => {
      if (
        err.status === 401 &&
        getApiErrorCode(err) === 'AUTH_TOKEN_EXPIRED' &&
        !req.url.includes('/auth/refresh')
      ) {
        return auth.refresh().pipe(
          switchMap((tokens) => {
            const retry = req.clone({
              setHeaders: {
                Authorization: `Bearer ${tokens.accessToken}`,
                'X-Request-Id': crypto.randomUUID(),
              },
            });
            return next(retry);
          }),
          catchError((refreshErr) => {
            auth.clearSession();
            return throwError(() => refreshErr);
          }),
        );
      }
      return throwError(() => err);
    }),
  );
};

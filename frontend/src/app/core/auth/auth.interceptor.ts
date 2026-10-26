import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';

import { AuthService } from './auth.service';

const AUTH_ENDPOINT = '/api/v1/auth/';

export const authInterceptor: HttpInterceptorFn = (request, next) => {
  const auth = inject(AuthService);
  if (request.url.includes(AUTH_ENDPOINT)) return next(request);

  const token = auth.token();
  const authorizedRequest = token
    ? request.clone({ setHeaders: { Authorization: `Bearer ${token}` }, withCredentials: true })
    : request.clone({ withCredentials: true });

  return next(authorizedRequest).pipe(
    catchError((error: unknown) => {
      if (!(error instanceof HttpErrorResponse) || error.status !== 401 || !token) {
        return throwError(() => error);
      }
      return auth.refresh().pipe(
        switchMap(() => {
          const refreshedToken = auth.token();
          return next(
            request.clone({
              setHeaders: refreshedToken ? { Authorization: `Bearer ${refreshedToken}` } : {},
              withCredentials: true,
            }),
          );
        }),
        catchError((refreshError: unknown) => {
          auth.clearSession();
          return throwError(() => refreshError);
        }),
      );
    }),
  );
};

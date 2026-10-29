import { CanActivateFn, Router } from '@angular/router';
import { catchError, map, of } from 'rxjs';
import { inject } from '@angular/core';

import { AuthService } from './auth.service';

export const authenticatedGuard: CanActivateFn = (_route, state) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  if (auth.isAuthenticated()) return true;

  return auth.refresh().pipe(
    map(() => true),
    catchError(() => {
      auth.clearSession();
      return of(router.createUrlTree(['/login'], { queryParams: { returnUrl: state.url } }));
    }),
  );
};

export const anonymousGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  return auth.isAuthenticated() ? router.createUrlTree(['/home']) : true;
};

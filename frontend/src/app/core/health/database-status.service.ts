import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { catchError, map, of, switchMap, timer } from 'rxjs';

export type DatabaseStatus = 'checking' | 'ready' | 'unavailable';

/** Live database state from the backend readiness probe, refreshed every minute. */
@Injectable({ providedIn: 'root' })
export class DatabaseStatusService {
  private readonly http = inject(HttpClient);

  readonly status = toSignal(
    timer(0, 60_000).pipe(
      switchMap(() =>
        this.http.get('/health/ready').pipe(
          map((): DatabaseStatus => 'ready'),
          catchError(() => of<DatabaseStatus>('unavailable')),
        ),
      ),
    ),
    { initialValue: 'checking' as DatabaseStatus },
  );

  readonly label = (status: DatabaseStatus): string =>
    ({ checking: 'Verifica in corso…', ready: 'Connesso', unavailable: 'Non raggiungibile' })[status];
}

import { HttpErrorResponse } from '@angular/common/http';

import { ApiError } from './api.types';

/** Message to show for a failed request: the API's own text when available. */
export function apiErrorMessage(error: unknown, fallback: string): string {
  return error instanceof HttpErrorResponse ? ((error.error as ApiError | null)?.error?.message ?? fallback) : fallback;
}

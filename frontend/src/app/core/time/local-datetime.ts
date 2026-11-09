const pad = (value: number): string => String(value).padStart(2, '0');

/** `YYYY-MM-DD` of a date in the browser's time zone. */
export function localDateKey(date: Date): string {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

/**
 * ISO timestamp with the local offset, e.g. `2026-11-08T20:45:00+01:00`.
 * Unlike toISOString() it keeps the local date in the first ten characters,
 * which the backend uses to match activities with roles valid on that day.
 */
export function toOffsetIso(datetimeLocal: string): string {
  const date = new Date(datetimeLocal);
  const offset = -date.getTimezoneOffset();
  const sign = offset >= 0 ? '+' : '-';
  const hours = pad(Math.floor(Math.abs(offset) / 60));
  const minutes = pad(Math.abs(offset) % 60);
  return `${localDateKey(date)}T${pad(date.getHours())}:${pad(date.getMinutes())}:00${sign}${hours}:${minutes}`;
}

/** Value for an `<input type="datetime-local">` from a stored timestamp, in local time. */
export function toDatetimeLocal(iso: string): string {
  const date = new Date(iso);
  return `${localDateKey(date)}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

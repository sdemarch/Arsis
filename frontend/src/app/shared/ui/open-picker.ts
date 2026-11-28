const PICKER_TYPES = new Set(['date', 'time', 'datetime-local', 'month', 'week']);

/**
 * Opens the browser's own calendar (or time) picker when a date or time field is
 * clicked, instead of leaving the user to type into its segments. Bound once on the
 * app shell, so it applies to every such field in the application.
 */
export function openPickerOnClick(event: MouseEvent): void {
  const input = event.target;
  if (!(input instanceof HTMLInputElement) || !PICKER_TYPES.has(input.type)) return;
  if (input.disabled || input.readOnly) return;
  try {
    input.showPicker?.();
  } catch {
    // Already open or not allowed by the browser: typing still works.
  }
}

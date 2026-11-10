import { DOCUMENT } from '@angular/common';
import { Injectable, inject, signal } from '@angular/core';

export type AppTheme = 'light' | 'dark';

const STORAGE_KEY = 'arsis.theme';

/** Applies the user's active colour theme and keeps a local override across visits. */
@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly document = inject(DOCUMENT);
  readonly theme = signal<AppTheme>(this.readTheme());

  constructor() {
    this.apply(this.theme());
  }

  applyDefault(theme: AppTheme): void {
    if (this.hasLocalOverride()) return;
    this.apply(theme);
  }

  toggle(): void {
    this.set(this.theme() === 'light' ? 'dark' : 'light');
  }

  set(theme: AppTheme): void {
    this.writeLocalOverride(theme);
    this.apply(theme);
  }

  private apply(theme: AppTheme): void {
    this.document.documentElement.dataset['theme'] = theme;
    this.theme.set(theme);
  }

  private readTheme(): AppTheme {
    const stored = this.readLocalOverride();
    return stored ?? (this.document.documentElement.dataset['theme'] === 'dark' ? 'dark' : 'light');
  }

  private hasLocalOverride(): boolean {
    return this.readLocalOverride() !== null;
  }

  private readLocalOverride(): AppTheme | null {
    try {
      const value = this.document.defaultView?.localStorage.getItem(STORAGE_KEY);
      return value === 'light' || value === 'dark' ? value : null;
    } catch {
      return null;
    }
  }

  private writeLocalOverride(theme: AppTheme): void {
    try {
      this.document.defaultView?.localStorage.setItem(STORAGE_KEY, theme);
    } catch {
      // The UI remains usable when browser storage is unavailable.
    }
  }
}

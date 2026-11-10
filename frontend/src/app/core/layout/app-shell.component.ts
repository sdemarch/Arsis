import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { filter, map, startWith } from 'rxjs';

import { NAVIGATION } from './navigation';
import { AuthService } from '../auth/auth.service';
import { ThemeService } from '../theme/theme.service';
import { SettingsService } from '../../features/settings/settings.service';

/** `/school/lessons/3?tab=x` → `school`. */
function firstSegment(url: string): string {
  return url.split(/[?#]/)[0].split('/').filter(Boolean)[0] ?? '';
}

@Component({
  selector: 'arsis-app-shell',
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  template: `
    <header class="topbar">
      <nav class="topnav" aria-label="Aree principali">
        @for (area of topbarAreas; track area.path) {
          <a [routerLink]="area.path" [class.is-active]="area === matchedArea()" [attr.aria-current]="area === matchedArea() ? 'page' : null">{{ area.label }}</a>
        }
      </nav>
      <div class="topbar-actions">
        <button class="logout-button" type="button" (click)="logout()">Esci</button>
      </div>
    </header>

    <div class="workspace">
      <aside class="sidebar">
        <a class="sidebar__brand" routerLink="/home" aria-label="Arsis, vai alla Home">
          <img src="assets/brand/arsis-logo-icon.svg" alt="" />
          <span class="sidebar__brand-name" aria-hidden="true">Arsis</span>
        </a>
        <p class="sidebar__eyebrow">{{ activeArea().label }}</p>
        <nav aria-label="Navigazione area">
          @for (item of activeArea().children; track item.label) {
            <a
              [routerLink]="item.path"
              [queryParams]="item.queryParams ?? null"
              routerLinkActive="is-active"
              [routerLinkActiveOptions]="{ exact: true }"
            >
              {{ item.label }}
            </a>
          }
        </nav>
        <div class="sidebar__footer">
          <a class="sidebar-profile" routerLink="/settings" aria-label="Apri le configurazioni dal profilo" [attr.aria-current]="matchedArea()?.path === '/settings' ? 'page' : null">
            <span class="sidebar-profile__avatar">{{ userInitials() }}</span>
            <span class="sidebar-profile__identity"><strong>{{ auth.user()?.display_name }}</strong><small>Configurazioni</small></span>
          </a>
          <button class="theme-toggle" type="button" (click)="theme.toggle()" [attr.aria-label]="theme.theme() === 'light' ? 'Attiva tema scuro' : 'Attiva tema chiaro'" [attr.aria-pressed]="theme.theme() === 'dark'" [attr.title]="theme.theme() === 'light' ? 'Tema chiaro: passa a scuro' : 'Tema scuro: passa a chiaro'">
            @if (theme.theme() === 'light') {
              <svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" /></svg>
            } @else {
              <svg aria-hidden="true" viewBox="0 0 24 24"><path d="M20.5 14.1A8.5 8.5 0 1 1 9.9 3.5 6.7 6.7 0 0 0 20.5 14.1Z" /></svg>
            }
          </button>
        </div>
      </aside>
      <div class="page-column">
        <main class="content" id="main-content"><router-outlet /></main>
        <footer class="app-footer">
          <span>{{ settings.general()?.organization_name ?? 'Arsis' }}</span>
        </footer>
      </div>
    </div>
  `,
  styleUrl: './app-shell.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AppShellComponent {
  protected readonly navigation = NAVIGATION;
  protected readonly topbarAreas = NAVIGATION.filter((area) => area.inTopbar !== false);
  private readonly router = inject(Router);
  protected readonly auth = inject(AuthService);
  protected readonly settings = inject(SettingsService);
  protected readonly theme = inject(ThemeService);
  private readonly currentUrl = toSignal(
    this.router.events.pipe(
      filter((event): event is NavigationEnd => event instanceof NavigationEnd),
      map((event) => event.urlAfterRedirects),
      startWith(this.router.url),
    ),
    { initialValue: this.router.url },
  );

  /** Area owning the current page, matched on the first URL segment: /school/lessons → Scuola. */
  protected readonly matchedArea = computed(() => {
    const section = firstSegment(this.currentUrl());
    return this.navigation.find((area) => firstSegment(area.path) === section) ?? null;
  });
  // A URL outside every area (only possible for unknown routes) falls back to Home.
  protected readonly activeArea = computed(() => this.matchedArea() ?? this.navigation[0]);

  constructor() {
    this.settings.loadGeneral().subscribe({
      next: (settings) => this.theme.applyDefault(settings.default_theme),
      error: () => undefined,
    });
  }

  protected userInitials(): string {
    return (this.auth.user()?.display_name ?? 'U')
      .split(/\s+/)
      .map((part) => part[0])
      .join('')
      .slice(0, 2)
      .toUpperCase();
  }

  protected logout(): void {
    this.auth.logout().subscribe({
      next: () => void this.router.navigateByUrl('/login'),
      error: () => {
        this.auth.clearSession();
        void this.router.navigateByUrl('/login');
      },
    });
  }
}

import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { filter, map, startWith } from 'rxjs';

import { NAVIGATION } from './navigation';
import { AuthService } from '../auth/auth.service';
import { DatabaseStatusService } from '../health/database-status.service';
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
        <button class="icon-button" type="button" aria-label="Notifiche">●</button>
        <a class="user-menu" routerLink="/settings" aria-label="Apri le configurazioni dal profilo" [attr.aria-current]="matchedArea()?.path === '/settings' ? 'page' : null">
          <span>{{ userInitials() }}</span>
          <small>{{ auth.user()?.display_name }}</small>
        </a>
        <button class="icon-button" type="button" aria-label="Esci" (click)="logout()">↪</button>
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
          <span class="status-dot" [class.status-dot--down]="database.status() === 'unavailable'" [class.status-dot--pending]="database.status() === 'checking'"></span>
          <div><strong>Database locale</strong><small>{{ database.label(database.status()) }}</small></div>
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
  protected readonly database = inject(DatabaseStatusService);
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
    this.settings.loadGeneral().subscribe({ error: () => undefined });
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

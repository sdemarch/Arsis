import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { filter, map, startWith } from 'rxjs';

import { NAVIGATION } from './navigation';
import applicationData from '../../../assets/mock/application.json';

@Component({
  selector: 'arsis-app-shell',
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  template: `
    <header class="topbar">
      <nav class="topnav" aria-label="Aree principali">
        @for (area of navigation; track area.path) {
          <a [routerLink]="area.path" routerLinkActive="is-active">{{ area.label }}</a>
        }
      </nav>
      <div class="topbar-actions">
        <button class="icon-button" type="button" aria-label="Notifiche">●</button>
        <a class="user-menu" routerLink="/settings" aria-label="Apri le configurazioni dal profilo">
          <span>SM</span>
          <small>Stefano</small>
        </a>
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
          <span class="status-dot"></span>
          <div><strong>Database locale</strong><small>Connesso</small></div>
        </div>
      </aside>
      <div class="page-column">
        <main class="content" id="main-content"><router-outlet /></main>
        <footer class="app-footer">
          <span>{{ application.organization.name }}</span>
        </footer>
      </div>
    </div>
  `,
  styleUrl: './app-shell.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AppShellComponent {
  protected readonly navigation = NAVIGATION;
  protected readonly application = applicationData;
  private readonly router = inject(Router);
  private readonly currentUrl = toSignal(
    this.router.events.pipe(
      filter((event): event is NavigationEnd => event instanceof NavigationEnd),
      map((event) => event.urlAfterRedirects),
      startWith(this.router.url),
    ),
    { initialValue: this.router.url },
  );

  protected readonly activeArea = computed(
    () =>
      this.navigation.find((area) => this.currentUrl().startsWith(area.path)) ?? this.navigation[0],
  );
}

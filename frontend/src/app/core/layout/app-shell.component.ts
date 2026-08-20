import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { filter, map, startWith } from 'rxjs';

import { NAVIGATION } from './navigation';

@Component({
  selector: 'arsis-app-shell',
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  template: `
    <header class="topbar">
      <a class="brand" routerLink="/home" aria-label="Arsis, vai alla Home">
        <span class="brand__mark" aria-hidden="true">A</span>
        <span>Arsis</span>
      </a>
      <nav class="topnav" aria-label="Aree principali">
        @for (area of navigation; track area.path) {
          <a [routerLink]="area.path" routerLinkActive="is-active">{{ area.label }}</a>
        }
      </nav>
      <a class="user-menu" routerLink="/settings" aria-label="Apri configurazione">SM</a>
    </header>

    <div class="workspace">
      <aside class="sidebar">
        <p class="sidebar__eyebrow">{{ activeArea().label }}</p>
        <nav aria-label="Navigazione area">
          @for (item of activeArea().children; track item.path) {
            <a [routerLink]="item.path" routerLinkActive="is-active" [routerLinkActiveOptions]="{ exact: true }">
              {{ item.label }}
            </a>
          }
        </nav>
      </aside>
      <main class="content" id="main-content"><router-outlet /></main>
    </div>
  `,
  styleUrl: './app-shell.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AppShellComponent {
  protected readonly navigation = NAVIGATION;
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

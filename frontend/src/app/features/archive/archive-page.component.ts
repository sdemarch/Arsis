import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { PageHeaderComponent } from '../../shared/ui/page-header.component';
import { SettingsService } from '../settings/settings.service';

@Component({
  selector: 'arsis-archive-page',
  imports: [PageHeaderComponent, RouterLink],
  template: `
    <arsis-page-header eyebrow="Archivio" title="Archivio documentale" description="Accedi ai documenti condivisi dell’associazione." />
    <section class="archive-card card">
      <div class="drive-icon" aria-hidden="true">△</div>
      <div>
        <p class="eyebrow">Google Drive</p>
        <h2>Archivio {{ settings.general()?.organization_name || 'Arsis' }}</h2>
        <p>Verbali, documenti associativi, materiali didattici e spartiti sono organizzati nella cartella Drive condivisa.</p>
        @if (archiveUrl()) {
          <small>{{ archiveUrl() }}</small>
        } @else if (loaded()) {
          <small class="missing">Nessuna cartella configurata.</small>
        }
      </div>
      @if (archiveUrl()) {
        <a class="button button--primary button--large" [href]="archiveUrl()" target="_blank" rel="noopener">Apri Google Drive ↗</a>
      } @else if (loaded()) {
        <a class="button button--secondary button--large" routerLink="/settings">Configura la cartella</a>
      }
    </section>
    @if (failed()) { <p class="error" role="alert">Impossibile leggere le configurazioni dell’archivio.</p> }
    <aside class="info-card"><strong>Come funziona l’archivio</strong><p>Arsis memorizza soltanto il collegamento alla cartella. L’accesso ai documenti dipende dai permessi configurati su Google Drive.</p></aside>
  `,
  styles: `
    .archive-card { align-items: center; display: grid; gap: var(--sp-6); grid-template-columns: 72px 1fr auto; padding: var(--sp-8); }
    .drive-icon { align-items: center; background: var(--color-accent-soft); border-radius: var(--radius-xl); color: var(--color-accent); display: flex; font-size: var(--text-2xl); height: 72px; justify-content: center; width: 72px; }
    .eyebrow { color: var(--color-accent-hover); font-size: var(--text-xs); font-weight: var(--weight-semi); letter-spacing: .08em; margin: 0 0 var(--sp-1); text-transform: uppercase; }
    h2 { font-size: var(--text-2xl); margin: 0; }
    .archive-card p { color: var(--text-secondary); margin: var(--sp-2) 0; max-width: 650px; }
    .archive-card small { color: var(--text-tertiary); font-family: var(--font-mono); overflow-wrap: anywhere; }
    .archive-card small.missing { color: var(--color-warn); font-family: inherit; }
    .error { color: var(--color-danger); }
    .info-card { background: var(--color-accent-soft); border-radius: var(--radius-lg); color: var(--color-accent-hover); margin-top: var(--sp-5); padding: var(--sp-5); }
    .info-card p { margin: var(--sp-1) 0 0; }
    @media (max-width: 800px) { .archive-card { grid-template-columns: 1fr; } }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ArchivePageComponent {
  protected readonly settings = inject(SettingsService);
  protected readonly archiveUrl = computed(() => this.settings.general()?.archive_google_drive_url.trim() ?? '');
  protected readonly loaded = computed(() => this.settings.general() !== null);
  protected readonly failed = signal(false);

  constructor() {
    // Always re-read: the folder may have just been changed from Configurazioni.
    this.settings.loadGeneral().subscribe({ error: () => this.failed.set(true) });
  }
}

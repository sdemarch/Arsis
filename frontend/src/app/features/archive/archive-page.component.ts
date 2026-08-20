import { ChangeDetectionStrategy, Component } from '@angular/core';

import settingsData from '../../../assets/mock/settings.json';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';

@Component({
  selector: 'arsis-archive-page',
  imports: [PageHeaderComponent],
  template: `
    <arsis-page-header eyebrow="Archivio" title="Archivio documentale" description="Accedi ai documenti condivisi dell’associazione." />
    <section class="archive-card card">
      <div class="drive-icon" aria-hidden="true">△</div>
      <div><p class="eyebrow">Google Drive</p><h2>Archivio Arsis</h2><p>Verbali, documenti associativi, materiali didattici e spartiti sono organizzati nella cartella Drive condivisa.</p><small>{{ archiveUrl }}</small></div>
      <a class="button button--primary button--large" [href]="archiveUrl" target="_blank" rel="noopener">Apri Google Drive ↗</a>
    </section>
    <aside class="info-card"><strong>Come funziona l’archivio</strong><p>Arsis memorizza soltanto il collegamento alla cartella. L’accesso ai documenti dipende dai permessi configurati su Google Drive.</p></aside>
  `,
  styles: `
    .archive-card { align-items: center; display: grid; gap: var(--sp-6); grid-template-columns: 72px 1fr auto; padding: var(--sp-8); }
    .drive-icon { align-items: center; background: var(--color-accent-soft); border-radius: var(--radius-xl); color: var(--color-accent); display: flex; font-size: var(--text-2xl); height: 72px; justify-content: center; width: 72px; }
    .eyebrow { color: var(--color-accent-hover); font-size: var(--text-xs); font-weight: var(--weight-semi); letter-spacing: .08em; margin: 0 0 var(--sp-1); text-transform: uppercase; }
    h2 { font-size: var(--text-2xl); margin: 0; }
    .archive-card p { color: var(--text-secondary); margin: var(--sp-2) 0; max-width: 650px; }
    .archive-card small { color: var(--text-tertiary); font-family: var(--font-mono); }
    .info-card { background: var(--color-accent-soft); border-radius: var(--radius-lg); color: var(--color-accent-hover); margin-top: var(--sp-5); padding: var(--sp-5); }
    .info-card p { margin: var(--sp-1) 0 0; }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ArchivePageComponent {
  protected readonly archiveUrl = settingsData.archiveUrl;
}


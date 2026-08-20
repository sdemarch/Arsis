import { ChangeDetectionStrategy, Component } from '@angular/core';

import settingsData from '../../../assets/mock/settings.json';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';

@Component({
  selector: 'arsis-settings-page',
  imports: [PageHeaderComponent],
  template: `
    <arsis-page-header eyebrow="Configurazione" title="Impostazioni" description="Configura cataloghi e preferenze generali dell’applicazione." />
    <section class="settings-grid">
      @for (catalogue of catalogues; track catalogue.label) {
        <article class="settings-card card"><div class="settings-icon">{{ catalogue.label.slice(0, 2).toUpperCase() }}</div><div><h2>{{ catalogue.label }}</h2><p>{{ catalogue.count }} elementi · {{ catalogue.detail }}</p></div><button class="button button--secondary">Gestisci</button></article>
      }
    </section>
    <section class="config-section card">
      <header><div><p class="eyebrow">Archivio</p><h2>Collegamento Google Drive</h2></div><span class="status-badge status-badge--success">Configurato</span></header>
      <label><span>URL cartella principale</span><div><input [value]="archiveUrl" /><button class="button button--secondary">Salva</button></div></label>
    </section>
    <section class="config-section card">
      <header><div><p class="eyebrow">Sistema</p><h2>Database locale</h2></div><span class="status-badge status-badge--success">{{ database.status }}</span></header>
      <dl><div><dt>Motore</dt><dd>{{ database.engine }}</dd></div><div><dt>File</dt><dd class="data-value">{{ database.file }}</dd></div><div><dt>Schema</dt><dd>{{ database.version }}</dd></div></dl>
    </section>
  `,
  styles: `
    .settings-grid { display: grid; gap: var(--sp-4); grid-template-columns: repeat(3, 1fr); margin-bottom: var(--sp-6); }
    .settings-card { align-items: center; display: grid; gap: var(--sp-3); grid-template-columns: 44px 1fr auto; padding: var(--sp-4); }
    .settings-icon { align-items: center; background: var(--color-accent-soft); border-radius: var(--radius-md); color: var(--color-accent-hover); display: flex; font-size: var(--text-xs); font-weight: var(--weight-semi); height: 44px; justify-content: center; }
    h2 { font-family: var(--font-sans); font-size: var(--text-lg); margin: 0; }
    .settings-card p { color: var(--text-secondary); font-size: var(--text-sm); margin: var(--sp-1) 0 0; }
    .config-section { margin-top: var(--sp-4); padding: var(--sp-6); }
    .config-section header { align-items: center; border-bottom: var(--border-thin) solid var(--border-subtle); display: flex; justify-content: space-between; margin-bottom: var(--sp-5); padding-bottom: var(--sp-4); }
    .eyebrow { color: var(--color-accent-hover); font-size: var(--text-xs); font-weight: var(--weight-semi); letter-spacing: .08em; margin: 0 0 var(--sp-1); text-transform: uppercase; }
    label { display: grid; font-size: var(--text-sm); gap: var(--sp-2); }
    label > div { display: flex; gap: var(--sp-2); }
    input { background: var(--bg-raised); border: var(--border-thin) solid var(--border-default); border-radius: var(--radius-md); color: var(--text-primary); flex: 1; padding: 0 var(--sp-3); }
    dl { display: grid; grid-template-columns: repeat(3, 1fr); margin: 0; }
    dl div { display: grid; gap: var(--sp-1); }
    dt { color: var(--text-tertiary); font-size: var(--text-xs); text-transform: uppercase; }
    dd { margin: 0; }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SettingsPageComponent {
  protected readonly archiveUrl = settingsData.archiveUrl;
  protected readonly catalogues = settingsData.catalogues;
  protected readonly database = settingsData.database;
}


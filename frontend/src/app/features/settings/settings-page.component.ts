import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';

import settingsData from '../../../assets/mock/settings.json';
import { ConfigurationStore } from '../../core/config/configuration.store';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';

@Component({
  selector: 'arsis-settings-page',
  imports: [PageHeaderComponent, FormsModule],
  template: `
    <arsis-page-header eyebrow="Profilo" title="Configurazioni" description="Gestisci etichette, cataloghi e preferenze generali dell’applicazione." />
    <section class="settings-grid">
      @for (catalogue of catalogues; track catalogue.label) {
        <article class="settings-card card"><div class="settings-icon">{{ catalogue.label.slice(0, 2).toUpperCase() }}</div><div><h2>{{ catalogue.label }}</h2><p>{{ catalogue.count }} elementi · {{ catalogue.detail }}</p></div>@if (catalogue.label === 'Ruoli anagrafici') { <a class="button button--secondary" href="#roles">Gestisci</a> } @else { <button class="button button--secondary" type="button">Gestisci</button> }</article>
      }
    </section>
    <section class="config-section card" id="roles">
      <header><div><p class="eyebrow">Anagrafiche</p><h2>Ruoli selezionabili</h2><p class="section-description">Queste etichette sono disponibili nelle schede persona.</p></div><span class="status-badge status-badge--success">{{ activeRolesCount() }} attivi</span></header>
      <div class="role-list">
        @for (role of roles(); track role.id) {
          <div class="role-row">
            <span class="role-tag" [class.is-disabled]="!role.active">{{ role.label }}</span>
            <div><strong>{{ role.label }}</strong><small>{{ role.description }}</small></div>
            <button class="button button--secondary" type="button" (click)="toggleRole(role.id)">{{ role.active ? 'Disattiva' : 'Riattiva' }}</button>
          </div>
        }
      </div>
      <form class="new-role" (submit)="addRole(); $event.preventDefault()">
        <label><span>Nuovo ruolo</span><input name="newRole" [(ngModel)]="newRoleLabel" placeholder="Es. Volontario" /></label>
        <button class="button button--primary" type="submit" [disabled]="!newRoleLabel.trim()">＋ Aggiungi etichetta</button>
      </form>
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
    .settings-grid { display: grid; gap: var(--sp-4); grid-template-columns: repeat(2, 1fr); margin-bottom: var(--sp-6); }
    .settings-card { align-items: center; display: grid; gap: var(--sp-3); grid-template-columns: 44px 1fr auto; padding: var(--sp-4); }
    .settings-icon { align-items: center; background: var(--color-accent-soft); border-radius: var(--radius-md); color: var(--color-accent-hover); display: flex; font-size: var(--text-xs); font-weight: var(--weight-semi); height: 44px; justify-content: center; }
    h2 { font-family: var(--font-sans); font-size: var(--text-lg); margin: 0; }
    .settings-card p { color: var(--text-secondary); font-size: var(--text-sm); margin: var(--sp-1) 0 0; }
    .config-section { margin-top: var(--sp-4); padding: var(--sp-6); }
    .config-section header { align-items: center; border-bottom: var(--border-thin) solid var(--border-subtle); display: flex; justify-content: space-between; margin-bottom: var(--sp-5); padding-bottom: var(--sp-4); }
    .section-description { color: var(--text-secondary); font-size: var(--text-sm); margin: var(--sp-1) 0 0; }
    .eyebrow { color: var(--color-accent-hover); font-size: var(--text-xs); font-weight: var(--weight-semi); letter-spacing: .08em; margin: 0 0 var(--sp-1); text-transform: uppercase; }
    label { display: grid; font-size: var(--text-sm); gap: var(--sp-2); }
    label > div { display: flex; gap: var(--sp-2); }
    input { background: var(--bg-raised); border: var(--border-thin) solid var(--border-default); border-radius: var(--radius-md); color: var(--text-primary); flex: 1; padding: 0 var(--sp-3); }
    dl { display: grid; grid-template-columns: repeat(3, 1fr); margin: 0; }
    dl div { display: grid; gap: var(--sp-1); }
    dt { color: var(--text-tertiary); font-size: var(--text-xs); text-transform: uppercase; }
    dd { margin: 0; }
    .role-list { display: grid; }
    .role-row { align-items: center; border-bottom: var(--border-thin) solid var(--border-subtle); display: grid; gap: var(--sp-4); grid-template-columns: 110px 1fr auto; padding: var(--sp-3) 0; }
    .role-row > div { display: grid; }
    .role-row small { color: var(--text-tertiary); }
    .role-tag { background: var(--color-accent-soft); border-radius: var(--radius-full); color: var(--color-accent-hover); font-size: var(--text-xs); justify-self: start; padding: var(--sp-1) var(--sp-2); }
    .role-tag.is-disabled { background: var(--bg-raised); color: var(--text-disabled); text-decoration: line-through; }
    .new-role { align-items: end; background: var(--bg-raised); border-radius: var(--radius-md); display: grid; gap: var(--sp-3); grid-template-columns: 1fr auto; margin-top: var(--sp-5); padding: var(--sp-4); }
    .new-role input { background: var(--bg-surface); min-height: 38px; }
    button:disabled { cursor: not-allowed; opacity: .55; }
    @media (max-width: 800px) { .settings-grid { grid-template-columns: 1fr; } .role-row { grid-template-columns: 1fr auto; } .role-row .role-tag { grid-column: 1 / -1; } .new-role { grid-template-columns: 1fr; } dl { gap: var(--sp-4); grid-template-columns: 1fr; } }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SettingsPageComponent {
  private readonly configuration = inject(ConfigurationStore);
  protected readonly archiveUrl = settingsData.archiveUrl;
  protected readonly catalogues = settingsData.catalogues;
  protected readonly database = settingsData.database;
  protected readonly roles = this.configuration.roles;
  protected readonly activeRolesCount = computed(() => this.roles().filter((role) => role.active).length);
  protected newRoleLabel = '';

  protected toggleRole(roleId: string): void {
    this.configuration.toggleRole(roleId);
  }

  protected addRole(): void {
    const label = this.newRoleLabel.trim();
    if (!label) return;
    this.configuration.addRole(label);
    this.newRoleLabel = '';
  }
}

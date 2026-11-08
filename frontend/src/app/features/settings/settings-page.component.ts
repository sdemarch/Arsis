import { ChangeDetectionStrategy, Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { AuthService } from '../../core/auth/auth.service';
import { DatabaseStatusService } from '../../core/health/database-status.service';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';
import { GeneralSettings, ResponsibleUser, SettingsService } from './settings.service';

@Component({
  selector: 'arsis-settings-page',
  imports: [PageHeaderComponent, FormsModule, RouterLink],
  template: `
    <arsis-page-header eyebrow="Profilo" title="Configurazioni" description="Gestisci i dati generali e i cataloghi dell’applicazione." />
    <section class="settings-grid">
      <article class="settings-card card"><div class="settings-icon">ST</div><div><h2>Strumenti e sezioni</h2><p>Organizza il catalogo musicale utilizzato nelle anagrafiche.</p></div><a class="button button--secondary" routerLink="/settings/catalogues">Gestisci</a></article>
      <article class="settings-card card"><div class="settings-icon">CC</div><div><h2>Categorie contabili</h2><p>Definisci le voci di entrata e uscita della prima nota.</p></div><a class="button button--secondary" routerLink="/settings/accounting-categories">Gestisci</a></article>
      <article class="settings-card card"><div class="settings-icon">DB</div><div><h2>Database locale</h2><p>I dati sono conservati nel salvataggio SQLite dell’installazione.</p></div><span class="status-badge" [class.status-badge--success]="database.status() === 'ready'" [class.status-badge--warn]="database.status() === 'checking'" [class.status-badge--danger]="database.status() === 'unavailable'">{{ database.label(database.status()) }}</span></article>
    </section>
    <form class="config-section card" (ngSubmit)="save()">
      <header><div><p class="eyebrow">Organizzazione</p><h2>Identità dell’applicazione</h2><p class="section-description">Questo nome viene mostrato nel piè di pagina dell’interfaccia.</p></div></header>
      <label><span>Nome organizzazione</span><input name="organizationName" [(ngModel)]="organizationName" required maxlength="200" /></label>
      <footer><button class="button button--primary" type="submit" [disabled]="saving || !loaded">{{ saving ? 'Salvataggio…' : 'Salva configurazioni' }}</button><span class="feedback" [class.feedback--error]="errorMessage">{{ errorMessage || successMessage }}</span></footer>
    </form>
    <section class="config-section card">
      <header><div><p class="eyebrow">Accessi</p><h2>Utenti responsabili</h2><p class="section-description">Possono accedere e gestire l’intera applicazione.</p></div></header>
      <div class="user-list">
        @for (user of responsibleUsers; track user.id) {
          <div class="user-row"><div><strong>{{ user.display_name }}</strong><small>{{ user.email }}</small></div><span class="status-badge" [class.status-badge--success]="user.is_active">{{ user.is_active ? 'Attivo' : 'Disattivo' }}</span><button class="button button--secondary" type="button" (click)="toggleUser(user)" [disabled]="user.id === currentUserId">{{ user.is_active ? 'Disattiva' : 'Riattiva' }}</button></div>
        }
      </div>
      <form class="new-user" (ngSubmit)="addUser()">
        <label><span>Nome</span><input name="responsibleName" [(ngModel)]="newUserName" required maxlength="200" /></label>
        <label><span>Email</span><input name="responsibleEmail" [(ngModel)]="newUserEmail" required type="email" maxlength="320" /></label>
        <label><span>Password iniziale</span><input name="responsiblePassword" [(ngModel)]="newUserPassword" required type="password" minlength="12" maxlength="256" /></label>
        <button class="button button--secondary" type="submit" [disabled]="savingUser">Aggiungi responsabile</button>
      </form>
      @if (userErrorMessage) { <p class="feedback feedback--error">{{ userErrorMessage }}</p> }
    </section>
    <form class="config-section card" (ngSubmit)="save()">
      <header><div><p class="eyebrow">Archivio</p><h2>Collegamento Google Drive</h2><p class="section-description">Cartella principale usata per l’archivio documentale.</p></div></header>
      <label><span>URL cartella principale</span><input name="archiveUrl" [(ngModel)]="archiveGoogleDriveUrl" maxlength="2000" placeholder="https://drive.google.com/..." /></label>
      <footer><button class="button button--primary" type="submit" [disabled]="saving || !loaded">{{ saving ? 'Salvataggio…' : 'Salva configurazioni' }}</button><span class="feedback" [class.feedback--error]="errorMessage">{{ errorMessage || successMessage }}</span></footer>
    </form>
    <form class="config-section card" (ngSubmit)="save()">
      <header><div><p class="eyebrow">Interfaccia</p><h2>Tema predefinito</h2><p class="section-description">Preferenza salvata per la futura selezione del tema dell’applicazione.</p></div></header>
      <label><span>Tema</span><select name="defaultTheme" [(ngModel)]="defaultTheme"><option value="light">Chiaro</option><option value="dark">Scuro</option></select></label>
      <footer><button class="button button--primary" type="submit" [disabled]="saving || !loaded">{{ saving ? 'Salvataggio…' : 'Salva configurazioni' }}</button><span class="feedback" [class.feedback--error]="errorMessage">{{ errorMessage || successMessage }}</span></footer>
    </form>
  `,
  styles: `
    .settings-grid { display: grid; gap: var(--sp-4); grid-template-columns: repeat(2, 1fr); margin-bottom: var(--sp-6); }
    .settings-card { align-items: center; display: grid; gap: var(--sp-3); grid-template-columns: 44px 1fr auto; padding: var(--sp-4); }
    .settings-icon { align-items: center; background: var(--color-accent-soft); border-radius: var(--radius-md); color: var(--color-accent-hover); display: flex; font-size: var(--text-xs); font-weight: var(--weight-semi); height: 44px; justify-content: center; }
    h2 { font-family: var(--font-sans); font-size: var(--text-lg); margin: 0; }
    .settings-card p, .section-description { color: var(--text-secondary); font-size: var(--text-sm); margin: var(--sp-1) 0 0; }
    .config-section { display: grid; gap: var(--sp-4); margin-top: var(--sp-4); padding: var(--sp-6); }
    .config-section header { border-bottom: var(--border-thin) solid var(--border-subtle); padding-bottom: var(--sp-4); }
    .eyebrow { color: var(--color-accent-hover); font-size: var(--text-xs); font-weight: var(--weight-semi); letter-spacing: .08em; margin: 0 0 var(--sp-1); text-transform: uppercase; }
    label { display: grid; font-size: var(--text-sm); gap: var(--sp-2); }
    input, select { background: var(--bg-raised); border: var(--border-thin) solid var(--border-default); border-radius: var(--radius-md); color: var(--text-primary); min-height: 40px; padding: 0 var(--sp-3); }
    footer { align-items: center; display: flex; gap: var(--sp-3); }
    .feedback { color: var(--color-success); font-size: var(--text-sm); }.feedback--error { color: var(--color-danger); }
    .user-list { display: grid; }.user-row { align-items: center; border-bottom: var(--border-thin) solid var(--border-subtle); display: grid; gap: var(--sp-3); grid-template-columns: 1fr auto auto; padding: var(--sp-3) 0; }.user-row > div { display: grid; }.user-row small { color: var(--text-tertiary); }.new-user { align-items: end; background: var(--bg-raised); border-radius: var(--radius-md); display: grid; gap: var(--sp-3); grid-template-columns: 1fr 1fr 1fr auto; padding: var(--sp-4); }
    @media (max-width: 800px) { .settings-grid, .new-user { grid-template-columns: 1fr; } .user-row { grid-template-columns: 1fr auto; } }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SettingsPageComponent implements OnInit {
  private readonly settings = inject(SettingsService);
  private readonly auth = inject(AuthService);
  protected readonly database = inject(DatabaseStatusService);
  protected organizationName = '';
  protected archiveGoogleDriveUrl = '';
  protected defaultTheme: GeneralSettings['default_theme'] = 'light';
  protected loaded = false;
  protected saving = false;
  protected successMessage = '';
  protected errorMessage = '';
  protected responsibleUsers: ResponsibleUser[] = [];
  protected currentUserId: number | null = null;
  protected newUserName = '';
  protected newUserEmail = '';
  protected newUserPassword = '';
  protected savingUser = false;
  protected userErrorMessage = '';

  ngOnInit(): void {
    this.settings.loadGeneral().subscribe({
      next: (settings) => this.setForm(settings),
      error: () => this.errorMessage = 'Impossibile caricare le configurazioni.',
    });
    this.loadUsers();
  }

  protected save(): void {
    const current = this.settings.general();
    if (!current || !this.organizationName.trim()) return;
    this.saving = true;
    this.successMessage = '';
    this.errorMessage = '';
    this.settings.saveGeneral({
      ...current,
      organization_name: this.organizationName.trim(),
      archive_google_drive_url: this.archiveGoogleDriveUrl.trim(),
      default_theme: this.defaultTheme,
    }).subscribe({
      next: (settings) => { this.setForm(settings); this.saving = false; this.successMessage = 'Configurazioni salvate.'; },
      error: () => { this.saving = false; this.errorMessage = 'Salvataggio non riuscito: ricarica la pagina e riprova.'; },
    });
  }

  private setForm(settings: GeneralSettings): void {
    this.organizationName = settings.organization_name;
    this.archiveGoogleDriveUrl = settings.archive_google_drive_url;
    this.defaultTheme = settings.default_theme;
    this.loaded = true;
  }

  protected addUser(): void {
    if (!this.newUserName.trim() || !this.newUserEmail.trim() || this.newUserPassword.length < 12) return;
    this.savingUser = true;
    this.userErrorMessage = '';
    this.settings.addResponsibleUser({
      display_name: this.newUserName.trim(), email: this.newUserEmail.trim(), password: this.newUserPassword,
    }).subscribe({
      next: () => { this.newUserName = ''; this.newUserEmail = ''; this.newUserPassword = ''; this.savingUser = false; this.loadUsers(); },
      error: () => { this.savingUser = false; this.userErrorMessage = 'Impossibile aggiungere il responsabile.'; },
    });
  }

  protected toggleUser(user: ResponsibleUser): void {
    this.userErrorMessage = '';
    this.settings.updateResponsibleUser(user.id, { is_active: !user.is_active, version: user.version }).subscribe({
      next: () => this.loadUsers(),
      error: () => this.userErrorMessage = 'Non è stato possibile aggiornare il responsabile.',
    });
  }

  private loadUsers(): void {
    this.settings.responsibleUsers().subscribe({
      next: (users) => {
        this.responsibleUsers = users;
        this.currentUserId = this.auth.user()?.id ?? null;
      },
      error: () => this.userErrorMessage = 'Impossibile caricare i responsabili.',
    });
  }
}

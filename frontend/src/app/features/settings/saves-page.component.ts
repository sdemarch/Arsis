import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { apiErrorMessage } from '../../core/api/api-error';
import { AuthService } from '../../core/auth/auth.service';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';
import { SaveImportResult, SaveSummary, SavesService, downloadName } from './saves.service';

@Component({
  selector: 'arsis-saves-page',
  imports: [DatePipe, FormsModule, PageHeaderComponent, RouterLink],
  template: `
    <arsis-page-header eyebrow="Configurazioni" title="Salvataggi" description="Copia tutti i dati in un file .arsis-save o ripristinali da un salvataggio.">
      <a class="button button--secondary" routerLink="/settings">← Configurazioni</a>
    </arsis-page-header>

    <section class="card">
      <h2>Esporta</h2>
      <p>Il file contiene database e allegati: conservalo in un luogo sicuro o usalo per spostare Arsis su un altro PC.</p>
      <button type="button" class="button button--primary" [disabled]="exporting()" (click)="exportSave()">{{ exporting() ? 'Preparazione…' : 'Scarica salvataggio' }}</button>
      @if (exportError()) { <p class="feedback feedback--error" role="alert">{{ exportError() }}</p> }
    </section>

    <section class="card">
      <h2>Importa</h2>
      @if (result(); as done) {
        <p class="feedback feedback--success" role="status">Importazione completata.</p>
        <p>I dati precedenti sono stati salvati in <code>backups\\{{ done.backup_file }}</code>.</p>
        <p>Accedi di nuovo con le credenziali di un responsabile presente nel salvataggio.</p>
        <button type="button" class="button button--primary" (click)="signInAgain()">Vai all’accesso</button>
      } @else {
        <p>Sostituisce <strong>tutti</strong> i dati attuali con quelli del salvataggio. Prima di procedere Arsis salva una copia dei dati attuali.</p>
        <label class="file"><span>File di salvataggio</span><input type="file" accept=".arsis-save" [disabled]="busy()" (change)="selectFile($event)" /></label>
        @if (inspecting()) { <p>Verifica del file…</p> }
        @if (summary(); as save) {
          <dl class="summary">
            <div><dt>Creato il</dt><dd>{{ save.created_at | date: 'd MMMM y, HH:mm' }}</dd></div>
            <div><dt>Organizzazione</dt><dd>{{ save.organization_name ?? '—' }}</dd></div>
            <div><dt>Persone</dt><dd>{{ save.contents.people }}</dd></div>
            <div><dt>Attività</dt><dd>{{ save.contents.activities }}</dd></div>
            <div><dt>Corsi</dt><dd>{{ save.contents.courses }}</dd></div>
            <div><dt>Movimenti contabili</dt><dd>{{ save.contents.accounting_movements }}</dd></div>
            <div><dt>Responsabili</dt><dd>{{ save.contents.responsible_users }}</dd></div>
            <div><dt>Allegati</dt><dd>{{ save.contents.attachments }}</dd></div>
          </dl>
          @if (save.pending_migrations) {
            <p class="note">Il salvataggio proviene da una versione precedente di Arsis: verrà aggiornato durante l’importazione.</p>
          }
          <form class="confirm" (ngSubmit)="importSave()">
            <label><span>Conferma con la tua password</span><input type="password" name="password" [(ngModel)]="password" required autocomplete="current-password" /></label>
            <button class="button button--danger" [disabled]="busy() || !password">{{ importing() ? 'Importazione…' : 'Sostituisci i dati' }}</button>
          </form>
        }
        @if (importError()) { <p class="feedback feedback--error" role="alert">{{ importError() }}</p> }
      }
    </section>
  `,
  styles: `
    .card { padding: var(--sp-6); }
    .card + .card { margin-top: var(--sp-5); }
    h2 { margin-top: 0; }
    p { color: var(--text-secondary); }
    label { display: grid; gap: var(--sp-2); max-width: 420px; }
    input[type='password'] { min-height: 38px; padding: var(--sp-2); }
    .summary { display: grid; gap: var(--sp-3) var(--sp-6); grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); margin: var(--sp-5) 0; }
    dt { color: var(--text-secondary); font-size: var(--text-xs); }
    dd { font-weight: var(--weight-semi); margin: 0; }
    .note { color: var(--text-primary); }
    .confirm { align-items: end; display: flex; flex-wrap: wrap; gap: var(--sp-3); }
    .feedback--error { color: var(--color-danger); }
    .feedback--success { color: var(--color-success); }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SavesPageComponent {
  private readonly saves = inject(SavesService);
  private readonly auth = inject(AuthService);
  private file: File | null = null;

  protected readonly exporting = signal(false);
  protected readonly exportError = signal('');
  protected readonly inspecting = signal(false);
  protected readonly importing = signal(false);
  protected readonly summary = signal<SaveSummary | null>(null);
  protected readonly result = signal<SaveImportResult | null>(null);
  protected readonly importError = signal('');
  protected password = '';

  protected busy(): boolean {
    return this.inspecting() || this.importing();
  }

  protected exportSave(): void {
    this.exporting.set(true);
    this.exportError.set('');
    this.saves.exportSave().subscribe({
      next: (response) => {
        const url = URL.createObjectURL(response.body!);
        const link = Object.assign(document.createElement('a'), { href: url, download: downloadName(response) });
        link.click();
        URL.revokeObjectURL(url);
        this.exporting.set(false);
      },
      error: () => {
        this.exportError.set('Esportazione non riuscita.');
        this.exporting.set(false);
      },
    });
  }

  protected selectFile(event: Event): void {
    this.file = (event.target as HTMLInputElement).files?.[0] ?? null;
    this.summary.set(null);
    this.importError.set('');
    this.password = '';
    if (!this.file) return;
    this.inspecting.set(true);
    this.saves.inspect(this.file).subscribe({
      next: (summary) => {
        this.summary.set(summary);
        this.inspecting.set(false);
      },
      error: (error: unknown) => {
        this.importError.set(apiErrorMessage(error, 'Il file non è un salvataggio valido.'));
        this.inspecting.set(false);
      },
    });
  }

  protected importSave(): void {
    if (!this.file || !this.password) return;
    this.importing.set(true);
    this.importError.set('');
    this.saves.importSave(this.file, this.password).subscribe({
      next: (result) => {
        this.result.set(result);
        this.importing.set(false);
      },
      error: (error: unknown) => {
        this.importError.set(apiErrorMessage(error, 'Importazione non riuscita.'));
        this.importing.set(false);
      },
    });
  }

  protected signInAgain(): void {
    // A full reload drops every cached view of the replaced data.
    this.auth.clearSession();
    window.location.assign('/login');
  }
}

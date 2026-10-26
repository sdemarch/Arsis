import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { ActivatedRoute } from '@angular/router';
import { forkJoin } from 'rxjs';

import { DetailCardComponent } from '../../shared/ui/detail-card.component';
import { PeopleService } from './people.service';

const ROLE_LABELS: Record<string, string> = {
  member: 'Socio',
  musician: 'Musicante',
  student: 'Allievo',
  teacher: 'Insegnante',
};

@Component({
  selector: 'arsis-person-detail',
  imports: [DetailCardComponent],
  template: `
    @if (person(); as person) {
      <arsis-detail-card backLink="/people" backLabel="Tutte le persone" eyebrow="Persona" [title]="person.first_name + ' ' + person.last_name" [subtitle]="roleNames().join(' · ')" [editable]="false">
        <span detail-visual class="avatar avatar--large av-blue">{{ initials() }}</span>
        <div class="detail-sections">
          <section>
            <header><div><p class="section-kicker">Anagrafica</p><h2>Dati personali</h2></div><span class="status-badge status-badge--success">{{ person.archived_at ? 'Archiviata' : 'Attiva' }}</span></header>
            <div class="field-grid">
              <label><span>Nome e cognome</span><strong>{{ person.first_name }} {{ person.last_name }}</strong></label>
              <label><span>Data di nascita</span><strong>{{ person.birth_date || 'Non indicata' }}</strong></label>
              <label><span>Luogo di nascita</span><strong>{{ person.birth_place || 'Non indicato' }}</strong></label>
              <label><span>Codice fiscale</span><strong>{{ person.tax_code || 'Non indicato' }}</strong></label>
              <label class="field-grid__wide"><span>Ruoli</span><div class="tag-list">@for (role of roleNames(); track role) { <em>{{ role }}</em> }</div></label>
              <label class="field-grid__wide"><span>Indirizzo</span><strong>{{ person.residence_address || 'Non indicato' }}</strong></label>
            </div>
          </section>
          <section>
            <header><div><p class="section-kicker">Recapiti</p><h2>Contatti</h2></div></header>
            <div class="field-grid">
              <label><span>Email</span><strong>{{ person.email || 'Non indicata' }}</strong></label>
              <label><span>Telefono</span><strong>{{ person.phone || 'Non indicato' }}</strong></label>
            </div>
          </section>
          <section>
            <header><div><p class="section-kicker">Informazioni interne</p><h2>Note</h2></div></header>
            <p class="empty-value">{{ person.notes || 'Nessuna nota inserita.' }}</p>
          </section>
        </div>
      </arsis-detail-card>
    } @else { <p class="empty-value">Caricamento della persona…</p> }
  `,
  styleUrl: '../../shared/ui/detail-fields.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PersonDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly peopleService = inject(PeopleService);
  private readonly personId = Number(this.route.snapshot.paramMap.get('personId'));
  private readonly data = toSignal(
    forkJoin({
      person: this.peopleService.getPerson(this.personId),
      roles: this.peopleService.listRoles(this.personId),
    }),
    { initialValue: null },
  );

  protected readonly person = computed(() => this.data()?.person ?? null);
  protected readonly roleNames = computed(() =>
    (this.data()?.roles ?? []).map((role) => ROLE_LABELS[role.role_type] ?? role.role_type),
  );
  protected readonly initials = computed(() => {
    const person = this.person();
    return person ? `${person.first_name[0] ?? ''}${person.last_name[0] ?? ''}` : '';
  });
}

import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterLink } from '@angular/router';

import peopleData from '../../../assets/mock/people.json';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';

@Component({
  selector: 'arsis-people-page',
  imports: [PageHeaderComponent, RouterLink],
  template: `
    <arsis-page-header eyebrow="Soci" title="Persone" description="Anagrafica unica di soci, musicanti, allievi e insegnanti.">
      <a class="button button--primary" routerLink="/people/new">＋ Nuova persona</a>
    </arsis-page-header>

    <div class="summary-line">
      <span><strong>{{ summary.active }}</strong> persone attive</span>
      <span><strong>{{ summary.archived }}</strong> archiviate</span>
    </div>

    <div class="toolbar">
      <div class="toolbar__group">
        <input class="search-input" type="search" placeholder="Cerca nome, email o telefono…" aria-label="Cerca persone" />
        <button class="button button--secondary" type="button">Tutti i ruoli⌄</button>
        <button class="button button--secondary" type="button">Attive⌄</button>
      </div>
      <button class="button button--secondary" type="button">Azzera filtri</button>
    </div>

    <div class="table-shell">
      <table>
        <thead><tr><th>Persona</th><th>Contatti</th><th>Ruoli</th><th>Stato</th><th>Ultima modifica</th><th></th></tr></thead>
        <tbody>
          @for (person of people; track person.id) {
            <tr>
              <td><a class="person" [routerLink]="['/people', person.id]"><span class="avatar {{ person.avatar }}">{{ person.initials }}</span><strong>{{ person.name }}</strong></a></td>
              <td><div class="contacts"><span>{{ person.email }}</span><small>{{ person.phone }}</small></div></td>
              <td><div class="roles">@for (role of person.roles; track role) { <span>{{ role }}</span> }</div></td>
              <td><span class="status-badge status-badge--success">{{ person.status }}</span></td>
              <td><time>{{ person.updated }}</time></td>
              <td><button class="row-menu" type="button" aria-label="Azioni per {{ person.name }}">•••</button></td>
            </tr>
          }
        </tbody>
      </table>
      <footer class="table-footer"><span>Mostrate {{ people.length }} di {{ summary.active }} persone</span><div><button disabled>←</button><strong>1</strong><button>2</button><button>3</button><button>→</button></div></footer>
    </div>
  `,
  styles: `
    .summary-line { color: var(--text-secondary); display: flex; font-size: var(--text-sm); gap: var(--sp-5); margin: calc(var(--sp-5) * -1) 0 var(--sp-6); }
    .summary-line strong { color: var(--text-primary); }
    .person { align-items: center; color: var(--text-primary); display: flex; gap: var(--sp-3); text-decoration: none; }
    .contacts { display: grid; }
    .contacts small { color: var(--text-tertiary); }
    .roles { display: flex; flex-wrap: wrap; gap: var(--sp-1); }
    .roles span { background: var(--bg-raised); border-radius: var(--radius-full); color: var(--text-secondary); font-size: var(--text-xs); padding: var(--sp-1) var(--sp-2); }
    td time { color: var(--text-secondary); font-size: var(--text-sm); }
    .row-menu { background: transparent; border: 0; color: var(--text-tertiary); cursor: pointer; }
    .table-footer { align-items: center; border-top: var(--border-thin) solid var(--border-subtle); color: var(--text-secondary); display: flex; font-size: var(--text-sm); justify-content: space-between; padding: var(--sp-3) var(--sp-4); }
    .table-footer div { display: flex; gap: var(--sp-1); }
    .table-footer button, .table-footer strong { align-items: center; background: transparent; border: 0; border-radius: var(--radius-sm); color: var(--text-secondary); display: flex; height: 28px; justify-content: center; width: 28px; }
    .table-footer strong { background: var(--color-accent-soft); color: var(--color-accent-hover); }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PeoplePageComponent {
  protected readonly people = peopleData.people;
  protected readonly summary = peopleData.summary;
}

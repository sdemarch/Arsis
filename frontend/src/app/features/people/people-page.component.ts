import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import peopleData from '../../../assets/mock/people.json';
import { ConfigurationStore } from '../../core/config/configuration.store';
import { FilterDropdownComponent, FilterOption } from '../../shared/ui/filter-dropdown.component';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';

@Component({
  selector: 'arsis-people-page',
  imports: [FilterDropdownComponent, FormsModule, PageHeaderComponent, RouterLink],
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
        <input class="search-input" type="search" placeholder="Cerca nome, email o telefono…" aria-label="Cerca persone" [ngModel]="search()" (ngModelChange)="setSearch($event)" />
        <arsis-filter-dropdown label="Tutti i ruoli" [options]="roleOptions()" [selected]="selectedRoles()" [multiple]="true" (selectionChange)="setRoles($event)" />
        <arsis-filter-dropdown label="Tutti gli stati" [options]="statusOptions" [selected]="selectedStatuses()" (selectionChange)="setStatuses($event)" />
      </div>
      <button class="button button--secondary" type="button" [disabled]="!hasFilters()" (click)="clearFilters()">Azzera filtri</button>
    </div>

    <div class="table-shell">
      <table>
        <thead><tr><th>Persona</th><th>Contatti</th><th>Ruoli</th><th>Stato</th><th>Ultima modifica</th><th></th></tr></thead>
        <tbody>
          @for (person of filteredPeople(); track person.id) {
            <tr [routerLink]="['/people', person.id]" tabindex="0" aria-label="Apri la scheda di {{ person.name }}">
              <td><a class="person" [routerLink]="['/people', person.id]"><span class="avatar {{ person.avatar }}">{{ person.initials }}</span><strong>{{ person.name }}</strong></a></td>
              <td><div class="contacts"><span>{{ person.email }}</span><small>{{ person.phone }}</small></div></td>
              <td><div class="roles">@for (role of person.roles; track role) { <span>{{ role }}</span> }</div></td>
              <td><span class="status-badge status-badge--success">{{ person.status }}</span></td>
              <td><time>{{ person.updated }}</time></td>
              <td><button class="row-menu" type="button" aria-label="Azioni per {{ person.name }}">•••</button></td>
            </tr>
          }
          @empty { <tr><td class="empty-state" colspan="6">Nessuna persona corrisponde ai filtri selezionati.</td></tr> }
        </tbody>
      </table>
      <footer class="table-footer"><span>Mostrate {{ filteredPeople().length }} di {{ people.length }} persone</span><div><button disabled>←</button><strong>1</strong><button>2</button><button>3</button><button>→</button></div></footer>
    </div>
  `,
  styles: `
    .summary-line { color: var(--text-secondary); display: flex; font-size: var(--text-sm); gap: var(--sp-5); margin: calc(var(--sp-5) * -1) 0 var(--sp-6); }
    .summary-line strong { color: var(--text-primary); }
    tbody tr { cursor: pointer; }
    .person { align-items: center; color: var(--text-primary); display: flex; gap: var(--sp-3); text-decoration: none; }
    .contacts { display: grid; }
    .contacts small { color: var(--text-tertiary); }
    .roles { display: flex; flex-wrap: wrap; gap: var(--sp-1); }
    .roles span { background: var(--bg-raised); border-radius: var(--radius-full); color: var(--text-secondary); font-size: var(--text-xs); padding: var(--sp-1) var(--sp-2); }
    td time { color: var(--text-secondary); font-size: var(--text-sm); }
    .row-menu { background: transparent; border: 0; color: var(--text-tertiary); cursor: pointer; }
    .toolbar .button:disabled { cursor: not-allowed; opacity: .5; }
    .empty-state { color: var(--text-tertiary); padding: var(--sp-8); text-align: center; }
    .table-footer { align-items: center; border-top: var(--border-thin) solid var(--border-subtle); color: var(--text-secondary); display: flex; font-size: var(--text-sm); justify-content: space-between; padding: var(--sp-3) var(--sp-4); }
    .table-footer div { display: flex; gap: var(--sp-1); }
    .table-footer button, .table-footer strong { align-items: center; background: transparent; border: 0; border-radius: var(--radius-sm); color: var(--text-secondary); display: flex; height: 28px; justify-content: center; width: 28px; }
    .table-footer strong { background: var(--color-accent-soft); color: var(--color-accent-hover); }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PeoplePageComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly configuration = inject(ConfigurationStore);
  private readonly queryParams = toSignal(this.route.queryParamMap, { initialValue: this.route.snapshot.queryParamMap });

  protected readonly people = peopleData.people;
  protected readonly summary = peopleData.summary;
  protected readonly search = computed(() => this.queryParams().get('q')?.trim() ?? '');
  protected readonly selectedRoles = computed(() => this.queryParams().getAll('role'));
  protected readonly selectedStatuses = computed(() => this.queryParams().getAll('status'));
  protected readonly roleOptions = computed<readonly FilterOption[]>(() =>
    this.configuration.roles().filter((role) => role.active).map((role) => ({ label: role.label, value: role.id })),
  );
  protected readonly statusOptions: readonly FilterOption[] = [
    { label: 'Attive', value: 'active' },
    { label: 'Archiviate', value: 'archived' },
  ];
  protected readonly hasFilters = computed(() => Boolean(this.search() || this.selectedRoles().length || this.selectedStatuses().length));
  protected readonly filteredPeople = computed(() => {
    const query = this.search().toLocaleLowerCase('it');
    const selectedRoleLabels = this.selectedRoles()
      .map((roleId) => this.configuration.roles().find((role) => role.id === roleId)?.label)
      .filter((role): role is string => Boolean(role));
    const statuses = this.selectedStatuses();

    return this.people.filter((person) => {
      const matchesQuery = !query || [person.name, person.email, person.phone].some((value) => value.toLocaleLowerCase('it').includes(query));
      const matchesRoles = !selectedRoleLabels.length || selectedRoleLabels.some((role) => person.roles.includes(role));
      const personStatus = person.status === 'Attiva' ? 'active' : 'archived';
      const matchesStatus = !statuses.length || statuses.includes(personStatus);
      return matchesQuery && matchesRoles && matchesStatus;
    });
  });

  protected setSearch(query: string): void {
    this.updateQuery({ q: query.trim() || null });
  }

  protected setRoles(roles: readonly string[]): void {
    this.updateQuery({ role: roles.length ? [...roles] : null });
  }

  protected setStatuses(statuses: readonly string[]): void {
    this.updateQuery({ status: statuses.length ? [...statuses] : null });
  }

  protected clearFilters(): void {
    this.updateQuery({ q: null, role: null, status: null });
  }

  private updateQuery(queryParams: Record<string, string | string[] | null>): void {
    void this.router.navigate([], { relativeTo: this.route, queryParams, queryParamsHandling: 'merge', replaceUrl: true });
  }
}

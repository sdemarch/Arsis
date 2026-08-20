import { ChangeDetectionStrategy, Component } from '@angular/core';
import { PlaceholderPageComponent } from '../../shared/ui/placeholder-page.component';

@Component({
  selector: 'arsis-people-page',
  imports: [PlaceholderPageComponent],
  template: `<arsis-placeholder-page eyebrow="Soci" title="Persone" description="Anagrafica unica, ruoli e contatti associati." />`,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PeoplePageComponent {}


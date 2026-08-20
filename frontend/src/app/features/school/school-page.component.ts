import { ChangeDetectionStrategy, Component } from '@angular/core';
import { PlaceholderPageComponent } from '../../shared/ui/placeholder-page.component';

@Component({
  selector: 'arsis-school-page',
  imports: [PlaceholderPageComponent],
  template: `<arsis-placeholder-page eyebrow="Scuola" title="Scuola di musica" description="Corsi, iscrizioni, lezioni e presenze." />`,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SchoolPageComponent {}


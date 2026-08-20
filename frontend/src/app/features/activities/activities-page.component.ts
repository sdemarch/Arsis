import { ChangeDetectionStrategy, Component } from '@angular/core';
import { PlaceholderPageComponent } from '../../shared/ui/placeholder-page.component';

@Component({
  selector: 'arsis-activities-page',
  imports: [PlaceholderPageComponent],
  template: `<arsis-placeholder-page eyebrow="Attività" title="Calendario e attività" description="Prove, concerti, eventi e registro presenze." />`,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ActivitiesPageComponent {}


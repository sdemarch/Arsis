import { ChangeDetectionStrategy, Component } from '@angular/core';
import { PlaceholderPageComponent } from '../../shared/ui/placeholder-page.component';

@Component({
  selector: 'arsis-settings-page',
  imports: [PlaceholderPageComponent],
  template: `<arsis-placeholder-page eyebrow="Configurazione" title="Impostazioni" description="Strumenti, sezioni, archivio e utenti responsabili." />`,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SettingsPageComponent {}


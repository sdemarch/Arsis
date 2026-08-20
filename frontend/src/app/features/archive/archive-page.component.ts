import { ChangeDetectionStrategy, Component } from '@angular/core';
import { PlaceholderPageComponent } from '../../shared/ui/placeholder-page.component';

@Component({
  selector: 'arsis-archive-page',
  imports: [PlaceholderPageComponent],
  template: `<arsis-placeholder-page eyebrow="Archivio" title="Archivio documentale" description="Collegamento alla cartella principale Google Drive." />`,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ArchivePageComponent {}


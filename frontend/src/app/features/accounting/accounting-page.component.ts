import { ChangeDetectionStrategy, Component } from '@angular/core';
import { PageHeaderComponent } from '../../shared/ui/page-header.component';

@Component({
  selector: 'arsis-accounting-page',
  imports: [PageHeaderComponent],
  template: `<arsis-page-header eyebrow="Contabilità" title="Funzionalità da definire" description="Rate, pagamenti, compensi e rimborsi saranno progettati dopo un’analisi dedicata." />`,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AccountingPageComponent {}


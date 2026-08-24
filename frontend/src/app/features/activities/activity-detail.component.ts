import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';

import activityData from '../../../assets/mock/activities.json';
import { DetailCardComponent } from '../../shared/ui/detail-card.component';

@Component({
  selector: 'arsis-activity-detail',
  imports: [DetailCardComponent, FormsModule],
  template: `
    <arsis-detail-card backLink="/activities" backLabel="Tutte le attività" eyebrow="Attività" [title]="draft.title" [subtitle]="draft.type + ' · ' + draft.status" [editing]="editing()" (editRequested)="toggleEditing()">
      <div detail-visual class="date-visual"><strong>{{ draft.date.split(' ')[0] }}</strong><span>{{ draft.date.split(' ')[1] }}</span></div>
      <div class="detail-sections">
        <section>
          <header><div><p class="section-kicker">Programmazione</p><h2>Dettagli attività</h2></div><span class="status-badge status-badge--{{ draft.tone }}">{{ draft.status }}</span></header>
          <div class="field-grid">
            <label><span>Titolo</span>@if (editing()) { <input [(ngModel)]="draft.title" /> } @else { <strong>{{ draft.title }}</strong> }</label>
            <label><span>Tipologia</span>@if (editing()) { <select [(ngModel)]="draft.type"><option>Prova</option><option>Concerto</option><option>Evento</option></select> } @else { <strong>{{ draft.type }}</strong> }</label>
            <label><span>Data</span>@if (editing()) { <input [(ngModel)]="draft.date" /> } @else { <strong>{{ draft.weekday }}, {{ draft.date }}</strong> }</label>
            <label><span>Orario</span>@if (editing()) { <input [(ngModel)]="draft.time" /> } @else { <strong>{{ draft.time }}</strong> }</label>
            <label><span>Luogo</span>@if (editing()) { <input [(ngModel)]="draft.location" /> } @else { <strong>{{ draft.location }}</strong> }</label>
            <label><span>Stato</span>@if (editing()) { <select [(ngModel)]="draft.status"><option>Confermata</option><option>Pianificata</option><option>Annullata</option></select> } @else { <strong>{{ draft.status }}</strong> }</label>
          </div>
        </section>
        <section>
          <header><div><p class="section-kicker">Partecipazione</p><h2>Convocazioni</h2></div></header>
          <div class="field-grid"><label><span>Partecipanti convocati</span>@if (editing()) { <input type="number" min="0" [(ngModel)]="draft.participants" /> } @else { <strong>{{ draft.participants }} persone</strong> }</label></div>
        </section>
        <section>
          <header><div><p class="section-kicker">Informazioni interne</p><h2>Note organizzative</h2></div></header>
          @if (editing()) { <textarea [(ngModel)]="notes" rows="4" placeholder="Aggiungi indicazioni per l’attività…"></textarea> } @else { <p class="empty-value">{{ notes || 'Nessuna nota inserita.' }}</p> }
        </section>
      </div>
    </arsis-detail-card>
  `,
  styleUrls: ['../../shared/ui/detail-fields.css', './activity-detail.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ActivityDetailComponent {
  private readonly activityId = inject(ActivatedRoute).snapshot.paramMap.get('activityId');
  private readonly source = activityData.activities.find((activity) => activity.id === this.activityId) ?? activityData.activities[0];
  protected readonly editing = signal(false);
  protected draft = { ...this.source };
  protected notes = '';

  protected toggleEditing(): void {
    this.editing.update((value) => !value);
  }
}

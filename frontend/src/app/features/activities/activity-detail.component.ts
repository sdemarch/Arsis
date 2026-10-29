import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

import { DetailCardComponent } from '../../shared/ui/detail-card.component';
import { ActivitiesService, Activity, ActivityWrite } from './activities.service';

const TYPE_LABELS: Record<Activity['type'], string> = { rehearsal: 'Prova', concert: 'Concerto', event: 'Evento' };
const STATUS_LABELS: Record<Activity['status'], string> = { planned: 'Pianificata', confirmed: 'Confermata', cancelled: 'Annullata', completed: 'Completata' };

@Component({
  selector: 'arsis-activity-detail', imports: [DetailCardComponent, FormsModule],
  template: `@if (activity(); as item) { <arsis-detail-card backLink="/activities" backLabel="Tutte le attività" eyebrow="Attività" [title]="item.title" [subtitle]="typeLabel(item.type) + ' · ' + statusLabel(item.status)" [editing]="editing()" [editable]="!item.archived_at" (editRequested)="editing() ? save() : beginEdit()"><div detail-visual class="date-visual"><strong>{{ date(item.starts_at) }}</strong></div><div class="detail-sections"><section><header><div><p class="section-kicker">Programmazione</p><h2>Dettagli attività</h2></div><span class="status-badge">{{ statusLabel(item.status) }}</span></header><div class="field-grid"><label><span>Titolo</span>@if(editing()){<input name="title" [(ngModel)]="draft.title"/>}@else{<strong>{{item.title}}</strong>}</label><label><span>Tipologia</span>@if(editing()){<select name="type" [(ngModel)]="draft.type"><option value="rehearsal">Prova</option><option value="concert">Concerto</option><option value="event">Evento</option></select>}@else{<strong>{{typeLabel(item.type)}}</strong>}</label><label><span>Inizio</span>@if(editing()){<input name="starts" type="datetime-local" [(ngModel)]="draft.starts_at"/>}@else{<strong>{{item.starts_at}}</strong>}</label><label><span>Luogo</span>@if(editing()){<input name="location" [(ngModel)]="draft.location"/>}@else{<strong>{{item.location||'Non indicato'}}</strong>}</label><label><span>Stato</span>@if(editing()){<select name="status" [(ngModel)]="draft.status"><option value="planned">Pianificata</option><option value="confirmed">Confermata</option><option value="cancelled">Annullata</option><option value="completed">Completata</option></select>}@else{<strong>{{statusLabel(item.status)}}</strong>}</label></div></section><section><header><div><p class="section-kicker">Note</p><h2>Informazioni interne</h2></div></header>@if(editing()){<textarea name="notes" [(ngModel)]="draft.notes" rows="4"></textarea>}@else{<p class="empty-value">{{item.notes||'Nessuna nota inserita.'}}</p>}</section>@if(!item.archived_at){<section><button type="button" class="button button--secondary" (click)="archive()">Archivia attività</button></section>}</div></arsis-detail-card> } @else {<p>Caricamento attività…</p>}`,
  styleUrls: ['../../shared/ui/detail-fields.css', './activity-detail.component.css'], changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ActivityDetailComponent {
  private readonly service=inject(ActivitiesService); private readonly router=inject(Router); private readonly id=Number(inject(ActivatedRoute).snapshot.paramMap.get('activityId'));
  protected readonly activity=signal<Activity|null>(null); protected readonly editing=signal(false); protected draft={title:'',type:'rehearsal' as Activity['type'],starts_at:'',location:'',status:'planned' as Activity['status'],notes:''};
  constructor(){this.load();} protected typeLabel(type:Activity['type']){return TYPE_LABELS[type];} protected statusLabel(status:Activity['status']){return STATUS_LABELS[status];} protected date(value:string){return new Intl.DateTimeFormat('it-IT',{dateStyle:'medium'}).format(new Date(value));}
  protected beginEdit(){const a=this.activity();if(!a)return;this.draft={title:a.title,type:a.type,starts_at:a.starts_at.slice(0,16),location:a.location??'',status:a.status,notes:a.notes??''};this.editing.set(true);}
  protected save(){const a=this.activity();if(!a)return;const payload:ActivityWrite={...this.draft,starts_at:new Date(this.draft.starts_at).toISOString(),location:this.draft.location||null,notes:this.draft.notes||null,version:a.version};this.service.update(a.id,payload).subscribe({next:()=>{this.editing.set(false);this.load();}});}
  protected archive(){const a=this.activity();if(a&&window.confirm(`Archiviare ${a.title}?`))this.service.archive(a.id,a.version).subscribe({next:()=>this.load()});}
  private load(){this.service.get(this.id).subscribe({next:a=>this.activity.set(a)});}
}

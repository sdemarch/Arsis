import { Routes } from '@angular/router';
import { ActivitiesPageComponent } from './activities-page.component';

export const ACTIVITIES_ROUTES: Routes = [
  { path: '', component: ActivitiesPageComponent },
  { path: 'calendar', component: ActivitiesPageComponent },
  { path: 'attendance', component: ActivitiesPageComponent },
  { path: ':activityId', loadComponent: () => import('./activity-detail.component').then((module) => module.ActivityDetailComponent) },
  { path: ':activityId/attendance', component: ActivitiesPageComponent },
];

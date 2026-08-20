import { Routes } from '@angular/router';
import { ActivitiesPageComponent } from './activities-page.component';

export const ACTIVITIES_ROUTES: Routes = [
  { path: '', component: ActivitiesPageComponent },
  { path: 'calendar', component: ActivitiesPageComponent },
  { path: 'attendance', component: ActivitiesPageComponent },
  { path: ':activityId', component: ActivitiesPageComponent },
  { path: ':activityId/attendance', component: ActivitiesPageComponent },
];


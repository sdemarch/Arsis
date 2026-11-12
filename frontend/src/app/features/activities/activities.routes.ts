import { Routes } from '@angular/router';
import { ActivitiesPageComponent } from './activities-page.component';

export const ACTIVITIES_ROUTES: Routes = [
  { path: '', component: ActivitiesPageComponent },
  { path: 'calendar', component: ActivitiesPageComponent },
  { path: 'attendance', component: ActivitiesPageComponent },
  { path: 'refunds', loadComponent: () => import('./activity-refunds-page.component').then((module) => module.ActivityRefundsPageComponent) },
  { path: 'new', loadComponent: () => import('./activity-create.component').then((module) => module.ActivityCreateComponent) },
  { path: ':activityId', loadComponent: () => import('./activity-detail.component').then((module) => module.ActivityDetailComponent) },
  { path: ':activityId/attendance', loadComponent: () => import('./activity-attendance.component').then((module) => module.ActivityAttendanceComponent) },
];

import { Routes } from '@angular/router';
import { SchoolPageComponent } from './school-page.component';

export const SCHOOL_ROUTES: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'courses' },
  { path: 'courses', component: SchoolPageComponent },
  { path: 'courses/:courseId', loadComponent: () => import('./course-detail.component').then((module) => module.CourseDetailComponent) },
  { path: 'enrollments', component: SchoolPageComponent },
  { path: 'lessons', component: SchoolPageComponent },
  { path: 'lessons/:lessonId', component: SchoolPageComponent },
  { path: 'lessons/:lessonId/attendance', component: SchoolPageComponent },
  { path: 'attendance', component: SchoolPageComponent },
];

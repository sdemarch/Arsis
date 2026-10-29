import { Routes } from '@angular/router';
import { EnrollmentsPageComponent } from './enrollments-page.component';
import { SchoolPageComponent } from './school-page.component';

export const SCHOOL_ROUTES: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'courses' },
  { path: 'courses', component: SchoolPageComponent },
  { path: 'courses/new', loadComponent: () => import('./course-create.component').then((module) => module.CourseCreateComponent) },
  { path: 'courses/:courseId', loadComponent: () => import('./course-detail.component').then((module) => module.CourseDetailComponent) },
  { path: 'enrollments', component: EnrollmentsPageComponent },
  { path: 'enrollments/new', loadComponent: () => import('./enrollment-create.component').then((module) => module.EnrollmentCreateComponent) },
  { path: 'enrollments/:enrollmentId', loadComponent: () => import('./enrollment-detail.component').then((module) => module.EnrollmentDetailComponent) },
  { path: 'lessons', component: SchoolPageComponent },
  { path: 'lessons/:lessonId', component: SchoolPageComponent },
  { path: 'lessons/:lessonId/attendance', component: SchoolPageComponent },
  { path: 'attendance', component: SchoolPageComponent },
];

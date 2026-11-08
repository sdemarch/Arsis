import { Routes } from '@angular/router';
import { EnrollmentsPageComponent } from './enrollments-page.component';
import { LessonsPageComponent } from './lessons-page.component';
import { SchoolPageComponent } from './school-page.component';

export const SCHOOL_ROUTES: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'courses' },
  { path: 'courses', component: SchoolPageComponent },
  { path: 'courses/new', loadComponent: () => import('./course-create.component').then((module) => module.CourseCreateComponent) },
  { path: 'courses/:courseId', loadComponent: () => import('./course-detail.component').then((module) => module.CourseDetailComponent) },
  { path: 'enrollments', component: EnrollmentsPageComponent },
  { path: 'enrollments/new', loadComponent: () => import('./enrollment-create.component').then((module) => module.EnrollmentCreateComponent) },
  { path: 'enrollments/:enrollmentId', loadComponent: () => import('./enrollment-detail.component').then((module) => module.EnrollmentDetailComponent) },
  { path: 'lessons', component: LessonsPageComponent },
  { path: 'lessons/new', loadComponent: () => import('./lesson-create.component').then((module) => module.LessonCreateComponent) },
  { path: 'lessons/:lessonId', loadComponent: () => import('./lesson-detail.component').then((module) => module.LessonDetailComponent) },
  { path: 'lessons/:lessonId/attendance', loadComponent: () => import('./lesson-attendance.component').then((module) => module.LessonAttendanceComponent) },
  { path: 'attendance', redirectTo: 'lessons', pathMatch: 'full' },
];

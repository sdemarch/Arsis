import { Routes } from '@angular/router';

export const PEOPLE_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./people-page.component').then((module) => module.PeoplePageComponent),
  },
  {
    path: ':personId',
    loadComponent: () =>
      import('./person-detail.component').then((module) => module.PersonDetailComponent),
  },
];

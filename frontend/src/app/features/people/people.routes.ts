import { Routes } from '@angular/router';

export const PEOPLE_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./people-page.component').then((module) => module.PeoplePageComponent),
  },
  {
    path: 'new',
    loadComponent: () =>
      import('./person-create.component').then((module) => module.PersonCreateComponent),
  },
  {
    path: ':personId',
    loadComponent: () =>
      import('./person-detail.component').then((module) => module.PersonDetailComponent),
  },
];

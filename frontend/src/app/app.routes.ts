import { Routes } from '@angular/router';

export const appRoutes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./core/layout/app-shell.component').then((module) => module.AppShellComponent),
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'home' },
      {
        path: 'home',
        loadComponent: () =>
          import('./features/home/home-page.component').then((module) => module.HomePageComponent),
      },
      {
        path: 'people',
        loadChildren: () => import('./features/people/people.routes').then((module) => module.PEOPLE_ROUTES),
      },
      {
        path: 'activities',
        loadChildren: () =>
          import('./features/activities/activities.routes').then((module) => module.ACTIVITIES_ROUTES),
      },
      {
        path: 'school',
        loadChildren: () => import('./features/school/school.routes').then((module) => module.SCHOOL_ROUTES),
      },
      {
        path: 'archive',
        loadComponent: () =>
          import('./features/archive/archive-page.component').then((module) => module.ArchivePageComponent),
      },
      {
        path: 'accounting',
        loadComponent: () =>
          import('./features/accounting/accounting-page.component').then(
            (module) => module.AccountingPageComponent,
          ),
      },
      {
        path: 'settings',
        loadComponent: () =>
          import('./features/settings/settings-page.component').then((module) => module.SettingsPageComponent),
      },
    ],
  },
  { path: '**', redirectTo: 'home' },
];


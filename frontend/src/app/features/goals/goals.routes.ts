import { Routes } from '@angular/router';

export const GOALS_ROUTES: Routes = [
  { path: '', loadComponent: () => import('./goals-board.component').then((module) => module.GoalsBoardComponent) },
  {
    path: 'history',
    loadComponent: () => import('./goals-history.component').then((module) => module.GoalsHistoryComponent),
  },
  {
    path: 'config',
    loadComponent: () => import('./milestones-config.component').then((module) => module.MilestonesConfigComponent),
  },
];

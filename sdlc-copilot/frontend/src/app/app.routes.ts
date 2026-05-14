import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    loadComponent: () => import('./pages/dashboard/dashboard.component').then(m => m.DashboardComponent),
  },
  {
    path: 'requirements/:id',
    loadComponent: () => import('./pages/requirement-detail/requirement-detail.component').then(m => m.RequirementDetailComponent),
  },
  { path: '**', redirectTo: '' },
];

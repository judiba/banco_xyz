
import { Routes } from '@angular/router';
import { authGuard } from './core/auth/auth.guard';


export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () =>
      import('./pages/login/login.component').then((m) => m.LoginComponent),
  },
  {
    path: '',
    pathMatch: 'full',
    loadComponent: () =>
      import('./pages/login/login.component').then((m) => m.LoginComponent),
  },
  {
    path: 'home',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./pages/home/home.component').then((m) => m.HomeComponent),
    children: [
      {
        path: '',
        pathMatch: 'full',
        loadComponent: () =>
          import('./pages/home-chat/home-chat.component').then(
            (m) => m.HomeChatComponent,
          ),
      },
      {
        path: 'buscar-conversas',
        loadComponent: () =>
          import('./pages/pesq-conversas/pesq-conversas.component').then(
            (m) => m.PesqConversasComponent,
          ),
      },
      {
        path: 'pastas/:id',
        loadComponent: () =>
          import('./pages/pastas/dentro-pasta.component').then(
            (m) => m.DentroPastaComponent,
          ),
      },
      {
        path: 'pastas',
        loadComponent: () =>
          import('./pages/pastas/pastas.component').then(
            (m) => m.PastasComponent,
          ),
      },
    ],
  },
  {
    path: 'buscar-conversas',
    pathMatch: 'full',
    redirectTo: 'home/buscar-conversas',
  },
  {
    path: 'pastas/:id',
    pathMatch: 'full',
    redirectTo: 'home/pastas/:id',
  },
  {
    path: 'pastas',
    pathMatch: 'full',
    redirectTo: 'home/pastas',
  },
  {
    path: '**',
    redirectTo: '',
  },
];

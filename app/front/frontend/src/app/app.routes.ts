import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { authGuard } from './guards/auth.guard';
import { LandingComponent } from './components/landing/landing.component';
import { ColectionComponent } from './components/colection/colection.component';
import { OutfitComponent } from './components/outfit/outfit.component';
import { SettingsComponent } from './components/settings/settings.component';

export const routes: Routes = [
  // Rutas públicas
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },

  // Ruta protegida
  { 
    path: 'dashboard', 
    component: DashboardComponent, 
    canActivate: [authGuard],
    children: [
      { path: 'landing', component: LandingComponent },
      { path: 'colection', component: ColectionComponent },
      { path: 'outfit', component: OutfitComponent },
      { path: 'settings', component: SettingsComponent },
      { path: '', redirectTo: 'landing', pathMatch: 'full' } 
    ]
  },

  // Redirecciones por defecto
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: '**', redirectTo: '/login' }
];
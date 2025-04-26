import { Routes } from '@angular/router';
import { HomeComponent } from './components/pages/home/home.component';
import { UsersComponent } from './components/pages/users/users.component';
export const routes: Routes =  [
  { path: '', component: HomeComponent },
  { path: 'users', component: UsersComponent},
  // Add other routes here
  { path: '**', redirectTo: '' }
];

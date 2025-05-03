import { Routes } from '@angular/router';
import { HomeComponent } from './components/pages/home/home.component';
import { UsersComponent } from './components/pages/users/users.component';
import { BanksComponent } from './components/pages/banks/banks.component';
import { AccountsComponent } from './components/pages/accounts/accounts.component';
import { NotFoundComponent } from './components/pages/not-found/not-found.component';
export const routes: Routes =  [
  { path: '', component: HomeComponent },
  { path: 'users', component: UsersComponent},
  { path: 'banks', component: BanksComponent},
  { path: 'accounts', component: AccountsComponent},
  { path: 'not-found', component: NotFoundComponent },
  // Add other routes here
  { path: '**', redirectTo: '/not-found', pathMatch: 'full' } // Redirect to not-found route
];

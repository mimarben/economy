import { Routes } from '@angular/router';
import { HomeComponent } from './components/pages/home/home.component';
import { UsersComponent } from './components/pages/users/users.component';
import { BanksComponent } from './components/pages/banks/banks.component';
import { AccountsComponent } from './components/pages/banks/accounts/accounts.component';
import { HouseholdsComponent } from './components/pages/households/households.component';
import { HouseholdmembersComponent } from './components/pages/households/householdmembers/householdmembers.component';
import { SavingsComponent } from './components/pages/savings/savings.component';
import { SavingsLogComponent } from './components/pages/savings/savings-log/savings-log/savings-log.component';
import { SourcesComponent } from './components/pages/savings/sources/sources.component';
import { NotFoundComponent } from './components/pages/not-found/not-found.component';
export const routes: Routes =  [
  { path: '', component: HomeComponent },
  { path: 'users', component: UsersComponent},
  { path: 'banks', component: BanksComponent},
  { path: 'accounts', component: AccountsComponent},
  { path: 'households', component: HouseholdsComponent},
  { path: 'households-members', component: HouseholdmembersComponent},
  { path: 'sources', component: SourcesComponent},
  { path: 'savings_log', component: SavingsLogComponent},
  { path: 'savings', component: SavingsComponent},
  { path: 'not-found', component: NotFoundComponent },
  // Add other routes here
  { path: '**', redirectTo: '/not-found', pathMatch: 'full' } // Redirect to not-found route
];

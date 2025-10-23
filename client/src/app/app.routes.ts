import { Routes } from '@angular/router';
import { HomeComponent } from './components/pages/home/home.component';
import { UsersComponent } from './components/pages/users/users.component';
import { BanksComponent } from './components/pages/banks/banks.component';
import { BanksAccountsComponent } from './components/pages/banks/banks-accounts/banks-accounts.component';
import { HouseholdsComponent } from './components/pages/households/households.component';
import { HouseholdmembersComponent } from './components/pages/households/householdmembers/householdmembers.component';
import { SavingsComponent } from './components/pages/savings/savings.component';
import { SavingsLogComponent } from './components/pages/savings/savings-log/savings-log/savings-log.component';
import { SourcesComponent } from './components/pages/savings/sources/sources.component';
import { InvestmentsComponent } from './components/pages/investments/investments.component';
import { InvestmentsLogComponent } from './components/pages/investments/investments-log/investments-log.component';
import { InvestmentsCategoriesComponent } from './components/pages/investments/investments-categories/investments-categories.component';
import { NotFoundComponent } from './components/pages/not-found/not-found.component';

export const routes: Routes =  [
  { path: '', component: HomeComponent, data: { title: 'home.title' } },
  { path: 'users', component: UsersComponent, data: { title: 'users.title' }},
  { path: 'banks', component: BanksComponent, data: { title: 'banks.title' } },
  { path: 'accounts', component: BanksAccountsComponent, data: { title: 'accounts.title' } },
  { path: 'households', component: HouseholdsComponent, data: { title: 'households.title' } },
  { path: 'households_members', component: HouseholdmembersComponent, data: { title: 'households_members.title' } },
  { path: 'savings', component: SavingsComponent, data: { title: 'savings.title' } },
  { path: 'sources', component: SourcesComponent, data: { title: 'sources.title' } },
  { path: 'savings_log', component: SavingsLogComponent, data: { title: 'savings_log.title' } },
  { path: 'investments', component: InvestmentsComponent, data: { title: 'investments.title' } },
  { path: 'investments_categories', component: InvestmentsCategoriesComponent, data: { title: 'investments_categories.title' } },
  { path: 'investments_log', component: InvestmentsLogComponent, data: { title: 'investments_log.title' } },
  { path: 'not_found', component: NotFoundComponent, data: { title: 'not_found.title' }  },
  // Add other routes here
  { path: '**', redirectTo: '/not-found', pathMatch: 'full' } // Redirect to not-found route
];

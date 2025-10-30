import { Routes } from '@angular/router';
import { HomeComponent } from './components/pages/home/home.component';
import { UsersComponent } from './components/pages/users/users.component';
import { ExpensesComponent } from './components/pages/expenses/expeneses.component';
import { ExepensesCategoriesComponent } from './components/pages/expenses/expenses-categories/expenses-categories.component';
import { PlacesCategoriesComponent } from './components/pages/expenses/places-categories/places-categories.component';
import { IncomesComponent } from './components/pages/incomes/incomes-component';
import { IncomesCategoriesComponent } from './components/pages/incomes/incomes-categories/incomes-categories';
import { BanksComponent } from './components/pages/banks/banks.component';
import { BanksAccountsComponent } from './components/pages/banks/banks-accounts/banks-accounts.component';
import { HouseholdsComponent } from './components/pages/households/households.component';
import { HouseholdmembersComponent } from './components/pages/households/household-members/household-members.component';
import { SavingsComponent } from './components/pages/savings/savings.component';
import { SavingsLogComponent } from './components/pages/savings/savings-log/savings-log/savings-log.component';
import { SourcesComponent } from './components/pages/sources/sources.component';
import { InvestmentsComponent } from './components/pages/investments/investments.component';
import { InvestmentsLogComponent } from './components/pages/investments/investments-log/investments-log.component';
import { InvestmentsCategoriesComponent } from './components/pages/investments/investments-categories/investments-categories.component';
import { NotFoundComponent } from './components/pages/not-found/not-found.component';
import { SummaryComponent} from './components/pages/financial/summary-component/summary-component';

export const routes: Routes =  [
  { path: '', component: HomeComponent, data: { title: 'home.title' } },
  { path: 'users', component: UsersComponent, data: { title: 'users.title' }},
  { path: 'banks', component: BanksComponent, data: { title: 'banks.title' } },
  { path: 'accounts', component: BanksAccountsComponent, data: { title: 'accounts.title' } },
  { path: 'households', component: HouseholdsComponent, data: { title: 'households.title' } },
  { path: 'households_members', component: HouseholdmembersComponent, data: { title: 'households_members.title' } },
  { path: 'savings', component: SavingsComponent, data: { title: 'savings.title' } },
  { path: 'savings_log', component: SavingsLogComponent, data: { title: 'savings_log.title' } },
  { path: 'sources', component: SourcesComponent, data: { title: 'sources.title' } },
  { path: 'expenses', component: ExpensesComponent, data: { title: 'expenses.title' } },
  { path: 'expenses_categories', component: ExepensesCategoriesComponent, data: { title: 'expenses_categories.title' } },
  { path: 'places', component: PlacesCategoriesComponent, data: { title: 'palces.title' } },
  { path: 'incomes', component: IncomesComponent, data: { title: 'incomes.title' } },
  { path: 'incomes_categories', component: IncomesCategoriesComponent, data: { title: 'incomes_categories.title' } },
  { path: 'investments', component: InvestmentsComponent, data: { title: 'investments.title' } },
  { path: 'investments_categories', component: InvestmentsCategoriesComponent, data: { title: 'investments_categories.title' } },
  { path: 'investments_log', component: InvestmentsLogComponent, data: { title: 'investments_log.title' } },
  { path: 'financial_summary', component: SummaryComponent, data: { title: 'summary.title' } },
  { path: 'not_found', component: NotFoundComponent, data: { title: 'not_found.title' }  },
  // Add other routes here
  { path: '**', redirectTo: '/not-found', pathMatch: 'full' } // Redirect to not-found route
];

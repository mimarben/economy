import { Routes } from '@angular/router';
import { HomeComponent } from './features/home/home.component';
import { authGuard } from './core/guards/auth.guard';
import { UsersComponent } from '@components/users/users.component';
import { ExpensesComponent } from './features/expenses/expeneses.component';
import { IncomesComponent } from  './features/incomes/incomes-component'
import { IncomesCategoriesComponent } from './features/incomes/incomes-categories/incomes-categories.component';
import { ExpensesCategoriesComponent } from './features/expenses/expenses-categories/expenses-categories.component';
import { BanksComponent } from './features/banks/banks.component';
import { BanksAccountsComponent } from './features/banks/banks-accounts/banks-accounts.component';
import { HouseholdsComponent } from './features/households/households.component';
import { HouseholdmembersComponent } from './features/households/household-members/household-members.component';
import { SavingsComponent } from './features/savings/savings.component';
import { SavingsLogComponent } from './features/savings/savings-log/savings-log/savings-log.component';
import { SourcesComponent } from './features/sources/sources.component';
import { InvestmentsComponent } from './features/investments/investments.component';
import { InvestmentsLogComponent } from './features/investments/investments-log/investments-log.component';
import { InvestmentsCategoriesComponent } from './features/investments/investments-categories/investments-categories.component';
import { NotFoundComponent } from './features/not-found/not-found.component';
import { SummaryComponent} from './features/financial/summary-component/summary-component';
import { ExcelImportComponent } from './features/import/excel/excel-import.component';
import { LoginComponent } from './features/auth/login/login.component';
import { LayoutComponent } from './core/layout/layout/layout.component';
export const routes: Routes = [
  // Rutas SIN layout
  { path: 'login', component: LoginComponent, data: { title: 'login.title' } },
  { path: 'not_found', component: NotFoundComponent, data: { title: 'not_found.title' } },

  // Rutas CON layout (header + footer + menu)
  {
    path: '',
    component: LayoutComponent,
    canActivate: [authGuard], // authGuard aquí una sola vez para todas
    children: [
      { path: '', component: HomeComponent, data: { title: 'home.title' } },
      { path: 'users', component: UsersComponent, data: { title: 'users.title' } },
      { path: 'banks', component: BanksComponent, data: { title: 'banks.title' } },
      { path: 'accounts', component: BanksAccountsComponent, data: { title: 'accounts.title' } },
      { path: 'households', component: HouseholdsComponent, data: { title: 'households.title' } },
      { path: 'households_members', component: HouseholdmembersComponent, data: { title: 'households_members.title' } },
      { path: 'savings', component: SavingsComponent, data: { title: 'savings.title' } },
      { path: 'savings_log', component: SavingsLogComponent, data: { title: 'savings_log.title' } },
      { path: 'sources', component: SourcesComponent, data: { title: 'sources.title' } },
      { path: 'expenses', component: ExpensesComponent, data: { title: 'expenses.title' } },
      { path: 'expenses_categories', component: ExpensesCategoriesComponent, data: { title: 'expenses_categories.title' } },
      { path: 'incomes', component: IncomesComponent, data: { title: 'incomes.title' } },
      { path: 'incomes_categories', component: IncomesCategoriesComponent, data: { title: 'incomes_categories.title' } },
      { path: 'investments', component: InvestmentsComponent, data: { title: 'investments.title' } },
      { path: 'investments_categories', component: InvestmentsCategoriesComponent, data: { title: 'investments_categories.title' } },
      { path: 'investments_log', component: InvestmentsLogComponent, data: { title: 'investments_log.title' } },
      { path: 'financial_summary', component: SummaryComponent, data: { title: 'summary.title' } },
      { path: 'excel_import', component: ExcelImportComponent, data: { title: 'excel_import.title' } },
    ]
  },

  { path: '**', redirectTo: '/not_found', pathMatch: 'full' }
];

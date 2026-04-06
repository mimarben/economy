import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { LayoutComponent } from './layout/layout/layout.component';

export const routes: Routes = [
  // Routes without layout
  { path: 'login', loadComponent: () => import('./features/auth/login/login.component').then((m) => m.LoginComponent), data: { title: 'login.title' } },
  { path: 'not_found', loadComponent: () => import('./features/not-found/not-found.component').then((m) => m.NotFoundComponent), data: { title: 'not_found.title' } },

  // Routes with layout (header + footer + menu)
  {
    path: '',
    component: LayoutComponent,
    canActivate: [authGuard], // Single guard for all children
    children: [
      { path: '', loadComponent: () => import('./features/home/home.component').then((m) => m.HomeComponent), data: { title: 'home.title' } },
      { path: 'users', loadComponent: () => import('./features/users/users.component').then((m) => m.UsersComponent), data: { title: 'users.title' } },
      { path: 'banks', loadComponent: () => import('./features/banks/banks.component').then((m) => m.BanksComponent), data: { title: 'banks.title' } },
      { path: 'accounts', loadComponent: () => import('./features/banks/banks-accounts/banks-accounts.component').then((m) => m.BanksAccountsComponent), data: { title: 'accounts.title' } },
      { path: 'households', loadComponent: () => import('./features/households/households.component').then((m) => m.HouseholdsComponent), data: { title: 'households.title' } },
      { path: 'household-members', loadComponent: () => import('./features/households/household-members/household-members.component').then((m) => m.HouseholdmembersComponent), data: { title: 'households_members.title' } },
      { path: 'savings', loadComponent: () => import('./features/savings/savings.component').then((m) => m.SavingsComponent), data: { title: 'savings.title' } },
      { path: 'savings_log', loadComponent: () => import('./features/savings/savings-log/savings-log/savings-log.component').then((m) => m.SavingsLogComponent), data: { title: 'savings_log.title' } },
      { path: 'sources', loadComponent: () => import('./features/sources/sources.component').then((m) => m.SourcesComponent), data: { title: 'sources.title' } },
      { path: 'expenses', loadComponent: () => import('./features/expenses/expenses.component').then((m) => m.ExpensesComponent), data: { title: 'expenses.title' } },
      { path: 'expenses_categories', loadComponent: () => import('./features/expenses/expenses-categories/expenses-categories.component').then((m) => m.ExpensesCategoriesComponent), data: { title: 'expenses_categories.title' } },
      { path: 'incomes', loadComponent: () => import('./features/incomes/incomes-component').then((m) => m.IncomesComponent), data: { title: 'incomes.title' } },
      { path: 'incomes_categories', loadComponent: () => import('./features/incomes/incomes-categories/incomes-categories.component').then((m) => m.IncomesCategoriesComponent), data: { title: 'incomes_categories.title' } },
      { path: 'investments', loadComponent: () => import('./features/investments/investments.component').then((m) => m.InvestmentsComponent), data: { title: 'investments.title' } },
      { path: 'investments_categories', loadComponent: () => import('./features/investments/investments-categories/investments-categories.component').then((m) => m.InvestmentsCategoriesComponent), data: { title: 'investments_categories.title' } },
      { path: 'investments_log', loadComponent: () => import('./features/investments/investments-log/investments-log.component').then((m) => m.InvestmentsLogComponent), data: { title: 'investments_log.title' } },
      { path: 'financial_summary', loadComponent: () => import('./features/financial/summary-component/summary-component').then((m) => m.SummaryComponent), data: { title: 'summary.title' } },
      { path: 'excel_import', loadComponent: () => import('./features/import/excel/excel-import.component').then((m) => m.ExcelImportComponent), data: { title: 'excel_import.title' } },
      { path: 'import_origins', loadComponent: () => import('./features/import/origins/import-origins.component').then((m) => m.ImportOriginsComponent), data: { title: 'import_origins.title' } },
      { path: 'import_profiles', loadComponent: () => import('./features/import/profiles/import-profiles.component').then((m) => m.ImportProfilesComponent), data: { title: 'import_profiles.title' } },
      { path: 'charts', loadComponent: () => import('./features/charts/components/charts-container/charts-container.component').then((m) => m.ChartsContainerComponent), data: { title: 'charts.title' } },
      { path: 'category_rules', loadComponent: () => import('./features/category-rules/category-rules.component').then((m) => m.CategoryRulesComponent), data: { title: 'category_rules.title' } },
      { path: 'cards', loadComponent: () => import('./features/cards/cards.component').then((m) => m.CardsComponent), data: { title: 'cards.title' } },
    ]
  },

  { path: '**', redirectTo: '/not_found', pathMatch: 'full' }
];

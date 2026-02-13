import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MaterialModule } from '../../../utils/material.module';

interface MenuLink {
  label: string;
  route: string;
  icon?: string;
  symbol?: string;
  exact?: boolean;
}

interface MenuSection {
  title: string;
  icon?: string;
  symbol?: string;
  links: MenuLink[];
}

@Component({
  selector: 'app-side-menu',
  imports: [MaterialModule, CommonModule, RouterModule],
  templateUrl: './side-menu.component.html',
  styleUrl: './side-menu.component.css'
})
export class SideMenuComponent {
  @Input() isHidden = false;

  readonly topLinks: MenuLink[] = [
    { label: 'Home', route: '/', icon: 'home', exact: true },
    { label: 'Users', route: '/users', icon: 'person' },
    { label: 'Import', route: '/excel_import', icon: 'upload' }
  ];

  readonly sections: MenuSection[] = [
    {
      title: 'Expenses',
      icon: 'credit_card',
      links: [
        { label: 'Expenses', route: '/expenses' },
        { label: 'Expenses Category', route: '/expenses_categories' },
        { label: 'Sources', route: '/sources' }
      ]
    },
    {
      title: 'Incomes',
      icon: 'attach_money',
      links: [
        { label: 'Incomes', route: '/incomes' },
        { label: 'Incomes Category', route: '/incomes_categories' },
        { label: 'Source', route: '/sources' }
      ]
    },
    {
      title: 'Investments',
      symbol: 'finance_mode',
      links: [
        { label: 'Investments', route: '/investments' },
        { label: 'Investments Category', route: '/investments_categories' },
        { label: 'Investments Log', route: '/investments_log' }
      ]
    },
    {
      title: 'Savings',
      symbol: 'savings',
      links: [
        { label: 'Savings', route: '/savings' },
        { label: 'Savings Log', route: '/savings_log' },
        { label: 'Source', route: '/sources' }
      ]
    },
    {
      title: 'House Hold',
      symbol: 'location_away',
      links: [
        { label: 'House Hold', route: '/households' },
        { label: 'HouseHold Members', route: '/households_members' }
      ]
    },
    {
      title: 'Banks',
      symbol: 'account_balance',
      links: [
        { label: 'Banks', route: '/banks' },
        { label: 'Accounts', route: '/accounts' }
      ]
    }
  ];

  readonly bottomLinks: MenuLink[] = [
    { label: 'Financial Summary', route: '/financial_summary', icon: 'assignment' }
  ];
}

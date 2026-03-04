import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MaterialModule } from '../../../utils/material.module';

interface MenuLink {
  label: string;
  route: string;
  icon?: string;
  exact?: boolean;
}

interface MenuSection {
  title: string;
  icon: string;
  links: MenuLink[];
}

const TOP_LINKS: MenuLink[] = [
  { label: 'Home',   route: '/',            icon: 'home',   exact: true },
  { label: 'Users',  route: '/users',       icon: 'person' },
  { label: 'Import', route: '/excel_import', icon: 'upload' }
];

const SECTIONS: MenuSection[] = [
  {
    title: 'Expenses',
    icon: 'credit_card',
    links: [
      { label: 'Expenses',          route: '/expenses' },
      { label: 'Expenses Category', route: '/expenses_categories' },
      { label: 'Sources',           route: '/sources' }
    ]
  },
  {
    title: 'Incomes',
    icon: 'attach_money',
    links: [
      { label: 'Incomes',          route: '/incomes' },
      { label: 'Incomes Category', route: '/incomes_categories' },
      { label: 'Sources',          route: '/sources' }
    ]
  },
  {
    title: 'Investments',
    icon: 'finance_mode',
    links: [
      { label: 'Investments',          route: '/investments' },
      { label: 'Investments Category', route: '/investments_categories' },
      { label: 'Investments Log',      route: '/investments_log' }
    ]
  },
  {
    title: 'Savings',
    icon: 'savings',
    links: [
      { label: 'Savings',     route: '/savings' },
      { label: 'Savings Log', route: '/savings_log' },
      { label: 'Sources',     route: '/sources' }
    ]
  },
  {
    title: 'House Hold',
    icon: 'location_away',
    links: [
      { label: 'House Hold',        route: '/households' },
      { label: 'HouseHold Members', route: '/households_members' }
    ]
  },
  {
    title: 'Banks',
    icon: 'account_balance',
    links: [
      { label: 'Banks',    route: '/banks' },
      { label: 'Accounts', route: '/accounts' }
    ]
  }
];

const BOTTOM_LINKS: MenuLink[] = [
  { label: 'Financial Summary', route: '/financial_summary', icon: 'assignment' }
];

@Component({
  selector: 'app-side-menu',
  standalone: true,
  imports: [CommonModule, RouterModule, MaterialModule],
  templateUrl: './side-menu.component.html',
  styleUrls: ['./side-menu.component.css']
})
export class SideMenuComponent {

  @Input() isHidden = false;

  readonly topLinks    = TOP_LINKS;
  readonly sections    = SECTIONS;
  readonly bottomLinks = BOTTOM_LINKS;
}

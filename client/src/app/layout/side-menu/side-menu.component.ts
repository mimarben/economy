import { Component, EventEmitter, Input, Output} from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MATERIAL_IMPORTS } from '@app/utils/material.imports';

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
  { label: 'Users',  route: '/users',       icon: 'person' }
];

const SECTIONS: MenuSection[] = [
  {
    title: 'Import',
    icon: 'upload',
    links: [
      { label: 'Excel Import', route: '/excel_import' },
      { label: 'Import Origins', route: '/import_origins' },
      { label: 'Import Profiles', route: '/import_profiles' }
    ]
  },
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
      { label: 'HouseHold Members', route: '/household-members' }
    ]
  },
  {
    title: 'Banks',
    icon: 'account_balance',
    links: [
      { label: 'Banks',    route: '/banks' },
      { label: 'Accounts', route: '/accounts' },
      { label: 'Cards',    route: '/cards' }
    ]
  },
  {
    title: 'Analytics',
    icon: 'bar_chart',
    links: [
      { label: 'Charts',            route: '/charts' },
      { label: 'Financial Summary', route: '/financial_summary' }
    ]
  },
  {
    title: 'Rules',
    icon: 'rule',
    links: [
      { label: 'Category Rules', route: '/category_rules' },
      { label: 'Source Rules',   route: '/source_rules' }
    ]
  }
];

const BOTTOM_LINKS: MenuLink[] = [];

@Component({
  selector: 'app-side-menu',
  standalone: true,
  imports: [CommonModule, RouterModule, ...MATERIAL_IMPORTS],
  templateUrl: './side-menu.component.html',
  styleUrls: ['./side-menu.component.scss']
})
export class SideMenuComponent {

  @Input() isExpanded = true;
  @Input() isShowing = false;

  @Output() toggleExpand = new EventEmitter<void>();

  expandedSections: Record<string, boolean> = {};

  readonly topLinks    = TOP_LINKS;
  readonly sections    = SECTIONS;
  readonly bottomLinks = BOTTOM_LINKS;

 /* toggleSection(title: string) {
    this.expandedSections[title] = !this.expandedSections[title];
  }
 */
}

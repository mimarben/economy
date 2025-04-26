import { Component, Input, } from '@angular/core';
import { MaterialModule } from '../../../material.module';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
@Component({
  selector: 'app-side-menu',
  imports: [
    MaterialModule,
    CommonModule,
    RouterModule
  ],
  templateUrl: './side-menu.component.html',
  styleUrl: './side-menu.component.css'
})


export class SideMenuComponent {
  @Input() isHidden = false;


  // In your component.ts
usersMenuOpen = false;
expensesMenuOpen = false;
incomesMenuOpen = false;
investmentsMenuOpen = false;
savingsMenuOpen = false;
householdsMenuOpen = false;
banksMenuOpen = false;
  usersSubmenu() {
    this.usersMenuOpen = !this.usersMenuOpen;
  }
  expensesSubmenu(){
    this.expensesMenuOpen = !this.expensesMenuOpen;
  }
  incomesSubmenu(){
    this.incomesMenuOpen = !this.incomesMenuOpen;
  }
  investmentsSubmenu(){
    this.investmentsMenuOpen = !this.investmentsMenuOpen;
  }
  savingsSubmenu() {
    this.savingsMenuOpen = !this.savingsMenuOpen;
  }
  householdsSubmenu() {
    this.householdsMenuOpen = !this.householdsMenuOpen;
  }
  banksSubmenu() {
    this.banksMenuOpen = !this.banksMenuOpen;
  }


}

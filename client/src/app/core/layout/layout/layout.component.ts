import { Component, OnInit, AfterViewInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ActivatedRoute, Router } from '@angular/router';

import { HeaderComponent } from '../header/header.component';
import { SideMenuComponent } from '../side-menu/side-menu.component';
import { FooterComponent } from '../footer/footer.component';

@Component({
  selector: 'app-layout',
  imports: [
    RouterOutlet,
    HeaderComponent,
    SideMenuComponent,
    FooterComponent
  ],
  templateUrl: './layout.component.html',
  styleUrl: './layout.component.css'
})
export class LayoutComponent {
  isSideMenuHidden = false;
  pageTitle = '';
  constructor(private router: Router, private activatedRoute: ActivatedRoute) {}
  setHeaderTitle() {
    let route = this.activatedRoute;
    while (route.firstChild) {
      route = route.firstChild;
    }
    this.pageTitle = route.snapshot.data['title'] || '';
  }

  handleToggleSideMenu() {
    this.isSideMenuHidden = !this.isSideMenuHidden;
  }


}

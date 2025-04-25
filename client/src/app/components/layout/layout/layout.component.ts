import { Component, OnInit, AfterViewInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';


import { TopMenuComponent } from '../top-menu/top-menu.component';
import { SideMenuComponent } from '../side-menu/side-menu.component';
import { FooterComponent } from '../footer/footer.component';

@Component({
  selector: 'app-layout',
  imports: [
    RouterOutlet,
    TopMenuComponent,
    SideMenuComponent,
    FooterComponent
  ],
  templateUrl: './layout.component.html',
  styleUrl: './layout.component.css'
})
export class LayoutComponent {
  ngOnInit() {
    console.log('LayoutComponent initialized');
  }

  ngAfterViewInit() {
    console.log('LayoutComponent view initialized');
  }
}

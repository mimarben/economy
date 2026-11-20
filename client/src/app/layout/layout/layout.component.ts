import { Component, OnInit, OnDestroy } from '@angular/core';
import { BreakpointObserver } from '@angular/cdk/layout';
import { RouterOutlet } from '@angular/router';
import { ActivatedRoute, Router, NavigationEnd } from '@angular/router';
import { CommonModule } from '@angular/common';
import { filter, Subscription } from 'rxjs';
import { MATERIAL_IMPORTS } from '@utils_module/material.imports';
import { HeaderComponent } from '../header/header.component';
import { SideMenuComponent } from '../side-menu/side-menu.component';
import { FooterComponent } from '../footer/footer.component';


@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    HeaderComponent,
    SideMenuComponent,
    FooterComponent,
    ...MATERIAL_IMPORTS,
  ],
  templateUrl: './layout.component.html',
  styleUrl: './layout.component.scss',
})
export class LayoutComponent implements OnInit, OnDestroy {
  pageTitle = '';
  sidenavMode: 'side' | 'over' = 'side';
  sidenavOpened = true;

  private routerSubscription?: Subscription;
  private breakpointSubscription?: Subscription;

  constructor(
    private router: Router,
    private activatedRoute: ActivatedRoute,
    private breakpointObserver: BreakpointObserver,
  ) {}

  ngOnInit() {
    this.setHeaderTitle(); // Set initial title
    this.breakpointSubscription = this.breakpointObserver
      .observe('(max-width: 600px)')
      .subscribe(({ matches }) => {
        this.sidenavMode = matches ? 'over' : 'side';
        this.sidenavOpened = !matches;
      });

    this.routerSubscription = this.router.events
      .pipe(filter((event) => event instanceof NavigationEnd))
      .subscribe((event: NavigationEnd) => {
        this.setHeaderTitle();
        if (this.sidenavMode === 'over') {
          this.sidenavOpened = false;
        }
      });
  }

  ngOnDestroy() {
    this.routerSubscription?.unsubscribe();
    this.breakpointSubscription?.unsubscribe();
  }

  setHeaderTitle() {
    let route = this.activatedRoute;
    while (route.firstChild) {
      route = route.firstChild;
    }
    this.pageTitle = route.snapshot.data['title'] || '';
  }
}

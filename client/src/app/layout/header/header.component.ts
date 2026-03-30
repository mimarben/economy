import { Component, Output, Input, EventEmitter } from '@angular/core';
import { MATERIAL_IMPORTS } from '@app/utils/material.imports';
import { SHARED_IMPORTS } from '@app/utils/shared.imports';
import { AuthService } from '@services/auth/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-header',
  standalone:true,
  imports: [
    ...MATERIAL_IMPORTS,
    ...SHARED_IMPORTS
  ],
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss'
})
export class HeaderComponent {
  @Output() toggleSidenav = new EventEmitter<void>()
  @Input() title: string = '';

  constructor(
    private authService: AuthService,
    private router: Router
  ){}

  toggleMenu(){
    this.toggleSidenav.emit();
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}

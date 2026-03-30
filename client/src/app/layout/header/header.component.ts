import { Component, Output, Input, EventEmitter } from '@angular/core';
import { MaterialModule } from '@app/utils/material.module';
import { TranslateModule } from '@ngx-translate/core';
import { AuthService } from '@services/auth/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-header',
  standalone:true,
  imports: [
    MaterialModule,
    TranslateModule
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

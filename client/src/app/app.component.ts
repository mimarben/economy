import { Component, HostListener } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { AuthService } from '@auth_services/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, TranslateModule],
  template: `<router-outlet></router-outlet>`
})
export class AppComponent {
  constructor(
    private authService: AuthService
  ){}

  @HostListener('document:click')
  @HostListener('document:keydown')
  @HostListener('document:touchstart')
  @HostListener('document:touchmove')
  @HostListener('document:mousemove')
  @HostListener('document:pointerdown')
  @HostListener('window:scroll')
  @HostListener('window:wheel')
  trackActivity(): void {
    this.authService.registerUserActivity();
  }

  @HostListener('document:visibilitychange')
  onVisibilityChange(): void {
    if (document.visibilityState === 'visible') {
      this.authService.registerUserActivity();
    }
  }
}

import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { AppTranslateService } from '@utils/app-translate.service';
import { SessionActivityService } from '@core_services/auth/session-activity.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, TranslateModule],
  template: `<router-outlet></router-outlet>`
})
export class AppComponent {
  constructor(
    private translateService: AppTranslateService,
    private sessionActivityService: SessionActivityService
  ){
    this.sessionActivityService.startTracking();
  }
}

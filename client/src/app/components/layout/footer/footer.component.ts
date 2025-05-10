import { Component } from '@angular/core';
import { MaterialModule } from '../../../utils/utils/material.module';

import { TranslateModule } from '@ngx-translate/core';
@Component({
  selector: 'app-footer',
  imports: [
    MaterialModule,
    TranslateModule
  ],
  templateUrl: './footer.component.html',
  styleUrl: './footer.component.css'
})
export class FooterComponent {

}

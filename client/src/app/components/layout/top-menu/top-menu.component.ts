import { Component, Output, EventEmitter } from '@angular/core';
import { MaterialModule } from '../../../material.module';
@Component({
  selector: 'app-top-menu',
  imports: [
    MaterialModule
  ],
  templateUrl: './top-menu.component.html',
  styleUrl: './top-menu.component.css'
})
export class TopMenuComponent {
  @Output() toggleSidenav = new EventEmitter<void>()
}

import { Component, Output, Input, EventEmitter } from '@angular/core';
import { MaterialModule } from '@utils/material.module';
import { UtilsModule } from '@utils/utils.module';
@Component({
  selector: 'app-header',
  standalone:true,
  imports: [
    MaterialModule,
    UtilsModule
  ],
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss'
})
export class HeaderComponent {
  @Output() toggleSidenav = new EventEmitter<void>()
  @Input() title: string = '';
  constructor(){}
  toggleMenu(){
    this.toggleSidenav.emit();
  }
}

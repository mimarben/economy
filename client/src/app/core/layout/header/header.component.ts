import { Component, Output, Input, EventEmitter, OnChanges, SimpleChanges } from '@angular/core';
import { MaterialModule } from '../../../utils/material.module';
import { AppTranslateService } from '../../../utils/app-translate.service';
import { UtilsModule } from '../../../utils/utils.module';
@Component({
  selector: 'app-header',
  imports: [
    MaterialModule,
    UtilsModule
  ],
  templateUrl: './header.component.html',
  styleUrl: './header.component.css'
})
export class HeaderComponent implements OnChanges{
  @Output() toggleSidenav = new EventEmitter<void>()
  @Input() title: string = '';
  constructor(private translateService: AppTranslateService){}
  ngOnChanges(changes: SimpleChanges) {
    if (changes['title']) {
      console.log('Title changed:', this.translateService.translateKey(this.title));
    }
  }
}

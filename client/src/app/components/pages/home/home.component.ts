import { Component } from '@angular/core';
import { MaterialModule } from '../../../utils/material.module';
import { CommonModule } from '@angular/common';

import { AppTranslateService } from '../../../utils/app-translate.service';
import { LanguageBase as Language } from '../../../models/LanguageBase';
import { TranslateModule } from '@ngx-translate/core';
@Component({
  selector: 'app-home',
  imports: [
    MaterialModule,
    CommonModule,
    TranslateModule
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent {
  languages: Language[] = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'es', name: 'Español', flag: '🇪🇸' }
  ];

  currentLanguage: string;

  constructor(private translateService: AppTranslateService) {
    this.currentLanguage = translateService.getCurrentLanguage();
  }

  ngOnInit(): void {
    // Filtrar solo los idiomas disponibles en la configuración
    const availableLanguages = this.translateService.getAvailableLanguages();
    this.languages = this.languages.filter(lang =>
      availableLanguages.includes(lang.code)
    );
  }

  changeLanguage(langCode: string): void {
    this.translateService.setLanguage(langCode);
    this.currentLanguage = langCode;
  }
}

// app-translate.service.ts
import { Injectable } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { Observable, firstValueFrom } from 'rxjs';
import { environment } from '@env/environment';
@Injectable({
  providedIn: 'root'
})
export class AppTranslateService {
  private availableLanguages: string[] = environment.i18n.availableLanguages;
  private defaultLanguage: string = environment.i18n.defaultLanguage;

  constructor(private translate: TranslateService) {
    this.initialize();
  }

  /**
   * Initialize translation service
   */
  initialize(): void {
    // Comment translated to English.
    this.translate.addLangs(this.availableLanguages);

    // Comment translated to English.
    this.translate.setDefaultLang(this.defaultLanguage);

    // Comment translated to English.
    const savedLang = localStorage.getItem('preferredLanguage');

    if (savedLang && this.availableLanguages.includes(savedLang)) {
      this.translate.use(savedLang);
    } else {
      // Comment translated to English.
      const browserLang = this.translate.getBrowserLang();
      if (browserLang && this.availableLanguages.includes(browserLang)) {
        this.translate.use(browserLang);
      } else {
        this.translate.use(this.defaultLanguage);
      }
    }
  }

  /**
   * Change application language
   * @param lang Language code to use
   */
  setLanguage(lang: string): void {
    if (this.availableLanguages.includes(lang)) {
      this.translate.use(lang);
      // Persist preference in localStorage
      localStorage.setItem('preferredLanguage', lang);
    } else {
      console.warn(`Language "${lang}" is not available`);
    }
  }

  /**
   * Get current language
   * @returns Current language code
   */
  getCurrentLanguage(): string {
    return this.translate.currentLang || this.defaultLanguage;
  }

  /**
   * Get all available languages
   * @returns Array with available language codes
   */
  getAvailableLanguages(): string[] {
    return this.availableLanguages;
  }

  /**
   * Translate a key (synchronous)
   * @param key Translation key
   * @param params Translation parameters (optional)
   * @returns Translated text
   */
  translateKey(key: string, params?: object): string {
    if (!key){return 'error translation'}
    return this.translate.instant(key, params);
  }

  /**
   * Translate a key (asynchronous)
   * @param key Translation key
   * @param params Translation parameters (optional)
   * @returns Promise with translated text
   */
  async translateKeyAsync(key: string, params?: object): Promise<string> {
    return await firstValueFrom(this.translate.get(key, params));
  }

  /**
   * Get an observable for key translation
   * @param key Translation key
   * @param params Translation parameters (optional)
   * @returns Observable with translated text
   */
  getTranslation(key: string, params?: object): Observable<string> {
    return this.translate.get(key, params);
  }

  /**
   * Subscribe to language changes
   * @returns Observable emitted on language changes
   */
  onLangChange(): Observable<any> {
    return this.translate.onLangChange;
  }
}

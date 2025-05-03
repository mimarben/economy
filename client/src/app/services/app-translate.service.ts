// app-translate.service.ts
import { Injectable } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { Observable, firstValueFrom } from 'rxjs';
import { environment } from '../../environments/environment';

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
   * Inicializa el servicio de traducción
   */
  initialize(): void {
    // Establece idiomas disponibles
    this.translate.addLangs(this.availableLanguages);

    // Establece el idioma por defecto
    this.translate.setDefaultLang(this.defaultLanguage);

    // Intenta cargar idioma guardado previamente
    const savedLang = localStorage.getItem('preferredLanguage');

    if (savedLang && this.availableLanguages.includes(savedLang)) {
      this.translate.use(savedLang);
    } else {
      // Intenta detectar el idioma del navegador
      const browserLang = this.translate.getBrowserLang();
      if (browserLang && this.availableLanguages.includes(browserLang)) {
        this.translate.use(browserLang);
      } else {
        this.translate.use(this.defaultLanguage);
      }
    }
  }

  /**
   * Cambia el idioma de la aplicación
   * @param lang Código del idioma a utilizar
   */
  setLanguage(lang: string): void {
    if (this.availableLanguages.includes(lang)) {
      this.translate.use(lang);
      // Guardar preferencia en localStorage
      localStorage.setItem('preferredLanguage', lang);
    } else {
      console.warn(`El idioma "${lang}" no está disponible`);
    }
  }

  /**
   * Obtiene el idioma actual
   * @returns Código del idioma actual
   */
  getCurrentLanguage(): string {
    return this.translate.currentLang || this.defaultLanguage;
  }

  /**
   * Obtiene todos los idiomas disponibles
   * @returns Array con códigos de idiomas disponibles
   */
  getAvailableLanguages(): string[] {
    return this.availableLanguages;
  }

  /**
   * Traduce una clave (sincrónico)
   * @param key Clave de traducción
   * @param params Parámetros para la traducción (opcional)
   * @returns Texto traducido
   */
  translateKey(key: string, params?: object): string {
    return this.translate.instant(key, params);
  }

  /**
   * Traduce una clave (asincrónico)
   * @param key Clave de traducción
   * @param params Parámetros para la traducción (opcional)
   * @returns Promesa con el texto traducido
   */
  async translateKeyAsync(key: string, params?: object): Promise<string> {
    return await firstValueFrom(this.translate.get(key, params));
  }

  /**
   * Obtiene un observable para la traducción de una clave
   * @param key Clave de traducción
   * @param params Parámetros para la traducción (opcional)
   * @returns Observable con el texto traducido
   */
  getTranslation(key: string, params?: object): Observable<string> {
    return this.translate.get(key, params);
  }

  /**
   * Suscribirse a cambios de idioma
   * @returns Observable que emite cuando cambia el idioma
   */
  onLangChange(): Observable<any> {
    return this.translate.onLangChange;
  }
}

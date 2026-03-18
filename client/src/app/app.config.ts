import { ApplicationConfig, provideZoneChangeDetection, ErrorHandler } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, HTTP_INTERCEPTORS, withInterceptorsFromDi } from '@angular/common/http';

import { routes } from './app.routes';
import { provideHotToastConfig } from '@ngxpert/hot-toast';

import { provideTranslateService } from '@ngx-translate/core';
import { provideTranslateHttpLoader } from '@ngx-translate/http-loader';


import { environment } from '../environments/environment';
import { HttpInterceptorService } from '@core_services/http.interceptor';
import { ErrorHandlerService } from '@core_services/error-handler.service';


export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),

    provideRouter(routes),

    provideHttpClient(withInterceptorsFromDi()),

    provideTranslateService({
      defaultLanguage: environment.i18n.defaultLanguage,
      loader: provideTranslateHttpLoader({
        prefix: './assets/i18n/',
        suffix: '.json'
      })
    }),

    provideHotToastConfig(),

    // ✅ Register Global HTTP Interceptor
    {
      provide: HTTP_INTERCEPTORS,
      useClass: HttpInterceptorService,
      multi: true,
    },

    // ✅ Register Global Error Handler
    {
      provide: ErrorHandler,
      useClass: ErrorHandlerService,
    }
  ]
};

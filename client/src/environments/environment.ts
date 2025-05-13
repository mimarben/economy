export enum ToastType {
  Success = 'success',
  Error = 'error',
  Warning = 'warning',
  Info = 'info',
}

export const environment = {
  production: false,
  apiUrl: 'http://localhost:5001/api',
  headers: {
    'Content-Type': 'application/json'
  },
  toastType: {
    Success: ToastType.Success,
    Error: ToastType.Error,
    Warning: ToastType.Warning,
    Info: ToastType.Info
  },
  i18n: {
    defaultLanguage: 'en',
    availableLanguages: ['en', 'es',]
  },
  date_formats:{
    parse: { dateInput: 'DD-MM-YYYY' },
    display: {
      dateInput: 'DD-MM-YYYY',
      monthYearLabel: 'MMM YYYY',
      dateA11yLabel: 'DD-MM-YYYY',
      monthYearA11yLabel: 'MMMM YYYY',
  }
  },
  locations:{
    defaultLocation: "es-ES",
    availableLocations: ["es-ES", "en-GB", "en-US"]
  }
};
